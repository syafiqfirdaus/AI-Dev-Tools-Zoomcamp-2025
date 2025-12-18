# VSCode MCP Integration

This directory contains the VSCode MCP (Model Context Protocol) integration for the MCP Development Workflow system.

## Quick Start

1. **Install Dependencies**
   ```bash
   cd 03-mcp
   pip install -e .
   ```

2. **Set up VSCode Configuration**
   ```bash
   python scripts/setup_vscode.py
   ```

3. **Install VSCode MCP Extension**
   - Open VSCode
   - Install the MCP extension from the marketplace
   - Restart VSCode

4. **Test the Setup**
   ```bash
   python scripts/test_mcp_config.py
   ```

## Files and Structure

```
03-mcp/
├── mcp.json                    # VSCode MCP configuration
├── config/
│   └── mcp_config.py          # Configuration management and validation
├── scripts/
│   ├── setup_vscode.py        # Automated VSCode setup script
│   └── test_mcp_config.py     # Configuration testing script
├── docs/
│   └── VSCODE_SETUP.md        # Detailed setup documentation
└── mcp_server/                # MCP server implementation
    ├── stdio_server.py        # stdio MCP server
    ├── http_server.py         # HTTP MCP server
    └── ...
```

## Configuration

The `mcp.json` file defines the MCP servers available to VSCode:

- **mcp-dev-workflow-stdio**: Main stdio server (enabled by default)
- **mcp-dev-workflow-http**: HTTP server (disabled by default)

### Available Tools

- `echo` - Simple echo tool for testing
- `get_weather` - Weather information retrieval
- `context7_search_libraries` - Search for libraries (requires API key)
- `context7_get_documentation` - Get library documentation (requires API key)
- `context7_get_examples` - Get code examples (requires API key)

## Environment Variables

- `CONTEXT7_API_KEY` - API key for Context7 integration (optional)

Set this in your shell profile or VSCode settings:
```bash
export CONTEXT7_API_KEY="your_api_key_here"
```

## Scripts

### setup_vscode.py

Automatically configures VSCode with MCP settings:

```bash
# Basic setup
python scripts/setup_vscode.py

# Custom configuration file
python scripts/setup_vscode.py --config custom.json

# Dry run (show what would be done)
python scripts/setup_vscode.py --dry-run

# Don't merge with existing config
python scripts/setup_vscode.py --no-merge
```

### test_mcp_config.py

Tests MCP configuration and server connectivity:

```bash
# Test default configuration
python scripts/test_mcp_config.py

# Test with custom timeout
python scripts/test_mcp_config.py --timeout 30

# Test custom configuration
python scripts/test_mcp_config.py --config custom.json
```

### mcp_config.py

Validates MCP configuration files:

```bash
# Validate configuration
python config/mcp_config.py mcp.json

# Validate with custom base path
python config/mcp_config.py --base-path /project mcp.json
```

## Troubleshooting

### Common Issues

1. **Server not starting**
   - Check Python is in PATH
   - Verify working directory exists
   - Check dependencies are installed

2. **Tools not available**
   - Restart VSCode after configuration changes
   - Check server is not disabled
   - Verify MCP extension is installed

3. **Context7 tools missing**
   - Set CONTEXT7_API_KEY environment variable
   - Restart VSCode after setting the variable

### Debug Mode

Enable debug logging by modifying the server args in `mcp.json`:

```json
{
  "args": ["-m", "mcp_server.stdio_server", "--log-level", "DEBUG"]
}
```

### Validation

Always validate your configuration after changes:

```bash
python config/mcp_config.py mcp.json
```

## Security

- Only auto-approve safe tools (echo, get_weather)
- Don't hardcode API keys in configuration
- Use environment variables for sensitive data
- Review tool permissions before enabling auto-approval

## Support

For detailed setup instructions, see [docs/VSCODE_SETUP.md](docs/VSCODE_SETUP.md).

For issues:
1. Check configuration with validation script
2. Review VSCode Developer Console
3. Check server logs for errors
4. Verify all dependencies are installed