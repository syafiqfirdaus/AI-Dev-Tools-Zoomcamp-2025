"""
Standard input/output transport implementation for MCP communication.
"""

import asyncio
import json
import logging
import sys
from typing import Optional

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


class StdioTransport(Transport):
    """Transport implementation using standard input/output for JSON-RPC communication."""

    def __init__(self):
        """Initialize stdio transport."""
        self._running = False
        self._stdin_reader: Optional[asyncio.StreamReader] = None
        self._stdout_writer: Optional[asyncio.StreamWriter] = None

    async def start(self) -> None:
        """Start the stdio transport layer."""
        logger.info("Starting stdio transport")
        
        # Create async stdin/stdout streams
        loop = asyncio.get_event_loop()
        self._stdin_reader = asyncio.StreamReader()
        stdin_protocol = asyncio.StreamReaderProtocol(self._stdin_reader)
        await loop.connect_read_pipe(lambda: stdin_protocol, sys.stdin)
        
        # For stdout, we'll use the synchronous sys.stdout with proper flushing
        self._running = True
        logger.info("Stdio transport started")

    async def stop(self) -> None:
        """Stop the stdio transport layer and clean up resources."""
        logger.info("Stopping stdio transport")
        self._running = False
        
        # Close stdin reader if it exists
        if self._stdin_reader is not None:
            # Note: We don't close stdin as it's owned by the system
            self._stdin_reader = None
        
        # Flush stdout
        sys.stdout.flush()
        logger.info("Stdio transport stopped")

    async def send_message(self, message: JSONRPCResponse) -> None:
        """
        Send a JSON-RPC response message to stdout.
        
        Args:
            message: The JSON-RPC response to send
        """
        if not self._running:
            raise RuntimeError("Transport not started")
        
        try:
            # Serialize message to JSON
            json_str = serialize_message(message)
            
            # Write to stdout with newline delimiter
            sys.stdout.write(json_str + '\n')
            sys.stdout.flush()
            
            logger.debug(f"Sent message: {json_str}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise RuntimeError(f"Failed to send message: {e}")

    async def receive_message(self) -> Optional[JSONRPCRequest]:
        """
        Receive a JSON-RPC request message from stdin.
        
        Returns:
            The received JSON-RPC request, or None if no message available or error occurred
        """
        if not self._running or self._stdin_reader is None:
            return None
        
        try:
            # Read a line from stdin
            line_bytes = await self._stdin_reader.readline()
            
            if not line_bytes:
                # EOF reached
                logger.info("EOF reached on stdin")
                return None
            
            # Decode and strip whitespace
            line = line_bytes.decode('utf-8').strip()
            
            if not line:
                # Empty line, continue reading
                return None
            
            logger.debug(f"Received raw message: {line}")
            
            # Parse JSON-RPC request
            try:
                request = deserialize_request(line)
                logger.debug(f"Parsed request: method={request.method}, id={request.id}")
                return request
                
            except ValueError as e:
                # Malformed JSON-RPC - log error but don't crash
                logger.error(f"Malformed JSON-RPC request: {e}")
                
                # Try to extract ID for error response using more robust parsing
                request_id = None
                try:
                    # First try normal JSON parsing
                    parsed_json = json.loads(line)
                    request_id = parsed_json.get('id')
                except json.JSONDecodeError:
                    # If that fails, try to extract ID with regex as fallback
                    import re
                    id_match = re.search(r'"id"\s*:\s*"([^"]*)"', line)
                    if id_match:
                        request_id = id_match.group(1)
                    else:
                        # Try numeric ID
                        id_match = re.search(r'"id"\s*:\s*(\d+)', line)
                        if id_match:
                            try:
                                request_id = int(id_match.group(1))
                            except ValueError:
                                pass
                except Exception:
                    pass
                
                # Send error response for malformed request
                error_response = JSONRPCResponse.create_error(
                    JSONRPCError(
                        code=JSONRPCErrorCodes.PARSE_ERROR,
                        message=f"Parse error: {str(e)}"
                    ),
                    request_id
                )
                
                # Send error response immediately
                await self.send_message(error_response)
                return None
                
        except asyncio.CancelledError:
            # Task was cancelled, return None
            logger.info("Message receive cancelled")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error receiving message: {e}")
            return None