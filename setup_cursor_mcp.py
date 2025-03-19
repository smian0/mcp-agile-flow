#!/usr/bin/env python
"""
Setup script for Cursor MCP configuration.

This script helps users set up the MCP Agile Flow server with the Cursor IDE.
It creates or updates the ~/.cursor/mcp.json file with the correct configuration.
"""
import os
import sys
import json
from pathlib import Path
import shutil

def main():
    """Set up the Cursor MCP configuration."""
    # Get the project root directory
    project_root = Path(__file__).resolve().parent
    
    # Get the Python interpreter path
    python_path = sys.executable
    
    # Ensure it's using the virtualenv if available
    venv_path = project_root / ".venv" / "bin" / "python"
    if venv_path.exists():
        python_path = str(venv_path)
    
    # Create the MCP configuration
    mcp_config = {
        "mcp-agile-flow": {
            "command": python_path,
            "args": [
                str(project_root / "run_mcp_server.py")
            ],
            "autoApprove": [
                "hello-world",
                "add-note",
                "get-project-path"
            ],
            "disabled": False
        },
        "mcp-agile-flow-simple": {
            "command": python_path,
            "args": [
                str(project_root / "simple_server.py")
            ],
            "autoApprove": [
                "hello-world",
                "add-note",
                "get-project-path",
                "Hey Sho",
                "debug-tools"
            ],
            "disabled": False
        }
    }
    
    # Get the cursor config directory
    cursor_dir = Path.home() / ".cursor"
    if not cursor_dir.exists():
        cursor_dir.mkdir(parents=True)
    
    # Get the MCP config file
    mcp_file = cursor_dir / "mcp.json"
    
    # Load existing config if any
    existing_config = {}
    if mcp_file.exists():
        try:
            with open(mcp_file, "r") as f:
                existing_config = json.load(f)
            
            # Back up the existing file
            backup_file = mcp_file.with_suffix(".json.bak")
            shutil.copy2(mcp_file, backup_file)
            print(f"Backed up existing config to {backup_file}")
        except Exception as e:
            print(f"Error reading existing config: {e}")
            print("Creating a new configuration file")
    
    # Update the config with our new servers
    if existing_config:
        existing_config.update(mcp_config)
    else:
        existing_config = mcp_config
    
    # Write the updated config
    with open(mcp_file, "w") as f:
        json.dump(existing_config, f, indent=2)
    
    print(f"Updated Cursor MCP configuration at {mcp_file}")
    print(f"MCP servers registered: mcp-agile-flow, mcp-agile-flow-simple")
    print("\nYou can now use these MCP servers in Cursor.\n")
    print("For standard MCP server:")
    print("  - Command will run: " + python_path)
    print("  - Arguments: " + str(project_root / "run_mcp_server.py"))
    print("\nFor Simple server with 'Hey Sho' tool:")
    print("  - Command will run: " + python_path)
    print("  - Arguments: " + str(project_root / "simple_server.py"))
    print("\nTest the Simple server with these MCP tool calls:")
    print('  {"name": "Hey Sho", "arguments": {"message": "Hey Sho, get project path"}}')
    print('  {"name": "debug-tools", "arguments": {}}')

if __name__ == "__main__":
    main() 