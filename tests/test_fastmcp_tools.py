"""
Tests for FastMCP Tools implementation.
"""

import json
import os
import pytest
import tempfile
from unittest.mock import patch

from mcp_agile_flow.fastmcp_tools import get_project_settings


def test_get_project_settings_with_default_path():
    """Test get_project_settings with default path (uses current directory)."""
    # Call the tool function
    result = get_project_settings()
    
    # Parse the result as JSON
    settings = json.loads(result)
    
    # Check that the result has the expected keys
    assert "project_path" in settings
    assert "current_directory" in settings
    assert "knowledge_graph_directory" in settings
    assert "ai_docs_directory" in settings
    assert "project_type" in settings
    assert "project_metadata" in settings
    assert "source" in settings
    assert "is_root" in settings
    assert "is_writable" in settings
    assert "exists" in settings
    
    # Check specific values
    assert settings["project_type"] == "generic"
    assert isinstance(settings["project_metadata"], dict)
    assert os.path.exists(settings["project_path"])
    assert os.path.exists(settings["current_directory"])


def test_get_project_settings_with_proposed_path():
    """Test get_project_settings with a proposed path."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Call the tool function with the temp directory
        result = get_project_settings(proposed_path=temp_dir)
        
        # Parse the result as JSON
        settings = json.loads(result)
        
        # Check that the result has the temporary directory as project path
        assert settings["project_path"] == temp_dir
        assert settings["source"] == "proposed path parameter"
        assert settings["is_root"] is False


def test_get_project_settings_with_environment_variable():
    """Test get_project_settings with an environment variable."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Patch the environment variable
        with patch.dict(os.environ, {"PROJECT_PATH": temp_dir}):
            # Call the tool function
            result = get_project_settings()
            
            # Parse the result as JSON
            settings = json.loads(result)
            
            # Check that the result has the environment variable value as project path
            assert settings["project_path"] == temp_dir
            assert settings["source"] == "PROJECT_PATH environment variable"
            assert settings["is_project_path_manually_set"] is True


def test_get_project_settings_with_nonexistent_path():
    """Test get_project_settings with a nonexistent path."""
    # Create a path that doesn't exist
    nonexistent_path = "/path/that/does/not/exist"
    
    # Call the tool function with the nonexistent path
    result = get_project_settings(proposed_path=nonexistent_path)
    
    # Parse the result as JSON
    settings = json.loads(result)
    
    # Check that a fallback path was used
    assert settings["project_path"] != nonexistent_path
    assert "fallback" in settings["source"]
    assert os.path.exists(settings["project_path"])


def test_get_project_settings_with_root_path():
    """Test get_project_settings with root path."""
    # Call the tool function with root path
    result = get_project_settings(proposed_path="/")
    
    # Parse the result as JSON
    settings = json.loads(result)
    
    # Check that a safe path was used (not root)
    assert settings["project_path"] != "/"
    assert "fallback" in settings["source"]
    assert settings["is_root"] is False 