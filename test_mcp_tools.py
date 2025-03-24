#!/usr/bin/env python3
"""
Test script for MCP tools using the MCP client.
"""
import asyncio
import json
from src.mcp_agile_flow import call_tool, call_tool_sync

async def test_tools_async():
    """Test the tools using the async interface."""
    print("Testing tools using async interface...")
    
    # Clear any existing thoughts
    clear_result = await call_tool("clear-thoughts")
    print("Clear thoughts result:", json.dumps(clear_result, indent=2))
    
    # Add a thought
    think_result = await call_tool("think", {"thought": "This is a test thought from async."})
    print("Think result:", json.dumps(think_result, indent=2))
    
    # Get thoughts
    get_result = await call_tool("get-thoughts")
    print("Get thoughts result:", json.dumps(get_result, indent=2))
    
    # Try with underscore version
    get_result_underscore = await call_tool("get_thoughts")
    print("Get thoughts result (underscore):", json.dumps(get_result_underscore, indent=2))
    
    # Get stats
    stats_result = await call_tool("get-thought-stats")
    print("Get stats result:", json.dumps(stats_result, indent=2))

def test_tools_sync():
    """Test the tools using the sync interface."""
    print("\nTesting tools using sync interface...")
    
    # Clear any existing thoughts
    clear_result = call_tool_sync("clear-thoughts")
    print("Clear thoughts result:", json.dumps(clear_result, indent=2))
    
    # Add a thought
    think_result = call_tool_sync("think", {"thought": "This is a test thought from sync."})
    print("Think result:", json.dumps(think_result, indent=2))
    
    # Get thoughts
    get_result = call_tool_sync("get-thoughts")
    print("Get thoughts result:", json.dumps(get_result, indent=2))
    
    # Try with underscore version
    get_result_underscore = call_tool_sync("get_thoughts")
    print("Get thoughts result (underscore):", json.dumps(get_result_underscore, indent=2))
    
    # Get stats
    stats_result = call_tool_sync("get-thought-stats")
    print("Get stats result:", json.dumps(stats_result, indent=2))

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_tools_async())
    
    # Run the sync test
    test_tools_sync() 