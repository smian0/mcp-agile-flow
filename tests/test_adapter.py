"""
Tests for the production adapter.

This file tests the adapter.py file which provides a compatibility layer
for clients migrating from the legacy server to FastMCP.
"""

import asyncio
import os
import pytest
from pathlib import Path

@pytest.mark.asyncio
async def test_adapter_defaults_to_fastmcp():
    """Test that the adapter defaults to FastMCP implementation."""
    # Import the adapter
    from src.mcp_agile_flow.adapter import call_tool, USE_LEGACY
    
    # Verify it defaults to FastMCP
    assert USE_LEGACY is False

@pytest.mark.asyncio
async def test_adapter_basic_functionality():
    """Test that the adapter can call tools successfully."""
    # Import the adapter
    from src.mcp_agile_flow.adapter import call_tool
    
    # Call a simple tool
    result = await call_tool("get-project-settings", {})
    
    # Check that the result has the expected structure
    assert "project_path" in result
    assert "current_directory" in result
    assert Path(result["project_path"]).exists()

# Needs to be a regular function, not async, to properly test the sync version
def test_adapter_sync_version():
    """Test the synchronous version of the adapter."""
    # Import the adapter
    from src.mcp_agile_flow.adapter import call_tool_sync
    
    # Call a simple tool
    result = call_tool_sync("get-project-settings", {})
    
    # Check that the result has the expected structure
    assert "project_path" in result
    assert "current_directory" in result
    assert Path(result["project_path"]).exists()

@pytest.mark.asyncio
async def test_adapter_with_both_implementations():
    """Test the adapter with both implementations."""
    # Save the current environment variable
    original_value = os.environ.get("MCP_USE_LEGACY")
    
    try:
        # Set the environment variable to use FastMCP
        os.environ["MCP_USE_LEGACY"] = "false"
        
        # Import the adapter (this will reset the USE_LEGACY flag)
        import importlib
        import src.mcp_agile_flow.adapter
        importlib.reload(src.mcp_agile_flow.adapter)
        
        # Call a tool with FastMCP
        result_fastmcp = await src.mcp_agile_flow.adapter.call_tool("get-project-settings", {})
        
        # Set the environment variable to use legacy implementation
        os.environ["MCP_USE_LEGACY"] = "true"
        
        # Reload the adapter
        importlib.reload(src.mcp_agile_flow.adapter)
        
        # Call a tool with legacy implementation
        result_legacy = await src.mcp_agile_flow.adapter.call_tool("get-project-settings", {})
        
        # Both should have the same structure
        assert "project_path" in result_fastmcp
        assert "project_path" in result_legacy
        
    finally:
        # Restore the original environment variable
        if original_value is not None:
            os.environ["MCP_USE_LEGACY"] = original_value
        else:
            os.environ.pop("MCP_USE_LEGACY", None)
        
        # Reload the adapter again to restore its original state
        importlib.reload(src.mcp_agile_flow.adapter) 