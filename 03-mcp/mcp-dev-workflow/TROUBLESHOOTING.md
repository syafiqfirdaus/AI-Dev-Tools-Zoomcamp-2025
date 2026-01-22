# MCP Development Workflow - Troubleshooting Guide

This guide helps you resolve common issues when setting up and using the MCP Development Workflow system.

## Table of Contents

- [Setup Issues](#setup-issues)
- [Environment Issues](#environment-issues)
- [Server Issues](#server-issues)
- [Integration Issues](#integration-issues)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

## Setup Issues

### Python Version Problems

**Problem**: `Python version X.Y is too old. Python 3.12+ required.`

**Solutions**:
1. **Install Python 3.12+**:
   ```bash
   # Using pyenv (recommended)
   pyenv install 3.12.0
   pyenv local 3.12.0
   
   # Using system package manager
   # Ubuntu/Debian
   sudo apt update && sudo apt install python3.12 python3.12-venv
   
   # macOS with Homebrew
   brew install python@3.12
   
   # Windows: Download from python.org
   ```

2. **Verify installation**:
   ```bash
   python --version  # Should show 3.12.x
   python3.12 --version  # Alternative command
   ```

3. **Use specific Python version**:
   ```bash
   python3.12 scripts/setup.py
   ```

### Virtual Environment Creation Fails

**Problem**: `Failed to create virtual environment`

**Solutions**:
1. **Check permissions**:
   ```bash
   # Ensure you have write permissions in the project directory
   ls -la
   chmod 755 .
   ```

2. **Clear existing environment**:
   ```bash
   rm -rf .venv
   python scripts/setup.py
   ```

3. **Use alternative venv creation**:
   ```bash
   python -m venv .venv --clear
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate.bat  # Windows
   pip install -e .[test,dev]
   ```

### Dependency Installation Fails

**Problem**: `Failed to install dependencies`

**Solutions**:
1. **Update pip first**:
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install with verbose output**:
   ```bash
   pip install -e .[test,dev] -v
   ```

3. **Install from requirements.txt**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Clear pip cache**:
   ```bash
   pip cache purge
   pip install -e .[test,dev] --no-cache-dir
   ```

5. **Network issues**:
   ```bash
   # Use alternative index
   pip install -e .[test,dev] -i https://pypi.org/simple/
   
   # Behind corporate firewall
   pip install -e .[test,dev] --trusted-host pypi.org --trusted-host pypi.python.org
   ```

## Environment Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'mcp'`

**Solutions**:
1. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate.bat  # Windows
   ```

2. **Verify installation**:
   ```bash
   pip list | grep mcp
   python -c "import mcp; print(mcp.__version__)"
   ```

3. **Reinstall in development mode**:
   ```bash
   pip install -e .
   ```

### Path Issues

**Problem**: `Cannot find module or script`

**Solutions**:
1. **Run from project root**:
   ```bash
   cd /path/to/mcp-dev-workflow
   python scripts/setup.py
   ```

2. **Check PYTHONPATH**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   python scripts/run_stdio_server.py
   ```

3. **Use absolute paths**:
   ```bash
   python /full/path/to/scripts/run_stdio_server.py
   ```

## Server Issues

### Stdio Server Problems

**Problem**: Server doesn't respond to JSON-RPC requests

**Solutions**:
1. **Check JSON format**:
   ```json
   {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
   ```

2. **Enable debug mode**:
   ```bash
   python scripts/run_stdio_server.py --debug
   ```

3. **Test with simple request**:
   ```json
   {"jsonrpc":"2.0","id":1,"method":"tools/list"}
   ```

4. **Check for syntax errors**:
   ```bash
   python -m py_compile mcp_server/stdio_server.py
   ```

### HTTP Server Problems

**Problem**: `Port 8000 is already in use`

**Solutions**:
1. **Use different port**:
   ```bash
   python scripts/run_http_server.py --port 8080
   ```

2. **Find and kill process using port**:
   ```bash
   # Linux/macOS
   lsof -ti:8000 | xargs kill -9
   
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

3. **Use automatic port selection**:
   ```bash
   python scripts/run_http_server.py --port 0  # Uses random available port
   ```

**Problem**: `CORS errors in browser`

**Solutions**:
1. **Check CORS configuration**:
   - Ensure FastAPI CORS middleware is properly configured
   - Verify allowed origins include your client domain

2. **Test with curl instead of browser**:
   ```bash
   curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

### Tool Execution Errors

**Problem**: `Tool 'xyz' not found`

**Solutions**:
1. **List available tools**:
   ```json
   {"jsonrpc":"2.0","id":1,"method":"tools/list"}
   ```

2. **Check tool registration**:
   ```bash
   python -c "from mcp_server.core.server import MCPServer; s = MCPServer(); print(s.tools_manager.list_tools())"
   ```

3. **Verify tool implementation**:
   ```bash
   python -m py_compile mcp_server/tools/weather.py
   ```

## Integration Issues

### VSCode Integration

**Problem**: MCP servers not recognized in VSCode

**Solutions**:
1. **Check mcp.json configuration**:
   ```json
   {
     "mcpServers": {
       "mcp-dev-workflow": {
         "command": "/path/to/.venv/bin/python",
         "args": ["/path/to/mcp_server/stdio_server.py"],
         "disabled": false
       }
     }
   }
   ```

2. **Verify paths are absolute**:
   ```bash
   which python  # Use this path in mcp.json
   pwd  # Use this + relative path for server script
   ```

3. **Restart VSCode after configuration changes**

4. **Check VSCode MCP extension logs**:
   - Open VSCode Developer Tools
   - Check Console for MCP-related errors

### MCP Inspector Issues

**Problem**: Cannot connect to server in MCP Inspector

**Solutions**:
1. **Verify server is running**:
   ```bash
   python scripts/run_stdio_server.py &
   ps aux | grep stdio_server
   ```

2. **Check command and arguments**:
   - Command: `/path/to/.venv/bin/python`
   - Arguments: `/path/to/mcp_server/stdio_server.py`

3. **Test server manually first**:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python scripts/run_stdio_server.py
   ```

### Context7 Integration

**Problem**: `Authentication failed` with Context7

**Solutions**:
1. **Verify API key**:
   ```bash
   export CONTEXT7_API_KEY="your-api-key-here"
   python -c "import os; print('API Key set:', bool(os.getenv('CONTEXT7_API_KEY')))"
   ```

2. **Test API connection**:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.context7.com/health
   ```

3. **Check rate limits**:
   - Wait a few minutes if you've made many requests
   - Implement exponential backoff in your code

## Performance Issues

### Slow Server Response

**Solutions**:
1. **Enable async mode**:
   ```bash
   python scripts/run_http_server.py --workers 4
   ```

2. **Check system resources**:
   ```bash
   top
   free -h
   df -h
   ```

3. **Profile the application**:
   ```bash
   python -m cProfile scripts/run_stdio_server.py
   ```

### Memory Issues

**Solutions**:
1. **Monitor memory usage**:
   ```bash
   python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
   ```

2. **Reduce concurrent requests**:
   ```bash
   python scripts/run_http_server.py --workers 1
   ```

3. **Clear caches periodically**:
   ```python
   import gc
   gc.collect()
   ```

## Getting Help

### Diagnostic Information

When reporting issues, please include:

1. **System information**:
   ```bash
   python --version
   pip --version
   uname -a  # Linux/macOS
   systeminfo  # Windows
   ```

2. **Environment details**:
   ```bash
   pip list
   echo $PYTHONPATH
   which python
   ```

3. **Error logs**:
   ```bash
   python scripts/run_stdio_server.py --debug 2>&1 | tee debug.log
   ```

4. **Configuration files**:
   - `pyproject.toml`
   - `mcp.json`
   - Environment variables

### Running Diagnostics

Use the built-in diagnostic tools:

```bash
# Verify complete setup
python scripts/verify_setup.py

# Test server functionality
python scripts/test_mcp_config.py

# Check MCP Inspector integration
python scripts/verify_inspector_integration.py
```

### Common Commands Summary

```bash
# Setup and verification
python scripts/setup.py
python scripts/verify_setup.py

# Server operations
python scripts/run_stdio_server.py --debug
python scripts/run_http_server.py --port 8080 --debug

# Environment management
source .venv/bin/activate  # Activate environment
deactivate  # Deactivate environment
pip list  # List installed packages

# Testing
pytest tests/ -v
python -m pytest tests/test_stdio_integration.py::test_basic_communication
```

### Support Resources

- **Documentation**: Check README.md and docs/ directory
- **Examples**: See examples/ directory for working code
- **Tests**: Run tests to verify functionality
- **Issues**: Check existing issues in the project repository

### Emergency Reset

If all else fails, perform a complete reset:

```bash
# Backup any important changes
git stash

# Clean environment
rm -rf .venv
rm -rf __pycache__
rm -rf *.egg-info
find . -name "*.pyc" -delete

# Fresh setup
python scripts/setup.py
python scripts/verify_setup.py
```

This should resolve most issues and get you back to a working state.