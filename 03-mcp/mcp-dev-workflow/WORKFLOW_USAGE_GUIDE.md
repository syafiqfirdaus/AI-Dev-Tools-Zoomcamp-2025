# MCP Development Workflow Usage Guide

This guide provides comprehensive instructions for using the MCP Development Workflow system in real-world development scenarios.

## Quick Start

### 1. Environment Setup

```bash
# Navigate to the MCP project directory
cd 03-mcp

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Set Context7 API key (optional - examples work with mock data)
export CONTEXT7_API_KEY="your-api-key-here"
```

### 2. Run Basic Workflow Demo

```bash
# Run the complete workflow demonstration
python workflow_demo.py
```

This will:
- Set up multiple MCP servers
- Demonstrate documentation workflow using Context7
- Show multi-server coordination
- Test error handling and recovery
- Generate a comprehensive report

### 3. Run Specific Examples

```bash
# FastAPI development workflow
python examples/fastapi_development_example.py

# Multi-server coordination
python examples/multi_server_coordination_example.py
```

## Development Scenarios

### Scenario 1: Building a New Feature

**Use Case**: You're implementing a new authentication system for your FastAPI application.

**Workflow**:

1. **Research Phase**
   ```bash
   python examples/fastapi_development_example.py
   ```
   - Searches for relevant authentication libraries
   - Discovers FastAPI-Users, python-jose, passlib
   - Gets current documentation for each library

2. **Implementation Phase**
   - Use retrieved code examples as starting points
   - Follow best practices from documentation
   - Implement with confidence using up-to-date information

3. **Validation Phase**
   - Cross-reference implementation with latest docs
   - Verify security best practices
   - Test with multiple server configurations

**Expected Output**:
- List of recommended libraries with descriptions
- Current documentation for FastAPI security features
- Code examples for middleware implementation
- Implementation plan with specific steps

### Scenario 2: Debugging and Troubleshooting

**Use Case**: You're encountering issues with your current implementation and need to debug.

**Workflow**:

1. **Problem Analysis**
   ```python
   # Use Context7 to get current documentation
   await server.tools_manager.execute_tool(
       "context7_get_documentation",
       {"library": "fastapi", "version": "latest"}
   )
   ```

2. **Solution Research**
   ```python
   # Search for specific error patterns
   await server.tools_manager.execute_tool(
       "context7_search_libraries",
       {"query": "fastapi authentication error", "limit": 10}
   )
   ```

3. **Code Comparison**
   ```python
   # Get working examples
   await server.tools_manager.execute_tool(
       "context7_get_examples",
       {"library": "fastapi", "topic": "middleware", "limit": 5}
   )
   ```

### Scenario 3: Code Review and Best Practices

**Use Case**: Reviewing code for compliance with current best practices.

**Workflow**:

1. **Documentation Verification**
   - Check if code follows current library recommendations
   - Verify against latest security guidelines
   - Ensure compatibility with current versions

2. **Pattern Validation**
   - Compare implementation patterns with official examples
   - Check for deprecated methods or approaches
   - Validate error handling strategies

3. **Performance Review**
   - Use multi-server coordination to test under load
   - Validate failover and recovery mechanisms
   - Check response times and success rates

## Advanced Usage Patterns

### 1. Multi-Server Load Balancing

```python
from examples.multi_server_coordination_example import MultiServerCoordinator

coordinator = MultiServerCoordinator()
await coordinator.setup_servers()

# Round-robin load balancing
result = await coordinator.round_robin_request(
    "context7_search_libraries",
    {"query": "fastapi", "limit": 5}
)

# Weighted load balancing (based on performance)
result = await coordinator.weighted_request(
    "context7_get_documentation",
    {"library": "fastapi"}
)

# Automatic failover
result = await coordinator.failover_request(
    "get_weather",
    {"city": "London"},
    max_attempts=3
)
```

### 2. Request Aggregation

```python
# Process multiple requests simultaneously
weather_cities = ["London", "New York", "Tokyo"]
arguments_list = [{"city": city} for city in weather_cities]

result = await coordinator.aggregate_request(
    "get_weather",
    arguments_list
)

# Result contains data from all cities processed in parallel
```

### 3. Error Handling and Recovery

