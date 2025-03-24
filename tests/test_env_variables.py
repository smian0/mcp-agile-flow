"""
Tests for environment variable handling and project path resolution.

This file tests how the tools handle environment variables and project paths.
"""

import os
import tempfile
import pytest
import json
from pathlib import Path
from unittest import mock

# Import the adapter instead of server
from src.mcp_agile_flow import call_tool, call_tool_sync

# Set up test environment
os.environ["PYTEST_ENV_VAR_TEST"] = "true"

@pytest.mark.asyncio
async def test_env_variables_in_get_project_settings():
    """Test that project settings are processed correctly."""
    # Call the tool
    result = await call_tool("get-project-settings", {})
    result_dict = result
    
    # Verify that we have the expected structure
    assert "project_path" in result_dict
    assert "current_directory" in result_dict
    assert "is_project_path_manually_set" in result_dict
    assert "source" in result_dict
    
    # The path should exist
    assert Path(result_dict["project_path"]).exists()

@pytest.mark.asyncio
async def test_proposed_path_handling():
    """Test that proposed paths are handled correctly."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Call the tool with the temporary directory as the proposed path
        result = await call_tool("get-project-settings", {"proposed_path": tmp_dir})
        result_dict = result
        
        # Verify that the proposed path was used
        assert result_dict["project_path"] == tmp_dir
