"""
Tests for the get-project-settings tool functionality.

Tests the ability to retrieve project settings information.
"""
import asyncio
import json
import sys
import os
import pytest
import logging
from pathlib import Path
from datetime import datetime

# Create loggers
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import from the main package
from src.mcp_agile_flow.simple_server import handle_call_tool

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

def test_get_project_settings_with_environment_variable():
    """Test the get-project-settings tool with a PROJECT_PATH environment variable set."""
    logger.info("Testing get-project-settings with PROJECT_PATH...")
    
    # Save the original PROJECT_PATH environment variable
    original_project_path = os.environ.get("PROJECT_PATH")
    
    try:
        # Set environment variable to current directory
        test_path = os.getcwd()
        os.environ["PROJECT_PATH"] = test_path
        
        # Run the tool
        result = asyncio.run(handle_call_tool("get-project-settings", {}))
        
        # Verify we got a text response
        assert result[0].type == "text"
        settings_data = json.loads(result[0].text)
        
        # Save the settings to the test_outputs directory
        save_test_output("project_settings_with_env", settings_data)
        
        # Verify the project path matches our environment variable
        assert settings_data["project_path"] == test_path
        
    finally:
        # Restore the original PROJECT_PATH or remove it if it wasn't set
        if original_project_path is not None:
            os.environ["PROJECT_PATH"] = original_project_path
        else:
            os.environ.pop("PROJECT_PATH", None)

def test_get_project_settings_default_paths():
    """Test that the get-project-settings tool creates expected default paths."""
    logger.info("Testing get-project-settings default paths...")
    
    # Save the original PROJECT_PATH environment variable
    original_project_path = os.environ.get("PROJECT_PATH")
    
    try:
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
        
    finally:
        # Restore the original PROJECT_PATH if it was set
        if original_project_path is not None:
            os.environ["PROJECT_PATH"] = original_project_path 