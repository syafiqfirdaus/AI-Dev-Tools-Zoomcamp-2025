#!/usr/bin/env python3
"""
Main stdio MCP server executable.

This script creates and runs an MCP server using stdio transport,
registering available tools and handling JSON-RPC communication.
"""

import argparse
import asyncio
import logging
import os
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
from mcp_server.transport.stdio import StdioTransport


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure logging to stderr so it doesn't interfere with stdio communication
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="MCP Development Workflow - stdio server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start server with default settings
  %(prog)s --log-level DEBUG  # Start with debug logging
  %(prog)s --server-name my-server  # Start with custom server name

JSON-RPC Communication:
  The server communicates via stdin/stdout using JSON-RPC 2.0 protocol.
  
  Example requests:
  1. Initialize: {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
  2. List tools: {"jsonrpc":"2.0","id":2,"method":"tools/list"}
  3. Call tool: {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_weather","arguments":{"city":"London"}}}
        """
    )
    
    parser.add_argument(
        "--server-name",
        default="mcp-dev-workflow",
        help="Name of the MCP server (default: mcp-dev-workflow)"
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
        version="MCP Development Workflow Server v0.1.0"
    )
    
    return parser.parse_args()


async def create_server(server_name: str) -> MCPServer:
    """
    Create and configure the MCP server with tools.
    
    Args:
        server_name: Name for the server
        
    Returns:
        Configured MCP server instance
    """
    # Create stdio transport
    transport = StdioTransport()
    
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


async def run_server(server: MCPServer) -> None:
    """
    Run the MCP server until interrupted.
    
    Args:
        server: MCP server instance to run
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting MCP stdio server...")
        await server.start()
        
        logger.info("Server started successfully. Waiting for JSON-RPC requests on stdin...")
        
        # Keep the server running until interrupted
        while server._running:
            await asyncio.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Stopping server...")
        await server.stop()
        logger.info("Server stopped")


async def main_async() -> None:
    """Main async entry point."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"MCP Development Workflow Server starting...")
    logger.info(f"Server name: {args.server_name}")
    logger.info(f"Log level: {args.log_level}")
    
    # Create and run server
    server = await create_server(args.server_name)
    await run_server(server)


def main() -> None:
    """Main entry point for the stdio server."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nServer interrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()