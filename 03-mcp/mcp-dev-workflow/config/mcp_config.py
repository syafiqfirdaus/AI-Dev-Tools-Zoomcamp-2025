"""
MCP Configuration management and validation.

This module provides functionality to load, validate, and manage
MCP server configurations for VSCode integration.
"""

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging


logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Configuration for a single MCP server."""
    
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    cwd: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    disabled: bool = False
    auto_approve: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate server configuration after initialization."""
        if not self.name:
            raise ValueError("Server name cannot be empty")
        if not self.command:
            raise ValueError("Server command cannot be empty")
    
    @classmethod
    def from_dict(cls, name: str, config_dict: Dict[str, Any]) -> 'ServerConfig':
        """
        Create ServerConfig from dictionary.
        
        Args:
            name: Server name
            config_dict: Configuration dictionary
            
        Returns:
            ServerConfig instance
            
        Raises:
            ValueError: If configuration is invalid
        """
        try:
            return cls(
                name=name,
                command=config_dict.get("command", ""),
                args=config_dict.get("args", []),
                cwd=config_dict.get("cwd"),
                env=config_dict.get("env", {}),
                disabled=config_dict.get("disabled", False),
                auto_approve=config_dict.get("autoApprove", [])
            )
        except Exception as e:
            raise ValueError(f"Invalid configuration for server '{name}': {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ServerConfig to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            "command": self.command,
            "args": self.args,
            "cwd": self.cwd,
            "env": self.env,
            "disabled": self.disabled,
            "autoApprove": self.auto_approve
        }
    
    def validate_paths(self, base_path: Optional[Path] = None) -> List[str]:
        """
        Validate file paths in the configuration.
        
        Args:
            base_path: Base path for relative path resolution
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate working directory
        if self.cwd:
            cwd_path = Path(self.cwd)
            if not cwd_path.is_absolute() and base_path:
                cwd_path = base_path / cwd_path
            
            if not cwd_path.exists():
                errors.append(f"Working directory does not exist: {cwd_path}")
            elif not cwd_path.is_dir():
                errors.append(f"Working directory is not a directory: {cwd_path}")
        
        return errors
    
    def validate_command(self) -> List[str]:
        """
        Validate the command and arguments.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check if command exists in PATH or is an absolute path
        if self.command.startswith("/") or self.command.startswith("./"):
            # Absolute or relative path
            if not Path(self.command).exists():
                errors.append(f"Command not found: {self.command}")
        else:
            # Check if command is in PATH
            import shutil
            if not shutil.which(self.command):
                errors.append(f"Command not found in PATH: {self.command}")
        
        return errors


@dataclass
class MCPConfig:
    """Complete MCP configuration containing all servers."""
    
    mcp_servers: Dict[str, ServerConfig] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'MCPConfig':
        """
        Load MCP configuration from JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            MCPConfig instance
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration is invalid
            json.JSONDecodeError: If JSON is malformed
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in {config_path}: {e.msg}", e.doc, e.pos)
        
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object")
        
        if "mcpServers" not in data:
            raise ValueError("Configuration must contain 'mcpServers' key")
        
        servers = {}
        for server_name, server_config in data["mcpServers"].items():
            if not isinstance(server_config, dict):
                raise ValueError(f"Server configuration for '{server_name}' must be an object")
            
            servers[server_name] = ServerConfig.from_dict(server_name, server_config)
        
        return cls(mcp_servers=servers)
    
    def to_file(self, config_path: Union[str, Path]) -> None:
        """
        Save MCP configuration to JSON file.
        
        Args:
            config_path: Path to save the configuration file
        """
        config_path = Path(config_path)
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "mcpServers": {
                name: server.to_dict()
                for name, server in self.mcp_servers.items()
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def validate(self, base_path: Optional[Path] = None) -> List[str]:
        """
        Validate the entire configuration.
        
        Args:
            base_path: Base path for relative path resolution
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if not self.mcp_servers:
            errors.append("No MCP servers configured")
            return errors
        
        for server_name, server_config in self.mcp_servers.items():
            # Validate server configuration
            try:
                server_errors = server_config.validate_paths(base_path)
                server_errors.extend(server_config.validate_command())
                
                for error in server_errors:
                    errors.append(f"Server '{server_name}': {error}")
                    
            except Exception as e:
                errors.append(f"Server '{server_name}': Validation failed: {e}")
        
        return errors
    
    def get_enabled_servers(self) -> Dict[str, ServerConfig]:
        """
        Get all enabled servers.
        
        Returns:
            Dictionary of enabled servers
        """
        return {
            name: server
            for name, server in self.mcp_servers.items()
            if not server.disabled
        }
    
    def get_server(self, name: str) -> Optional[ServerConfig]:
        """
        Get server configuration by name.
        
        Args:
            name: Server name
            
        Returns:
            ServerConfig if found, None otherwise
        """
        return self.mcp_servers.get(name)


def validate_config_file(config_path: Union[str, Path], base_path: Optional[Path] = None) -> bool:
    """
    Validate an MCP configuration file and print results.
    
    Args:
        config_path: Path to the configuration file
        base_path: Base path for relative path resolution
        
    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        config = MCPConfig.from_file(config_path)
        errors = config.validate(base_path)
        
        if errors:
            print(f"Configuration validation failed for {config_path}:")
            for error in errors:
                print(f"  ❌ {error}")
            return False
        else:
            print(f"✅ Configuration is valid: {config_path}")
            
            # Print summary
            enabled_servers = config.get_enabled_servers()
            disabled_servers = {
                name: server
                for name, server in config.mcp_servers.items()
                if server.disabled
            }
            
            print(f"   📊 Total servers: {len(config.mcp_servers)}")
            print(f"   ✅ Enabled servers: {len(enabled_servers)}")
            if enabled_servers:
                for name in enabled_servers:
                    print(f"      • {name}")
            
            if disabled_servers:
                print(f"   ⏸️  Disabled servers: {len(disabled_servers)}")
                for name in disabled_servers:
                    print(f"      • {name}")
            
            return True
            
    except FileNotFoundError as e:
        print(f"❌ Configuration file not found: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Command-line interface for configuration validation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate MCP configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s mcp.json                    # Validate mcp.json in current directory
  %(prog)s --base-path /project mcp.json  # Validate with custom base path
        """
    )
    
    parser.add_argument(
        "config_file",
        help="Path to the MCP configuration file"
    )
    
    parser.add_argument(
        "--base-path",
        type=Path,
        help="Base path for resolving relative paths in configuration"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Validate configuration
    success = validate_config_file(args.config_file, args.base_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()