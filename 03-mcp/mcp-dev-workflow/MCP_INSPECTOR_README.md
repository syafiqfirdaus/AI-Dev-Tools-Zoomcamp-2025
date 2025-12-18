# MCP Inspector Integration

This directory contains scripts and documentation for integrating MCP servers with MCP Inspector for visual testing and debugging.

## Quick Start

### 1. Verify Your Setup

```bash
# Test basic server functionality
python scripts/test_with_inspector.py test

# Run comprehensive verification
python scripts/verify_inspector_integration.py
```

### 2. Test with MCP Inspector

```bash
# Test stdio server (easiest)
python scripts/test_with_inspector.py stdio

# Test HTTP server
python scripts/test_with_inspector.py http

# Test both servers
python scripts/test_with_inspector.py both
```

## Available Scripts

### Core Testing Scripts

- **`scripts/test_with_inspector.py`** - Simple testing interface
  - `test` - Basic functionality verification
  - `stdio` - Launch MCP Inspector with stdio server
  - `http` - Start HTTP server for Inspector testing
  - `both` - Test both server types

- **`scripts/verify_inspector_integration.py`** - Comprehensive verification
  - Tests server startup, tool listing, execution, and error handling
  - Supports both stdio and HTTP servers
  - Generates detailed verification reports

- **`scripts/setup_mcp_inspector.py`** - Advanced setup and configuration
  - Interactive setup wizard
  - Configuration file generation
  - Multiple server testing

### Configuration Scripts

- **`scripts/test_mcp_config.py`** - Test MCP configuration files
- **`scripts/verify_setup.py`** - Verify project setup

## Available Tools for Testing

### Core Tools (Always Available)

1. **echo** - Echo back messages
   ```json
   {"message": "Hello, World!"}
   ```

2. **get_weather** - Get weather information
   ```json
   {"city": "London"}
   ```

### Context7 Tools (Requires API Key)

Set `CONTEXT7_API_KEY` environment variable to enable:

3. **search_libraries** - Search programming libraries
4. **get_documentation** - Get library documentation  
5. **get_examples** - Get code examples

## Prerequisites

### Required

- **Python 3.12+** with virtual environment activated
- **Node.js** (for MCP Inspector)

### Install MCP Inspector

```bash
# Via npm (recommended)
npm install -g @modelcontextprotocol/inspector

# Via npx (no installation)
npx @modelcontextprotocol/inspector --help

# Via Homebrew (macOS/Linux)
brew install mcp-inspector
```

## Usage Examples

### Manual MCP Inspector Usage

```bash
# Stdio server
npx @modelcontextprotocol/inspector python -m mcp_server.stdio_server

# HTTP server (start server first)
python -m mcp_server.http_server --port 8001
# Then configure Inspector with: http://localhost:8001/jsonrpc
```

### Environment Variables

```bash
# Optional: Enable Context7 tools
export CONTEXT7_API_KEY="your-api-key"

# Required for proper module loading
export PYTHONPATH="."
```

## Troubleshooting

### Common Issues

1. **Node.js not found**
   ```bash
   # Install Node.js from https://nodejs.org/
   node --version
   ```

2. **MCP Inspector not available**
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

3. **Server connection failed**
   ```bash
   # Verify server works
   python scripts/test_with_inspector.py test
   ```

4. **Context7 tools missing**
   ```bash
   # Set API key
   export CONTEXT7_API_KEY="your-key"
   ```

### Debug Mode

```bash
# Enable debug logging
python scripts/verify_inspector_integration.py --log-level DEBUG
python -m mcp_server.stdio_server --log-level DEBUG
```

## Integration with Development

### VSCode Configuration

After verifying Inspector functionality:

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
      }
    }
  }
}
```

### Automated Testing

```bash
# Add to CI/CD pipeline
python scripts/verify_inspector_integration.py
```

## Documentation

- **`docs/MCP_INSPECTOR_GUIDE.md`** - Comprehensive usage guide
- **`docs/VSCODE_SETUP.md`** - VSCode integration guide

## Support

1. Run verification scripts to identify issues
2. Check server logs with debug logging enabled
3. Refer to the comprehensive guide in `docs/MCP_INSPECTOR_GUIDE.md`

---

**Next Steps**: After successful verification, you can use MCP Inspector to visually test your tools and integrate the servers with VSCode or other MCP clients.