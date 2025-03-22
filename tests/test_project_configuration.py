"""
Tests for project configuration functionality.

These tests verify:
1. PROJECT_PATH environment variable is properly used by the application
2. get-project-settings tool works correctly
3. initialize-ide-rules tool works with project paths
4. Default paths are created as expected
"""
import asyncio
import json
import os
import pytest
import tempfile
import shutil
import logging
import sys
from pathlib import Path
from datetime import datetime

# Create loggers
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import from the main package
from src.mcp_agile_flow.simple_server import handle_call_tool
from src.mcp_agile_flow.utils import get_project_settings

# Define path to test_outputs directory
TEST_OUTPUTS_DIR = Path(__file__).parent / "test_outputs"

def save_test_output(test_name, output_data, suffix="json"):
    """
    Save test output to the test_outputs directory.
    
    Args:
        test_name: Name of the test
        output_data: Data to save (string or dict)
        suffix: File suffix (default: json)
    
    Returns:
        Path to the saved file
    """
    # Create the test_outputs directory if it doesn't exist
    TEST_OUTPUTS_DIR.mkdir(exist_ok=True)
    
    # Create a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.{suffix}"
    output_path = TEST_OUTPUTS_DIR / filename
    
    # Save the data
    if isinstance(output_data, dict):
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
    else:
        with open(output_path, 'w') as f:
            f.write(str(output_data))
    
    logger.info(f"Saved test output to {output_path}")
    return output_path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
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


# --- Tests for direct project settings access ---

def test_get_project_settings_with_project_path(temp_dir, env_cleanup):
    """Test that get_project_settings uses PROJECT_PATH when set."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    logger.info(f"PROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
    
    # Get project settings
    settings = get_project_settings()
    
    # Verify the project path is set to the temp directory
    assert settings["project_path"] == temp_dir
    assert settings["is_project_path_manually_set"] == True


# --- Tests for get-project-settings tool ---

def test_get_project_settings_tool():
    """Test the get-project-settings tool functionality directly."""
    logger.info("Testing get-project-settings tool...")
    
    # Run the async function and get the result
    result = asyncio.run(handle_call_tool("get-project-settings", {}))
    
    # Verify we got a text response
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Get the text content and parse the JSON
    settings_info = result[0].text
    settings_data = json.loads(settings_info)
    
    # Log the settings
    logger.info("\nProject settings from tool:")
    for line in settings_info.splitlines():
        logger.info(line)
    
    # Save the settings to the test_outputs directory
    save_test_output("project_settings", settings_data)
    
    # Basic verification of the JSON response
    assert "project_path" in settings_data
    assert "knowledge_graph_directory" in settings_data
    assert os.path.isdir(settings_data["project_path"])
    
    # Verify the new project type and metadata fields are present
    assert "project_type" in settings_data
    assert "project_metadata" in settings_data
    assert isinstance(settings_data["project_type"], str)
    assert isinstance(settings_data["project_metadata"], dict)


def test_get_project_settings_tool_with_project_path(temp_dir, env_cleanup):
    """Test that get-project-settings tool uses PROJECT_PATH when set."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    logger.info(f"PROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
    
    # Call the tool
    result = asyncio.run(handle_call_tool("get-project-settings", {}))
    
    # Check the response
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Parse the JSON response
    response_data = json.loads(result[0].text)
    
    # Save the settings to test outputs
    save_test_output("project_settings_with_env", response_data)
    
    # Verify the project path is set to the temp directory
    assert response_data["project_path"] == temp_dir
    assert response_data["is_project_path_manually_set"] == True


def test_get_project_settings_default_paths(env_cleanup):
    """Test that the get-project-settings tool creates expected default paths."""
    logger.info("Testing get-project-settings default paths...")
    
    # Remove PROJECT_PATH if it exists to test default behavior
    if "PROJECT_PATH" in os.environ:
        del os.environ["PROJECT_PATH"]
    
    # Run the tool
    result = asyncio.run(handle_call_tool("get-project-settings", {}))
    
    # Verify we got a text response
    assert result[0].type == "text"
    settings_data = json.loads(result[0].text)
    
    # Save the settings to the test_outputs directory
    save_test_output("project_settings_default", settings_data)
    
    # Verify default paths are set and relate to each other correctly
    project_path = settings_data["project_path"]
    
    # Knowledge graph directory should be within the project path
    assert settings_data["knowledge_graph_directory"].startswith(project_path)
    
    # AI docs directory should be within the project path
    assert settings_data["ai_docs_directory"].startswith(project_path)
    
    # Templates directory might not always be present, so check if it exists first
    if "ai_templates_directory" in settings_data:
        assert settings_data["ai_templates_directory"].startswith(project_path)


# --- Tests for initialize-ide-rules tool ---

def test_initialize_ide_rules_with_project_path(temp_dir, env_cleanup):
    """Test that initialize-ide-rules works with PROJECT_PATH environment variable."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    logger.info(f"PROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
    
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