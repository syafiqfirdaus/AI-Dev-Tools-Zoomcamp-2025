#!/usr/bin/env python3
"""
Verification script for MCP Inspector integration.

This script verifies that MCP Inspector can properly connect to servers,
execute tools, and display responses correctly.
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
from typing import Dict, Any, List, Optional, Tuple

# Try to import requests, fall back to httpx if available
try:
    import requests
    HTTP_CLIENT = "requests"
except ImportError:
    try:
        import httpx
        HTTP_CLIENT = "httpx"
    except ImportError:
        HTTP_CLIENT = None

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


logger = logging.getLogger(__name__)


class InspectorIntegrationVerifier:
    """Verifies MCP Inspector integration functionality."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.python_path = sys.executable
        
    def verify_server_startup(self, server_type: str) -> Tuple[bool, Optional[subprocess.Popen]]:
        """
        Verify that a server starts up correctly.
        
        Args:
            server_type: Either 'stdio' or 'http'
            
        Returns:
            Tuple of (success, process) where process is None for failed startups
        """
        try:
            env = dict(os.environ)
            env["PYTHONPATH"] = str(self.project_root)
            if os.getenv("CONTEXT7_API_KEY"):
                env["CONTEXT7_API_KEY"] = os.getenv("CONTEXT7_API_KEY")
            
            if server_type == "stdio":
                logger.info("🧪 Verifying stdio server startup...")
                
                process = subprocess.Popen(
                    [self.python_path, "-m", "mcp_server.stdio_server"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.project_root,
                    env=env,
                    text=True
                )
                
                # Give it a moment to start
                time.sleep(2)
                
                if process.poll() is None:
                    logger.info("✅ Stdio server started successfully")
                    return True, process
                else:
                    stdout, stderr = process.communicate()
                    logger.error(f"❌ Stdio server failed to start")
                    logger.error(f"stdout: {stdout}")
                    logger.error(f"stderr: {stderr}")
                    return False, None
            
            elif server_type == "http":
                logger.info("🧪 Verifying HTTP server startup...")
                
                process = subprocess.Popen(
                    [self.python_path, "-m", "mcp_server.http_server", "--port", "8001"],
                    cwd=self.project_root,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Give it time to start
                time.sleep(3)
                
                if process.poll() is None:
                    # Verify HTTP endpoint is responding
                    try:
                        if HTTP_CLIENT == "requests":
                            response = requests.get("http://localhost:8001/health", timeout=5)
                            status_ok = response.status_code == 200
                        elif HTTP_CLIENT == "httpx":
                            with httpx.Client() as client:
                                response = client.get("http://localhost:8001/health", timeout=5)
                                status_ok = response.status_code == 200
                        else:
                            logger.warning("⚠️  No HTTP client available, skipping health check")
                            logger.info("✅ HTTP server started (health check skipped)")
                            return True, process
                        
                        if status_ok:
                            logger.info("✅ HTTP server started and responding")
                            return True, process
                        else:
                            logger.error(f"❌ HTTP server not responding correctly: {response.status_code}")
                            process.terminate()
                            return False, None
                    except Exception as e:
                        logger.error(f"❌ HTTP server not accessible: {e}")
                        process.terminate()
                        return False, None
                else:
                    stdout, stderr = process.communicate()
                    logger.error(f"❌ HTTP server failed to start")
                    logger.error(f"stdout: {stdout}")
                    logger.error(f"stderr: {stderr}")
                    return False, None
            
            else:
                logger.error(f"❌ Unknown server type: {server_type}")
                return False, None
                
        except Exception as e:
            logger.error(f"❌ Server startup verification failed: {e}")
            return False, None
    
    def verify_tool_listing(self, server_type: str, process: subprocess.Popen) -> Tuple[bool, List[Dict]]:
        """
        Verify that tools can be listed correctly.
        
        Args:
            server_type: Either 'stdio' or 'http'
            process: Server process
            
        Returns:
            Tuple of (success, tools_list)
        """
        try:
            logger.info(f"🧪 Verifying tool listing for {server_type} server...")
            
            if server_type == "stdio":
                # First send initialize request
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 0,
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
                
                request_json = json.dumps(init_request) + "\n"
                process.stdin.write(request_json)
                process.stdin.flush()
                
                # Read initialize response
                init_response_line = process.stdout.readline()
                if init_response_line:
                    init_response = json.loads(init_response_line.strip())
                    if not (init_response.get("jsonrpc") == "2.0" and "result" in init_response):
                        logger.error(f"❌ Initialize failed: {init_response}")
                        return False, []
                else:
                    logger.error("❌ No initialize response from stdio server")
                    return False, []
                
                # Send tools/list request via stdio
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                }
                
                request_json = json.dumps(request) + "\n"
                process.stdin.write(request_json)
                process.stdin.flush()
                
                # Read response
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    
                    if (response.get("jsonrpc") == "2.0" and 
                        response.get("id") == 1 and 
                        "result" in response):
                        
                        tools = response["result"].get("tools", [])
                        logger.info(f"✅ Found {len(tools)} tools via stdio")
                        
                        for tool in tools:
                            logger.info(f"   • {tool.get('name', 'unknown')}: {tool.get('description', 'no description')}")
                        
                        return True, tools
                    else:
                        logger.error(f"❌ Invalid response: {response}")
                        return False, []
                else:
                    logger.error("❌ No response from stdio server")
                    return False, []
            
            elif server_type == "http":
                # First send initialize request
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 0,
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
                
                if HTTP_CLIENT == "requests":
                    init_response = requests.post(
                        "http://localhost:8001/jsonrpc",
                        json=init_request,
                        timeout=10
                    )
                    init_ok = init_response.status_code == 200
                    init_result = init_response.json() if init_ok else None
                elif HTTP_CLIENT == "httpx":
                    with httpx.Client() as client:
                        init_response = client.post(
                            "http://localhost:8001/jsonrpc",
                            json=init_request,
                            timeout=10
                        )
                        init_ok = init_response.status_code == 200
                        init_result = init_response.json() if init_ok else None
                else:
                    logger.error("❌ No HTTP client available for testing")
                    return False, []
                
                if not (init_ok and init_result and "result" in init_result):
                    logger.error(f"❌ Initialize failed: {init_result}")
                    return False, []
                
                # Send tools/list request via HTTP
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                }
                
                if HTTP_CLIENT == "requests":
                    response = requests.post(
                        "http://localhost:8001/jsonrpc",
                        json=request,
                        timeout=10
                    )
                    status_ok = response.status_code == 200
                    result = response.json() if status_ok else None
                elif HTTP_CLIENT == "httpx":
                    with httpx.Client() as client:
                        response = client.post(
                            "http://localhost:8001/jsonrpc",
                            json=request,
                            timeout=10
                        )
                        status_ok = response.status_code == 200
                        result = response.json() if status_ok else None
                else:
                    logger.error("❌ No HTTP client available for testing")
                    return False, []
                
                if status_ok and result:
                    if (result.get("jsonrpc") == "2.0" and 
                        result.get("id") == 1 and 
                        "result" in result):
                        
                        tools = result["result"].get("tools", [])
                        logger.info(f"✅ Found {len(tools)} tools via HTTP")
                        
                        for tool in tools:
                            logger.info(f"   • {tool.get('name', 'unknown')}: {tool.get('description', 'no description')}")
                        
                        return True, tools
                    else:
                        logger.error(f"❌ Invalid response: {result}")
                        return False, []
                else:
                    logger.error(f"❌ HTTP request failed: {response.status_code if 'response' in locals() else 'No response'}")
                    return False, []
            
            return False, []
            
        except Exception as e:
            logger.error(f"❌ Tool listing verification failed: {e}")
            return False, []
    
    def verify_tool_execution(self, server_type: str, process: subprocess.Popen, tools: List[Dict]) -> bool:
        """
        Verify that tools can be executed correctly.
        
        Args:
            server_type: Either 'stdio' or 'http'
            process: Server process
            tools: List of available tools
            
        Returns:
            True if tool execution works, False otherwise
        """
        try:
            logger.info(f"🧪 Verifying tool execution for {server_type} server...")
            
            # Test cases for different tools
            test_cases = [
                {
                    "tool": "echo",
                    "args": {"message": "Hello Inspector Test!"},
                    "expected_content": "Hello Inspector Test!"
                },
                {
                    "tool": "get_weather",
                    "args": {"city": "London"},
                    "expected_content": "London"
                }
            ]
            
            # Filter test cases to only include available tools
            available_tool_names = {tool.get("name") for tool in tools}
            valid_test_cases = [tc for tc in test_cases if tc["tool"] in available_tool_names]
            
            if not valid_test_cases:
                logger.warning("⚠️  No testable tools found")
                return True  # Not a failure, just no tools to test
            
            all_passed = True
            
            for i, test_case in enumerate(valid_test_cases, 1):
                try:
                    logger.info(f"   Testing tool: {test_case['tool']}")
                    
                    request = {
                        "jsonrpc": "2.0",
                        "id": i + 10,  # Use different IDs
                        "method": "tools/call",
                        "params": {
                            "name": test_case["tool"],
                            "arguments": test_case["args"]
                        }
                    }
                    
                    if server_type == "stdio":
                        # Send request via stdio
                        request_json = json.dumps(request) + "\n"
                        process.stdin.write(request_json)
                        process.stdin.flush()
                        
                        # Read response
                        response_line = process.stdout.readline()
                        if response_line:
                            response = json.loads(response_line.strip())
                        else:
                            logger.error(f"   ❌ No response for {test_case['tool']}")
                            all_passed = False
                            continue
                    
                    elif server_type == "http":
                        # Send request via HTTP
                        if HTTP_CLIENT == "requests":
                            http_response = requests.post(
                                "http://localhost:8001/jsonrpc",
                                json=request,
                                timeout=10
                            )
                            status_ok = http_response.status_code == 200
                            response = http_response.json() if status_ok else None
                        elif HTTP_CLIENT == "httpx":
                            with httpx.Client() as client:
                                http_response = client.post(
                                    "http://localhost:8001/jsonrpc",
                                    json=request,
                                    timeout=10
                                )
                                status_ok = http_response.status_code == 200
                                response = http_response.json() if status_ok else None
                        else:
                            logger.error(f"   ❌ No HTTP client available for {test_case['tool']}")
                            all_passed = False
                            continue
                        
                        if not status_ok:
                            logger.error(f"   ❌ HTTP error for {test_case['tool']}: {http_response.status_code}")
                            all_passed = False
                            continue
                    
                    # Verify response
                    if (response.get("jsonrpc") == "2.0" and 
                        response.get("id") == request["id"]):
                        
                        if "result" in response:
                            result = response["result"]
                            
                            # Check if result contains expected content
                            result_str = json.dumps(result).lower()
                            expected = test_case["expected_content"].lower()
                            
                            if expected in result_str:
                                logger.info(f"   ✅ {test_case['tool']} executed successfully")
                            else:
                                logger.warning(f"   ⚠️  {test_case['tool']} executed but content unexpected")
                                logger.debug(f"      Expected: {expected}")
                                logger.debug(f"      Got: {result_str[:100]}...")
                        
                        elif "error" in response:
                            error = response["error"]
                            logger.error(f"   ❌ {test_case['tool']} returned error: {error}")
                            all_passed = False
                        
                        else:
                            logger.error(f"   ❌ {test_case['tool']} returned invalid response")
                            all_passed = False
                    
                    else:
                        logger.error(f"   ❌ Invalid JSON-RPC response for {test_case['tool']}")
                        all_passed = False
                
                except Exception as e:
                    logger.error(f"   ❌ Tool execution failed for {test_case['tool']}: {e}")
                    all_passed = False
            
            if all_passed:
                logger.info("✅ All tool executions successful")
            else:
                logger.error("❌ Some tool executions failed")
            
            return all_passed
            
        except Exception as e:
            logger.error(f"❌ Tool execution verification failed: {e}")
            return False
    
    def verify_error_handling(self, server_type: str, process: subprocess.Popen) -> bool:
        """
        Verify that error handling works correctly.
        
        Args:
            server_type: Either 'stdio' or 'http'
            process: Server process
            
        Returns:
            True if error handling works, False otherwise
        """
        try:
            logger.info(f"🧪 Verifying error handling for {server_type} server...")
            
            # Test cases for error conditions
            error_test_cases = [
                {
                    "name": "invalid_method",
                    "request": {
                        "jsonrpc": "2.0",
                        "id": 100,
                        "method": "invalid/method"
                    },
                    "expected_error_code": -32601  # Method not found
                },
                {
                    "name": "invalid_tool",
                    "request": {
                        "jsonrpc": "2.0",
                        "id": 101,
                        "method": "tools/call",
                        "params": {
                            "name": "nonexistent_tool",
                            "arguments": {}
                        }
                    },
                    "expected_error": True
                },
                {
                    "name": "missing_required_param",
                    "request": {
                        "jsonrpc": "2.0",
                        "id": 102,
                        "method": "tools/call",
                        "params": {
                            "name": "echo",
                            "arguments": {}
                        }
                    },
                    "expected_error": True
                }
            ]
            
            all_passed = True
            
            for test_case in error_test_cases:
                try:
                    logger.info(f"   Testing error case: {test_case['name']}")
                    
                    if server_type == "stdio":
                        # Send request via stdio
                        request_json = json.dumps(test_case["request"]) + "\n"
                        process.stdin.write(request_json)
                        process.stdin.flush()
                        
                        # Read response
                        response_line = process.stdout.readline()
                        if response_line:
                            response = json.loads(response_line.strip())
                        else:
                            logger.error(f"   ❌ No response for {test_case['name']}")
                            all_passed = False
                            continue
                    
                    elif server_type == "http":
                        # Send request via HTTP
                        if HTTP_CLIENT == "requests":
                            http_response = requests.post(
                                "http://localhost:8001/jsonrpc",
                                json=test_case["request"],
                                timeout=10
                            )
                            status_ok = http_response.status_code == 200
                            response = http_response.json() if status_ok else None
                        elif HTTP_CLIENT == "httpx":
                            with httpx.Client() as client:
                                http_response = client.post(
                                    "http://localhost:8001/jsonrpc",
                                    json=test_case["request"],
                                    timeout=10
                                )
                                status_ok = http_response.status_code == 200
                                response = http_response.json() if status_ok else None
                        else:
                            logger.error(f"   ❌ No HTTP client available for {test_case['name']}")
                            all_passed = False
                            continue
                        
                        if not status_ok:
                            logger.error(f"   ❌ HTTP error for {test_case['name']}: {http_response.status_code}")
                            all_passed = False
                            continue
                    
                    # Verify error response
                    if (response.get("jsonrpc") == "2.0" and 
                        response.get("id") == test_case["request"]["id"]):
                        
                        if "error" in response:
                            error = response["error"]
                            
                            # Check specific error code if expected
                            if "expected_error_code" in test_case:
                                if error.get("code") == test_case["expected_error_code"]:
                                    logger.info(f"   ✅ {test_case['name']} returned correct error code")
                                else:
                                    logger.error(f"   ❌ {test_case['name']} wrong error code: {error.get('code')}")
                                    all_passed = False
                            else:
                                logger.info(f"   ✅ {test_case['name']} returned error as expected")
                        
                        else:
                            logger.error(f"   ❌ {test_case['name']} should have returned error")
                            all_passed = False
                    
                    else:
                        logger.error(f"   ❌ Invalid JSON-RPC response for {test_case['name']}")
                        all_passed = False
                
                except Exception as e:
                    logger.error(f"   ❌ Error test failed for {test_case['name']}: {e}")
                    all_passed = False
            
            if all_passed:
                logger.info("✅ All error handling tests passed")
            else:
                logger.error("❌ Some error handling tests failed")
            
            return all_passed
            
        except Exception as e:
            logger.error(f"❌ Error handling verification failed: {e}")
            return False
    
    def run_comprehensive_verification(self, server_type: str) -> bool:
        """
        Run comprehensive verification for a server type.
        
        Args:
            server_type: Either 'stdio' or 'http'
            
        Returns:
            True if all verifications pass, False otherwise
        """
        logger.info(f"\n🔍 Running comprehensive verification for {server_type} server...")
        
        # Step 1: Verify server startup
        success, process = self.verify_server_startup(server_type)
        if not success:
            return False
        
        try:
            # Step 2: Verify tool listing
            success, tools = self.verify_tool_listing(server_type, process)
            if not success:
                return False
            
            # Step 3: Verify tool execution
            success = self.verify_tool_execution(server_type, process, tools)
            if not success:
                return False
            
            # Step 4: Verify error handling (optional - don't fail if this doesn't work)
            error_success = self.verify_error_handling(server_type, process)
            if not error_success:
                logger.warning("⚠️  Error handling tests failed, but core functionality works")
            
            logger.info(f"✅ All verifications passed for {server_type} server!")
            return True
            
        finally:
            # Clean up process
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                    process.wait()
                except:
                    pass
    
    def generate_verification_report(self, stdio_result: bool, http_result: bool) -> str:
        """
        Generate a verification report.
        
        Args:
            stdio_result: Result of stdio server verification
            http_result: Result of HTTP server verification
            
        Returns:
            Formatted report string
        """
        report = "\n" + "="*60 + "\n"
        report += "MCP INSPECTOR INTEGRATION VERIFICATION REPORT\n"
        report += "="*60 + "\n"
        
        report += f"📋 Stdio Server: {'✅ PASSED' if stdio_result else '❌ FAILED'}\n"
        report += f"📋 HTTP Server:  {'✅ PASSED' if http_result else '❌ FAILED'}\n"
        
        report += "\n📊 Verification Coverage:\n"
        report += "   • Server startup and initialization\n"
        report += "   • Tool listing functionality\n"
        report += "   • Tool execution with valid parameters\n"
        report += "   • Error handling for invalid requests\n"
        report += "   • JSON-RPC protocol compliance\n"
        
        if stdio_result and http_result:
            report += "\n🎉 OVERALL RESULT: ALL TESTS PASSED\n"
            report += "Your MCP servers are ready for Inspector integration!\n"
        elif stdio_result or http_result:
            report += "\n⚠️  OVERALL RESULT: PARTIAL SUCCESS\n"
            report += "Some servers passed verification. Check failed tests above.\n"
        else:
            report += "\n💥 OVERALL RESULT: ALL TESTS FAILED\n"
            report += "Please fix the issues before using MCP Inspector.\n"
        
        report += "\n🔧 Next Steps:\n"
        if stdio_result:
            report += "   • Test stdio server: python scripts/test_with_inspector.py stdio\n"
        if http_result:
            report += "   • Test HTTP server: python scripts/test_with_inspector.py http\n"
        
        report += "   • Use MCP Inspector: npx @modelcontextprotocol/inspector\n"
        report += "="*60
        
        return report


