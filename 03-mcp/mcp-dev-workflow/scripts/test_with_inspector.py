#!/usr/bin/env python3
"""
Quick test script for MCP Inspector integration.

This script provides simple commands to test MCP servers with the Inspector.
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


logger = logging.getLogger(__name__)


def get_python_path() -> str:
    """Get the current Python executable path."""
    return sys.executable


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def test_stdio_server_basic() -> bool:
    """
    Test stdio server with basic JSON-RPC requests.
    
    Returns:
        True if server responds correctly, False otherwise
    """
    try:
        project_root = get_project_root()
        python_path = get_python_path()
        
        # Prepare environment
        env = dict(os.environ)
        env["PYTHONPATH"] = str(project_root)
        if os.getenv("CONTEXT7_API_KEY"):
            env["CONTEXT7_API_KEY"] = os.getenv("CONTEXT7_API_KEY")
        
        logger.info("Starting stdio server for basic test...")
        
        # Start server process
        process = subprocess.Popen(
            [python_path, "-m", "mcp_server.stdio_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_root,
            env=env,
            text=True
        )
        
        # Test requests
        test_requests = [
            {
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
            },
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            },
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "echo",
                    "arguments": {
                        "message": "Hello from test!"
                    }
                }
            }
        ]
        
        all_passed = True
        
        for i, request in enumerate(test_requests, 1):
            try:
                # Send request
                request_json = json.dumps(request) + "\n"
                process.stdin.write(request_json)
                process.stdin.flush()
                
                # Read response with timeout
                try:
                    response_line = process.stdout.readline()
                except Exception as e:
                    logger.error(f"❌ Failed to read response: {e}")
                    response_line = ""
                
                if response_line:
                    response = json.loads(response_line)
                    
                    if response.get("jsonrpc") == "2.0" and response.get("id") == request["id"]:
                        if "result" in response:
                            logger.info(f"✅ Test {i} passed: {request['method']}")
                            if request["method"] == "tools/list":
                                tools = response["result"].get("tools", [])
                                logger.info(f"   Found {len(tools)} tools: {[t.get('name') for t in tools]}")
                        else:
                            logger.error(f"❌ Test {i} failed: {response.get('error', 'Unknown error')}")
                            all_passed = False
                    else:
                        logger.error(f"❌ Test {i} failed: Invalid response format")
                        all_passed = False
                else:
                    logger.error(f"❌ Test {i} failed: No response")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"❌ Test {i} failed: {e}")
                all_passed = False
        
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
        
        return all_passed
        
    except Exception as e:
        logger.error(f"❌ Basic server test failed: {e}")
        return False


def start_inspector_stdio() -> Optional[subprocess.Popen]:
    """
    Start MCP Inspector with stdio server.
    
    Returns:
        Process object if successful, None otherwise
    """
    try:
        project_root = get_project_root()
        python_path = get_python_path()
        
        # Check if npx is available
        try:
            subprocess.run(["npx", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ npx not found. Please install Node.js")
            return None
        
        # Prepare command
        cmd = [
            "npx", "@modelcontextprotocol/inspector",
            python_path, "-m", "mcp_server.stdio_server"
        ]
        
        # Set up environment
        env = dict(os.environ)
        env["PYTHONPATH"] = str(project_root)
        if os.getenv("CONTEXT7_API_KEY"):
            env["CONTEXT7_API_KEY"] = os.getenv("CONTEXT7_API_KEY")
        
        logger.info("Starting MCP Inspector with stdio server...")
        logger.info(f"Command: {' '.join(cmd)}")
        
        # Start inspector
        process = subprocess.Popen(
            cmd,
            cwd=project_root,
            env=env
        )
        
        # Give it time to start
        time.sleep(3)
        
        if process.poll() is None:
            logger.info("✅ MCP Inspector started successfully")
            logger.info("🌐 Inspector should be available at: http://localhost:6274")
            logger.info("📋 Available tools: echo, get_weather")
            if os.getenv("CONTEXT7_API_KEY"):
                logger.info("📋 Context7 tools: search_libraries, get_documentation, get_examples")
            return process
        else:
            logger.error("❌ MCP Inspector failed to start")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to start MCP Inspector: {e}")
        return None


def start_http_server() -> Optional[subprocess.Popen]:
    """
    Start HTTP MCP server for inspector testing.
    
    Returns:
        Process object if successful, None otherwise
    """
    try:
        project_root = get_project_root()
        python_path = get_python_path()
        
        # Set up environment
        env = dict(os.environ)
        env["PYTHONPATH"] = str(project_root)
        if os.getenv("CONTEXT7_API_KEY"):
            env["CONTEXT7_API_KEY"] = os.getenv("CONTEXT7_API_KEY")
        
        logger.info("Starting HTTP MCP server...")
        
        # Start server
        process = subprocess.Popen(
            [python_path, "-m", "mcp_server.http_server", "--port", "8001"],
            cwd=project_root,
            env=env
        )
        
        # Give it time to start
        time.sleep(3)
        
        if process.poll() is None:
            logger.info("✅ HTTP MCP server started successfully")
            logger.info("🌐 Server available at: http://localhost:8001")
            logger.info("🔗 JSON-RPC endpoint: http://localhost:8001/jsonrpc")
            logger.info("❤️  Health check: http://localhost:8001/health")
            return process
        else:
            logger.error("❌ HTTP MCP server failed to start")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to start HTTP server: {e}")
        return None


def print_inspector_instructions():
    """Print instructions for using MCP Inspector."""
    print("\n" + "="*60)
    print("MCP INSPECTOR USAGE INSTRUCTIONS")
    print("="*60)
    print("1. STDIO Server Testing:")
    print("   - Inspector should open automatically in your browser")
    print("   - Server configuration is handled automatically")
    print("   - Test available tools in the Inspector interface")
    print()
    print("2. HTTP Server Testing:")
    print("   - Open MCP Inspector manually: npx @modelcontextprotocol/inspector")
    print("   - Configure HTTP server with URL: http://localhost:8001/jsonrpc")
    print("   - Test available tools in the Inspector interface")
    print()
    print("3. Available Tools to Test:")
    print("   - echo: Test with any message")
    print("   - get_weather: Test with city names like 'London', 'New York'")
    if os.getenv("CONTEXT7_API_KEY"):
        print("   - search_libraries: Search for programming libraries")
        print("   - get_documentation: Get docs for specific libraries")
        print("   - get_examples: Get code examples")
    else:
        print("   - Set CONTEXT7_API_KEY environment variable for Context7 tools")
    print()
    print("4. What to Verify:")
    print("   - All tools are listed correctly")
    print("   - Tool execution returns expected results")
    print("   - Error handling works for invalid inputs")
    print("   - Response format is correct JSON-RPC")
    print("="*60)


def main():
    """Command-line interface for MCP Inspector testing."""
    parser = argparse.ArgumentParser(
        description="Test MCP servers with Inspector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s stdio                        # Test stdio server with Inspector
  %(prog)s http                         # Start HTTP server for Inspector testing
  %(prog)s test                         # Run basic server functionality test
  %(prog)s both                         # Test both stdio and HTTP servers

Prerequisites:
  - Node.js installed (for MCP Inspector)
  - MCP Inspector: npm install -g @modelcontextprotocol/inspector
  - Optional: CONTEXT7_API_KEY environment variable for Context7 tools
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["stdio", "http", "test", "both"],
        help="Testing mode to run"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s: %(message)s"
    )
    
    try:
        if args.mode == "test":
            # Run basic functionality test
            logger.info("🧪 Running basic server functionality test...")
            success = test_stdio_server_basic()
            
            if success:
                logger.info("✅ Basic server test passed!")
                print("\n" + "="*50)
                print("✅ SERVER FUNCTIONALITY TEST: PASSED")
                print("="*50)
                print("Your MCP server is working correctly.")
                print("You can now test it with MCP Inspector.")
            else:
                logger.error("❌ Basic server test failed!")
                print("\n" + "="*50)
                print("❌ SERVER FUNCTIONALITY TEST: FAILED")
                print("="*50)
                print("Please check the error messages above.")
            
            sys.exit(0 if success else 1)
        
        elif args.mode == "stdio":
            # Test stdio server with Inspector
            logger.info("🚀 Starting stdio server with MCP Inspector...")
            
            # First run basic test
            if not test_stdio_server_basic():
                logger.error("❌ Basic server test failed. Fix issues before using Inspector.")
                sys.exit(1)
            
            # Start Inspector
            process = start_inspector_stdio()
            if process:
                print_inspector_instructions()
                
                try:
                    logger.info("\nPress Ctrl+C to stop the Inspector...")
                    process.wait()
                except KeyboardInterrupt:
                    logger.info("\nStopping MCP Inspector...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
            else:
                sys.exit(1)
        
        elif args.mode == "http":
            # Start HTTP server for Inspector testing
            logger.info("🚀 Starting HTTP server for MCP Inspector testing...")
            
            process = start_http_server()
            if process:
                print_inspector_instructions()
                
                try:
                    logger.info("\nHTTP server is running. Use MCP Inspector to test.")
                    logger.info("Press Ctrl+C to stop the server...")
                    process.wait()
                except KeyboardInterrupt:
                    logger.info("\nStopping HTTP server...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
            else:
                sys.exit(1)
        
        elif args.mode == "both":
            # Test both servers
            logger.info("🚀 Testing both stdio and HTTP servers...")
            
            # First run basic test
            if not test_stdio_server_basic():
                logger.error("❌ Basic server test failed. Fix issues before proceeding.")
                sys.exit(1)
            
            logger.info("\n📋 Step 1: Testing stdio server with Inspector...")
            stdio_process = start_inspector_stdio()
            
            if stdio_process:
                print_inspector_instructions()
                
                try:
                    input("\nPress Enter to continue to HTTP server test (or Ctrl+C to stop)...")
                except KeyboardInterrupt:
                    logger.info("\nStopping...")
                    stdio_process.terminate()
                    sys.exit(0)
                
                # Stop stdio inspector
                stdio_process.terminate()
                try:
                    stdio_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    stdio_process.kill()
            
            logger.info("\n📋 Step 2: Testing HTTP server...")
            http_process = start_http_server()
            
            if http_process:
                try:
                    logger.info("\nHTTP server is running. Test with MCP Inspector.")
                    logger.info("Press Ctrl+C when done...")
                    http_process.wait()
                except KeyboardInterrupt:
                    logger.info("\nStopping HTTP server...")
                    http_process.terminate()
                    try:
                        http_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        http_process.kill()
            
            logger.info("✅ Both server tests completed!")
    
    except KeyboardInterrupt:
        logger.info("\nTesting interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()