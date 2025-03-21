"""
MCP Configuration Migration Tool

Provides functionality to migrate MCP configurations between different IDEs,
with smart merging and conflict resolution capabilities.
"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple, List

# Define IDE configuration paths
IDE_PATHS = {
    "cursor": {
        "darwin": "~/.cursor/mcp.json",
        "linux": "~/.cursor/mcp.json",
        "windows": "%APPDATA%\\Cursor\\mcp.json"
    },
    "windsurf-next": {
        "darwin": "~/.codeium/windsurf-next/mcp_config.json",
        "linux": "~/.codeium/windsurf-next/mcp_config.json",
        "windows": "%APPDATA%\\Codeium\\windsurf-next\\mcp_config.json"
    },
    "windsurf": {
        "darwin": "~/.codeium/windsurf/mcp_config.json",
        "linux": "~/.codeium/windsurf/mcp_config.json",
        "windows": "%APPDATA%\\Codeium\\windsurf\\mcp_config.json"
    },
    "cline": {
        "darwin": "~/Library/Application Support/Code - Insiders/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json",
        "linux": "~/.config/Code - Insiders/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json",
        "windows": "%APPDATA%\\Code - Insiders\\User\\globalStorage\\saoudrizwan.claude-dev\\settings\\cline_mcp_settings.json"
    },
    "roo": {
        "darwin": "~/Library/Application Support/Code - Insiders/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json",
        "linux": "~/.config/Code - Insiders/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json",
        "windows": "%APPDATA%\\Code - Insiders\\User\\globalStorage\\rooveterinaryinc.roo-cline\\settings\\cline_mcp_settings.json"
    }
}

def get_ide_path(ide: str) -> str:
    """Get the configuration path for an IDE on the current platform."""
    platform = "darwin" if os.name == "posix" and os.uname().sysname == "Darwin" else \
              "linux" if os.name == "posix" else \
              "windows"
    
    # Check for environment variable override
    env_var = f"MCP_{ide.upper().replace('-', '_')}_PATH"
    if env_var in os.environ:
        return os.path.expanduser(os.environ[env_var])
    
    # Get default path for platform
    if ide not in IDE_PATHS:
        raise ValueError(f"Unknown IDE: {ide}")
    
    path = IDE_PATHS[ide][platform]
    
    # Expand environment variables and user home
    if platform == "windows":
        path = os.path.expandvars(path)
    return os.path.expanduser(path)

def create_backup(file_path: str) -> Optional[str]:
    """Create a backup of a file if it exists."""
    if not os.path.exists(file_path):
        return None
    
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    return backup_path

def detect_conflicts(source_config: Dict, target_config: Dict) -> List[str]:
    """Detect conflicts between source and target configurations."""
    conflicts = []
    
    if "mcpServers" in source_config and "mcpServers" in target_config:
        source_servers = source_config["mcpServers"]
        target_servers = target_config["mcpServers"]
        
        # Check each server in source config
        for server_name, server_config in source_servers.items():
            if server_name in target_servers:
                # Server exists in both configs, check if they're different
                if server_config != target_servers[server_name]:
                    conflicts.append(server_name)
    
    return conflicts

def get_conflict_details(source_config: Dict, target_config: Dict, conflicts: List[str]) -> Dict:
    """
    Generate detailed information about each conflict.
    
    Args:
        source_config: Source configuration dictionary
        target_config: Target configuration dictionary
        conflicts: List of conflicting server names
    
    Returns:
        Dictionary mapping server names to their source and target configurations
    """
    conflict_details = {}
    
    if "mcpServers" in source_config and "mcpServers" in target_config:
        source_servers = source_config["mcpServers"]
        target_servers = target_config["mcpServers"]
        
        for server_name in conflicts:
            conflict_details[server_name] = {
                "source": source_servers.get(server_name, {}),
                "target": target_servers.get(server_name, {})
            }
    
    return conflict_details

def merge_configurations(source_config: Dict, target_config: Dict, conflict_resolutions: Dict[str, bool]) -> Dict:
    """
    Merge source configuration into target configuration.
    
    Args:
        source_config: Source configuration dictionary
        target_config: Target configuration dictionary
        conflict_resolutions: Dictionary of server names and whether to overwrite them
                            (True = use source, False = keep target)
    
    Returns:
        Merged configuration dictionary
    """
    # Start with the target config
    merged = target_config.copy()
    
    # If target doesn't have mcpServers, initialize it
    if "mcpServers" not in merged:
        merged["mcpServers"] = {}
    
    # If source has mcpServers, merge them
    if "mcpServers" in source_config:
        for server_name, server_config in source_config["mcpServers"].items():
            # If server exists in target and we have a conflict resolution
            if server_name in merged["mcpServers"] and server_name in conflict_resolutions:
                if conflict_resolutions[server_name]:
                    # Use source configuration
                    merged["mcpServers"][server_name] = server_config
                # If False, keep target configuration
            else:
                # No conflict or not in target, add from source
                merged["mcpServers"][server_name] = server_config
    
    return merged

def migrate_config(from_ide: str, to_ide: str, backup: bool = True) -> Tuple[bool, Optional[str], List[str], Dict]:
    """
    Migrate MCP configuration from one IDE to another.
    
    Args:
        from_ide: Source IDE name
        to_ide: Target IDE name
        backup: Whether to create backups before modifying files
    
    Returns:
        Tuple of (success, error_message, conflicts, conflict_details)
        - success: Whether the operation completed (may be True even with conflicts)
        - error_message: Error message if operation failed
        - conflicts: List of conflicting server names
        - conflict_details: Dictionary of detailed conflict information
    """
    try:
        # Get paths
        source_path = get_ide_path(from_ide)
        target_path = get_ide_path(to_ide)
        
        # Check if source exists
        if not os.path.exists(source_path):
            return False, f"Source configuration not found at {source_path}", [], {}
        
        # Read source configuration
        try:
            with open(source_path, 'r') as f:
                source_config = json.load(f)
        except json.JSONDecodeError:
            return False, f"Invalid JSON in source configuration at {source_path}", [], {}
        
        # Read target configuration if it exists
        target_config = {}
        if os.path.exists(target_path):
            try:
                with open(target_path, 'r') as f:
                    target_config = json.load(f)
            except json.JSONDecodeError:
                return False, f"Invalid JSON in target configuration at {target_path}", [], {}
        
        # Detect conflicts
        conflicts = detect_conflicts(source_config, target_config)
        
        # Generate conflict details if there are conflicts
        conflict_details = {}
        if conflicts:
            conflict_details = get_conflict_details(source_config, target_config, conflicts)
        
        # Create backup of target if it exists and backup is requested
        if backup and os.path.exists(target_path):
            backup_path = create_backup(target_path)
            if not backup_path:
                return False, f"Failed to create backup of {target_path}", [], {}
        
        # Return if we found conflicts - user needs to resolve them
        if conflicts:
            return True, None, conflicts, conflict_details
        
        # No conflicts, perform basic merge
        merged_config = merge_configurations(source_config, target_config, {})
        
        # Create target directory if it doesn't exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Write merged configuration
        with open(target_path, 'w') as f:
            json.dump(merged_config, f, indent=2)
        
        return True, None, [], {}
        
    except Exception as e:
        return False, str(e), [], {}