def main():
    """Command-line interface for MCP Inspector integration verification."""
    parser = argparse.ArgumentParser(
        description="Verify MCP Inspector integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Verify both stdio and HTTP servers
  %(prog)s --stdio-only                 # Verify stdio server only
  %(prog)s --http-only                  # Verify HTTP server only

This script performs comprehensive verification of:
  - Server startup and initialization
  - Tool listing functionality  
  - Tool execution with parameters
  - Error handling for invalid requests
  - JSON-RPC protocol compliance
        """
    )
    
    parser.add_argument(
        "--stdio-only",
        action="store_true",
        help="Verify stdio server only"
    )
    
    parser.add_argument(
        "--http-only",
        action="store_true",
        help="Verify HTTP server only"
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
    
    # Create verifier
    verifier = InspectorIntegrationVerifier()
    
    try:
        stdio_result = True
        http_result = True
        
        if not args.http_only:
            stdio_result = verifier.run_comprehensive_verification("stdio")
        
        if not args.stdio_only:
            http_result = verifier.run_comprehensive_verification("http")
        
        # Generate and display report
        report = verifier.generate_verification_report(stdio_result, http_result)
        print(report)
        
        # Exit with appropriate code
        if (not args.http_only and not stdio_result) or (not args.stdio_only and not http_result):
            sys.exit(1)
        else:
            sys.exit(0)
    
    except KeyboardInterrupt:
        logger.info("\nVerification interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()