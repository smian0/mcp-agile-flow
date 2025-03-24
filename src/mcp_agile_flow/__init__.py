"""
MCP Agile Flow - A package for enhancing agile workflows with AI-assisted tools.

This package provides tools for managing project structure, documentation, and IDE integration
using the Model Context Protocol (MCP).

Primary tools:
- get-project-settings: Returns project settings including paths and configuration
- initialize-ide: Initialize a project with rules for a specific IDE
- initialize-ide-rules: Initialize a project with rules for a specific IDE (specialized)
- migrate-mcp-config: Migrate MCP configuration between different IDEs
- prime-context: Analyze project AI documentation to build context

The knowledge graph functionality has been migrated to a separate MCP server.
"""

import asyncio
import json
from typing import Dict, Any

from .version import __version__, get_version

# List of supported tools
SUPPORTED_TOOLS = [
    "initialize-ide",
    "initialize-ide-rules",
    "get-project-settings",
    "prime-context", 
    "migrate-mcp-config"
]

async def call_tool(name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Call an MCP tool with the specified name and arguments.
    
    Args:
        name: The name of the tool to call
        arguments: The arguments to pass to the tool
        
    Returns:
        The parsed JSON response as a dictionary
    """
    if arguments is None:
        arguments = {}
        
    # Check if the tool is supported
    if name not in SUPPORTED_TOOLS:
        return {
            "success": False,
            "error": f"Tool '{name}' is not supported. Supported tools: {', '.join(SUPPORTED_TOOLS)}"
        }
        
    # Call the appropriate function from fastmcp_tools
    try:
        # Import tools only when needed to avoid circular imports
        if name == "initialize-ide":
            from .fastmcp_tools import initialize_ide
            result = initialize_ide(**arguments)
        elif name == "initialize-ide-rules":
            from .fastmcp_tools import initialize_ide_rules
            result = initialize_ide_rules(**arguments)
        elif name == "get-project-settings":
            from .fastmcp_tools import get_project_settings
            result = get_project_settings(**arguments)
        elif name == "prime-context":
            from .fastmcp_tools import prime_context
            result = prime_context(**arguments)
        elif name == "migrate-mcp-config":
            from .fastmcp_tools import migrate_mcp_config
            result = migrate_mcp_config(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
        # Parse the JSON result
        return json.loads(result)
    except Exception as e:
        # Return an error response in the same format as the server would
        return {
            "success": False,
            "error": f"Error processing tool '{name}': {str(e)}"
        }

def call_tool_sync(name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Synchronous version of call_tool.
    
    This is a convenience function for code that can't use async/await.
    
    Args:
        name: The name of the tool to call
        arguments: The arguments to pass to the tool
        
    Returns:
        The parsed JSON response as a dictionary
    """
    try:
        # First, try to get the current event loop
        loop = asyncio.get_event_loop()
        
        # Check if the loop is already running
        if loop.is_running():
            # If we're in an existing event loop, create a new one for this call
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(call_tool(name, arguments))
            finally:
                loop.close()
        else:
            # If we have a loop but it's not running, use it
            return loop.run_until_complete(call_tool(name, arguments))
    except RuntimeError:
        # If we can't get an event loop, create a new one
        return asyncio.run(call_tool(name, arguments))

__all__ = ["__version__", "get_version", "call_tool", "call_tool_sync"]
