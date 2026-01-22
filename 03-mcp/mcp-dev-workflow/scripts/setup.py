#!/usr/bin/env python3
"""
Automated setup script for MCP Development Workflow
Creates Python environment, installs dependencies, and configures the project.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional


class SetupError(Exception):
    """Custom exception for setup errors."""
    pass


class MCPSetup:
    """Main setup class for MCP Development Workflow."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / ".venv"
        self.python_executable = None
        
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements (3.12+)."""
        print("🔍 Checking Python version...")
        
        if sys.version_info < (3, 12):
            print(f"❌ Python version {sys.version_info.major}.{sys.version_info.minor} is too old.")
            print("   Python 3.12 or higher is required.")
            print("   Please install Python 3.12+ and try again.")
            return False
            
        print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} meets requirements")
        return True
    
    def check_system_dependencies(self) -> bool:
        """Check if required system tools are available."""
        print("🔍 Checking system dependencies...")
        
        required_tools = ["git", "pip"]
        missing_tools = []
        
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"❌ Missing required tools: {', '.join(missing_tools)}")
            print("   Please install the missing tools and try again.")
            return False
            
        print("✅ All required system tools are available")
        return True
    
    def create_virtual_environment(self) -> bool:
        """Create Python virtual environment."""
        print("🏗️  Creating virtual environment...")
        
        try:
            # Remove existing venv if it exists
            if self.venv_path.exists():
                print("   Removing existing virtual environment...")
                shutil.rmtree(self.venv_path)
            
            # Create new virtual environment
            result = subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], capture_output=True, text=True, check=True)
            
            # Set python executable path
            if os.name == 'nt':  # Windows
                self.python_executable = self.venv_path / "Scripts" / "python.exe"
                pip_executable = self.venv_path / "Scripts" / "pip.exe"
            else:  # Unix-like
                self.python_executable = self.venv_path / "bin" / "python"
                pip_executable = self.venv_path / "bin" / "pip"
            
            if not self.python_executable.exists():
                raise SetupError("Virtual environment creation failed - Python executable not found")
                
            print("✅ Virtual environment created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            print(f"   Error output: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error creating virtual environment: {e}")
            return False
    
    def upgrade_pip(self) -> bool:
        """Upgrade pip to latest version."""
        print("📦 Upgrading pip...")
        
        try:
            result = subprocess.run([
                str(self.python_executable), "-m", "pip", "install", "--upgrade", "pip"
            ], capture_output=True, text=True, check=True)
            
            print("✅ Pip upgraded successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to upgrade pip: {e}")
            print(f"   Error output: {e.stderr}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install project dependencies."""
        print("📦 Installing project dependencies...")
        
        try:
            # Install in editable mode with all extras
            result = subprocess.run([
                str(self.python_executable), "-m", "pip", "install", 
                "-e", ".[test,dev]"
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            print("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print(f"   Error output: {e.stderr}")
            print("   Trying alternative installation method...")
            
            # Fallback: install from requirements.txt
            return self.install_from_requirements()
    
    def install_from_requirements(self) -> bool:
        """Fallback method to install from requirements.txt."""
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ No requirements.txt file found for fallback installation")
            return False
        
        try:
            result = subprocess.run([
                str(self.python_executable), "-m", "pip", "install", 
                "-r", str(requirements_file)
            ], capture_output=True, text=True, check=True)
            
            print("✅ Dependencies installed from requirements.txt")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install from requirements.txt: {e}")
            print(f"   Error output: {e.stderr}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify that installation was successful."""
        print("🔍 Verifying installation...")
        
        try:
            # Run the verification script
            verify_script = self.project_root / "scripts" / "verify_setup.py"
            result = subprocess.run([
                str(self.python_executable), str(verify_script)
            ], capture_output=True, text=True, check=True)
            
            print("✅ Installation verification passed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation verification failed: {e}")
            print(f"   Error output: {e.stderr}")
            return False
    
    def create_activation_script(self) -> bool:
        """Create platform-specific activation script."""
        print("📝 Creating activation scripts...")
        
        try:
            # Create cross-platform activation script
            if os.name == 'nt':  # Windows
                activate_script = self.project_root / "activate.bat"
                script_content = f"""@echo off
echo 🚀 Activating MCP Development Workflow environment...
call "{self.venv_path}\\Scripts\\activate.bat"
echo ✅ Environment activated successfully!
echo 📍 Virtual environment: %VIRTUAL_ENV%
python --version
echo.
echo Available commands:
echo   - Run tests: pytest
echo   - Verify setup: python scripts\\verify_setup.py
echo   - Format code: black .
echo   - Type check: mypy .
echo.
echo To deactivate, run: deactivate
"""
            else:  # Unix-like
                activate_script = self.project_root / "activate.sh"
                script_content = f"""#!/bin/bash
echo "🚀 Activating MCP Development Workflow environment..."
source "{self.venv_path}/bin/activate"
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
"""
                # Make script executable
                activate_script.write_text(script_content)
                os.chmod(activate_script, 0o755)
                
            activate_script.write_text(script_content)
            print("✅ Activation script created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create activation script: {e}")
            return False
    
    def run_setup(self) -> bool:
        """Run the complete setup process."""
        print("🚀 Starting MCP Development Workflow setup...\n")
        
        setup_steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking system dependencies", self.check_system_dependencies),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Upgrading pip", self.upgrade_pip),
            ("Installing dependencies", self.install_dependencies),
            ("Verifying installation", self.verify_installation),
            ("Creating activation script", self.create_activation_script),
        ]
        
        for step_name, step_func in setup_steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"\n❌ Setup failed at step: {step_name}")
                print("   Please check the error messages above and try again.")
                return False
        
        print("\n" + "="*60)
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Activate the environment:")
        if os.name == 'nt':
            print("   activate.bat")
        else:
            print("   source activate.sh")
        print("2. Verify setup: python scripts/verify_setup.py")
        print("3. Run tests: pytest")
        print("4. Start developing with MCP!")
        print("\n📚 See README.md for usage instructions.")
        
        return True


def main():
    """Main entry point."""
    try:
        setup = MCPSetup()
        success = setup.run_setup()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())