"""
Core MCP server components.
"""

from .protocol import (
    Content,
    InitializeParams,
    InitializeResult,
    JSONRPCError,
    JSONRPCErrorCodes,
    JSONRPCRequest,
    JSONRPCResponse,
    ServerCapabilities,
    ToolResult,
    ToolSchema,
    deserialize_request,
    serialize_message,
)

__all__ = [
    "Content",
    "InitializeParams", 
    "InitializeResult",
    "JSONRPCError",
    "JSONRPCErrorCodes",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "ServerCapabilities",
    "ToolResult",
    "ToolSchema",
    "deserialize_request",
    "serialize_message",
]