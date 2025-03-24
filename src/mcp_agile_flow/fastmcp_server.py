"""
MCP Agile Flow - FastMCP Server Implementation

This module implements the MCP server with tools for agile workflow.
It uses the FastMCP API from the official MCP SDK.
"""

import logging
import os
import json

from mcp.server.fastmcp import FastMCP

# Import all FastMCP tool implementations
from mcp_agile_flow.fastmcp_tools import (
    get_project_settings,
    initialize_ide,
    prime_context,
    migrate_mcp_config,
    initialize_ide_rules,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create the FastMCP server instance
mcp = FastMCP("agile-flow")  # Must match the name in client configuration

# Register all action-oriented tools (operations that modify state)
mcp.tool(name="initialize-ide")(initialize_ide)
mcp.tool(name="initialize-ide-rules")(initialize_ide_rules)
mcp.tool(name="prime-context")(prime_context)
mcp.tool(name="migrate-mcp-config")(migrate_mcp_config)

# Register information retrieval tools (read-only operations)
mcp.tool(name="get-project-settings")(get_project_settings)

# Add resource-based API for data retrieval operations
# Project settings resources
@mcp.resource("settings://project")
def project_settings_resource() -> dict:
    """
    Resource representing the project settings.
    
    Returns the comprehensive project settings including project path, 
    AI docs directory, project type, metadata, and other configuration.
    
    Returns:
        Dict containing the project settings
    """
    logger.info("Resource access: settings://project")
    
    # Call the existing implementation but parse the JSON into a dict
    settings_json = get_project_settings()
    return json.loads(settings_json)

@mcp.resource("settings://project/{path}")
def project_settings_with_path(path: str) -> dict:
    """
    Resource representing the project settings for a specific path.
    
    Returns the comprehensive project settings for the specified path.
    
    Args:
        path: The project path to use
        
    Returns:
        Dict containing the project settings
    """
    logger.info(f"Resource access: settings://project/{path}")
    
    # Call the existing implementation but parse the JSON into a dict
    settings_json = get_project_settings(proposed_path=path)
    return json.loads(settings_json)

def run():
    """Entry point for running the server."""
    logger.info("Starting MCP Agile Flow server (FastMCP mode)")
    print("Starting MCP Agile Flow server...", file=os.sys.stderr)
    
    # Debug: Print registered resources
    resources = []
    for attr_name in dir(mcp):
        if attr_name.startswith('_') and 'resource' in attr_name.lower():
            resource_attr = getattr(mcp, attr_name, None)
            if isinstance(resource_attr, dict):
                resources = list(resource_attr.keys())
                break
    
    print(f"Registered resources: {resources}", file=os.sys.stderr)
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    # Configure logging when run directly
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    run() 