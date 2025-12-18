#!/usr/bin/env python3
"""
Main HTTP MCP server executable.

This script creates and runs an MCP server using HTTP transport with FastAPI,
registering available tools and handling JSON-RPC communication over HTTP.
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from typing import Optional

from mcp_server.core.server import MCPServer
from mcp_server.tools import (
    EchoTool, 
    WeatherTool, 
    Context7Client,
    Context7SearchTool,
    Context7DocumentationTool,
    Context7ExamplesTool,
)
from mcp_server.transport.http import HTTPTransport


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="MCP Development Workflow - HTTP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Start server on default port 8000
  %(prog)s --port 8080                  # Start server on port 8080
  %(prog)s --host 0.0.0.0 --port 8080   # Start server accessible from all interfaces
  %(prog)s --log-level DEBUG            # Start with debug logging

HTTP Communication:
  The server accepts JSON-RPC 2.0 requests via HTTP POST to /jsonrpc endpoint.
  
  Example requests:
  1. Initialize: POST http://localhost:8000/jsonrpc
     {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
  
  2. List tools: POST http://localhost:8000/jsonrpc
     {"jsonrpc":"2.0","id":2,"method":"tools/list"}
  
  3. Call tool: POST http://localhost:8000/jsonrpc
     {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_weather","arguments":{"city":"London"}}}

  Health check: GET http://localhost:8000/health
        """
    )
    
    parser.add_argument(
        "--server-name",
        default="mcp-dev-workflow-http",
        help="Name of the MCP server (default: mcp-dev-workflow-http)"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="MCP Development Workflow HTTP Server v0.1.0"
    )
    
    return parser.parse_args()


async def create_server(server_name: str, host: str, port: int) -> MCPServer:
    """
    Create and configure the MCP server with tools.
    
    Args:
        server_name: Name for the server
        host: Host address to bind to
        port: Port number to bind to
        
    Returns:
        Configured MCP server instance
    """
    # Create HTTP transport
    transport = HTTPTransport(host=host, port=port)
    
    # Create server
    server = MCPServer(transport, server_name)
    
    # Register available tools
    server.register_tool(EchoTool())
    server.register_tool(WeatherTool())
    
    # Register Context7 tools if API key is available
    context7_api_key = os.getenv("CONTEXT7_API_KEY")
    if context7_api_key:
        try:
            context7_client = Context7Client(context7_api_key)
            server.register_tool(Context7SearchTool(context7_client))
            server.register_tool(Context7DocumentationTool(context7_client))
            server.register_tool(Context7ExamplesTool(context7_client))
            
            logger = logging.getLogger(__name__)
            logger.info("Context7 tools registered successfully")
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to register Context7 tools: {e}")
    else:
        logger = logging.getLogger(__name__)
        logger.info("Context7 API key not found. Set CONTEXT7_API_KEY environment variable to enable Context7 tools.")
    
    logger = logging.getLogger(__name__)
    logger.info(f"Server '{server_name}' created with {len(server.tools_manager.tools)} tools")
    
    return server


async def run_server(server: MCPServer, host: str, port: int) -> None:
    """
    Run the MCP server until interrupted.
    
    Args:
        server: MCP server instance to run
        host: Host address
        port: Port number
    """
    logger = logging.getLogger(__name__)
    
    # Set up signal handlers for graceful shutdown
    shutdown_event = asyncio.Event()
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        shutdown_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Starting MCP HTTP server...")
        await server.start()
        
        logger.info(f"Server started successfully on http://{host}:{port}")
        logger.info(f"JSON-RPC endpoint: http://{host}:{port}/jsonrpc")
        logger.info(f"Health check endpoint: http://{host}:{port}/health")
        logger.info("Server is ready to accept requests. Press Ctrl+C to stop.")
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Stopping server...")
        await server.stop()
        logger.info("Server stopped")


async def check_port_availability(host: str, port: int) -> bool:
    """
    Check if the specified port is available.
    
    Args:
        host: Host address
        port: Port number
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        # Try to bind to the port
        server = await asyncio.start_server(lambda r, w: None, host, port)
        server.close()
        await server.wait_closed()
        return True
    except OSError:
        return False


async def main_async() -> None:
    """Main async entry point."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"MCP Development Workflow HTTP Server starting...")
    logger.info(f"Server name: {args.server_name}")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Log level: {args.log_level}")
    
    # Check port availability
    if not await check_port_availability(args.host, args.port):
        logger.error(f"Port {args.port} is already in use on {args.host}")
        logger.info("Try using a different port with --port option")
        
        # Suggest alternative ports
        suggested_ports = [8001, 8080, 8888, 9000]
        for suggested_port in suggested_ports:
            if await check_port_availability(args.host, suggested_port):
                logger.info(f"Alternative port available: {suggested_port}")
                break
        
        sys.exit(1)
    
    # Create and run server
    server = await create_server(args.server_name, args.host, args.port)
    await run_server(server, args.host, args.port)


def main() -> None:
    """Main entry point for the HTTP server."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nServer interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()