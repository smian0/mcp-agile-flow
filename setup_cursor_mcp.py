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
    # Using module-based approach for better reliability
    mcp_server_config = {
        "mcp-agile-flow": {
            "command": python_path,
            "args": [
                "-m",
                "mcp_agile_flow.server"
            ],
            "autoApprove": [
                "initialize-ide-rules",
                "get-project-path",
                "get-project-settings",
                "create_entities",
                "create_relations",
                "read_graph",
                "debug-tools",
                "get_mermaid_diagram",
                "add_observations",
                "delete_entities",
                "get-safe-project-path",
                "initialize-ide"
            ],
            "disabled": False,
            "timeout": 30
        }
    }
    
    # Get the cursor config directory
    cursor_dir = Path.home() / ".cursor"
    if not cursor_dir.exists():
        cursor_dir.mkdir(parents=True)
    
    # Get the MCP config file
    mcp_file = cursor_dir / "mcp.json"
    
    # Load existing config if any
    existing_config = {"mcpServers": {}}
    if mcp_file.exists():
        try:
            with open(mcp_file, "r") as f:
                existing_config = json.load(f)
            
            # Ensure mcpServers key exists
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}
                
            # Back up the existing file
            backup_file = mcp_file.with_suffix(".json.bak")
            shutil.copy2(mcp_file, backup_file)
            print(f"Backed up existing config to {backup_file}")
        except Exception as e:
            print(f"Error reading existing config: {e}")
            print("Creating a new configuration file")
            existing_config = {"mcpServers": {}}
    
    # Update the config with our new servers
    existing_config["mcpServers"].update(mcp_server_config)
    
    # Write the updated config
    with open(mcp_file, "w") as f:
        json.dump(existing_config, f, indent=2)
    
    print(f"Updated Cursor MCP configuration at {mcp_file}")
    print(f"MCP server registered: mcp-agile-flow")
    print("\nYou can now use the MCP server in Cursor.\n")
    print("For MCP Agile Flow server:")
    print("  - Command will run: " + python_path)
    print("  - Arguments: -m mcp_agile_flow.server")
    print("\nTest the server with these MCP tool calls:")
    print('  {"name": "get-project-settings", "arguments": {}}')
    print('  {"name": "initialize-ide", "arguments": {"ide": "cursor"}}')
    
    # Create a shell script for running the server directly for testing
    test_script = project_root / "test_mcp_server.sh"
    with open(test_script, "w") as f:
        f.write(f"""#!/bin/bash
# Script to test the MCP server directly
echo "Testing MCP Agile Flow server..."
{python_path} -m mcp_agile_flow.server
""")
    
    # Make the script executable
    os.chmod(test_script, 0o755)
    print(f"\nCreated test script at {test_script}")
    print("You can run this script to test the MCP server directly.")

if __name__ == "__main__":
    main() 