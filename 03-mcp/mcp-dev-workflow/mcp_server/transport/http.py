"""
HTTP transport implementation for MCP communication using FastAPI.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mcp_server.core.protocol import (
    JSONRPCError,
    JSONRPCErrorCodes,
    JSONRPCRequest,
    JSONRPCResponse,
    deserialize_request,
    serialize_message,
)
from mcp_server.transport.base import Transport

logger = logging.getLogger(__name__)


class HTTPTransport(Transport):
    """Transport implementation using HTTP with FastAPI for JSON-RPC communication."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        """
        Initialize HTTP transport.
        
        Args:
            host: Host address to bind to
            port: Port number to bind to
        """
        self.host = host
        self.port = port
        self._running = False
        self._server: Optional[uvicorn.Server] = None
        self._app: Optional[FastAPI] = None
        self._request_queue: asyncio.Queue[JSONRPCRequest] = asyncio.Queue()
        self._response_futures: dict[str, asyncio.Future[JSONRPCResponse]] = {}
        self._shutdown_event = asyncio.Event()

    def _create_app(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Manage application lifespan."""
            logger.info("HTTP transport application starting")
            yield
            logger.info("HTTP transport application shutting down")
            self._shutdown_event.set()

        app = FastAPI(
            title="MCP HTTP Server",
            description="Model Context Protocol HTTP Transport",
            version="1.0.0",
            lifespan=lifespan
        )

        # Add CORS middleware for cross-origin requests
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify actual origins
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )

        @app.post("/jsonrpc")
        async def handle_jsonrpc(request: Request) -> Response:
            """Handle JSON-RPC requests over HTTP."""
            try:
                # Read request body
                body = await request.body()
                if not body:
                    raise HTTPException(status_code=400, detail="Empty request body")

                # Parse JSON-RPC request
                try:
                    request_data = body.decode('utf-8')
                    jsonrpc_request = deserialize_request(request_data)
                except ValueError as e:
                    # Return JSON-RPC parse error
                    error_response = JSONRPCResponse.create_error(
                        JSONRPCError(
                            code=JSONRPCErrorCodes.PARSE_ERROR,
                            message=f"Parse error: {str(e)}"
                        ),
                        None
                    )
                    return JSONResponse(
                        content=error_response.to_dict(),
                        status_code=200  # JSON-RPC errors use 200 status
                    )

                # Queue the request for processing
                await self._request_queue.put(jsonrpc_request)

                # Wait for response if request has an ID (not a notification)
                if jsonrpc_request.id is not None:
                    # Create future for response
                    response_future: asyncio.Future[JSONRPCResponse] = asyncio.Future()
                    self._response_futures[str(jsonrpc_request.id)] = response_future

                    try:
                        # Wait for response with timeout
                        response = await asyncio.wait_for(response_future, timeout=30.0)
                        return JSONResponse(
                            content=response.to_dict(),
                            status_code=200
                        )
                    except asyncio.TimeoutError:
                        # Clean up future and return timeout error
                        self._response_futures.pop(str(jsonrpc_request.id), None)
                        error_response = JSONRPCResponse.create_error(
                            JSONRPCError(
                                code=JSONRPCErrorCodes.INTERNAL_ERROR,
                                message="Request timeout"
                            ),
                            jsonrpc_request.id
                        )
                        return JSONResponse(
                            content=error_response.to_dict(),
                            status_code=200
                        )
                else:
                    # Notification - no response expected
                    return Response(status_code=204)  # No Content

            except Exception as e:
                logger.error(f"Error handling JSON-RPC request: {e}")
                error_response = JSONRPCResponse.create_error(
                    JSONRPCError(
                        code=JSONRPCErrorCodes.INTERNAL_ERROR,
                        message=f"Internal error: {str(e)}"
                    ),
                    None
                )
                return JSONResponse(
                    content=error_response.to_dict(),
                    status_code=200
                )

        @app.get("/health")
        async def health_check() -> dict:
            """Health check endpoint."""
            return {"status": "healthy", "transport": "http"}

        return app

    async def start(self) -> None:
        """Start the HTTP transport layer."""
        if self._running:
            return

        logger.info(f"Starting HTTP transport on {self.host}:{self.port}")
        
        # Create FastAPI app
        self._app = self._create_app()
        
        # Configure uvicorn server
        config = uvicorn.Config(
            app=self._app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=False,  # Disable access logs to reduce noise
        )
        
        self._server = uvicorn.Server(config)
        self._running = True
        
        # Start server in background task
        asyncio.create_task(self._run_server())
        
        # Wait a bit for server to start
        await asyncio.sleep(0.1)
        logger.info(f"HTTP transport started on http://{self.host}:{self.port}")

    async def _run_server(self) -> None:
        """Run the uvicorn server."""
        try:
            if self._server:
                await self._server.serve()
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self._running = False

    async def stop(self) -> None:
        """Stop the HTTP transport layer and clean up resources."""
        if not self._running:
            return

        logger.info("Stopping HTTP transport")
        self._running = False
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop the server gracefully
        if self._server:
            self._server.should_exit = True
            # Wait for server to stop
            while not self._server.should_exit:
                await asyncio.sleep(0.1)
        
        # Cancel any pending response futures
        for future in self._response_futures.values():
            if not future.done():
                future.cancel()
        self._response_futures.clear()
        
        # Clear request queue
        while not self._request_queue.empty():
            try:
                self._request_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        logger.info("HTTP transport stopped")

    async def send_message(self, message: JSONRPCResponse) -> None:
        """
        Send a JSON-RPC response message.
        
        Args:
            message: The JSON-RPC response to send
        """
        if not self._running:
            raise RuntimeError("Transport not started")

        try:
            # Find the corresponding future for this response
            if message.id is not None:
                future = self._response_futures.pop(str(message.id), None)
                if future and not future.done():
                    future.set_result(message)
                    logger.debug(f"Sent response for request ID {message.id}")
                else:
                    logger.warning(f"No pending request found for response ID {message.id}")
            else:
                logger.warning("Received response with no ID - cannot route to HTTP client")
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise RuntimeError(f"Failed to send message: {e}")

    async def receive_message(self) -> Optional[JSONRPCRequest]:
        """
        Receive a JSON-RPC request message.
        
        Returns:
            The received JSON-RPC request, or None if no message available
        """
        if not self._running:
            return None

        try:
            # Wait for a request with a short timeout to allow for graceful shutdown
            request = await asyncio.wait_for(self._request_queue.get(), timeout=0.1)
            logger.debug(f"Received request: method={request.method}, id={request.id}")
            return request
            
        except asyncio.TimeoutError:
            # No message available, return None
            return None
            
        except asyncio.CancelledError:
            # Task was cancelled, return None
            logger.info("Message receive cancelled")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error receiving message: {e}")
            return None