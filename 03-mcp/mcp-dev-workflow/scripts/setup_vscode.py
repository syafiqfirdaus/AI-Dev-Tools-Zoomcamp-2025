#!/usr/bin/env python3
"""
VSCode MCP setup script.

This script helps set up MCP server configuration for VSCode integration,
including copying configuration files and providing setup instructions.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
import logging

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.mcp_config import MCPConfig, validate_config_file


logger = logging.getLogger(__name__)


def get_vscode_config_paths() -> Dict[str, Path]:
    """
    Get VSCode configuration directory paths for different platforms.
    
    Returns:
        Dictionary mapping platform names to config paths
    """
    home = Path.home()
    
    if sys.platform == "win32":
        # Windows
        appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return {
            "windows": appdata / "Code" / "User",
            "windows_insiders": appdata / "Code - Insiders" / "User"
        }
    elif sys.platform == "darwin":
        # macOS
        return {
            "macos": home / "Library" / "Application Support" / "Code" / "User",
            "macos_insiders": home / "Library" / "Application Support" / "Code - Insiders" / "User"
        }
    else:
        # Linux and other Unix-like systems
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
        return {
            "linux": config_home / "Code" / "User",
            "linux_insiders": config_home / "Code - Insiders" / "User"
        }


def find_vscode_config_dir() -> Optional[Path]:
    """
    Find the VSCode configuration directory.
    
    Returns:
        Path to VSCode config directory if found, None otherwise
    """
    config_paths = get_vscode_config_paths()
    
    # Try to find existing VSCode installation
    for platform, config_path in config_paths.items():
        if config_path.exists():
            logger.info(f"Found VSCode configuration directory: {config_path}")
            return config_path
    
    # If no existing installation found, suggest the default for current platform
    if sys.platform == "win32":
        return config_paths["windows"]
    elif sys.platform == "darwin":
        return config_paths["macos"]
    else:
        return config_paths["linux"]


def backup_existing_config(config_path: Path) -> Optional[Path]:
    """
    Create a backup of existing MCP configuration.
    
    Args:
        config_path: Path to the MCP configuration file
        
    Returns:
        Path to backup file if created, None otherwise
    """
    if not config_path.exists():
        return None
    
    backup_path = config_path.with_suffix(f"{config_path.suffix}.backup")
    counter = 1
    
    # Find unique backup filename
    while backup_path.exists():
        backup_path = config_path.with_suffix(f"{config_path.suffix}.backup.{counter}")
        counter += 1
    
    try:
        shutil.copy2(config_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return None


def merge_mcp_configs(existing_config: MCPConfig, new_config: MCPConfig) -> MCPConfig:
    """
    Merge new MCP configuration with existing one.
    
    Args:
        existing_config: Existing MCP configuration
        new_config: New MCP configuration to merge
        
    Returns:
        Merged MCP configuration
    """
    merged_servers = existing_config.mcp_servers.copy()
    
    for server_name, server_config in new_config.mcp_servers.items():
        if server_name in merged_servers:
            logger.warning(f"Server '{server_name}' already exists, will be overwritten")
        merged_servers[server_name] = server_config
    
    return MCPConfig(mcp_servers=merged_servers)


def setup_vscode_config(
    source_config: Path,
    target_dir: Optional[Path] = None,
    merge: bool = True,
    dry_run: bool = False
) -> bool:
    """
    Set up VSCode MCP configuration.
    
    Args:
        source_config: Path to source MCP configuration
        target_dir: Target VSCode configuration directory
        merge: Whether to merge with existing configuration
        dry_run: If True, only show what would be done
        
    Returns:
        True if setup was successful, False otherwise
    """
    # Find VSCode config directory if not provided
    if target_dir is None:
        target_dir = find_vscode_config_dir()
        if target_dir is None:
            logger.error("Could not find VSCode configuration directory")
            return False
    
    target_config = target_dir / "mcp.json"
    
    logger.info(f"Setting up MCP configuration for VSCode")
    logger.info(f"Source: {source_config}")
    logger.info(f"Target: {target_config}")
    
    if dry_run:
        logger.info("DRY RUN - No files will be modified")
    
    # Validate source configuration
    if not validate_config_file(source_config):
        logger.error("Source configuration is invalid")
        return False
    
    try:
        # Load source configuration
        new_config = MCPConfig.from_file(source_config)
        
        # Handle existing configuration
        if target_config.exists() and merge:
            logger.info("Existing MCP configuration found")
            
            if not dry_run:
                # Create backup
                backup_path = backup_existing_config(target_config)
                if backup_path:
                    logger.info(f"Backup created: {backup_path}")
            
            try:
                existing_config = MCPConfig.from_file(target_config)
                merged_config = merge_mcp_configs(existing_config, new_config)
                logger.info("Merging configurations")
            except Exception as e:
                logger.warning(f"Failed to load existing config, will overwrite: {e}")
                merged_config = new_config
        else:
            merged_config = new_config
            if target_config.exists():
                logger.info("Will overwrite existing configuration")
        
        if not dry_run:
            # Ensure target directory exists
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Save merged configuration
            merged_config.to_file(target_config)
            logger.info(f"✅ MCP configuration saved to: {target_config}")
        else:
            logger.info(f"Would save configuration to: {target_config}")
        
        # Print setup summary
        enabled_servers = merged_config.get_enabled_servers()
        logger.info(f"📊 Configuration summary:")
        logger.info(f"   Total servers: {len(merged_config.mcp_servers)}")
        logger.info(f"   Enabled servers: {len(enabled_servers)}")
        
        for name, server in enabled_servers.items():
            logger.info(f"      • {name}: {server.command} {' '.join(server.args)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup VSCode configuration: {e}")
        return False


def print_setup_instructions():
    """Print instructions for completing VSCode MCP setup."""
    print("\n" + "="*60)
    print("📋 VSCode MCP Setup Instructions")
    print("="*60)
    print()
    print("1. Install the VSCode MCP extension:")
    print("   - Open VSCode")
    print("   - Go to Extensions (Ctrl+Shift+X)")
    print("   - Search for 'MCP' and install the official extension")
    print()
    print("2. Restart VSCode to load the new MCP configuration")
    print()
    print("3. Verify MCP servers are working:")
    print("   - Open Command Palette (Ctrl+Shift+P)")
    print("   - Run 'MCP: List Servers' to see configured servers")
    print("   - Run 'MCP: Test Connection' to verify connectivity")
    print()
    print("4. Optional: Set up Context7 integration:")
    print("   - Get your Context7 API key from https://context7.com")
    print("   - Set environment variable: export CONTEXT7_API_KEY=your_key_here")
    print("   - Restart VSCode to enable Context7 tools")
    print()
    print("5. Start using MCP tools in VSCode:")
    print("   - Use AI features in VSCode (Copilot, etc.)")
    print("   - MCP tools will be available for AI assistance")
    print("   - Check the MCP panel for tool execution logs")
    print()
    print("🔧 Troubleshooting:")
    print("   - Check VSCode Developer Console for MCP errors")
    print("   - Verify Python environment and dependencies")
    print("   - Ensure MCP server scripts are executable")
    print("   - Check file paths in mcp.json configuration")
    print()


def main():
    """Command-line interface for VSCode MCP setup."""
    parser = argparse.ArgumentParser(
        description="Set up MCP configuration for VSCode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Use default mcp.json in current directory
  %(prog)s --config custom.json         # Use custom configuration file
  %(prog)s --target-dir ~/.config/Code/User  # Specify VSCode config directory
  %(prog)s --no-merge                   # Overwrite existing configuration
  %(prog)s --dry-run                    # Show what would be done without making changes
        """
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        default="mcp.json",
        help="Path to MCP configuration file (default: mcp.json)"
    )
    
    parser.add_argument(
        "--target-dir",
        type=Path,
        help="VSCode configuration directory (auto-detected if not specified)"
    )
    
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="Overwrite existing configuration instead of merging"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
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
        format="%(levelname)s: %(message)s"
    )
    
    # Check if source configuration exists
    if not args.config.exists():
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    # Set up VSCode configuration
    success = setup_vscode_config(
        source_config=args.config,
        target_dir=args.target_dir,
        merge=not args.no_merge,
        dry_run=args.dry_run
    )
    
    if success and not args.dry_run:
        print_setup_instructions()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()