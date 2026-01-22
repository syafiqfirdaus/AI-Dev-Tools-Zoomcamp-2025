#!/usr/bin/env python3
"""
Test script for MCP configuration and server connectivity.

This script tests the MCP configuration and verifies that servers
can be started and respond to basic requests.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.mcp_config import MCPConfig, validate_config_file


logger = logging.getLogger(__name__)


async def test_stdio_server(server_config: Dict[str, Any], timeout: int = 10) -> bool:
    """
    Test stdio MCP server by sending a basic request.
    
    Args:
        server_config: Server configuration dictionary
        timeout: Timeout in seconds
        
    Returns:
        True if server responds correctly, False otherwise
    """
    try:
        # Prepare command
        command = [server_config["command"]] + server_config.get("args", [])
        cwd = server_config.get("cwd", ".")
        env = server_config.get("env", {})
        
        # Merge with current environment
        full_env = dict(os.environ)
        full_env.update(env)
        
        logger.info(f"Starting stdio server: {' '.join(command)}")
        logger.info(f"Working directory: {cwd}")
        
        # Start server process
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=full_env
        )
        
        # Send initialize request
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
        
        request_data = json.dumps(init_request) + "\n"
        
        # Send request and wait for response
        try:
            process.stdin.write(request_data.encode())
            await process.stdin.drain()
            
            # Read response with timeout
            response_data = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=timeout
            )
            
            if response_data:
                response = json.loads(response_data.decode().strip())
                
                # Check if response is valid
                if (response.get("jsonrpc") == "2.0" and 
                    response.get("id") == 1 and 
                    "result" in response):
                    logger.info("✅ Server responded correctly to initialize request")
                    
                    # Test tools/list request
                    list_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list"
                    }
                    
                    request_data = json.dumps(list_request) + "\n"
                    process.stdin.write(request_data.encode())
                    await process.stdin.drain()
                    
                    response_data = await asyncio.wait_for(
                        process.stdout.readline(),
                        timeout=timeout
                    )
                    
                    if response_data:
                        response = json.loads(response_data.decode().strip())
                        if (response.get("jsonrpc") == "2.0" and 
                            response.get("id") == 2 and 
                            "result" in response):
                            tools = response["result"].get("tools", [])
                            logger.info(f"✅ Server returned {len(tools)} tools")
                            for tool in tools:
                                logger.info(f"   • {tool.get('name', 'unknown')}")
                            return True
                        else:
                            logger.error("❌ Invalid response to tools/list request")
                    else:
                        logger.error("❌ No response to tools/list request")
                else:
                    logger.error("❌ Invalid response to initialize request")
            else:
                logger.error("❌ No response from server")
                
        except asyncio.TimeoutError:
            logger.error(f"❌ Server did not respond within {timeout} seconds")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON response: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to test server: {e}")
        return False
    finally:
        # Clean up process
        try:
            if process.returncode is None:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5)
        except:
            try:
                process.kill()
                await process.wait()
            except:
                pass


async def test_mcp_configuration(config_path: Path) -> bool:
    """
    Test MCP configuration by validating and testing servers.
    
    Args:
        config_path: Path to MCP configuration file
        
    Returns:
        True if all tests pass, False otherwise
    """
    logger.info(f"Testing MCP configuration: {config_path}")
    
    # Validate configuration file
    if not validate_config_file(config_path):
        logger.error("❌ Configuration validation failed")
        return False
    
    # Load configuration
    try:
        config = MCPConfig.from_file(config_path)
    except Exception as e:
        logger.error(f"❌ Failed to load configuration: {e}")
        return False
    
    # Test enabled servers
    enabled_servers = config.get_enabled_servers()
    if not enabled_servers:
        logger.warning("⚠️  No enabled servers to test")
        return True
    
    logger.info(f"Testing {len(enabled_servers)} enabled servers...")
    
    all_passed = True
    for server_name, server_config in enabled_servers.items():
        logger.info(f"\n🧪 Testing server: {server_name}")
        
        # Convert server config to dictionary for testing
        server_dict = server_config.to_dict()
        
        # Only test stdio servers for now
        if "stdio" in server_name.lower():
            success = await test_stdio_server(server_dict)
            if success:
                logger.info(f"✅ Server '{server_name}' test passed")
            else:
                logger.error(f"❌ Server '{server_name}' test failed")
                all_passed = False
        else:
            logger.info(f"⏭️  Skipping HTTP server test for '{server_name}'")
    
    return all_passed


def main():
    """Command-line interface for MCP configuration testing."""
    parser = argparse.ArgumentParser(
        description="Test MCP configuration and server connectivity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Test default mcp.json
  %(prog)s --config custom.json         # Test custom configuration
  %(prog)s --timeout 30                 # Use 30-second timeout
        """
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        default="mcp.json",
        help="Path to MCP configuration file (default: mcp.json)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout for server responses in seconds (default: 10)"
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
    
    # os is already imported at the top
    
    # Check if configuration file exists
    if not args.config.exists():
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    # Run tests
    try:
        success = asyncio.run(test_mcp_configuration(args.config))
        
        if success:
            logger.info("\n🎉 All tests passed!")
            print("\n" + "="*50)
            print("✅ MCP Configuration Test Results: PASSED")
            print("="*50)
            print("Your MCP configuration is working correctly.")
            print("You can now use it with VSCode or other MCP clients.")
        else:
            logger.error("\n💥 Some tests failed!")
            print("\n" + "="*50)
            print("❌ MCP Configuration Test Results: FAILED")
            print("="*50)
            print("Please check the error messages above and fix the issues.")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()