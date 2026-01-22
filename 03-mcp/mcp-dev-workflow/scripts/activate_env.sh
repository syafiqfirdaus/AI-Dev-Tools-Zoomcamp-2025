#!/bin/bash
# Activation script for MCP Development Workflow environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "❌ Virtual environment not found at $PROJECT_ROOT/.venv"
    echo "Please run the setup first."
    exit 1
fi

# Activate the virtual environment
echo "🚀 Activating MCP Development Workflow environment..."
source "$PROJECT_ROOT/.venv/bin/activate"

# Verify activation
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Environment activated successfully!"
    echo "📍 Virtual environment: $VIRTUAL_ENV"
    echo "🐍 Python version: $(python --version)"
    echo ""
    echo "Available commands:"
    echo "  - Run tests: pytest"
    echo "  - Verify setup: python scripts/verify_setup.py"
    echo "  - Format code: black ."
    echo "  - Type check: mypy ."
    echo ""
    echo "To deactivate, run: deactivate"
else
    echo "❌ Failed to activate environment"
    exit 1
fi