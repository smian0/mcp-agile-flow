#!/usr/bin/env python
import sys
import json
import inspect
from typing import Dict, Any, List
import typing
import re

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("FastMCP not installed. Please install it with 'pip install mcp'.")
    sys.exit(1)

try:
    from mcp_agile_flow.fastmcp_tools import mcp
    # Import the actual functions to inspect them
    from mcp_agile_flow.fastmcp_tools import (
        get_project_settings,
        initialize_ide,
        initialize_ide_rules,
        prime_context,
        migrate_mcp_config,
        think,
        get_thoughts,
        clear_thoughts,
        get_thought_stats,
        process_natural_language
    )
except ImportError:
    print("mcp_agile_flow not installed. Please make sure it's installed.")
    sys.exit(1)

# Map of function names to their actual function objects
FUNCTION_MAP = {
    "get-project-settings": get_project_settings,
    "initialize-ide": initialize_ide,
    "initialize-ide-rules": initialize_ide_rules,
    "prime-context": prime_context,
    "migrate-mcp-config": migrate_mcp_config,
    "think": think,
    "get-thoughts": get_thoughts, 
    "clear-thoughts": clear_thoughts,
    "get-thought-stats": get_thought_stats,
    "process_natural_language": process_natural_language
}

def extract_annotation_description(annotation):
    """Extract description from an Annotated type."""
    # The string representation contains the description directly
    str_annotation = str(annotation)
    
    # Extract the description from the string representation using regex
    match = re.search(r"'(.*?)'", str_annotation)
    if match:
        return match.group(1)
    
    return "No description available"

def get_parameter_info(func) -> List[Dict[str, Any]]:
    """Get parameter information for a function."""
    params = []
    sig = inspect.signature(func)
    
    for name, param in sig.parameters.items():
        # Get annotations if available
        annotation = param.annotation
        description = extract_annotation_description(annotation)
        
        param_info = {
            "name": name,
            "type": str(annotation),
            "description": description,
            "default": str(param.default) if param.default is not param.empty else None
        }
        params.append(param_info)
    
    return params

def get_tool_details(tool_name: str) -> Dict[str, Any]:
    """Get details about a specific tool."""
    if tool_name not in FUNCTION_MAP:
        return {"error": f"Tool {tool_name} not found"}
    
    func = FUNCTION_MAP[tool_name]
    params = get_parameter_info(func)
    
    return {
        "name": tool_name,
        "description": func.__doc__ or "No description available",
        "parameters": params
    }

def list_all_tools() -> List[Dict[str, Any]]:
    """List all available tools and their parameters."""
    result = []
    
    for tool_name in FUNCTION_MAP.keys():
        tool_info = get_tool_details(tool_name)
        result.append(tool_info)
    
    return result

if __name__ == "__main__":
    # If a tool name is provided, show details for that tool
    if len(sys.argv) > 1:
        tool_name = sys.argv[1]
        details = get_tool_details(tool_name)
        print(json.dumps(details, indent=2))
    else:
        # Otherwise, list all tools
        all_tools = list_all_tools()
        print(json.dumps(all_tools, indent=2)) 