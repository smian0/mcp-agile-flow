#!/usr/bin/env python3
"""
Script to check if memory graph tools are registered with the MCP server.
"""

import sys
import os
import inspect
import pprint

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the MCP server and memory_graph module
from mcp_agile_flow.simple_server import mcp, handle_list_tools
from mcp_agile_flow.memory_graph import register_memory_tools
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
    
    # Check if the memory graph tools are registered
    print("\nChecking memory_graph.register_memory_tools function:")
    print(f"Function exists: {register_memory_tools is not None}")
    print(f"Function signature: {inspect.signature(register_memory_tools)}")
    
    # Get the actual tools
    print("\nTools registered with MCP server:")
    tools = await handle_list_tools()
    tool_names = [tool.name for tool in tools]
    print(f"Total tools: {len(tool_names)}")
    print("Tool names:")
    for name in tool_names:
        print(f"- {name}")
    
    # Check specifically for memory graph tools
    memory_tools = [
        "create_entities", "create_relations", "add_observations",
        "delete_entities", "delete_observations", "delete_relations",
        "read_graph", "search_nodes", "open_nodes"
    ]
    
    print("\nMemory graph tools check:")
    for tool in memory_tools:
        if tool in tool_names:
            print(f"✅ {tool} is registered")
        else:
            print(f"❌ {tool} is NOT registered")
    
    # Try manually registering the tools
    print("\nAttempting to manually register memory graph tools...")
    try:
        register_memory_tools(mcp)
        print("Manual registration completed without errors")
    except Exception as e:
        print(f"Error during manual registration: {e}")
    
    # Check again after manual registration
    print("\nTools after manual registration:")
    tools = await handle_list_tools()
    tool_names = [tool.name for tool in tools]
    print(f"Total tools: {len(tool_names)}")
    
    print("\nMemory graph tools check after manual registration:")
    for tool in memory_tools:
        if tool in tool_names:
            print(f"✅ {tool} is registered")
        else:
            print(f"❌ {tool} is NOT registered")
    
    # Check if we can create a new server and register tools with it
    print("\nTrying with a new MCP server instance:")
    new_mcp = Server("Test Server")
    
    # Register a simple list_tools handler
    @new_mcp.list_tools()
    async def test_list_tools():
        return []
    
    # Try to register memory tools with the new server
    print("Registering memory tools with new server...")
    try:
        register_memory_tools(new_mcp)
        print("Registration with new server completed without errors")
    except Exception as e:
        print(f"Error during registration with new server: {e}")
    
    # Check request handlers on new server
    print("\nNew MCP server request handlers:")
    new_request_handlers = getattr(new_mcp, "_request_handlers", {})
    print(f"New request handlers type: {type(new_request_handlers)}")
    for key, handler in new_request_handlers.items():
        print(f"- {key}: {handler.__name__}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
