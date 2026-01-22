"""
Integration tests for MCPServer with tools management system.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from mcp_server.core.protocol import JSONRPCRequest
from mcp_server.core.server import MCPServer
from mcp_server.tools import EchoTool
from mcp_server.transport.base import Transport


class MockTransport(Transport):
    """Mock transport for testing."""
    
    def __init__(self):
        self.messages = []
        self.received_messages = []
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
    
    async def send_message(self, message):
        self.messages.append(message)
    
    async def receive_message(self):
        if self.received_messages:
            return self.received_messages.pop(0)
        return None


class TestMCPServerToolsIntegration:
    """Test MCPServer integration with tools management system."""
    
    @pytest.mark.asyncio
    async def test_server_register_tool(self):
        """Test registering a tool with the server."""
        transport = MockTransport()
        server = MCPServer(transport)
        echo_tool = EchoTool()
        
        server.register_tool(echo_tool)
        
        assert server.tools_manager.has_tool("echo")
        assert server.tools_manager.get_tool("echo") is echo_tool
    
    @pytest.mark.asyncio
    async def test_server_initialize_and_list_tools(self):
        """Test server initialization and tools listing."""
        transport = MockTransport()
        server = MCPServer(transport)
        echo_tool = EchoTool()
        
        # Register tool
        server.register_tool(echo_tool)
        
        # Initialize server
        init_request = JSONRPCRequest(
            method="initialize",
            params={
                "protocol_version": "2024-11-05",
                "capabilities": {},
                "client_info": {"name": "test", "version": "1.0"}
            },
            id=1
        )
        
        init_response = await server.handle_request(init_request)
        assert init_response is not None
        assert init_response.error is None
        assert server.initialized
        
        # List tools
        list_request = JSONRPCRequest(
            method="tools/list",
            params={},
            id=2
        )
        
        list_response = await server.handle_request(list_request)
        assert list_response is not None
        assert list_response.error is None
        
        tools = list_response.result["tools"]
        assert len(tools) == 1
        assert tools[0]["name"] == "echo"
        assert "echo back" in tools[0]["description"].lower()
    
    @pytest.mark.asyncio
    async def test_server_call_tool(self):
        """Test calling a tool through the server."""
        transport = MockTransport()
        server = MCPServer(transport)
        echo_tool = EchoTool()
        
        # Register tool and initialize server
        server.register_tool(echo_tool)
        server.initialized = True  # Skip initialization for this test
        
        # Call tool
        call_request = JSONRPCRequest(
            method="tools/call",
            params={
                "name": "echo",
                "arguments": {"message": "Hello from integration test!"}
            },
            id=3
        )
        
        call_response = await server.handle_request(call_request)
        assert call_response is not None
        assert call_response.error is None
        
        result = call_response.result
        assert not result["is_error"]
        assert len(result["content"]) == 1
        assert result["content"][0]["text"] == "Echo: Hello from integration test!"
    
    @pytest.mark.asyncio
    async def test_server_call_nonexistent_tool(self):
        """Test calling a nonexistent tool returns error."""
        transport = MockTransport()
        server = MCPServer(transport)
        server.initialized = True  # Skip initialization for this test
        
        # Call nonexistent tool
        call_request = JSONRPCRequest(
            method="tools/call",
            params={
                "name": "nonexistent",
                "arguments": {}
            },
            id=4
        )
        
        call_response = await server.handle_request(call_request)
        assert call_response is not None
        assert call_response.error is not None
        assert "not found" in call_response.error.message.lower()
    
    @pytest.mark.asyncio
    async def test_server_call_tool_with_invalid_arguments(self):
        """Test calling a tool with invalid arguments returns error result."""
        transport = MockTransport()
        server = MCPServer(transport)
        echo_tool = EchoTool()
        
        # Register tool and initialize server
        server.register_tool(echo_tool)
        server.initialized = True  # Skip initialization for this test
        
        # Call tool with missing required argument
        call_request = JSONRPCRequest(
            method="tools/call",
            params={
                "name": "echo",
                "arguments": {}  # Missing required "message" argument
            },
            id=5
        )
        
        call_response = await server.handle_request(call_request)
        assert call_response is not None
        assert call_response.error is None  # Should not be a JSON-RPC error
        
        result = call_response.result
        assert result["is_error"]  # Should be a tool execution error
        assert "execution failed" in result["content"][0]["text"].lower()
    
    @pytest.mark.asyncio
    async def test_server_tools_list_before_initialization(self):
        """Test that tools/list before initialization returns error."""
        transport = MockTransport()
        server = MCPServer(transport)
        
        list_request = JSONRPCRequest(
            method="tools/list",
            params={},
            id=6
        )
        
        list_response = await server.handle_request(list_request)
        assert list_response is not None
        assert list_response.error is not None
        assert "not initialized" in list_response.error.message.lower()
    
    @pytest.mark.asyncio
    async def test_server_tools_call_before_initialization(self):
        """Test that tools/call before initialization returns error."""
        transport = MockTransport()
        server = MCPServer(transport)
        
        call_request = JSONRPCRequest(
            method="tools/call",
            params={
                "name": "echo",
                "arguments": {"message": "test"}
            },
            id=7
        )
        
        call_response = await server.handle_request(call_request)
        assert call_response is not None
        assert call_response.error is not None
        assert "not initialized" in call_response.error.message.lower()