#!/usr/bin/env python3
"""
Unified installation script for MCP Development Workflow
Provides multiple installation methods and comprehensive error handling.
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path


def print_banner():
    """Print installation banner."""
    print("=" * 60)
    print("🚀 MCP Development Workflow - Installation Script")
    print("=" * 60)
    print()


def check_prerequisites():
    """Check system prerequisites."""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 12):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} is too old")
        print("   Python 3.12+ is required")
        print("   Please install Python 3.12+ and try again")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check required tools
    required_tools = ["git", "pip"]
    for tool in required_tools:
        if shutil.which(tool):
            print(f"✅ {tool}")
        else:
            print(f"❌ {tool} not found")
            print(f"   Please install {tool} and try again")
            return False
    
    return True


def install_with_uv():
    """Install using uv (fastest method)."""
    print("📦 Installing with uv (recommended)...")
    
    try:
        # Check if uv is available
        if not shutil.which("uv"):
            print("   Installing uv...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "uv"
            ], check=True, capture_output=True)
        
        # Create environment and install
        subprocess.run(["uv", "venv", ".venv"], check=True)
        subprocess.run(["uv", "pip", "install", "-e", ".[test,dev]"], check=True)
        
        print("✅ Installation with uv completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ uv installation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error with uv: {e}")
        return False


def install_with_pip():
    """Install using standard pip."""
    print("📦 Installing with pip...")
    
    try:
        # Create virtual environment
        subprocess.run([
            sys.executable, "-m", "venv", ".venv"
        ], check=True)
        
        # Determine activation script path
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(".venv", "Scripts", "pip")
            python_path = os.path.join(".venv", "Scripts", "python")
        else:  # Unix/Linux/macOS
            pip_path = os.path.join(".venv", "bin", "pip")
            python_path = os.path.join(".venv", "bin", "python")
        
        # Install dependencies
        subprocess.run([
            python_path, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            python_path, "-m", "pip", "install", "-e", ".[test,dev]"
        ], check=True)
        
        print("✅ Installation with pip completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ pip installation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error with pip: {e}")
        return False


def install_with_conda():
    """Install using conda."""
    print("📦 Installing with conda...")
    
    try:
        # Check if conda is available
        if not shutil.which("conda"):
            print("❌ conda not found")
            return False
        
        # Create environment
        subprocess.run([
            "conda", "create", "-n", "mcp-dev", "python=3.12", "-y"
        ], check=True)
        
        # Install dependencies
        subprocess.run([
            "conda", "run", "-n", "mcp-dev", "pip", "install", "-e", ".[test,dev]"
        ], check=True)
        
        print("✅ Installation with conda completed")
        print("   Activate with: conda activate mcp-dev")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ conda installation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error with conda: {e}")
        return False


def verify_installation():
    """Verify the installation."""
    print("🔍 Verifying installation...")
    
    try:
        # Check if we can import the main modules
        if os.name == 'nt':  # Windows
            python_path = os.path.join(".venv", "Scripts", "python")
        else:  # Unix/Linux/macOS
            python_path = os.path.join(".venv", "bin", "python")
        
        # Test imports
        test_imports = [
            "import mcp_server",
            "import pytest",
            "import hypothesis",
            "import fastapi",
            "import uvicorn"
        ]
        
        for import_stmt in test_imports:
            result = subprocess.run([
                python_path, "-c", import_stmt
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                module_name = import_stmt.split()[1]
                print(f"✅ {module_name}")
            else:
                module_name = import_stmt.split()[1]
                print(f"❌ {module_name} - {result.stderr.strip()}")
                return False
        
        print("✅ All modules imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def print_next_steps():
    """Print next steps after installation."""
    print()
    print("🎉 Installation completed successfully!")
    print()
    print("Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source .venv/bin/activate")
    print()
    print("2. Run tests:")
    print("   python -m pytest tests/ -v")
    print()
    print("3. Start the stdio server:")
    print("   python -m mcp_server.stdio_server")
    print()
    print("4. Start the HTTP server:")
    print("   python -m mcp_server.http_server")
    print()
    print("For more information, see README.md")


def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(description="Install MCP Development Workflow")
    parser.add_argument(
        "--method", 
        choices=["uv", "pip", "conda"], 
        default="uv",
        help="Installation method (default: uv)"
    )
    parser.add_argument(
        "--skip-verify", 
        action="store_true",
        help="Skip installation verification"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Install based on method
    success = False
    if args.method == "uv":
        success = install_with_uv()
    elif args.method == "pip":
        success = install_with_pip()
    elif args.method == "conda":
        success = install_with_conda()
    
    if not success:
        print()
        print("❌ Installation failed")
        print("Try a different installation method:")
        print("  python install.py --method pip")
        print("  python install.py --method conda")
        sys.exit(1)
    
    # Verify installation
    if not args.skip_verify:
        if not verify_installation():
            print()
            print("❌ Installation verification failed")
            print("The installation may be incomplete")
            sys.exit(1)
    
    print_next_steps()


if __name__ == "__main__":
    main()