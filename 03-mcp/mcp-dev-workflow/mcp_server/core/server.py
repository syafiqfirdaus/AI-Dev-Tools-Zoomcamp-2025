"""
Base MCP server implementation with protocol handling and request routing.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from mcp_server.core.protocol import (
    InitializeParams,
    InitializeResult,
    JSONRPCError,
    JSONRPCErrorCodes,
    JSONRPCRequest,
    JSONRPCResponse,
    ServerCapabilities,
    ToolResult,
    ToolSchema,
)
from mcp_server.tools.base import Tool, ToolsManager
from mcp_server.transport.base import Transport

logger = logging.getLogger(__name__)


class MCPServer:
    """Base MCP server with protocol handling and request routing."""

    def __init__(self, transport: Transport, server_name: str = "mcp-dev-workflow"):
        """
        Initialize MCP server.
        
        Args:
            transport: Transport layer for communication
            server_name: Name of the server
        """
        self.transport = transport
        self.server_name = server_name
        self.server_version = "0.1.0"
        self.protocol_version = "2024-11-05"
        
        # Server state
        self.initialized = False
        self.capabilities = ServerCapabilities(
            tools={"list_changed": True},
            resources={},
            prompts={},
            logging={}
        )
        
        # Request handlers
        self._handlers: Dict[str, Callable] = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
        }
        
        # Tools manager
        self.tools_manager = ToolsManager()
        
        # Running state
        self._running = False

    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool with the server.
        
        Args:
            tool: Tool implementation
        """
        self.tools_manager.register_tool(tool)
        logger.info(f"Registered tool: {tool.name}")

    async def start(self) -> None:
        """Start the MCP server."""
        logger.info(f"Starting MCP server: {self.server_name}")
        await self.transport.start()
        self._running = True
        
        # Start message processing loop
        asyncio.create_task(self._message_loop())

    async def stop(self) -> None:
        """Stop the MCP server."""
        logger.info(f"Stopping MCP server: {self.server_name}")
        self._running = False
        await self.transport.stop()

    async def _message_loop(self) -> None:
        """Main message processing loop."""
        while self._running:
            try:
                request = await self.transport.receive_message()
                if request is not None:
                    response = await self.handle_request(request)
                    if response is not None:
                        await self.transport.send_message(response)
            except Exception as e:
                logger.error(f"Error in message loop: {e}")
                # Continue processing other messages
                continue

    async def handle_request(self, request: JSONRPCRequest) -> Optional[JSONRPCResponse]:
        """
        Handle a JSON-RPC request and return a response.
        
        Args:
            request: The JSON-RPC request to handle
            
        Returns:
            JSON-RPC response or None for notifications
        """
        try:
            # Validate JSON-RPC format
            if request.jsonrpc != "2.0":
                return JSONRPCResponse.create_error(
                    JSONRPCError(
                        code=JSONRPCErrorCodes.INVALID_REQUEST,
                        message="Invalid JSON-RPC version"
                    ),
                    request.id
                )

            # Handle notifications (no response expected)
            if request.id is None:
                # Handle known notifications
                if request.method == "notifications/initialized":
                    logger.info("Client initialization notification received")
                    return None
                else:
                    logger.warning(f"Unknown notification: {request.method}")
                    return None

            # Route to appropriate handler for requests (with ID)
            handler = self._handlers.get(request.method)
            if handler is None:
                return JSONRPCResponse.create_error(
                    JSONRPCError(
                        code=JSONRPCErrorCodes.METHOD_NOT_FOUND,
                        message=f"Method not found: {request.method}"
                    ),
                    request.id
                )

            # Execute handler
            result = await handler(request.params or {})
            
            # Return response
            return JSONRPCResponse.success(result, request.id)

        except Exception as e:
            logger.error(f"Error handling request {request.method}: {e}")
            if request.id is not None:
                return JSONRPCResponse.create_error(
                    JSONRPCError(
                        code=JSONRPCErrorCodes.INTERNAL_ERROR,
                        message=f"Internal error: {str(e)}"
                    ),
                    request.id
                )
            return None

    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        try:
            init_params = InitializeParams(**params)
            
            # Mark as initialized
            self.initialized = True
            
            # Create initialize result
            result = InitializeResult(
                protocol_version=self.protocol_version,
                capabilities=self.capabilities,
                server_info={
                    "name": self.server_name,
                    "version": self.server_version
                }
            )
            
            logger.info(f"Server initialized with client: {init_params.client_info}")
            return result.model_dump()
            
        except Exception as e:
            raise ValueError(f"Invalid initialize parameters: {e}")

    async def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        if not self.initialized:
            raise RuntimeError("Server not initialized")
        
        tool_schemas = self.tools_manager.list_tools()
        tools = []
        
        for schema in tool_schemas:
            if hasattr(schema, 'model_dump'):
                tools.append(schema.model_dump())
            elif hasattr(schema, 'dict'):
                tools.append(schema.dict())
            else:
                # Fallback for dict-like objects
                tools.append({
                    "name": schema.name,
                    "description": schema.description,
                    "input_schema": schema.input_schema
                })
        
        return {"tools": tools}

    async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        if not self.initialized:
            raise RuntimeError("Server not initialized")
        
        tool_name = params.get("name")
        if not tool_name:
            raise ValueError("Tool name is required")
        
        # Validate tool exists
        if not self.tools_manager.has_tool(tool_name):
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Execute tool through manager
        arguments = params.get("arguments", {})
        
        try:
            result = await self.tools_manager.execute_tool(tool_name, arguments)
            
            # Ensure result is in correct format
            if hasattr(result, 'model_dump'):
                return result.model_dump()
            elif hasattr(result, 'dict'):
                return result.dict()
            elif isinstance(result, dict):
                return result
            else:
                # Wrap simple results
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ],
                    "is_error": False
                }
        except Exception as e:
            # Return error result
            logger.error(f"Tool execution error for {tool_name}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool execution failed: {str(e)}"
                    }
                ],
                "is_error": True
            }