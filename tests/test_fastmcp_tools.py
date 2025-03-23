"""
Tests for FastMCP Tools implementation.
"""

import json
import os
import pytest
import tempfile
from unittest.mock import patch
from pathlib import Path
import shutil

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


def test_read_graph():
    """Test the read_graph function."""
    # Call the tool function
    result = read_graph()
    
    # Parse the result as JSON
    graph_data = json.loads(result)
    
    # Check that the result has the expected keys
    assert "success" in graph_data
    assert "project_type" in graph_data
    assert "project_metadata" in graph_data
    assert "entities" in graph_data
    assert "relations" in graph_data
    
    # Check specific values
    assert graph_data["success"] is True
    assert isinstance(graph_data["entities"], list)
    assert isinstance(graph_data["relations"], list)
    
    # Entities should have the expected structure when present
    if graph_data["entities"]:
        entity = graph_data["entities"][0]
        assert "name" in entity
        assert "entity_type" in entity
        assert "observations" in entity
    
    # Relations should have the expected structure when present  
    if graph_data["relations"]:
        relation = graph_data["relations"][0]
        assert "from_entity" in relation
        assert "to_entity" in relation
        assert "relation_type" in relation


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