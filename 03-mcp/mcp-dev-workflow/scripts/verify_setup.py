#!/usr/bin/env python3
"""
Setup verification script for MCP Development Workflow
Validates that the environment is properly configured with all required dependencies.
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check if Python version meets requirements."""
    if sys.version_info < (3, 12):
        print(f"❌ Python version {sys.version_info.major}.{sys.version_info.minor} is too old. Python 3.12+ required.")
        return False
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} meets requirements")
    return True


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        "mcp",
        "fastapi", 
        "uvicorn",
        "pydantic",
        "httpx",
        "pytest",
        "hypothesis"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0


def check_project_structure():
    """Check if project directory structure is properly created."""
    required_dirs = [
        "mcp_server",
        "mcp_server/core",
        "mcp_server/transport", 
        "mcp_server/tools",
        "config",
        "tests",
        "scripts"
    ]
    
    missing_dirs = []
    project_root = Path(__file__).parent.parent
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✅ Directory {dir_path} exists")
        else:
            print(f"❌ Directory {dir_path} is missing")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0


def check_config_files():
    """Check if required configuration files exist."""
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        ".gitignore"
    ]
    
    missing_files = []
    project_root = Path(__file__).parent.parent
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ File {file_path} exists")
        else:
            print(f"❌ File {file_path} is missing")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def main():
    """Run all verification checks."""
    print("🔍 Verifying MCP Development Workflow setup...\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Configuration Files", check_config_files)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All checks passed! Environment is ready for MCP development.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())