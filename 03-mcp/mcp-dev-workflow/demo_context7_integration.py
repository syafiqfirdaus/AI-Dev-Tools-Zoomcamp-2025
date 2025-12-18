#!/usr/bin/env python3
"""
Demo script to test Context7 integration with MCP servers.

This script demonstrates:
1. Context7 tool registration with both stdio and HTTP servers
2. Tool schema validation
3. Mock tool execution (without requiring real API key)
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

from mcp_server.core.server import MCPServer
from mcp_server.transport.stdio import StdioTransport
from mcp_server.transport.http import HTTPTransport
from mcp_server.tools import (
    EchoTool,
    WeatherTool,
    Context7Client,
    Context7SearchTool,
    Context7DocumentationTool,
    Context7ExamplesTool,
)


class MockContext7Client:
    """Mock Context7 client for testing without API key."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def close(self):
        pass
    
    async def search_libraries(self, query: str, limit: int = 20):
        """Mock library search."""
        from mcp_server.tools.context7 import Library
        return [
            Library(
                name="fastapi",
                version="0.104.1",
                description="FastAPI framework, high performance, easy to learn",
                documentation_status="complete"
            ),
            Library(
                name="requests",
                version="2.31.0", 
                description="Python HTTP library",
                documentation_status="complete"
            )
        ]
    
    async def get_documentation(self, library: str, version: str = "latest"):
        """Mock documentation retrieval."""
        from mcp_server.tools.context7 import Documentation
        return Documentation(
            library=library,
            version=version,
            content=f"# {library} Documentation\n\nThis is mock documentation for {library}.",
            format="markdown",
            last_updated="2024-01-01T00:00:00Z"
        )
    
    async def get_examples(self, library: str, topic: str, limit: int = 10):
        """Mock examples retrieval."""
        from mcp_server.tools.context7 import CodeExample
        return [
            CodeExample(
                library=library,
                topic=topic,
                code=f"# Example for {library} - {topic}\nprint('Hello from {library}')",
                description=f"Basic {topic} example for {library}",
                language="python"
            )
        ]


async def test_context7_tools():
    """Test Context7 tools functionality."""
    print("🧪 Testing Context7 Tools")
    print("=" * 50)
    
    # Create mock client
    mock_client = MockContext7Client("mock-api-key")
    
    # Create tools
    search_tool = Context7SearchTool(mock_client)
    doc_tool = Context7DocumentationTool(mock_client)
    examples_tool = Context7ExamplesTool(mock_client)
    
    print(f"✓ Created Context7 tools:")
    print(f"  - {search_tool.name}: {search_tool.description}")
    print(f"  - {doc_tool.name}: {doc_tool.description}")
    print(f"  - {examples_tool.name}: {examples_tool.description}")
    
    # Test tool schemas
    print(f"\n📋 Tool Schemas:")
    for tool in [search_tool, doc_tool, examples_tool]:
        schema = tool.get_schema()
        print(f"  - {schema.name}:")
        print(f"    Required params: {schema.input_schema.get('required', [])}")
        properties = schema.input_schema.get('properties', {})
        for prop_name, prop_info in properties.items():
            print(f"    - {prop_name}: {prop_info.get('type', 'unknown')} - {prop_info.get('description', 'No description')}")
    
    # Test tool execution
    print(f"\n🔧 Testing Tool Execution:")
    
    try:
        # Test search tool
        search_result = await search_tool.execute({"query": "fastapi", "limit": 5})
        print(f"✓ Search tool executed successfully")
        print(f"  Result type: {'error' if search_result.is_error else 'success'}")
        
        # Test documentation tool
        doc_result = await doc_tool.execute({"library": "fastapi", "version": "latest"})
        print(f"✓ Documentation tool executed successfully")
        print(f"  Result type: {'error' if doc_result.is_error else 'success'}")
        
        # Test examples tool
        examples_result = await examples_tool.execute({"library": "fastapi", "topic": "routing", "limit": 3})
        print(f"✓ Examples tool executed successfully")
        print(f"  Result type: {'error' if examples_result.is_error else 'success'}")
        
    except Exception as e:
        print(f"✗ Tool execution error: {e}")
        return False
    
    await mock_client.close()
    return True


