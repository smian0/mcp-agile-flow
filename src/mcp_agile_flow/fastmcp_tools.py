"""
FastMCP Tools for MCP Agile Flow

This module implements MCP Agile Flow tools using FastMCP for a more Pythonic interface.
These implementations coexist with the traditional MCP tools while we migrate.
"""

import json
import logging
import os
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP
from .utils import get_project_settings as get_settings_util

# Set up logging
logger = logging.getLogger(__name__)

# Create a FastMCP instance
fastmcp = FastMCP("agile-flow-fast")


@fastmcp.tool()
def get_project_settings(proposed_path: Optional[str] = None) -> str:
    """
    Returns comprehensive project settings including project path, knowledge graph directory, 
    AI docs directory, project type, metadata, and other configuration.
    
    Also validates the path to ensure it's safe and writable. If the root directory or a 
    non-writable path is detected, it will automatically use a safe alternative path.
    
    Args:
        proposed_path: Optional path to check. If not provided, standard environment 
                      variables or default paths will be used.
    
    Returns:
        JSON string containing the project settings
    """
    logger.info("FastMCP: Getting project settings")
    
    # Use the utility function to get project settings
    response_data = get_settings_util(
        proposed_path=proposed_path if proposed_path else None
    )
    
    # Add default project type and metadata
    # In a real implementation, we would get these from memory_manager if available
    response_data["project_type"] = "generic"
    response_data["project_metadata"] = {}
    
    # Log the response for debugging
    logger.info(f"FastMCP: Project settings response: {response_data}")
    
    # Return as a JSON string to match the expected return type
    return json.dumps(response_data, indent=2)


@fastmcp.tool()
def get_mermaid_diagram() -> str:
    """
    Get a Mermaid diagram representation of the knowledge graph.
    
    Returns:
        JSON string containing a Mermaid diagram representation
    """
    logger.info("FastMCP: Getting Mermaid diagram representation of knowledge graph")
    
    try:
        # This is a placeholder implementation
        # In a real implementation, you would:
        # 1. Import the necessary function to generate the diagram
        # 2. Call that function to get the diagram data
        # 3. Format and return it as JSON
        
        # Placeholder response
        response_data = {
            "success": True,
            "diagram_type": "mermaid",
            "content": "graph TD;\nA[Knowledge Graph] --> B[No nodes available];"
        }
        
        # Return as a JSON string to match the expected return type
        return json.dumps(response_data, indent=2)
    except Exception as e:
        logger.error(f"FastMCP: Error getting Mermaid diagram: {str(e)}")
        
        # Return error as JSON
        response_data = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(response_data, indent=2) 