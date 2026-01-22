#!/usr/bin/env python3
"""
Script to run MCP server in HTTP mode
Provides easy startup with configuration options and error handling.
"""

import sys
import argparse
import asyncio
import socket
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from mcp_server.http_server import main as http_main
except ImportError as e:
    print(f"❌ Failed to import MCP server: {e}")
    print("   Make sure you've run the setup script and activated the environment.")
    print("   Run: python scripts/setup.py")
    sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run MCP server in HTTP mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_http_server.py
  python scripts/run_http_server.py --port 8080
  python scripts/run_http_server.py --host 0.0.0.0 --port 8080 --debug

Test with curl:
  curl -X POST http://localhost:8000/mcp \\
    -H "Content-Type: application/json" \\
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
        """
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging and auto-reload"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
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


def check_port_available(host: str, port: int) -> bool:
    """Check if the specified port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
            return True
    except OSError:
        return False


def suggest_alternative_port(host: str, start_port: int) -> int:
    """Suggest an alternative port if the requested one is not available."""
    for port in range(start_port + 1, start_port + 100):
        if check_port_available(host, port):
            return port
    return None


def main():
    """Main entry point."""
    print("🚀 Starting MCP Server (HTTP mode)...")
    
    # Parse arguments
    args = parse_arguments()
    
    # Check environment
    if not check_environment():
        return 1
    
    # Check if port is available
    if not check_port_available(args.host, args.port):
        print(f"❌ Port {args.port} is already in use on {args.host}")
        
        # Suggest alternative port
        alt_port = suggest_alternative_port(args.host, args.port)
        if alt_port:
            print(f"💡 Suggested alternative port: {alt_port}")
            print(f"   Run with: --port {alt_port}")
        else:
            print("   No alternative ports found in range")
        return 1
    
    # Set up logging level
    import logging
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(level=log_level)
    
    if args.debug:
        print("🐛 Debug mode enabled")
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        print(f"🌐 Server starting on http://{args.host}:{args.port}")
        print(f"📡 MCP endpoint: http://{args.host}:{args.port}/mcp")
        print(f"📚 API docs: http://{args.host}:{args.port}/docs")
        print("   Press Ctrl+C to stop the server")
        print()
        
        # Prepare server configuration
        server_config = {
            "host": args.host,
            "port": args.port,
            "log_level": args.log_level.lower(),
            "workers": args.workers,
        }
        
        if args.debug:
            server_config["reload"] = True
            server_config["reload_dirs"] = [str(project_root)]
        
        # Run the HTTP server
        return http_main(**server_config)
        
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