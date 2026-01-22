"""
Core MCP protocol data structures and JSON-RPC message handling.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


# JSON-RPC Message Types
@dataclass
class JSONRPCRequest:
    """JSON-RPC 2.0 request message."""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> JSONRPCRequest:
        """Create JSONRPCRequest from dictionary."""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            method=data.get("method", ""),
            params=data.get("params"),
            id=data.get("id")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "jsonrpc": self.jsonrpc,
            "method": self.method
        }
        if self.params is not None:
            result["params"] = self.params
        if self.id is not None:
            result["id"] = self.id
        return result


@dataclass
class JSONRPCError:
    """JSON-RPC 2.0 error object."""
    code: int
    message: str
    data: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "code": self.code,
            "message": self.message
        }
        if self.data is not None:
            result["data"] = self.data
        return result


@dataclass
class JSONRPCResponse:
    """JSON-RPC 2.0 response message."""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        response = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.error is not None:
            response["error"] = self.error.to_dict()
        else:
            response["result"] = self.result
        return response

    @classmethod
    def success(cls, result: Any, request_id: Optional[Union[str, int]] = None) -> "JSONRPCResponse":
        """Create a success response."""
        return cls(id=request_id, result=result, error=None)

    @classmethod
    def create_error(cls, error: JSONRPCError, request_id: Optional[Union[str, int]] = None) -> "JSONRPCResponse":
        """Create an error response."""
        return cls(id=request_id, result=None, error=error)


# MCP Protocol Types
class ServerCapabilities(BaseModel):
    """MCP server capabilities."""
    tools: Optional[Dict[str, Any]] = Field(default_factory=dict)
    resources: Optional[Dict[str, Any]] = Field(default_factory=dict)
    prompts: Optional[Dict[str, Any]] = Field(default_factory=dict)
    logging: Optional[Dict[str, Any]] = Field(default_factory=dict)


class InitializeParams(BaseModel):
    """Parameters for initialize request."""
    protocol_version: str = Field(alias="protocolVersion")
    capabilities: Dict[str, Any]
    client_info: Dict[str, Any] = Field(alias="clientInfo")
    
    class Config:
        populate_by_name = True


class InitializeResult(BaseModel):
    """Result of initialize request."""
    protocol_version: str = "2024-11-05"
    capabilities: ServerCapabilities
    server_info: Dict[str, Any]


class ToolSchema(BaseModel):
    """Schema definition for an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]


class Content(BaseModel):
    """Content item in tool results."""
    type: str
    text: Optional[str] = None
    data: Optional[str] = None
    mime_type: Optional[str] = None


class ToolResult(BaseModel):
    """Result of tool execution."""
    content: List[Content]
    is_error: bool = False


# JSON-RPC Error Codes
class JSONRPCErrorCodes:
    """Standard JSON-RPC error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


def serialize_message(message: Union[JSONRPCRequest, JSONRPCResponse]) -> str:
    """Serialize a JSON-RPC message to string."""
    return json.dumps(message.to_dict())


def deserialize_request(data: str) -> JSONRPCRequest:
    """Deserialize a JSON-RPC request from string."""
    try:
        parsed = json.loads(data)
        return JSONRPCRequest.from_dict(parsed)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Invalid request format: {e}")