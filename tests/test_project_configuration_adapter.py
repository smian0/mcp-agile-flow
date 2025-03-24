"""
Tests for project configuration functionality with the test adapter.

These tests verify that the project configuration tools work correctly
with both implementations of MCP.
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the tool adapter
from src.mcp_agile_flow.test_adapter import call_tool


def save_test_output(test_name, output_data, suffix="json"):
    """Save test output data to a file."""
    # Create the test_outputs directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "test_outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Save the output to a file
    output_path = os.path.join(output_dir, f"{test_name}.{suffix}")
    
    with open(output_path, "w") as f:
        if isinstance(output_data, str):
            f.write(output_data)
        else:
            json.dump(output_data, f, indent=2)
    
    return output_path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def env_cleanup():
    """Clean up the PROJECT_PATH environment variable after tests."""
    # Save the original value of PROJECT_PATH
    original_value = os.environ.get("PROJECT_PATH")

    # Run the test
    yield

    # Restore or remove the environment variable
    if original_value is not None:
        os.environ["PROJECT_PATH"] = original_value
    else:
        os.environ.pop("PROJECT_PATH", None)


@pytest.mark.asyncio
async def test_get_project_settings():
    """Test the get-project-settings tool functionality directly."""
    # Call the tool
    result = await call_tool("get-project-settings", {})

    # Save the settings to the test_outputs directory
    save_test_output("project_settings_adapter", result)

    # Basic verification of the JSON response
    assert "project_path" in result
    assert os.path.isdir(result["project_path"])

    # Verify the project type and metadata fields are present
    assert "project_type" in result
    assert "project_metadata" in result
    assert isinstance(result["project_type"], str)
    assert isinstance(result["project_metadata"], dict)


@pytest.mark.asyncio
async def test_get_project_settings_with_project_path(temp_dir, env_cleanup):
    """Test that get-project-settings tool uses PROJECT_PATH when set."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")

    # Call the tool
    result = await call_tool("get-project-settings", {})

    # Save the settings to test outputs
    save_test_output("project_settings_with_env_adapter", result)

    # Verify the project path is set to the temp directory
    assert result["project_path"] == temp_dir
    assert result["is_project_path_manually_set"] is True


@pytest.mark.asyncio
async def test_get_project_settings_default_paths(env_cleanup):
    """Test that the get-project-settings tool creates expected default paths."""
    # Remove PROJECT_PATH if it exists to test default behavior
    if "PROJECT_PATH" in os.environ:
        del os.environ["PROJECT_PATH"]
        print("PROJECT_PATH environment variable removed")
    else:
        print("PROJECT_PATH environment variable not set")

    # Call the tool
    result = await call_tool("get-project-settings", {})

    # Save the settings to the test_outputs directory
    save_test_output("project_settings_default_adapter", result)

    # Verify default paths are set and relate to each other correctly
    project_path = result["project_path"]

    # AI docs directory should be within the project path
    assert result["ai_docs_directory"].startswith(project_path)

    # Templates directory might not always be present, so check if it exists first
    if "ai_templates_directory" in result:
        assert result["ai_templates_directory"].startswith(project_path)


@pytest.mark.asyncio
async def test_get_project_settings_with_proposed_path(temp_dir):
    """Test that get-project-settings tool accepts a proposed path."""
    # Call the tool with proposed_path parameter
    result = await call_tool("get-project-settings", {"proposed_path": temp_dir})

    # Verify the project path is set to the temp directory
    assert result["project_path"] == temp_dir 