```python
async def robust_documentation_lookup(library_name):
    """Example of robust documentation lookup with fallbacks."""
    
    # Primary: Try Context7 documentation
    try:
        result = await server.tools_manager.execute_tool(
            "context7_get_documentation",
            {"library": library_name}
        )
        if not result.is_error:
            return result
    except Exception as e:
        logger.warning(f"Context7 failed: {e}")
    
    # Fallback 1: Try library search
    try:
        result = await server.tools_manager.execute_tool(
            "context7_search_libraries",
            {"query": library_name, "limit": 1}
        )
        if not result.is_error:
            return result
    except Exception as e:
        logger.warning(f"Library search failed: {e}")
    
    # Fallback 2: Provide basic help
    return await server.tools_manager.execute_tool(
        "echo",
        {"message": f"Documentation for {library_name} not available. Please check the library name."}
    )
```

## Integration with Development Tools

### VSCode Integration

1. **Setup MCP Configuration**
   
   Create or update `.vscode/mcp.json`:
   ```json
   {
     "mcpServers": {
       "mcp-dev-workflow": {
         "command": "python",
         "args": ["/path/to/03-mcp/mcp_server/stdio_server.py"],
         "env": {
           "CONTEXT7_API_KEY": "your-api-key"
         }
       }
     }
   }
   ```

2. **Use in VSCode**
   - Install MCP extension for VSCode
   - Access MCP tools through Copilot chat
   - Use Context7 tools for live documentation

### MCP Inspector Integration

1. **Test stdio Server**
   ```bash
   npx @modelcontextprotocol/inspector python mcp_server/stdio_server.py
   ```

2. **Test HTTP Server**
   ```bash
   # Start HTTP server
   python mcp_server/http_server.py --port 8000
   
   # Connect MCP Inspector to http://localhost:8000
   ```

3. **Interactive Testing**
   - Use web interface to test tools
   - Validate request/response formats
   - Debug tool execution issues

## Configuration Options

### Environment Variables

```bash
# Context7 API key for live documentation
export CONTEXT7_API_KEY="your-api-key"

# Logging level
export MCP_LOG_LEVEL="DEBUG"  # DEBUG, INFO, WARNING, ERROR

# HTTP server configuration
export MCP_SERVER_HOST="127.0.0.1"
export MCP_SERVER_PORT="8000"
```

### Server Configuration

```python
# Custom server setup
transport = StdioTransport()
server = MCPServer(transport, "custom-server")

# Register only specific tools
server.register_tool(EchoTool())
server.register_tool(WeatherTool())

# Conditional Context7 registration
if os.getenv("CONTEXT7_API_KEY"):
    context7_client = Context7Client(os.getenv("CONTEXT7_API_KEY"))
    server.register_tool(Context7SearchTool(context7_client))
```

## Performance Optimization

### 1. Connection Pooling

```python
# Reuse Context7 client across requests
class OptimizedWorkflow:
    def __init__(self):
        self.context7_client = None
    
    async def setup(self):
        if os.getenv("CONTEXT7_API_KEY"):
            self.context7_client = Context7Client(os.getenv("CONTEXT7_API_KEY"))
    
    async def cleanup(self):
        if self.context7_client:
            await self.context7_client.close()
```

### 2. Request Batching

```python
# Batch multiple documentation requests
async def batch_documentation_lookup(libraries):
    """Efficiently lookup documentation for multiple libraries."""
    
    tasks = []
    for library in libraries:
        task = server.tools_manager.execute_tool(
            "context7_get_documentation",
            {"library": library}
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 3. Caching Strategies

```python
from functools import lru_cache
import asyncio

class CachedDocumentationClient:
    def __init__(self):
        self._cache = {}
    
    async def get_documentation(self, library, version="latest"):
        cache_key = f"{library}:{version}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = await self.context7_client.get_documentation(library, version)
        self._cache[cache_key] = result
        return result
```

## Monitoring and Metrics

### 1. Performance Tracking

```python
# Track request performance
class PerformanceTracker:
    def __init__(self):
        self.metrics = {}
    
    async def track_request(self, tool_name, arguments):
        start_time = time.time()
        
        try:
            result = await server.tools_manager.execute_tool(tool_name, arguments)
            success = not result.is_error
        except Exception as e:
            success = False
            result = {"error": str(e)}
        
        duration = time.time() - start_time
        
        # Record metrics
        if tool_name not in self.metrics:
            self.metrics[tool_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_time": 0.0
            }
        
        self.metrics[tool_name]["total_requests"] += 1
        self.metrics[tool_name]["total_time"] += duration
        
        if success:
            self.metrics[tool_name]["successful_requests"] += 1
        
        return result
