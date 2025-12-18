# VSCode MCP Integration Setup Guide

This guide explains how to set up and configure MCP (Model Context Protocol) servers for use with VSCode, enabling AI-powered development capabilities through the MCP extension.

## Overview

The MCP Development Workflow system provides two MCP servers that can be integrated with VSCode:

1. **stdio server** - Communicates via standard input/output (recommended for VSCode)
2. **HTTP server** - Communicates via HTTP requests (useful for web-based integrations)

## Prerequisites

- Python 3.12 or higher
- VSCode with MCP extension installed
- MCP Development Workflow system installed and configured

## Quick Setup

### 1. Automatic Setup (Recommended)

Use the provided setup script to automatically configure VSCode:

```bash
cd 03-mcp
python scripts/setup_vscode.py
```

This will:
- Detect your VSCode configuration directory
- Copy the MCP configuration to the correct location
- Merge with any existing MCP configuration
- Provide setup instructions

### 2. Manual Setup

If you prefer manual setup or need custom configuration:

1. **Locate VSCode Configuration Directory**

   The VSCode user configuration directory varies by platform:
   
   - **Windows**: `%APPDATA%\Code\User\`
   - **macOS**: `~/Library/Application Support/Code/User/`
   - **Linux**: `~/.config/Code/User/`

2. **Copy MCP Configuration**

   Copy the `mcp.json` file to your VSCode configuration directory:
   
   ```bash
   # Example for Linux
   cp 03-mcp/mcp.json ~/.config/Code/User/mcp.json
   ```

3. **Restart VSCode**

   Restart VSCode to load the new MCP configuration.

## Configuration Details

### MCP Configuration File (`mcp.json`)

The configuration file defines the MCP servers available to VSCode:

```json
{
  "mcpServers": {
    "mcp-dev-workflow-stdio": {
      "command": "python",
      "args": ["-m", "mcp_server.stdio_server"],
      "cwd": "03-mcp",
      "env": {
        "PYTHONPATH": "03-mcp",
        "CONTEXT7_API_KEY": "${env:CONTEXT7_API_KEY}"
      },
      "disabled": false,
      "autoApprove": [
        "echo",
        "get_weather"
      ]
    }
  }
}
```

### Configuration Parameters

- **`command`**: The command to execute the MCP server
- **`args`**: Command-line arguments for the server
- **`cwd`**: Working directory for the server process
- **`env`**: Environment variables for the server
- **`disabled`**: Whether the server is disabled (true/false)
- **`autoApprove`**: List of tools that don't require user approval

### Environment Variables

- **`CONTEXT7_API_KEY`**: API key for Context7 integration (optional)
- **`PYTHONPATH`**: Python module search path

## Available Tools

The MCP servers provide the following tools:

### Core Tools

1. **`echo`** - Simple echo tool for testing
   - Parameters: `message` (string)
   - Returns: The input message

2. **`get_weather`** - Weather information tool
   - Parameters: `city` (string), `units` (optional)
   - Returns: Weather data for the specified city

### Context7 Tools (requires API key)

3. **`context7_search`** - Search for libraries and documentation
   - Parameters: `query` (string)
   - Returns: Search results with library information

4. **`context7_documentation`** - Get documentation for a library
   - Parameters: `library` (string), `version` (optional)
   - Returns: Documentation content

5. **`context7_examples`** - Get code examples for a library
   - Parameters: `library` (string), `topic` (string)
   - Returns: Code examples

## Validation and Troubleshooting

### Validate Configuration

Use the validation script to check your configuration:

```bash
cd 03-mcp
python config/mcp_config.py mcp.json
```

This will check:
- JSON syntax and structure
- Required fields and data types
- File paths and command availability
- Environment variable references

### Common Issues and Solutions

#### 1. Server Not Starting

**Problem**: MCP server fails to start in VSCode

**Solutions**:
- Check that Python is in your PATH
- Verify the working directory (`cwd`) exists
- Ensure all dependencies are installed
- Check VSCode Developer Console for error messages

#### 2. Tools Not Available

**Problem**: MCP tools don't appear in VSCode

**Solutions**:
- Restart VSCode after configuration changes
- Check that the server is not disabled
- Verify the MCP extension is installed and enabled
- Check server logs for initialization errors

#### 3. Context7 Tools Missing

**Problem**: Context7 tools are not available

**Solutions**:
- Set the `CONTEXT7_API_KEY` environment variable
- Restart VSCode after setting the environment variable
- Verify the API key is valid
- Check server logs for authentication errors

#### 4. Permission Errors

**Problem**: Permission denied when accessing files

**Solutions**:
- Ensure the MCP server scripts are executable
- Check file permissions in the working directory
- Run VSCode with appropriate permissions

### Debug Mode

Enable debug logging by modifying the server configuration:

```json
{
  "mcpServers": {
    "mcp-dev-workflow-stdio": {
      "command": "python",
      "args": ["-m", "mcp_server.stdio_server", "--log-level", "DEBUG"],
      // ... other configuration
    }
  }
}
```

## Advanced Configuration

### Custom Server Configuration

You can customize the server configuration for your needs:

```json
{
  "mcpServers": {
    "my-custom-server": {
      "command": "python",
      "args": [
        "-m", "mcp_server.stdio_server",
        "--server-name", "my-custom-server",
        "--log-level", "INFO"
      ],
      "cwd": "/path/to/project",
      "env": {
        "PYTHONPATH": "/path/to/project",
        "CUSTOM_CONFIG": "value"
      },
      "disabled": false,
      "autoApprove": ["safe_tool1", "safe_tool2"]
    }
  }
}
```

### Multiple Server Configurations

You can configure multiple MCP servers:

```json
{
  "mcpServers": {
    "development-server": {
      "command": "python",
      "args": ["-m", "mcp_server.stdio_server"],
      "cwd": "03-mcp",
      "disabled": false
    },
    "production-server": {
      "command": "python",
      "args": ["-m", "mcp_server.stdio_server", "--server-name", "prod"],
      "cwd": "03-mcp",
      "disabled": true
    }
  }
}
```

### Environment-Specific Configuration

Use environment variables for flexible configuration:

```json
{
  "mcpServers": {
    "mcp-dev-workflow": {
      "command": "${env:MCP_PYTHON_PATH}",
      "args": ["-m", "mcp_server.stdio_server"],
      "cwd": "${env:MCP_PROJECT_PATH}",
      "env": {
        "LOG_LEVEL": "${env:MCP_LOG_LEVEL}",
        "CONTEXT7_API_KEY": "${env:CONTEXT7_API_KEY}"
      }
    }
  }
}
```

## Testing the Setup

### 1. Verify Server Connection

1. Open VSCode
2. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. Run "MCP: List Servers"
4. Verify your servers appear in the list

### 2. Test Tool Execution

1. Open Command Palette
2. Run "MCP: Execute Tool"
3. Select a server and tool
4. Provide required parameters
5. Verify the tool executes successfully

### 3. Use in AI Features

1. Open a code file
2. Use VSCode's AI features (Copilot, etc.)
3. The MCP tools should be available for AI assistance
4. Check the MCP panel for tool execution logs

## Security Considerations

### Auto-Approval

The `autoApprove` setting allows certain tools to run without user confirmation. Only include tools you trust:

```json
{
  "autoApprove": [
    "echo",           // Safe: just echoes input
    "get_weather"     // Safe: read-only weather data
  ]
}
```

**Do not auto-approve tools that**:
- Modify files or system state
- Access sensitive information
- Make network requests to untrusted endpoints
- Execute arbitrary code

### Environment Variables

Be careful with environment variables in the configuration:
- Don't hardcode sensitive values like API keys
- Use `${env:VARIABLE_NAME}` syntax for dynamic values
- Ensure environment variables are set before starting VSCode

### File Permissions

Ensure proper file permissions:
- MCP configuration files should be readable by your user
- Server scripts should be executable
- Working directories should be accessible

## Maintenance

### Updating Configuration

When updating the MCP configuration:

1. Modify the `mcp.json` file
2. Validate the configuration: `python config/mcp_config.py mcp.json`
3. Copy to VSCode configuration directory
4. Restart VSCode

### Backup Configuration

Always backup your MCP configuration before making changes:

```bash
cp ~/.config/Code/User/mcp.json ~/.config/Code/User/mcp.json.backup
```

The setup script automatically creates backups when merging configurations.

### Monitoring

Monitor MCP server health:
- Check VSCode Developer Console for errors
- Review server logs for issues
- Use the MCP panel to monitor tool execution
- Validate configuration periodically

## Support

If you encounter issues:

1. Check this documentation for common solutions
2. Validate your configuration with the provided tools
3. Review VSCode Developer Console for error messages
4. Check server logs for detailed error information
5. Ensure all dependencies are properly installed

For additional help, refer to:
- VSCode MCP extension documentation
- MCP protocol specification
- Project README and documentation files