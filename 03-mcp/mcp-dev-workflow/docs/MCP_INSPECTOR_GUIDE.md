# MCP Inspector Integration Guide

This guide explains how to use MCP Inspector to test and debug your MCP servers visually through a web interface.

## Overview

MCP Inspector is a web-based tool that provides a visual interface for testing MCP servers. It allows you to:

- Connect to MCP servers (stdio and HTTP modes)
- List available tools with their schemas
- Execute tools with custom parameters
- View request/response data in real-time
- Debug server communication issues

## Prerequisites

### Required Software

1. **Node.js** (version 14 or higher)
   ```bash
   # Check if Node.js is installed
   node --version
   
   # Install Node.js if needed
   # Visit: https://nodejs.org/
   ```

2. **MCP Inspector**
   ```bash
   # Install via npm (recommended)
   npm install -g @modelcontextprotocol/inspector
   
   # Or use via npx (no installation needed)
   npx @modelcontextprotocol/inspector --help
   
   # Or install via Homebrew (macOS/Linux)
   brew install mcp-inspector
   ```

3. **Python Environment** (already set up in this project)
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

### Optional: Context7 API Key

For full functionality including Context7 tools:

```bash
export CONTEXT7_API_KEY="your-api-key-here"
```

## Quick Start

### 1. Verify Server Functionality

Before using MCP Inspector, verify that your servers work correctly:

```bash
# Run comprehensive verification
python scripts/verify_inspector_integration.py

# Or test basic functionality
python scripts/test_with_inspector.py test
```

### 2. Test Stdio Server with Inspector

The easiest way to test the stdio server:

```bash
# Automated setup and launch
python scripts/test_with_inspector.py stdio
```

This will:
- Start MCP Inspector with the stdio server
- Open your browser automatically
- Display available tools for testing

### 3. Test HTTP Server with Inspector

For HTTP server testing:

```bash
# Start HTTP server
python scripts/test_with_inspector.py http

# Then manually configure Inspector:
# 1. Open: npx @modelcontextprotocol/inspector
# 2. Configure HTTP URL: http://localhost:8001/jsonrpc
```

## Manual Setup Instructions

### Stdio Server Configuration

1. **Start MCP Inspector with stdio server:**
   ```bash
   npx @modelcontextprotocol/inspector \
     python -m mcp_server.stdio_server
   ```

2. **Alternative with full path:**
   ```bash
   npx @modelcontextprotocol/inspector \
     /path/to/your/.venv/bin/python \
     /path/to/your/project/mcp_server/stdio_server.py
   ```

3. **With environment variables:**
   ```bash
   CONTEXT7_API_KEY="your-key" \
   PYTHONPATH="." \
   npx @modelcontextprotocol/inspector \
     python -m mcp_server.stdio_server
   ```

### HTTP Server Configuration

1. **Start the HTTP server:**
   ```bash
   python -m mcp_server.http_server --port 8001
   ```

2. **Open MCP Inspector separately:**
   ```bash
   npx @modelcontextprotocol/inspector
   ```

3. **Configure HTTP connection in Inspector:**
   - Server Type: HTTP
   - URL: `http://localhost:8001/jsonrpc`
   - Method: POST

## Available Tools for Testing

### Core Tools (Always Available)

1. **echo**
   - Description: Echo back a message
   - Parameters:
     ```json
     {
       "message": "Hello, World!"
     }
     ```
   - Expected Response: Returns the same message

2. **get_weather**
   - Description: Get weather information for a city
   - Parameters:
     ```json
     {
       "city": "London"
     }
     ```
   - Expected Response: Weather data for the specified city

### Context7 Tools (Requires API Key)

3. **search_libraries**
   - Description: Search for programming libraries
   - Parameters:
     ```json
     {
       "query": "web framework",
       "limit": 5
     }
     ```

4. **get_documentation**
   - Description: Get documentation for a library
   - Parameters:
     ```json
     {
       "library": "fastapi",
       "version": "latest"
     }
     ```

5. **get_examples**
   - Description: Get code examples for a library
   - Parameters:
     ```json
     {
       "library": "fastapi",
       "topic": "routing"
     }
     ```

## Testing Scenarios

### Basic Functionality Tests

1. **Tool Listing**
   - Verify all expected tools are listed
   - Check tool descriptions and schemas
   - Confirm parameter requirements

2. **Successful Tool Execution**
   - Test each tool with valid parameters
   - Verify response format and content
   - Check execution time and performance

3. **Error Handling**
   - Test with invalid tool names
   - Test with missing required parameters
   - Test with invalid parameter types
   - Verify error messages are helpful

### Advanced Testing

1. **Concurrent Requests**
   - Execute multiple tools simultaneously
   - Verify server handles concurrent requests