```

### 2. Health Monitoring

```python
async def health_check_workflow():
    """Comprehensive health check for MCP workflow."""
    
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "servers": {},
        "tools": {},
        "external_services": {}
    }
    
    # Check server health
    for server_name, server in servers.items():
        try:
            result = await server.tools_manager.execute_tool("echo", {"message": "health_check"})
            health_status["servers"][server_name] = {
                "status": "healthy" if not result.is_error else "unhealthy",
                "response_time": "< 100ms"  # Measure actual time
            }
        except Exception as e:
            health_status["servers"][server_name] = {
                "status": "unavailable",
                "error": str(e)
            }
    
    # Check Context7 service
    if context7_client:
        try:
            result = await context7_client.search_libraries("test", limit=1)
            health_status["external_services"]["context7"] = {
                "status": "available",
                "api_key_valid": True
            }
        except Exception as e:
            health_status["external_services"]["context7"] = {
                "status": "unavailable",
                "error": str(e)
            }
    
    return health_status
```

## Troubleshooting

### Common Issues

1. **Context7 API Key Issues**
   ```bash
   # Check if API key is set
   echo $CONTEXT7_API_KEY
   
   # Test API key validity
   python -c "
   import os
   from mcp_server.tools import Context7Client
   client = Context7Client(os.getenv('CONTEXT7_API_KEY'))
   print('API key is valid')
   "
   ```

2. **Port Conflicts**
   ```bash
   # Check if port is in use
   lsof -i :8000
   
   # Use alternative port
   python mcp_server/http_server.py --port 8001
   ```

3. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   which python
   
   # Install missing dependencies
   pip install -r requirements.txt
   ```

### Debug Mode

Enable detailed logging:

```bash
export MCP_LOG_LEVEL=DEBUG
python workflow_demo.py
```

### Testing Without Context7

All examples work with mock data when Context7 API key is not available:

```bash
unset CONTEXT7_API_KEY
python examples/fastapi_development_example.py
```

## Best Practices

### 1. Error Handling

- Always implement fallback strategies
- Use retry logic with exponential backoff
- Provide meaningful error messages
- Log errors for debugging

### 2. Performance

- Reuse client connections
- Implement request batching for multiple operations
- Use caching for frequently accessed data
- Monitor response times and success rates

### 3. Security

- Secure API key storage (environment variables, not code)
- Validate all inputs to tools
- Implement rate limiting for external API calls
- Use HTTPS for production deployments

### 4. Monitoring

- Track tool usage and performance
- Monitor external service availability
- Implement health checks
- Set up alerting for failures

## Production Deployment

### 1. Environment Setup

```bash
# Production environment variables
export CONTEXT7_API_KEY="production-api-key"
export MCP_LOG_LEVEL="INFO"
export MCP_SERVER_HOST="0.0.0.0"
export MCP_SERVER_PORT="8000"
```

### 2. Process Management

```bash
# Use process manager like systemd or supervisor
# Example systemd service file:

[Unit]
Description=MCP Development Workflow Server
After=network.target

[Service]
Type=simple
User=mcp-user
WorkingDirectory=/path/to/03-mcp
Environment=CONTEXT7_API_KEY=your-api-key
ExecStart=/path/to/.venv/bin/python mcp_server/http_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Load Balancing

```nginx
# Nginx configuration for load balancing
upstream mcp_servers {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name mcp.yourdomain.com;
    
    location / {
        proxy_pass http://mcp_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Contributing

To extend the workflow system:

1. **Add New Tools**
   - Implement Tool interface
   - Add to server registration
   - Include in examples

2. **Add New Examples**
   - Follow existing patterns
   - Include comprehensive error handling
   - Add documentation

3. **Improve Coordination**
   - Implement new load balancing strategies
   - Add monitoring capabilities
   - Enhance failover mechanisms

## Related Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Context7 API Documentation](https://context7.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [VSCode MCP Integration](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)