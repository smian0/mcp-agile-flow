"""
Tests for the production adapter.

This file tests the adapter.py file which provides a convenient interface
to the FastMCP functionality.
"""

import asyncio
import pytest
from pathlib import Path

@pytest.mark.asyncio
async def test_adapter_functionality():
    """Test that the adapter can call tools successfully."""
    # Import the adapter
    from src.mcp_agile_flow.adapter import call_tool
    
    # Call a simple tool
    result = await call_tool("get-project-settings", {})
    
    # Check that the result has the expected structure
    assert "project_path" in result
    assert "current_directory" in result
    assert Path(result["project_path"]).exists()

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