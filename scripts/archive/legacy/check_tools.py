#!/usr/bin/env python3
"""
Script to check tools registered with the MCP server.
"""

import sys
import os
import inspect
import pprint

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the MCP server module
from mcp_agile_flow.server import mcp, handle_list_tools
from mcp.server import Server

async def main():
    """Check the tools registered with the MCP server."""
    # Debug MCP server object
    print("MCP server object type:", type(mcp))
    print("MCP server attributes:")
    for attr in dir(mcp):
        if not attr.startswith('_'):
            print(f"- {attr}")
    
    # Check request handlers
    print("\nMCP server request handlers:")
    request_handlers = getattr(mcp, "_request_handlers", {})
    print(f"Request handlers type: {type(request_handlers)}")
    print(f"Request handlers content: {request_handlers}")
    
    # Check decorators
    print("\nMCP server decorators:")
    print(f"Has list_tools decorator: {hasattr(mcp, 'list_tools')}")
    print(f"Has call_tool decorator: {hasattr(mcp, 'call_tool')}")
    
    # Get the actual tools
    print("\nTools registered with MCP server:")
    tools = await handle_list_tools()
    tool_names = [tool.name for tool in tools]
    print(f"Total tools: {len(tool_names)}")
    print("Tool names:")
    for name in tool_names:
        print(f"- {name}")
    
    # Check specifically for FastMCP tools
    fastmcp_tools = [
        "get-project-settings", "get-mermaid-diagram", "read-graph",
        "initialize-ide", "initialize-ide-rules", "prime-context",
        "migrate-mcp-config", "create-entities", "create-relations",
        "add-observations", "delete-entities", "delete-observations",
        "delete-relations", "search-nodes", "open-nodes"
    ]
    
    print("\nFastMCP tools check:")
    for tool in fastmcp_tools:
        if tool in tool_names:
            print(f"✅ {tool} is registered")
        else:
            print(f"❌ {tool} is NOT registered")
    
    # Check if we can create a new server
    print("\nTrying with a new MCP server instance:")
    new_mcp = Server("Test Server")
    
    # Register a simple list_tools handler
    @new_mcp.list_tools()
    async def test_list_tools():
        return []
    
    # Check request handlers on new server
    print("\nNew MCP server request handlers:")
    new_request_handlers = getattr(new_mcp, "_request_handlers", {})
    print(f"New request handlers type: {type(new_request_handlers)}")
    for key, handler in new_request_handlers.items():
        print(f"- {key}: {handler.__name__}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
