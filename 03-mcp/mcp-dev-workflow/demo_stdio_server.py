#!/usr/bin/env python3
"""
Demo script showing how to use the stdio MCP server.
This demonstrates the JSON-RPC communication as shown in the README.
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any


async def demo_stdio_server():
    """Demonstrate the stdio server functionality."""
    print("🚀 MCP Development Workflow - stdio Server Demo")
    print("=" * 50)
    
    print("\n1. Starting the stdio server...")
    print("   Command: python mcp_server/stdio_server.py")
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "mcp_server/stdio_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    def send_request(request: Dict[str, Any], description: str) -> None:
        """Send a request and show the response."""
        print(f"\n{description}")
        request_json = json.dumps(request)
        print(f"📤 Request:  {request_json}")
        
        process.stdin.write(request_json + "\n")
        process.stdin.flush()
        
        # Read response if expected
        if request.get("id") is not None:
            response_line = process.stdout.readline().strip()
            if response_line:
                try:
                    response = json.loads(response_line)
                    print(f"📥 Response: {json.dumps(response, indent=2)}")
                except json.JSONDecodeError:
                    print(f"📥 Response: {response_line}")
        else:
            print("📥 Response: (notification - no response expected)")
    
    try:
        # Give server time to start
        await asyncio.sleep(0.5)
        
        # Demo the JSON-RPC requests from the README
        print("\n2. Initializing the MCP client...")
        send_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "demo-client",
                    "version": "1.0.0"
                }
            }
        }, "2.1 Initialize Request")
        
        print("\n3. Sending initialization notification...")
        send_request({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }, "3.1 Initialized Notification")
        
        print("\n4. Listing available tools...")
        send_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }, "4.1 Tools List Request")
        
        print("\n5. Calling the weather tool...")
        send_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_weather",
                "arguments": {
                    "city": "London"
                }
            }
        }, "5.1 Weather Tool Call")
        
        print("\n6. Calling the echo tool...")
        send_request({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "message": "Hello, MCP World! 🌍"
                }
            }
        }, "6.1 Echo Tool Call")
        
        print("\n7. Testing error handling with invalid tool...")
        send_request({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            }
        }, "7.1 Invalid Tool Call (Error Test)")
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\n💡 To run the server manually:")
        print("   python mcp_server/stdio_server.py")
        print("\n💡 Then paste JSON-RPC requests from manual_test_requests.txt")
        print("   or use the MCP Inspector for a visual interface.")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    
    finally:
        print("\n🛑 Stopping server...")
        process.terminate()
        process.wait()


if __name__ == "__main__":
    asyncio.run(demo_stdio_server())