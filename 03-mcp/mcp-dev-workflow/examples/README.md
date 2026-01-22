# MCP Development Workflow Examples

This directory contains practical examples and demonstrations of MCP (Model Context Protocol) usage in real development workflows.

## Overview

The examples in this directory demonstrate:

1. **Documentation-Driven Development**: Using Context7 integration for live documentation access
2. **Multi-Server Coordination**: Coordinating requests across multiple MCP servers
3. **Error Handling & Recovery**: Robust error handling strategies for production use
4. **Real-World Scenarios**: Practical development tasks using MCP tools

## Examples

### 1. FastAPI Development Workflow (`fastapi_development_example.py`)

Demonstrates a complete development workflow for building a FastAPI application:

- **Scenario**: Developer building a REST API with authentication
- **MCP Tools Used**: Context7 documentation, library search, code examples
- **Workflow Steps**:
  1. Search for authentication libraries
  2. Retrieve FastAPI documentation
  3. Get middleware code examples
  4. Coordinate between multiple servers

**Usage**:
```bash
# Set Context7 API key (optional - will use mock data if not set)
export CONTEXT7_API_KEY="your-api-key"

# Run the example
python examples/fastapi_development_example.py
```

### 2. Multi-Server Load Balancing (`multi_server_example.py`)

Shows how to coordinate requests across multiple MCP servers:

- **Servers**: stdio and HTTP servers running simultaneously
- **Load Balancing**: Round-robin request distribution
- **Failover**: Automatic failover to backup servers
- **Monitoring**: Request tracking and performance metrics

**Usage**:
```bash
python examples/multi_server_example.py
```

### 3. Error Handling Patterns (`error_handling_example.py`)

Demonstrates robust error handling strategies:

- **Retry Logic**: Exponential backoff for failed requests
- **Fallback Strategies**: Alternative approaches when primary tools fail
- **Graceful Degradation**: Maintaining functionality during partial failures
- **Error Recovery**: Automatic recovery from transient errors

**Usage**:
```bash
python examples/error_handling_example.py
```

### 4. Documentation Integration (`documentation_workflow_example.py`)

Shows practical documentation integration during development:

- **Live Documentation**: Real-time access to library documentation
- **Code Examples**: Contextual code examples for specific features
- **Library Discovery**: Finding relevant libraries for development tasks
- **Version Management**: Working with specific library versions

**Usage**:
```bash
# Requires Context7 API key for full functionality
export CONTEXT7_API_KEY="your-api-key"
python examples/documentation_workflow_example.py
```

## Configuration

### Environment Variables

- `CONTEXT7_API_KEY`: API key for Context7 integration (optional)
- `MCP_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `MCP_SERVER_PORT`: Port for HTTP server (default: 8000)

### MCP Server Configuration

The examples use the following MCP server configuration:

```json
{
  "mcpServers": {
    "mcp-dev-workflow": {
      "command": "python",
      "args": ["-m", "mcp_server.stdio_server"],
      "env": {
        "CONTEXT7_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Development Scenarios

### Scenario 1: Building a New Feature

1. **Research Phase**: Use Context7 to search for relevant libraries
2. **Documentation Phase**: Retrieve current documentation for chosen libraries
3. **Implementation Phase**: Get code examples and best practices
4. **Testing Phase**: Use multiple servers to validate implementation

### Scenario 2: Debugging Issues

1. **Problem Identification**: Use documentation tools to understand error messages
2. **Solution Research**: Search for similar issues and solutions
3. **Code Analysis**: Get examples of correct implementations
4. **Validation**: Test fixes across multiple server configurations

### Scenario 3: Code Review Assistance

1. **Documentation Verification**: Ensure code follows current best practices
2. **Library Updates**: Check for newer versions and breaking changes
3. **Example Validation**: Verify code patterns against official examples
4. **Security Review**: Check for security best practices

## Best Practices

### 1. Error Handling

```python
async def robust_tool_call(server, tool_name, arguments, max_retries=3):
    """Example of robust tool calling with retry logic."""
    for attempt in range(max_retries):
        try:
            result = await server.tools_manager.execute_tool(tool_name, arguments)
            if not result.is_error:
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    raise Exception(f"Tool {tool_name} failed after {max_retries} attempts")
```

### 2. Multi-Server Coordination

```python
async def coordinate_servers(servers, tool_name, arguments):
    """Example of coordinating requests across multiple servers."""
    results = []
    
    for server_name, server in servers.items():
        if tool_name in server.tools_manager.tools:
            try:
                result = await server.tools_manager.execute_tool(tool_name, arguments)
                results.append({
                    "server": server_name,
                    "result": result,
                    "success": not result.is_error
                })
            except Exception as e:
                results.append({
                    "server": server_name,
                    "error": str(e),
                    "success": False
                })
    
    return results
```

### 3. Fallback Strategies

```python
async def documentation_with_fallback(server, library):
    """Example of documentation retrieval with fallback."""
    # Primary: Try Context7 documentation
    if "context7_get_documentation" in server.tools_manager.tools:
        try:
            result = await server.tools_manager.execute_tool(
                "context7_get_documentation",
                {"library": library}
            )
            if not result.is_error:
                return result
        except Exception:
            pass
    
    # Fallback: Provide basic help message
    return await server.tools_manager.execute_tool(
        "echo",
        {"message": f"Documentation for {library} not available. Please check the library name."}
    )
```

## Integration with Development Tools

### VSCode Integration

Add to your VSCode `mcp.json`:

```json
{
  "mcpServers": {
    "mcp-dev-workflow": {
      "command": "python",
      "args": ["/path/to/mcp_server/stdio_server.py"],
      "env": {
        "CONTEXT7_API_KEY": "your-api-key"
      }
    }
  }
}
```

### MCP Inspector Integration

Test your servers with MCP Inspector:

```bash
# Test stdio server
npx @modelcontextprotocol/inspector python mcp_server/stdio_server.py

# Test HTTP server (start server first)
python mcp_server/http_server.py --port 8001
# Then connect MCP Inspector to http://localhost:8001
```

## Troubleshooting

### Common Issues

1. **Context7 API Key Issues**
   - Ensure API key is set in environment variables
   - Check API key validity at context7.com
   - Examples will use mock data if API key is not available

2. **Port Conflicts**
   - HTTP server will suggest alternative ports if default is in use
   - Use `--port` flag to specify custom port

3. **Tool Not Found Errors**
   - Verify tool registration in server setup
   - Check tool names match exactly (case-sensitive)

4. **Import Errors**
   - Ensure virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`

### Debug Mode

Enable debug logging for detailed information:

```bash
export MCP_LOG_LEVEL=DEBUG
python examples/fastapi_development_example.py
```

## Contributing

To add new examples:

1. Create a new Python file in the `examples/` directory
2. Follow the existing pattern for error handling and logging
3. Include comprehensive docstrings and comments
4. Add usage instructions to this README
5. Test with both Context7 API key and mock data scenarios

## Related Documentation

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Context7 API Documentation](https://context7.com/docs)
- [VSCode MCP Integration](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [MCP Inspector Guide](../docs/MCP_INSPECTOR_GUIDE.md)