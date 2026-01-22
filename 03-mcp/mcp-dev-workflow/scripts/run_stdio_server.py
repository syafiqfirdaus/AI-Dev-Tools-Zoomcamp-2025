#!/usr/bin/env python3
"""
Script to run MCP server in stdio mode
Provides easy startup with configuration options and error handling.
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from mcp_server.stdio_server import main as stdio_main
except ImportError as e:
    print(f"❌ Failed to import MCP server: {e}")
    print("   Make sure you've run the setup script and activated the environment.")
    print("   Run: python scripts/setup.py")
    sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run MCP server in stdio mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_stdio_server.py
  python scripts/run_stdio_server.py --debug
  python scripts/run_stdio_server.py --log-level INFO

Test with JSON-RPC requests:
  1. Initialize: {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
  2. Initialized: {"jsonrpc":"2.0","method":"notifications/initialized"}
  3. List tools: {"jsonrpc":"2.0","id":2,"method":"tools/list"}
  4. Call tool: {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_weather","arguments":{"city":"London"}}}
        """
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    return parser.parse_args()


def check_environment():
    """Check if the environment is properly set up."""
    try:
        import mcp
        import fastapi
        import uvicorn
        return True
    except ImportError as e:
        print(f"❌ Missing required dependencies: {e}")
        print("   Please run the setup script first:")
        print("   python scripts/setup.py")
        return False


def main():
    """Main entry point."""
    print("🚀 Starting MCP Server (stdio mode)...")
    
    # Parse arguments
    args = parse_arguments()
    
    # Check environment
    if not check_environment():
        return 1
    
    # Set up logging level
    import logging
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(level=log_level)
    
    if args.debug:
        print("🐛 Debug mode enabled")
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        print("📡 Server ready for JSON-RPC requests on stdin/stdout")
        print("   Send JSON-RPC requests line by line")
        print("   Press Ctrl+C to stop the server")
        print("   See --help for example requests")
        print()
        
        # Run the stdio server
        return stdio_main()
        
    except KeyboardInterrupt:
        print("\n⚠️  Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())