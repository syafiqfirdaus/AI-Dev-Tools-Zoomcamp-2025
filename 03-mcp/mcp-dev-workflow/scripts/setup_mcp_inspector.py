#!/usr/bin/env python3
"""
Setup script for MCP Inspector integration.

This script helps configure and test MCP servers with the MCP Inspector
web interface for visual debugging and testing.
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import shutil

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.mcp_config import MCPConfig


logger = logging.getLogger(__name__)


class MCPInspectorSetup:
    """Handles MCP Inspector setup and configuration."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.python_path = sys.executable
        self.inspector_url = None
        
    def check_node_installation(self) -> bool:
        """
        Check if Node.js is installed and available.
        
        Returns:
            True if Node.js is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"✅ Node.js found: {version}")
                return True
            else:
                logger.error("❌ Node.js not found or not working")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("❌ Node.js not found in PATH")
            return False
    
    def check_mcp_inspector_installation(self) -> bool:
        """
        Check if MCP Inspector is available via npx.
        
        Returns:
            True if MCP Inspector is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/inspector", "--help"], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                logger.info("✅ MCP Inspector is available via npx")
                return True
            else:
                logger.warning("⚠️  MCP Inspector may not be available")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("❌ npx not found or MCP Inspector not available")
            return False
    
    def install_mcp_inspector_via_brew(self) -> bool:
        """
        Try to install MCP Inspector via Homebrew (macOS/Linux).
        
        Returns:
            True if installation successful, False otherwise
        """
        try:
            # Check if brew is available
            result = subprocess.run(
                ["brew", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode != 0:
                logger.info("Homebrew not available")
                return False
            
            logger.info("Installing MCP Inspector via Homebrew...")
            result = subprocess.run(
                ["brew", "install", "mcp-inspector"], 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ MCP Inspector installed via Homebrew")
                return True
            else:
                logger.error(f"❌ Homebrew installation failed: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.info("Homebrew not available for MCP Inspector installation")
            return False
    
    def get_server_configurations(self) -> List[Dict[str, Any]]:
        """
        Get available MCP server configurations for testing.
        
        Returns:
            List of server configuration dictionaries
        """
        configs = []
        
        # Stdio server configuration
        stdio_config = {
            "name": "mcp-dev-workflow-stdio",
            "type": "stdio",
            "command": self.python_path,
            "args": ["-m", "mcp_server.stdio_server"],
            "cwd": str(self.project_root),
            "env": {
                "PYTHONPATH": str(self.project_root),
                "CONTEXT7_API_KEY": os.getenv("CONTEXT7_API_KEY", "")
            }
        }
        configs.append(stdio_config)
        
        # HTTP server configuration
        http_config = {
            "name": "mcp-dev-workflow-http",
            "type": "http",
            "url": "http://localhost:8001/jsonrpc",
            "command": self.python_path,
            "args": ["-m", "mcp_server.http_server", "--port", "8001"],
            "cwd": str(self.project_root),
            "env": {
                "PYTHONPATH": str(self.project_root),
                "CONTEXT7_API_KEY": os.getenv("CONTEXT7_API_KEY", "")
            }
        }
        configs.append(http_config)
        
        return configs
    
    def start_inspector_with_stdio_server(self, server_config: Dict[str, Any]) -> Optional[subprocess.Popen]:
        """
        Start MCP Inspector with stdio server configuration.
        
        Args:
            server_config: Server configuration dictionary
            
        Returns:
            Process object if successful, None otherwise
        """
        try:
            # Prepare command for MCP Inspector
            inspector_cmd = [
                "npx", "@modelcontextprotocol/inspector",
                server_config["command"]
            ] + server_config["args"]
            
            logger.info(f"Starting MCP Inspector with stdio server...")
            logger.info(f"Command: {' '.join(inspector_cmd)}")
            
            # Set up environment
            env = dict(os.environ)
            env.update(server_config.get("env", {}))
            
            # Start the inspector
            process = subprocess.Popen(
                inspector_cmd,
                cwd=server_config["cwd"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info("✅ MCP Inspector started successfully")
                
                # Try to extract the URL from output
                try:
                    # Read some output to find the URL
                    import select
                    if select.select([process.stdout], [], [], 1)[0]:
                        output = process.stdout.read(1024)
                        if "localhost" in output:
                            # Extract URL from output
                            lines = output.split('\n')
                            for line in lines:
                                if "localhost" in line and ("http" in line or "6274" in line):
                                    logger.info(f"Inspector URL: {line.strip()}")
                                    self.inspector_url = line.strip()
                                    break
                except:
                    pass
                
                if not self.inspector_url:
                    self.inspector_url = "http://localhost:6274"
                    logger.info(f"Inspector likely available at: {self.inspector_url}")
                
                return process
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ MCP Inspector failed to start")
                logger.error(f"stdout: {stdout}")
                logger.error(f"stderr: {stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to start MCP Inspector: {e}")
            return None
    
    def test_http_server_with_inspector(self, server_config: Dict[str, Any]) -> bool:
        """
        Test HTTP server configuration with MCP Inspector.
        
        Args:
            server_config: HTTP server configuration
            
        Returns:
            True if test successful, False otherwise
        """
        try:
            logger.info("Testing HTTP server configuration with MCP Inspector...")
            
            # Start the HTTP server first
            logger.info("Starting HTTP server...")
            
            env = dict(os.environ)
            env.update(server_config.get("env", {}))
            
            server_process = subprocess.Popen(
                [server_config["command"]] + server_config["args"],
                cwd=server_config["cwd"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give server time to start
            time.sleep(3)
            
            if server_process.poll() is not None:
                stdout, stderr = server_process.communicate()
                logger.error(f"❌ HTTP server failed to start")
                logger.error(f"stdout: {stdout}")
                logger.error(f"stderr: {stderr}")
                return False
            
            logger.info("✅ HTTP server started successfully")
            
            # Test the HTTP endpoint
            try:
                # Try to import an HTTP client
                http_client = None
                try:
                    import requests
                    http_client = "requests"
                except ImportError:
                    try:
                        import httpx
                        http_client = "httpx"
                    except ImportError:
                        pass
                
                if not http_client:
                    logger.warning("⚠️  No HTTP client available for testing")
                    logger.info("Install requests or httpx: pip install requests")
                    logger.info("Assuming HTTP server is working...")
                    
                    # Provide instructions without testing
                    logger.info("\n" + "="*60)
                    logger.info("HTTP SERVER READY FOR MCP INSPECTOR TESTING")
                    logger.info("="*60)
                    logger.info(f"1. Open MCP Inspector in your browser")
                    logger.info(f"2. Configure HTTP server with URL: {server_config['url']}")
                    logger.info(f"3. Test the available tools")
                    logger.info("="*60)
                    return True
                
                # Test health endpoint
                if http_client == "requests":
                    health_response = requests.get("http://localhost:8001/health", timeout=5)
                    health_ok = health_response.status_code == 200
                else:  # httpx
                    with httpx.Client() as client:
                        health_response = client.get("http://localhost:8001/health", timeout=5)
                        health_ok = health_response.status_code == 200
                
                if health_ok:
                    logger.info("✅ HTTP server health check passed")
                else:
                    logger.warning(f"⚠️  Health check returned status {health_response.status_code}")
                
                # Test JSON-RPC endpoint
                jsonrpc_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "inspector-test",
                            "version": "1.0.0"
                        }
                    }
                }
                
                if http_client == "requests":
                    response = requests.post(
                        "http://localhost:8001/jsonrpc",
                        json=jsonrpc_request,
                        timeout=10
                    )
                    response_ok = response.status_code == 200
                    result = response.json() if response_ok else None
                else:  # httpx
                    with httpx.Client() as client:
                        response = client.post(
                            "http://localhost:8001/jsonrpc",
                            json=jsonrpc_request,
                            timeout=10
                        )
                        response_ok = response.status_code == 200
                        result = response.json() if response_ok else None
                
                if response_ok and result:
                    if result.get("jsonrpc") == "2.0" and "result" in result:
                        logger.info("✅ HTTP server JSON-RPC endpoint working")
                        logger.info(f"Server URL for MCP Inspector: {server_config['url']}")
                        
                        # Provide instructions for manual testing
                        logger.info("\n" + "="*60)
                        logger.info("HTTP SERVER READY FOR MCP INSPECTOR TESTING")
                        logger.info("="*60)
                        logger.info(f"1. Open MCP Inspector in your browser")
                        logger.info(f"2. Configure HTTP server with URL: {server_config['url']}")
                        logger.info(f"3. Test the available tools")
                        logger.info("="*60)
                        
                        return True
                    else:
                        logger.error(f"❌ Invalid JSON-RPC response: {result}")
                else:
                    logger.error(f"❌ HTTP request failed with status {response.status_code if 'response' in locals() else 'unknown'}")
                    
            except ImportError:
                logger.warning("⚠️  HTTP client library not available for testing")
                logger.info("Install with: pip install requests")
                return False
            except Exception as e:
                logger.error(f"❌ HTTP server test failed: {e}")
            finally:
                # Clean up server process
                try:
                    server_process.terminate()
                    server_process.wait(timeout=5)
                except:
                    server_process.kill()
            
            return False
            
        except Exception as e:
            logger.error(f"❌ HTTP server test failed: {e}")
            return False
    
    def create_inspector_config_file(self, output_path: Path) -> bool:
        """
        Create a configuration file for MCP Inspector.
        
        Args:
            output_path: Path to write the configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            configs = self.get_server_configurations()
            
            inspector_config = {
                "servers": {}
            }
            
            for config in configs:
                if config["type"] == "stdio":
                    inspector_config["servers"][config["name"]] = {
                        "command": config["command"],
                        "args": config["args"],
                        "env": config["env"]
                    }
            
            with open(output_path, 'w') as f:
                json.dump(inspector_config, f, indent=2)
            
            logger.info(f"✅ Inspector configuration written to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create inspector config: {e}")
            return False
    
    def run_interactive_setup(self) -> bool:
        """
        Run interactive setup for MCP Inspector.
        
        Returns:
            True if setup successful, False otherwise
        """
        logger.info("🔧 MCP Inspector Interactive Setup")
        logger.info("="*50)
        
        # Check prerequisites
        if not self.check_node_installation():
            logger.error("Node.js is required for MCP Inspector")
            logger.info("Please install Node.js from: https://nodejs.org/")
            return False
        
        # Check MCP Inspector availability
        if not self.check_mcp_inspector_installation():
            logger.info("Attempting to install MCP Inspector...")
            if not self.install_mcp_inspector_via_brew():
                logger.info("Please install MCP Inspector manually:")
                logger.info("  npm install -g @modelcontextprotocol/inspector")
                logger.info("  or")
                logger.info("  brew install mcp-inspector")
                return False
        
        # Get server configurations
        configs = self.get_server_configurations()
        
        logger.info(f"\n📋 Available server configurations:")
        for i, config in enumerate(configs, 1):
            logger.info(f"  {i}. {config['name']} ({config['type']})")
        
        # Test stdio server
        stdio_config = next((c for c in configs if c["type"] == "stdio"), None)
        if stdio_config:
            logger.info(f"\n🧪 Testing stdio server configuration...")
            
            try:
                # Start inspector with stdio server
                inspector_process = self.start_inspector_with_stdio_server(stdio_config)
                
                if inspector_process:
                    logger.info("\n" + "="*60)
                    logger.info("STDIO SERVER READY FOR MCP INSPECTOR TESTING")
                    logger.info("="*60)
                    logger.info(f"MCP Inspector URL: {self.inspector_url}")
                    logger.info("Available tools: echo, get_weather")
                    if os.getenv("CONTEXT7_API_KEY"):
                        logger.info("Context7 tools: search_libraries, get_documentation, get_examples")
                    logger.info("\nPress Enter to continue to HTTP server test...")
                    logger.info("Press Ctrl+C to stop")
                    logger.info("="*60)
                    
                    try:
                        # Try to open browser
                        if self.inspector_url:
                            webbrowser.open(self.inspector_url)
                        
                        input()  # Wait for user input
                        
                    except KeyboardInterrupt:
                        logger.info("\nStopping stdio server test...")
                    finally:
                        # Clean up
                        try:
                            inspector_process.terminate()
                            inspector_process.wait(timeout=5)
                        except:
                            inspector_process.kill()
        
        # Test HTTP server
        http_config = next((c for c in configs if c["type"] == "http"), None)
        if http_config:
            logger.info(f"\n🧪 Testing HTTP server configuration...")
            success = self.test_http_server_with_inspector(http_config)
            
            if success:
                logger.info("\nPress Enter to finish setup...")
                try:
                    input()
                except KeyboardInterrupt:
                    pass
        
        logger.info("\n✅ MCP Inspector setup completed!")
        return True


def main():
    """Command-line interface for MCP Inspector setup."""
    parser = argparse.ArgumentParser(
        description="Setup and test MCP Inspector integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Run interactive setup
  %(prog)s --config-only                # Generate config file only
  %(prog)s --test-stdio                 # Test stdio server only
  %(prog)s --test-http                  # Test HTTP server only

MCP Inspector Usage:
  After setup, you can use MCP Inspector to visually test your MCP servers:
  
  1. For stdio servers:
     npx @modelcontextprotocol/inspector python -m mcp_server.stdio_server
  
  2. For HTTP servers:
     Start server: python -m mcp_server.http_server --port 8001
     Configure inspector with URL: http://localhost:8001/jsonrpc
        """
    )
    
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Generate configuration file only, don't run tests"
    )
    
    parser.add_argument(
        "--test-stdio",
        action="store_true",
        help="Test stdio server configuration only"
    )
    
    parser.add_argument(
        "--test-http",
        action="store_true",
        help="Test HTTP server configuration only"
    )
    
    parser.add_argument(
        "--output-config",
        type=Path,
        default="mcp_inspector_config.json",
        help="Output path for inspector configuration file"
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
    
    # Create setup instance
    setup = MCPInspectorSetup()
    
    try:
        if args.config_only:
            # Generate config file only
            success = setup.create_inspector_config_file(args.output_config)
            sys.exit(0 if success else 1)
        
        elif args.test_stdio:
            # Test stdio server only
            configs = setup.get_server_configurations()
            stdio_config = next((c for c in configs if c["type"] == "stdio"), None)
            if stdio_config:
                process = setup.start_inspector_with_stdio_server(stdio_config)
                if process:
                    logger.info("Press Ctrl+C to stop...")
                    try:
                        process.wait()
                    except KeyboardInterrupt:
                        process.terminate()
                    sys.exit(0)
            sys.exit(1)
        
        elif args.test_http:
            # Test HTTP server only
            configs = setup.get_server_configurations()
            http_config = next((c for c in configs if c["type"] == "http"), None)
            if http_config:
                success = setup.test_http_server_with_inspector(http_config)
                sys.exit(0 if success else 1)
            sys.exit(1)
        
        else:
            # Run interactive setup
            success = setup.run_interactive_setup()
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        logger.info("\nSetup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()