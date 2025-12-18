# MCP Development Workflow System

A comprehensive Model Context Protocol (MCP) implementation for AI-powered development workflows, featuring live documentation integration, multi-server coordination, and robust error handling.

## 🚀 Overview

The MCP Development Workflow System demonstrates practical usage of MCP servers in real-world development scenarios. It integrates with Context7 for live documentation access, provides multi-server coordination capabilities, and includes comprehensive examples for building AI-enhanced development tools.

### Key Features

- **Live Documentation Integration** - Access up-to-date library documentation through Context7
- **Multi-Server Coordination** - Load balancing, failover, and request aggregation across multiple MCP servers
- **Robust Error Handling** - Comprehensive error recovery with retry logic and fallback strategies
- **Real-World Examples** - Practical demonstrations including FastAPI development workflows
- **Production Ready** - Monitoring, metrics, and deployment configurations included

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Development Workflows](#-development-workflows)
- [API Reference](#-api-reference)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

## 🏃 Quick Start

### Prerequisites

- Python 3.12+
- Context7 API key (optional - examples work with mock data)
- Node.js (for MCP Inspector)

### Basic Setup

```bash
# Navigate to project directory
cd 03-mcp/mcp-dev-workflow

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set Context7 API key (optional)
export CONTEXT7_API_KEY="your-api-key-here"

# Run workflow demonstration
python workflow_demo.py
```

### Test with MCP Inspector

```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector

# Test stdio server
npx @modelcontextprotocol/inspector python mcp_server/stdio_server.py

# Test HTTP server (in separate terminal)
python mcp_server/http_server.py --port 8000
# Then connect inspector to http://localhost:8000
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Development Workflow System               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Clients    │    │  Development    │    │   External      │
│                 │    │     Tools       │    │   Services      │
│ • VSCode        │    │                 │    │                 │
│ • Copilot       │◄──►│ • MCP Inspector │◄──►│ • Context7 API  │
│ • Claude        │    │ • Custom Tools  │    │ • Weather API   │
│ • Custom Apps   │    │ • CI/CD         │    │ • GitHub API    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Protocol Layer                       │
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────┐          │
│  │  stdio Transport│              │  HTTP Transport │          │
│  │                 │              │                 │          │
│  │ • JSON-RPC      │              │ • REST API      │          │
│  │ • Bidirectional │              │ • WebSocket     │          │
│  │ • Process-based │              │ • Network-based │          │
│  └─────────────────┘              └─────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
         │                                       │
         │                                       │
         ▼                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Server Framework                        │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Tool Manager  │  │ Resource Manager│  │ Prompt Manager  │ │
│  │                 │  │                 │  │                 │ │
│  │ • Tool Registry │  │ • File Access   │  │ • Template Mgmt │ │
│  │ • Execution     │  │ • Data Sources  │  │ • Context Mgmt  │ │
│  │ • Validation    │  │ • Caching       │  │ • Generation    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Core Tools Layer                         │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Documentation   │  │   Coordination  │  │    Utilities    │ │
│  │     Tools       │  │     Tools       │  │                 │ │
│  │                 │  │                 │  │                 │ │
│  │ • Context7      │  │ • Load Balancer │  │ • Echo Tool     │ │
│  │   - Library     │  │ • Failover Mgmt │  │ • Weather Tool  │ │
│  │     Search      │  │ • Request       │  │ • File Tools    │ │
│  │   - Doc Lookup  │  │   Aggregation   │  │ • Validation    │ │
│  │   - Examples    │  │ • Health Check  │  │   Tools         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Server Coordination                    │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Load Balancing  │  │ Error Handling  │  │   Monitoring    │ │
│  │                 │  │                 │  │                 │ │
│  │ • Round Robin   │  │ • Retry Logic   │  │ • Metrics       │ │
│  │ • Weighted      │  │ • Exponential   │  │ • Health Checks │ │
│  │ • Performance   │  │   Backoff       │  │ • Performance   │ │
│  │   Based         │  │ • Fallback      │  │   Tracking      │ │
│  │ • Custom        │  │   Strategies    │  │ • Alerting      │ │
│  │   Strategies    │  │ • Circuit       │  │ • Reporting     │ │
│  │                 │  │   Breaker       │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Data Flow                                │
│                                                                 │
│  Client Request → MCP Protocol → Server Framework →             │
│  Tool Execution → External APIs → Response Processing →         │
│  Error Handling → Load Balancing → Client Response             │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Request       │───►│   Processing    │───►│  Response   │ │
│  │                 │    │                 │    │             │ │
│  │ • Validation    │    │ • Tool Lookup   │    │ • Success   │ │
│  │ • Routing       │    │ • Execution     │    │ • Error     │ │
│  │ • Load Balance  │    │ • Coordination  │    │ • Metrics   │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Components

#### 1. **Client Layer**
- **AI Clients**: VSCode, GitHub Copilot, Claude, custom applications
- **Development Tools**: MCP Inspector, CI/CD systems, custom tooling
- **External Services**: Context7 API, Weather APIs, GitHub API

#### 2. **Protocol Layer**
- **stdio Transport**: JSON-RPC over stdin/stdout for process-based communication
- **HTTP Transport**: REST API and WebSocket for network-based communication
- **Bidirectional Communication**: Full duplex communication between clients and servers

#### 3. **Server Framework**
- **Tool Manager**: Registry, execution, and validation of MCP tools
- **Resource Manager**: File access, data sources, and caching mechanisms
- **Prompt Manager**: Template management, context handling, and generation

#### 4. **Core Tools**
- **Documentation Tools**: Context7 integration for live documentation access
- **Coordination Tools**: Load balancing, failover management, request aggregation
- **Utility Tools**: Echo, weather, file operations, validation tools

#### 5. **Multi-Server Coordination**
- **Load Balancing**: Round-robin, weighted, performance-based strategies
- **Error Handling**: Retry logic, exponential backoff, fallback strategies
- **Monitoring**: Metrics collection, health checks, performance tracking

## 📦 Installation

### Method 1: Direct Installation

```bash
# Clone repository
git clone <repository-url>
cd 03-mcp/mcp-dev-workflow

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Method 2: Using uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to project
cd 03-mcp/mcp-dev-workflow

# Create and activate environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```

### Optional: Context7 Setup

1. Create account at [Context7](https://context7.com/)
2. Get API key from dashboard
3. Set environment variable:
   ```bash
   export CONTEXT7_API_KEY="your-api-key-here"
   ```

## 🔧 Usage Examples

### 1. Basic Workflow Demo

```bash
# Run complete workflow demonstration
python workflow_demo.py
```

**Output**: Comprehensive report showing:
- Documentation workflow using Context7
- Multi-server coordination examples
- Error handling and recovery scenarios
- Performance metrics and recommendations

### 2. FastAPI Development Example

```bash
# Run FastAPI development workflow
python examples/fastapi_development_example.py
```

**Demonstrates**:
- Library research for authentication systems
- Documentation retrieval for FastAPI security
- Code example generation
- Implementation planning

### 3. Multi-Server Coordination

```bash
# Run multi-server coordination example
python examples/multi_server_coordination_example.py
```

**Features**:
- Load balancing across multiple servers
- Automatic failover testing
- Request aggregation
- Performance monitoring

### 4. Interactive Testing

```bash
# Start stdio server for manual testing
python mcp_server/stdio_server.py

# In another terminal, send JSON-RPC requests:
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}' | python mcp_server/stdio_server.py
```

## ⚙️ Configuration

### Environment Variables

```bash
# Context7 API Configuration
export CONTEXT7_API_KEY="your-api-key"

# Logging Configuration
export MCP_LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR

# Server Configuration
export MCP_SERVER_HOST="127.0.0.1"
export MCP_SERVER_PORT="8000"

# Performance Configuration
export MCP_MAX_RETRIES="3"
export MCP_TIMEOUT="30"
```

### MCP Server Configuration

Create `.vscode/mcp.json` or update existing configuration:

```json
{
  "mcpServers": {
    "mcp-dev-workflow": {
      "command": "python",
      "args": ["/path/to/03-mcp/mcp-dev-workflow/mcp_server/stdio_server.py"],
      "env": {
        "CONTEXT7_API_KEY": "your-api-key",
        "MCP_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": ["echo", "get_weather"]
    }
  }
}
```

### Custom Tool Configuration

```python
# config/tools_config.py
TOOL_CONFIG = {
    "context7": {
        "enabled": True,
        "api_key_required": True,
        "rate_limit": 100,  # requests per minute
        "timeout": 30
    },
    "weather": {
        "enabled": True,
        "api_key_required": False,
        "default_units": "metric"
    },
    "echo": {
        "enabled": True,
        "max_message_length": 1000
    }
}
```

## 🔄 Development Workflows

### Workflow 1: Feature Development with Live Documentation

```python
async def feature_development_workflow():
    """Complete feature development workflow with live documentation."""
    
    # 1. Research Phase
    libraries = await search_libraries("fastapi authentication")
    
    # 2. Documentation Phase
    docs = await get_documentation("fastapi", version="latest")
    
    # 3. Example Phase
    examples = await get_code_examples("fastapi", topic="middleware")
    
    # 4. Implementation Planning
    plan = generate_implementation_plan(libraries, docs, examples)
    
    return {
        "libraries": libraries,
        "documentation": docs,
        "examples": examples,
        "implementation_plan": plan
    }
```

### Workflow 2: Code Review and Validation

```python
async def code_review_workflow(code_snippet, library_name):
    """Validate code against current best practices."""
    
    # Get current documentation
    current_docs = await get_documentation(library_name)
    
    # Get best practices
    best_practices = await get_examples(library_name, topic="best_practices")
    
    # Validate implementation
    validation_result = validate_code_patterns(
        code_snippet, 
        current_docs, 
        best_practices
    )
    
    return validation_result
```

### Workflow 3: Multi-Environment Testing

```python
async def multi_environment_testing():
    """Test across multiple server configurations."""
    
    coordinator = MultiServerCoordinator()
    await coordinator.setup_servers()
    
    # Test load balancing
    load_test_results = await coordinator.load_test(
        tool_name="context7_search_libraries",
        arguments={"query": "fastapi", "limit": 5},
        concurrent_requests=10
    )
    
    # Test failover
    failover_results = await coordinator.test_failover_scenarios()
    
    # Generate report
    report = generate_testing_report(load_test_results, failover_results)
    
    return report
```

## 📚 API Reference

### Core Tools

#### Context7 Tools

```python
# Search for libraries
await execute_tool("context7_search_libraries", {
    "query": "fastapi authentication",
    "limit": 10
})

# Get documentation
await execute_tool("context7_get_documentation", {
    "library": "fastapi",
    "version": "latest"
})

# Get code examples
await execute_tool("context7_get_examples", {
    "library": "fastapi",
    "topic": "middleware",
    "limit": 5
})
```

#### Utility Tools

```python
# Echo tool for testing
await execute_tool("echo", {
    "message": "Hello, MCP!"
})

# Weather tool for demonstration
await execute_tool("get_weather", {
    "city": "London",
    "units": "metric"
})
```

### Multi-Server Coordination

```python
from examples.multi_server_coordination_example import MultiServerCoordinator

coordinator = MultiServerCoordinator()

# Round-robin load balancing
result = await coordinator.round_robin_request(tool_name, arguments)

# Weighted load balancing
result = await coordinator.weighted_request(tool_name, arguments)

# Automatic failover
result = await coordinator.failover_request(
    tool_name, 
    arguments, 
    max_attempts=3
)

# Request aggregation
results = await coordinator.aggregate_request(
    tool_name, 
    arguments_list
)
```

### Error Handling

```python
from mcp_server.error_handling import RetryManager

retry_manager = RetryManager(
    max_retries=3,
    backoff_factor=2.0,
    max_backoff=60.0
)

result = await retry_manager.execute_with_retry(
    tool_function,
    *args,
    **kwargs
)
```

## 🚀 Deployment

### Development Deployment

```bash
# Start stdio server
python mcp_server/stdio_server.py

# Start HTTP server
python mcp_server/http_server.py --host 127.0.0.1 --port 8000
```

### Production Deployment

#### Using Docker

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "mcp_server/http_server.py", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t mcp-dev-workflow .
docker run -p 8000:8000 -e CONTEXT7_API_KEY=your-key mcp-dev-workflow
```

#### Using systemd

```ini
# /etc/systemd/system/mcp-dev-workflow.service
[Unit]
Description=MCP Development Workflow Server
After=network.target

[Service]
Type=simple
User=mcp-user
WorkingDirectory=/opt/mcp-dev-workflow
Environment=CONTEXT7_API_KEY=your-api-key
Environment=MCP_LOG_LEVEL=INFO
ExecStart=/opt/mcp-dev-workflow/.venv/bin/python mcp_server/http_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable mcp-dev-workflow
sudo systemctl start mcp-dev-workflow
```

#### Load Balancing with Nginx

```nginx
upstream mcp_servers {
    server 127.0.0.1:8000 weight=3;
    server 127.0.0.1:8001 weight=2;
    server 127.0.0.1:8002 weight=1;
}

server {
    listen 80;
    server_name mcp.yourdomain.com;
    
    location / {
        proxy_pass http://mcp_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Health check
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### Monitoring and Observability

#### Prometheus Metrics

```python
# Add to mcp_server/metrics.py
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter('mcp_requests_total', 'Total MCP requests', ['tool_name', 'status'])
REQUEST_DURATION = Histogram('mcp_request_duration_seconds', 'Request duration', ['tool_name'])
ACTIVE_CONNECTIONS = Gauge('mcp_active_connections', 'Active connections')
```

#### Health Checks

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "services": {
            "context7": await check_context7_health(),
            "database": await check_database_health()
        }
    }
```

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone repository
git clone https://github.com/yourusername/mcp-dev-workflow.git
cd mcp-dev-workflow

# Create development environment
uv venv
source .venv/bin/activate
uv sync --dev

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_server --cov-report=html

# Run specific test file
pytest tests/test_tools.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black .
isort .

# Type checking
mypy mcp_server/

# Linting
flake8 mcp_server/
```

### Adding New Tools

1. **Create Tool Class**
   ```python
   # mcp_server/tools/your_tool.py
   from mcp_server.tools.base import Tool
   
   class YourTool(Tool):
       name = "your_tool"
       description = "Description of your tool"
       
       async def execute(self, arguments: dict) -> dict:
           # Implementation
           return {"result": "success"}
   ```

2. **Register Tool**
   ```python
   # mcp_server/stdio_server.py
   from mcp_server.tools.your_tool import YourTool
   
   server.register_tool(YourTool())
   ```

3. **Add Tests**
   ```python
   # tests/test_your_tool.py
   import pytest
   from mcp_server.tools.your_tool import YourTool
   
   @pytest.mark.asyncio
   async def test_your_tool():
       tool = YourTool()
       result = await tool.execute({"param": "value"})
       assert result["result"] == "success"
   ```

### Documentation

- Update README.md for new features
- Add docstrings to all functions and classes
- Include examples in documentation
- Update API reference section

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Context7 API Documentation](https://context7.com/docs)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [VSCode MCP Integration](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-dev-workflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-dev-workflow/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/mcp-dev-workflow/wiki)

---

**Built with ❤️ for the AI development community**