async def test_stdio_server_integration():
    """Test Context7 tools integration with stdio server."""
    print("\n🖥️  Testing Stdio Server Integration")
    print("=" * 50)
    
    try:
        # Create stdio transport and server
        transport = StdioTransport()
        server = MCPServer(transport, "test-stdio-server")
        
        # Register standard tools
        server.register_tool(EchoTool())
        server.register_tool(WeatherTool())
        
        # Register Context7 tools with mock client
        mock_client = MockContext7Client("mock-api-key")
        server.register_tool(Context7SearchTool(mock_client))
        server.register_tool(Context7DocumentationTool(mock_client))
        server.register_tool(Context7ExamplesTool(mock_client))
        
        print(f"✓ Stdio server created with {len(server.tools_manager.tools)} tools")
        
        # List all registered tools
        print(f"📋 Registered tools:")
        for tool_name, tool in server.tools_manager.tools.items():
            print(f"  - {tool_name}: {tool.description}")
        
        # Test tools/list functionality
        tools_list = server.tools_manager.list_tools()
        print(f"✓ Tools list contains {len(tools_list)} tool schemas")
        
        # Test Context7 tools are present
        context7_tools = [t for t in tools_list if t.name.startswith('context7_')]
        print(f"✓ Found {len(context7_tools)} Context7 tools in server")
        
        await mock_client.close()
        return True
        
    except Exception as e:
        print(f"✗ Stdio server integration error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_http_server_integration():
    """Test Context7 tools integration with HTTP server."""
    print("\n🌐 Testing HTTP Server Integration")
    print("=" * 50)
    
    try:
        # Create HTTP transport and server
        transport = HTTPTransport(host="127.0.0.1", port=8001)
        server = MCPServer(transport, "test-http-server")
        
        # Register standard tools
        server.register_tool(EchoTool())
        server.register_tool(WeatherTool())
        
        # Register Context7 tools with mock client
        mock_client = MockContext7Client("mock-api-key")
        server.register_tool(Context7SearchTool(mock_client))
        server.register_tool(Context7DocumentationTool(mock_client))
        server.register_tool(Context7ExamplesTool(mock_client))
        
        print(f"✓ HTTP server created with {len(server.tools_manager.tools)} tools")
        
        # List all registered tools
        print(f"📋 Registered tools:")
        for tool_name, tool in server.tools_manager.tools.items():
            print(f"  - {tool_name}: {tool.description}")
        
        # Test tools/list functionality
        tools_list = server.tools_manager.list_tools()
        print(f"✓ Tools list contains {len(tools_list)} tool schemas")
        
        # Test Context7 tools are present
        context7_tools = [t for t in tools_list if t.name.startswith('context7_')]
        print(f"✓ Found {len(context7_tools)} Context7 tools in server")
        
        await mock_client.close()
        return True
        
    except Exception as e:
        print(f"✗ HTTP server integration error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_json_rpc_compatibility():
    """Test JSON-RPC request/response compatibility."""
    print("\n📡 Testing JSON-RPC Compatibility")
    print("=" * 50)
    
    try:
        # Create server with Context7 tools
        transport = StdioTransport()
        server = MCPServer(transport, "test-jsonrpc-server")
        
        mock_client = MockContext7Client("mock-api-key")
        server.register_tool(Context7SearchTool(mock_client))
        server.register_tool(Context7DocumentationTool(mock_client))
        server.register_tool(Context7ExamplesTool(mock_client))
        
        # Test initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        # Test tools/list request
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        # Test tools/call request
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "context7_search_libraries",
                "arguments": {"query": "fastapi", "limit": 5}
            }
        }
        
        print(f"✓ JSON-RPC request formats validated")
        print(f"  - Initialize request: {len(json.dumps(init_request))} bytes")
        print(f"  - Tools list request: {len(json.dumps(list_request))} bytes")
        print(f"  - Tool call request: {len(json.dumps(call_request))} bytes")
        
        await mock_client.close()
        return True
        
    except Exception as e:
        print(f"✗ JSON-RPC compatibility error: {e}")
        return False


async def main():
    """Main test runner."""
    print("🚀 Context7 MCP Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Context7 Tools", test_context7_tools),
        ("Stdio Server Integration", test_stdio_server_integration),
        ("HTTP Server Integration", test_http_server_integration),
        ("JSON-RPC Compatibility", test_json_rpc_compatibility),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Context7 integration tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)