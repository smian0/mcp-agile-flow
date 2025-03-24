"""
Tests for the MCP Agile Flow Tool API
"""
import json
import pytest
from unittest import mock

from src.mcp_agile_flow import call_tool, call_tool_sync, SUPPORTED_TOOLS


@pytest.mark.asyncio
async def test_call_tool_for_supported_tool():
    """Test that calling a supported tool works correctly."""
    tool_name = "get-project-settings"
    
    # Mock the get_project_settings function to avoid real implementation
    mock_result = {"success": True, "data": {"project_path": "/test/path"}}
    
    with mock.patch('src.mcp_agile_flow.fastmcp_tools.get_project_settings', 
                   return_value=json.dumps(mock_result)):
        result = await call_tool(tool_name)
    
    assert isinstance(result, dict)
    assert result["success"] is True


def test_call_tool_sync():
    """Test that the synchronous version works correctly."""
    tool_name = "get-project-settings"
    
    # Mock the get_project_settings function to avoid real implementation
    mock_result = {"success": True, "data": {"project_path": "/test/path"}}
    
    with mock.patch('src.mcp_agile_flow.fastmcp_tools.get_project_settings', 
                   return_value=json.dumps(mock_result)):
        result = call_tool_sync(tool_name)
    
    assert isinstance(result, dict)
    assert result["success"] is True


@pytest.mark.asyncio
async def test_call_tool_for_unsupported_tool():
    """Test that calling an unsupported tool returns an error."""
    tool_name = "unsupported-tool"
    
    result = await call_tool(tool_name)
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "not supported" in result["error"]
    assert all(tool in result["error"] for tool in SUPPORTED_TOOLS)


@pytest.mark.asyncio
async def test_call_tool_handles_exceptions():
    """Test that exceptions in tool execution are properly handled."""
    tool_name = "get-project-settings"
    
    # Mock the get_project_settings function to raise an exception
    with mock.patch('src.mcp_agile_flow.fastmcp_tools.get_project_settings', 
                   side_effect=ValueError("Test error")):
        result = await call_tool(tool_name)
    
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "Error processing tool" in result["error"]
    assert "Test error" in result["error"] 