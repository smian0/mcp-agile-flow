"""
Tests for FastMCP Tools implementation.
"""

import json
import os
import pytest
import tempfile
from unittest.mock import patch, mock_open
from pathlib import Path
import shutil
import logging

from mcp_agile_flow.fastmcp_tools import get_project_settings, read_graph, initialize_ide


def test_get_project_settings_with_default_path():
    """Test get_project_settings with default path (uses current directory)."""
    # Call the tool function
    result = get_project_settings()
    
    # Parse the result as JSON
    settings = json.loads(result)
    
    # Check that the result has the expected keys
    assert "project_path" in settings
    assert "current_directory" in settings
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


def test_read_graph():
    """Test the read_graph function."""
    # Call the tool function
    result = read_graph()
    
    # Parse the result as JSON
    graph_data = json.loads(result)
    
    # Check that the result indicates knowledge graph functionality has been moved
    assert "success" in graph_data
    assert graph_data["success"] is False
    assert "message" in graph_data
    assert "Memory graph functionality has been moved" in graph_data["message"]


def test_initialize_ide():
    """Test the initialize_ide function."""
    # Create a temporary directory to use as project path
    with tempfile.TemporaryDirectory() as temp_dir:
        # Call initialize_ide with the temporary directory
        result = initialize_ide(ide="cursor", project_path=temp_dir)
        data = json.loads(result)
        
        # Check for success
        assert "success" in data
        assert data["success"] is True
        
        # Check that the project path is correct
        assert data["project_path"] == temp_dir
        
        # Check that the expected directories were created
        assert os.path.exists(os.path.join(temp_dir, "ai-docs"))
        assert os.path.exists(os.path.join(temp_dir, ".ai-templates"))
        assert os.path.exists(os.path.join(temp_dir, ".cursor", "rules"))
        
        # Try with windsurf
        result = initialize_ide(ide="windsurf", project_path=temp_dir)
        data = json.loads(result)
        
        # Check for success
        assert data["success"] is True
        
        # Check that the expected file was created
        assert os.path.exists(os.path.join(temp_dir, ".windsurfrules"))
        
        # Check that the rules_file is correctly set in the response
        assert data["rules_file"] == os.path.join(temp_dir, ".windsurfrules")
        
        # Check that rules_directory is None for windsurf
        assert data["rules_directory"] is None
        
        # Check for windsurf-specific field
        assert data["initialized_windsurf"] is True


def test_prime_context():
    """Test the prime_context function."""
    # Create a temporary directory to use as project path
    with tempfile.TemporaryDirectory() as temp_dir:
        # Call prime_context with the temporary directory 
        from mcp_agile_flow.fastmcp_tools import prime_context
        result = prime_context(project_path=temp_dir)
        data = json.loads(result)
        
        # Check the response structure
        assert "context" in data
        assert "summary" in data
        
        # Check that context contains project info even when no files exist
        assert "project" in data["context"]
        assert "name" in data["context"]["project"]
        assert "status" in data["context"]["project"]
        
        # Check summary - should contain basic project info
        assert isinstance(data["summary"], str)
        assert "Project: " in data["summary"]
        assert "Status: " in data["summary"]
        
        # Test with different depth parameter
        result = prime_context(depth="minimal", project_path=temp_dir)
        minimal_data = json.loads(result)
        assert "context" in minimal_data
        assert "summary" in minimal_data 

def test_migrate_mcp_config_structure():
    """Test that the migrate_mcp_config function returns well-formed JSON."""
    from mcp_agile_flow.fastmcp_tools import migrate_mcp_config
    
    # Even if there's an error, the function should return valid JSON
    result = migrate_mcp_config("cursor", "windsurf")
    
    # Parse the result to ensure it's valid JSON
    data = json.loads(result)
    
    # Check basic structure
    assert isinstance(data, dict)
    assert "success" in data  # All responses should have a success field 