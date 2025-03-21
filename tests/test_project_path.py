"""
Tests for the PROJECT_PATH environment variable functionality.

These tests verify that the PROJECT_PATH environment variable
is properly used by the application.
"""
import asyncio
import json
import os
import pytest
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from the main package
from src.mcp_agile_flow.simple_server import handle_call_tool
from src.mcp_agile_flow.utils import get_project_settings


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def another_temp_dir():
    """Create another temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def env_cleanup():
    """Clean up environment variables after tests."""
    # Save the original value
    original_project_path = os.environ.get("PROJECT_PATH")
    
    # Run the test
    yield
    
    # Restore or remove the environment variable
    if original_project_path is not None:
        os.environ["PROJECT_PATH"] = original_project_path
    else:
        os.environ.pop("PROJECT_PATH", None)


def test_get_project_settings_with_project_path(temp_dir, env_cleanup):
    """Test that get_project_settings uses PROJECT_PATH when set."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
    
    # Get project settings
    settings = get_project_settings()
    
    # Verify the project path is set to the temp directory
    assert settings["project_path"] == temp_dir
    assert settings["is_project_path_manually_set"] == True


def test_get_project_settings_tool_with_project_path(temp_dir, env_cleanup):
    """Test that get-project-settings tool uses PROJECT_PATH when set."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
    
    # Call the tool
    result = asyncio.run(handle_call_tool("get-project-settings", {}))
    
    # Check the response
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Parse the JSON response
    response_data = json.loads(result[0].text)
    
    # Verify the project path is set to the temp directory
    assert response_data["project_path"] == temp_dir
    assert response_data["is_project_path_manually_set"] == True


def test_initialize_ide_rules_with_project_path(temp_dir, env_cleanup):
    """Test that initialize-ide-rules works with PROJECT_PATH environment variable."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
    
    # Call the tool
    result = asyncio.run(handle_call_tool("initialize-ide-rules", {"ide": "cursor"}))
    
    # Check the response
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Parse the JSON response
    response_data = json.loads(result[0].text)
    
    # Verify the command executed successfully
    assert response_data["success"] == True
    
    # Check that the directories were created
    cursor_dir = os.path.join(temp_dir, ".cursor")
    rules_dir = os.path.join(cursor_dir, "rules")
    templates_dir = os.path.join(temp_dir, ".ai-templates")
    
    assert os.path.exists(cursor_dir)
    assert os.path.exists(rules_dir)
    assert os.path.exists(templates_dir)
    
    # Check that the rules directory contains files
    assert len(os.listdir(rules_dir)) > 0
