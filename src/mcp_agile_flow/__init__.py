"""
MCP Agile Flow - A package for enhancing agile workflows with AI-assisted tools.

This package provides tools for managing project structure, documentation, and IDE integration
using the Model Context Protocol (MCP).

Primary tools:
- get_project_settings: Returns project settings including paths and configuration
- initialize_ide: Initialize a project with rules for a specific IDE
- initialize_ide_rules: Initialize a project with rules for a specific IDE (specialized)
- migrate_mcp_config: Migrate MCP configuration between different IDEs
- prime_context: Analyze project AI documentation to build context

The knowledge graph functionality has been migrated to a separate MCP server.
"""

import asyncio
import json
from typing import Dict, Any

from .version import __version__, get_version
from .utils import detect_mcp_command

# List of supported tools
SUPPORTED_TOOLS = [
    "initialize_ide",
    "initialize_ide_rules",
    "get_project_settings",
    "prime_context",
    "migrate_mcp_config",
    "think",
    "get_thoughts",
    "clear_thoughts",
    "get_thought_stats",
    "process_natural_language",
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
            "error": f"Tool '{name}' is not supported. Supported tools: {', '.join(SUPPORTED_TOOLS)}",
        }

    # Map between underscore and hyphen formats if needed
    tool_name_mapping = {
        "get_project_settings": "get-project-settings",
        "initialize_ide": "initialize-ide",
        "initialize_ide_rules": "initialize-ide-rules",
        "prime_context": "prime-context",
        "migrate_mcp_config": "migrate-mcp-config",
        "think": "think",
        "get_thoughts": "get-thoughts",
        "clear_thoughts": "clear-thoughts",
        "get_thought_stats": "get-thought-stats",
    }

    # Convert to hyphen format for FastMCP tools
    fastmcp_tool_name = tool_name_mapping.get(name, name)

    # Call the appropriate function from fastmcp_tools
    try:
        # Import tools only when needed to avoid circular imports
        from .fastmcp_tools import (
            get_project_settings,
            initialize_ide,
            initialize_ide_rules,
            prime_context,
            migrate_mcp_config,
            think,
            get_thoughts,
            clear_thoughts,
            get_thought_stats,
        )

        # Call the appropriate function based on the tool name
        if fastmcp_tool_name == "get-project-settings":
            result = get_project_settings(**arguments)
        elif fastmcp_tool_name == "initialize-ide":
            result = initialize_ide(**arguments)
        elif fastmcp_tool_name == "initialize-ide-rules":
            result = initialize_ide_rules(**arguments)
        elif fastmcp_tool_name == "prime-context":
            result = prime_context(**arguments)
        elif fastmcp_tool_name == "migrate-mcp-config":
            result = migrate_mcp_config(**arguments)
        elif fastmcp_tool_name == "think":
            result = think(**arguments)
        elif fastmcp_tool_name == "get-thoughts":
            result = get_thoughts()
        elif fastmcp_tool_name == "clear-thoughts":
            result = clear_thoughts()
        elif fastmcp_tool_name == "get-thought-stats":
            result = get_thought_stats()
        else:
            raise ValueError(f"Unknown tool: {name}")

        if asyncio.iscoroutine(result):
            result = await result

        # Handle different response types
        if isinstance(result, dict):
            # Already a dict, return as-is
            return result
        elif isinstance(result, str):
            # Try to parse JSON string
            try:
                return json.loads(result)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Invalid JSON response from tool: {str(e)}",
                    "message": "The tool returned malformed JSON",
                }
        else:
            # Unknown response type
            return {
                "success": False,
                "error": f"Unexpected response type from tool: {type(result)}",
                "message": "The tool returned an unexpected response format",
            }
    except Exception as e:
        # Return an error response in the same format as the server would
        return {"success": False, "error": f"Error processing tool '{name}': {str(e)}"}


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
    # Try to get the current running loop
    try:
        loop = asyncio.get_running_loop()
        # If we reached here, there is a running loop

        # Create a new loop for this call to avoid interfering with the running one
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(call_tool(name, arguments))
        finally:
            new_loop.close()
    except RuntimeError:
        # No running event loop
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(call_tool(name, arguments))
        finally:
            loop.close()


def process_natural_language(query: str) -> Dict[str, Any]:
    """
    Process natural language queries and map them to appropriate MCP tools.

    This function detects commands in natural language text and calls the
    appropriate MCP tool based on the detected intent.

    Args:
        query: The natural language query to process

    Returns:
        The response from the tool, or an error message if no command was detected
    """
    # Detect the command from the natural language query
    tool_name, arguments = detect_mcp_command(query)

    # If a command was detected, call the tool
    if tool_name:
        return call_tool_sync(tool_name, arguments)

    # No command was detected
    return {
        "success": False,
        "error": "No MCP command was detected in the query",
        "message": "Try using a more specific command or check the documentation for supported commands",
    }


__all__ = ["__version__", "get_version", "call_tool", "call_tool_sync", "process_natural_language"]
