#!/usr/bin/env python3
"""
Test script for the stdio MCP server.
Sends JSON-RPC requests and validates responses.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict, Optional


class StdioServerTester:
    """Test harness for the stdio MCP server."""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
    
    async def start_server(self) -> None:
        """Start the stdio server process."""
        self.process = subprocess.Popen(
            [sys.executable, "mcp_server/stdio_server.py", "--log-level", "ERROR"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Give the server a moment to start
        await asyncio.sleep(0.5)
    
    def send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC request and get response."""
        if not self.process:
            raise RuntimeError("Server not started")
        
        # Send request
        request_json = json.dumps(request)
        print(f"Sending: {request_json}")
        
        self.process.stdin.write(request_json + "\n")
        self.process.stdin.flush()
        
        # Read response (if expected)
        if request.get("id") is not None:
            response_line = self.process.stdout.readline().strip()
            if response_line:
                print(f"Received: {response_line}")
                return json.loads(response_line)
        
        return None
    
    def stop_server(self) -> None:
        """Stop the server process."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None


async def test_server_functionality():
    """Test the stdio server with the JSON-RPC requests from the README."""
    tester = StdioServerTester()
    
    try:
        print("Starting stdio server...")
        await tester.start_server()
        
        # Test 1: Initialize the client
        print("\n1. Testing initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        init_response = tester.send_request(init_request)
        if init_response and init_response.get("result"):
            print("✓ Initialize successful")
            print(f"  Server: {init_response['result'].get('server_info', {}).get('name')}")
            print(f"  Protocol: {init_response['result'].get('protocol_version')}")
        else:
            print("✗ Initialize failed")
            return False
        
        # Test 2: Send initialized notification
        print("\n2. Sending initialized notification...")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        tester.send_request(initialized_notification)
        print("✓ Initialized notification sent")
        
        # Test 3: List tools
        print("\n3. Testing tools/list request...")
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        list_response = tester.send_request(list_request)
        if list_response and list_response.get("result"):
            tools = list_response["result"].get("tools", [])
            print(f"✓ Tools list successful - found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool.get('name')}: {tool.get('description')}")
        else:
            print("✗ Tools list failed")
            return False
        
        # Test 4: Call weather tool
        print("\n4. Testing weather tool call...")
        weather_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_weather",
                "arguments": {
                    "city": "London"
                }
            }
        }
        
        weather_response = tester.send_request(weather_request)
        if weather_response and weather_response.get("result"):
            content = weather_response["result"].get("content", [])
            if content and len(content) > 0:
                print("✓ Weather tool call successful")
                print(f"  Response: {content[0].get('text', '')[:100]}...")
            else:
                print("✗ Weather tool call returned empty content")
                return False
        else:
            print("✗ Weather tool call failed")
            return False
        
        # Test 5: Call echo tool
        print("\n5. Testing echo tool call...")
        echo_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "message": "Hello, MCP!"
                }
            }
        }
        
        echo_response = tester.send_request(echo_request)
        if echo_response and echo_response.get("result"):
            content = echo_response["result"].get("content", [])
            if content and len(content) > 0:
                print("✓ Echo tool call successful")
                print(f"  Response: {content[0].get('text', '')}")
            else:
                print("✗ Echo tool call returned empty content")
                return False
        else:
            print("✗ Echo tool call failed")
            return False
        
        print("\n🎉 All tests passed! The stdio server is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    
    finally:
        print("\nStopping server...")
        tester.stop_server()


if __name__ == "__main__":
    success = asyncio.run(test_server_functionality())
    sys.exit(0 if success else 1)