2. **Large Payloads**
   - Test with large input parameters
   - Verify response handling for large outputs

3. **Network Conditions**
   - Test HTTP server with network delays
   - Verify timeout handling

## Troubleshooting

### Common Issues

1. **Inspector Won't Start**
   ```bash
   # Check Node.js installation
   node --version
   
   # Try installing Inspector globally
   npm install -g @modelcontextprotocol/inspector
   
   # Or use npx directly
   npx @modelcontextprotocol/inspector --help
   ```

2. **Server Connection Failed**
   ```bash
   # Verify server is running
   python scripts/verify_inspector_integration.py --stdio-only
   
   # Check for port conflicts (HTTP server)
   lsof -i :8001
   
   # Verify environment variables
   echo $PYTHONPATH
   echo $CONTEXT7_API_KEY
   ```

3. **Tools Not Listed**
   ```bash
   # Check server logs for errors
   python -m mcp_server.stdio_server --log-level DEBUG
   
   # Verify tool registration
   python scripts/test_with_inspector.py test
   ```

4. **Context7 Tools Missing**
   ```bash
   # Verify API key is set
   echo $CONTEXT7_API_KEY
   
   # Test Context7 connection
   python -c "
   import os
   from mcp_server.tools.context7 import Context7Client
   client = Context7Client(os.getenv('CONTEXT7_API_KEY'))
   print('Context7 client created successfully')
   "
   ```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Stdio server with debug logging
python -m mcp_server.stdio_server --log-level DEBUG

# HTTP server with debug logging  
python -m mcp_server.http_server --log-level DEBUG --port 8001

# Verification with debug logging
python scripts/verify_inspector_integration.py --log-level DEBUG
```

## Integration with Development Workflow

### VSCode Integration

After verifying Inspector functionality, you can configure VSCode:

1. **Update mcp.json configuration:**
   ```json
   {
     "mcpServers": {
       "mcp-dev-workflow-stdio": {
         "command": "python",
         "args": ["-m", "mcp_server.stdio_server"],
         "cwd": ".",
         "env": {
           "PYTHONPATH": ".",
           "CONTEXT7_API_KEY": "${env:CONTEXT7_API_KEY}"
         },
         "disabled": false
       }
     }
   }
   ```

2. **Test configuration:**
   ```bash
   python scripts/test_mcp_config.py
   ```

### Automated Testing

Include Inspector verification in your CI/CD pipeline:

```bash
# Add to your test script
python scripts/verify_inspector_integration.py
```

## Best Practices

### Development Workflow

1. **Start with Basic Tests**
   - Always run `verify_inspector_integration.py` first
   - Fix any basic functionality issues before using Inspector

2. **Use Inspector for Interactive Testing**
   - Test new tools as you develop them
   - Verify parameter validation works correctly
   - Check error messages are user-friendly

3. **Document Tool Behavior**
   - Use Inspector to understand tool responses
   - Document expected inputs and outputs
   - Create test cases based on Inspector findings

### Performance Considerations

1. **Monitor Response Times**
   - Use Inspector to identify slow tools
   - Optimize tools that take too long to execute

2. **Test Resource Usage**
   - Monitor server memory usage during testing
   - Verify servers handle multiple concurrent requests

3. **Validate Error Handling**
   - Test all error conditions through Inspector
   - Ensure servers remain stable after errors

## Advanced Configuration

### Custom Inspector Setup

Create custom configuration files for different environments:

```bash
# Generate Inspector configuration
python scripts/setup_mcp_inspector.py --config-only --output-config inspector-dev.json

# Use custom configuration
npx @modelcontextprotocol/inspector --config inspector-dev.json
```

### Multiple Server Testing

Test multiple servers simultaneously:

```bash
# Terminal 1: Start HTTP server
python -m mcp_server.http_server --port 8001

# Terminal 2: Start another HTTP server
python -m mcp_server.http_server --port 8002

# Terminal 3: Use Inspector to test both
npx @modelcontextprotocol/inspector
# Configure multiple HTTP connections in Inspector UI
```

## Support and Resources

### Documentation Links

- [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

### Getting Help

1. **Check Server Logs**
   - Enable debug logging for detailed information
   - Look for error messages and stack traces

2. **Verify Configuration**
   - Use provided verification scripts
   - Check environment variables and paths

3. **Test Incrementally**
   - Start with basic functionality tests
   - Add complexity gradually

4. **Community Resources**
   - MCP community forums and discussions
   - GitHub issues for specific problems

---

This guide should help you effectively use MCP Inspector to test and debug your MCP servers. For additional help, refer to the troubleshooting section or run the verification scripts provided in this project.