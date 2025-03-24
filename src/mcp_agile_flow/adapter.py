"""
Adapter Module for MCP Agile Flow

This module provides a convenient interface to the FastMCP implementation.
It offers both synchronous and asynchronous ways to call MCP tools.

Usage:
    from mcp_agile_flow.adapter import call_tool
    
    # Call a tool asynchronously
    result = await call_tool("initialize-ide", {"project_path": "/path/to/project"})
    
    # Or synchronously:
    from mcp_agile_flow.adapter import call_tool_sync
    result = call_tool_sync("initialize-ide", {"project_path": "/path/to/project"})
"""

import asyncio
import json
from typing import Dict, Any

class MCPAdapter:
    """Adapter class that provides a consistent interface for calling tools."""
    
    # List of supported tools
    SUPPORTED_TOOLS = [
        "initialize-ide",
        "initialize-ide-rules",
        "get-project-settings",
        "prime-context", 
        "migrate-mcp-config",
        "get-safe-project-path"
    ]
    
    @staticmethod
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
        if name not in MCPAdapter.SUPPORTED_TOOLS:
            return {
                "success": False,
                "error": f"Tool '{name}' is not supported by this adapter. Supported tools: {', '.join(MCPAdapter.SUPPORTED_TOOLS)}"
            }
            
        # Use the FastMCP implementation
        try:
            # Convert tool name format (handle-tool-name to handle_tool_name)
            function_name = name.replace("-", "_")
            
            # Import the appropriate function from fastmcp_tools
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
            elif name == "get-safe-project-path":
                from .fastmcp_tools import get_safe_project_path
                result = get_safe_project_path(**arguments)
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

# Convenience function for calling tools
async def call_tool(name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Call an MCP tool with the specified name and arguments.
    
    This is a convenience function that delegates to MCPAdapter.call_tool.
    
    Args:
        name: The name of the tool to call
        arguments: The arguments to pass to the tool
        
    Returns:
        The parsed JSON response as a dictionary
    """
    return await MCPAdapter.call_tool(name, arguments)

# Synchronous version for convenience
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