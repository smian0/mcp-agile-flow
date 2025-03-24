"""
Test Adapter Module for MCP Agile Flow

This module provides an adapter interface that allows tests to run against 
either the legacy server implementation or the new FastMCP implementation.
The goal is to make it easy to migrate tests incrementally.
"""

import asyncio
import json
import os
from typing import Dict, Any, Union

# Set this environment variable to determine which implementation to use
USE_FASTMCP = os.environ.get("MCP_USE_FASTMCP", "false").lower() in ("true", "1", "yes")

class MCPToolAdapter:
    """Adapter class that provides a consistent interface for calling tools."""
    
    # List of supported tools (tools implemented in both server and FastMCP)
    SUPPORTED_TOOLS = [
        "initialize-ide",
        "initialize-ide-rules",
        "get-project-settings",
        "prime-context", 
        "migrate-mcp-config"
    ]
    
    @staticmethod
    async def call_tool(name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call an MCP tool with the specified name and arguments.
        
        This method will use either the FastMCP implementation or the server implementation
        based on the USE_FASTMCP environment variable.
        
        Args:
            name: The name of the tool to call
            arguments: The arguments to pass to the tool
            
        Returns:
            The parsed JSON response as a dictionary
        """
        if arguments is None:
            arguments = {}
            
        # Check if the tool is supported
        if name not in MCPToolAdapter.SUPPORTED_TOOLS:
            return {
                "success": False,
                "error": f"Tool '{name}' is not supported by this adapter. Supported tools: {', '.join(MCPToolAdapter.SUPPORTED_TOOLS)}"
            }
            
        if USE_FASTMCP:
            # Use the FastMCP implementation directly
            return await MCPToolAdapter._call_fastmcp_tool(name, arguments)
        else:
            # Use the server implementation
            return await MCPToolAdapter._call_server_tool(name, arguments)
    
    @staticmethod
    async def _call_fastmcp_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool using the FastMCP implementation directly."""
        # Import the function dynamically to avoid circular imports
        try:
            # Convert tool name format (handle-tool-name to handle_tool_name)
            function_name = name.replace("-", "_")
            
            # Import the appropriate function from fastmcp_tools
            if name == "initialize-ide":
                from mcp_agile_flow.fastmcp_tools import initialize_ide
                result = initialize_ide(**arguments)
            elif name == "initialize-ide-rules":
                from mcp_agile_flow.fastmcp_tools import initialize_ide_rules
                result = initialize_ide_rules(**arguments)
            elif name == "get-project-settings":
                from mcp_agile_flow.fastmcp_tools import get_project_settings
                result = get_project_settings(**arguments)
            elif name == "prime-context":
                from mcp_agile_flow.fastmcp_tools import prime_context
                result = prime_context(**arguments)
            elif name == "migrate-mcp-config":
                from mcp_agile_flow.fastmcp_tools import migrate_mcp_config
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
    
    @staticmethod
    async def _call_server_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool using the server implementation."""
        from src.mcp_agile_flow.server import handle_call_tool
        
        # Call the tool through the server's handle_call_tool function
        result = await handle_call_tool(name, arguments)
        
        # Parse the response
        if result and len(result) > 0:
            return json.loads(result[0].text)
        else:
            return {
                "success": False,
                "error": f"No response from tool '{name}'"
            }

# Convenience function for calling tools
async def call_tool(name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Call an MCP tool with the specified name and arguments.
    
    This is a convenience function that delegates to MCPToolAdapter.call_tool.
    
    Args:
        name: The name of the tool to call
        arguments: The arguments to pass to the tool
        
    Returns:
        The parsed JSON response as a dictionary
    """
    return await MCPToolAdapter.call_tool(name, arguments) 