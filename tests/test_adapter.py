"""
Tests for the MCP Agile Flow Tool API
"""

import json
import pytest
import tempfile
import os

from src.mcp_agile_flow import call_tool, call_tool_sync, SUPPORTED_TOOLS


@pytest.mark.asyncio
async def test_call_tool_for_supported_tool():
    """Test that calling a supported tool works correctly."""
    tool_name = "get_project_settings"

    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["PROJECT_PATH"] = temp_dir
        result = await call_tool(tool_name)

        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["project_path"] == temp_dir


def test_call_tool_sync():
    """Test that the synchronous version works correctly."""
    tool_name = "get_project_settings"

    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["PROJECT_PATH"] = temp_dir
        result = call_tool_sync(tool_name)

        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["project_path"] == temp_dir


@pytest.mark.asyncio
async def test_call_tool_for_unsupported_tool():
    """Test that calling an unsupported tool returns an error."""
    tool_name = "unsupported_tool"

    result = await call_tool(tool_name)

    assert isinstance(result, dict)
    assert result["success"] is False
    assert "not supported" in result["error"]
    assert all(tool in result["error"] for tool in SUPPORTED_TOOLS)


@pytest.mark.asyncio
async def test_call_tool_handles_exceptions():
    """Test that exceptions in tool execution are properly handled."""
    tool_name = "get_project_settings"

    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent_dir = os.path.join(temp_dir, "does_not_exist")
        result = await call_tool(tool_name, {"proposed_path": non_existent_dir})

        assert isinstance(result, dict)
        assert result["success"] is True  # Fallback behavior returns success with warning
        assert result["source"] == "current directory (fallback from non-existent path)"
