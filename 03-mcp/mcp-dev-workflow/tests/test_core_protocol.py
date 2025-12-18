"""
Tests for core MCP protocol implementation.
"""

import json
import pytest
from unittest.mock import AsyncMock

from mcp_server.core import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    JSONRPCErrorCodes,
    deserialize_request,
    serialize_message,
)
from mcp_server.core.server import MCPServer
from mcp_server.transport import Transport


class MockTransport(Transport):
    """Mock transport for testing."""
    
    def __init__(self):
        self.messages = []
        self.responses = []
        self.started = False
        
    async def start(self):
        self.started = True
        
    async def stop(self):
        self.started = False
        
    async def send_message(self, message):
        self.responses.append(message)
        
    async def receive_message(self):
        if self.messages:
            return self.messages.pop(0)
        return None


class TestJSONRPCProtocol:
    """Test JSON-RPC protocol data structures."""
    
    def test_jsonrpc_request_creation(self):
        """Test creating JSON-RPC requests."""
        request = JSONRPCRequest(method="test", params={"key": "value"}, id=1)
        assert request.jsonrpc == "2.0"
        assert request.method == "test"
        assert request.params == {"key": "value"}
        assert request.id == 1
    
    def test_jsonrpc_request_from_dict(self):
        """Test creating JSON-RPC request from dictionary."""
        data = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocol_version": "2024-11-05"},
            "id": "test-id"
        }
        request = JSONRPCRequest.from_dict(data)
        assert request.method == "initialize"
        assert request.params == {"protocol_version": "2024-11-05"}
        assert request.id == "test-id"
    
    def test_jsonrpc_response_success(self):
        """Test creating success responses."""
        response = JSONRPCResponse.success({"result": "ok"}, "test-id")
        assert response.result == {"result": "ok"}
        assert response.id == "test-id"
        assert response.error is None
    
    def test_jsonrpc_response_error(self):
        """Test creating error responses."""
        error = JSONRPCError(code=-32601, message="Method not found")
        response = JSONRPCResponse.create_error(error, "test-id")
        assert response.error == error
        assert response.id == "test-id"
        assert response.result is None
    
    def test_serialize_deserialize_request(self):
        """Test serialization and deserialization."""
        original = JSONRPCRequest(method="test", params={"key": "value"}, id=1)
        serialized = serialize_message(original)
        
        # Parse back to verify JSON structure
        parsed_data = json.loads(serialized)
        deserialized = JSONRPCRequest.from_dict(parsed_data)
        
        assert deserialized.method == original.method
        assert deserialized.params == original.params
        assert deserialized.id == original.id


class TestMCPServer:
    """Test MCP server functionality."""
    
    @pytest.fixture
    def mock_transport(self):
        return MockTransport()
    
    @pytest.fixture
    def server(self, mock_transport):
        return MCPServer(mock_transport, "test-server")
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, server, mock_transport):
        """Test server starts correctly."""
        await server.start()
        assert mock_transport.started
        assert server._running
        
        await server.stop()
        assert not mock_transport.started
        assert not server._running
    
    @pytest.mark.asyncio
    async def test_handle_initialize_request(self, server):
        """Test handling initialize request."""
        request = JSONRPCRequest(
            method="initialize",
            params={
                "protocol_version": "2024-11-05",
                "capabilities": {},
                "client_info": {"name": "test-client", "version": "1.0"}
            },
            id=1
        )
        
        response = await server.handle_request(request)
        
        assert response is not None
        assert response.id == 1
        assert response.error is None
        assert "protocol_version" in response.result
        assert "capabilities" in response.result
        assert "server_info" in response.result
        assert server.initialized
    
    @pytest.mark.asyncio
    async def test_handle_invalid_method(self, server):
        """Test handling unknown method."""
        request = JSONRPCRequest(method="unknown_method", id=1)
        
        response = await server.handle_request(request)
        
        assert response is not None
        assert response.id == 1
        assert response.error is not None
        assert response.error.code == JSONRPCErrorCodes.METHOD_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_handle_invalid_jsonrpc_version(self, server):
        """Test handling invalid JSON-RPC version."""
        request = JSONRPCRequest(method="test", id=1)
        request.jsonrpc = "1.0"  # Invalid version
        
        response = await server.handle_request(request)
        
        assert response is not None
        assert response.id == 1
        assert response.error is not None
        assert response.error.code == JSONRPCErrorCodes.INVALID_REQUEST
    
    @pytest.mark.asyncio
    async def test_tools_list_before_initialization(self, server):
        """Test tools/list fails before initialization."""
        request = JSONRPCRequest(method="tools/list", id=1)
        
        response = await server.handle_request(request)
        
        assert response is not None
        assert response.error is not None
        assert response.error.code == JSONRPCErrorCodes.INTERNAL_ERROR
    
    @pytest.mark.asyncio
    async def test_tools_list_after_initialization(self, server):
        """Test tools/list works after initialization."""
        # Initialize first
        init_request = JSONRPCRequest(
            method="initialize",
            params={
                "protocol_version": "2024-11-05",
                "capabilities": {},
                "client_info": {"name": "test-client", "version": "1.0"}
            },
            id=1
        )
        await server.handle_request(init_request)
        
        # Now test tools/list
        request = JSONRPCRequest(method="tools/list", id=2)
        response = await server.handle_request(request)
        
        assert response is not None
        assert response.error is None
        assert "tools" in response.result
        assert isinstance(response.result["tools"], list)