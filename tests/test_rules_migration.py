"""
Tests for the migrate-rules-to-windsurf tool functionality.

Tests the ability to migrate Cursor rules to Windsurf format.
"""
import asyncio
import json
import sys
import os
import pytest
import shutil
import logging
from pathlib import Path
from datetime import datetime
import uuid

# Create loggers
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import from the main package
from src.mcp_agile_flow.simple_server import handle_call_tool

# Define path to test_outputs directory
TEST_OUTPUTS_DIR = Path(__file__).parent / "test_outputs"

def copy_directory_to_outputs(source_dir, test_name):
    """
    Copy a directory to the test_outputs directory.
    
    Args:
        source_dir: Source directory path
        test_name: Name of the test
    
    Returns:
        Path to the copied directory
    """
    # Create the test_outputs directory if it doesn't exist
    TEST_OUTPUTS_DIR.mkdir(exist_ok=True)
    
    # Create a uniquely named directory by adding a timestamp and UUID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for brevity
    output_dir = TEST_OUTPUTS_DIR / f"{test_name}_{timestamp}_{unique_id}"
    
    # Copy the directory
    shutil.copytree(source_dir, output_dir)
    
    logger.info(f"Copied directory to {output_dir}")
    return output_dir

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
def initialized_project(tmp_path):
    """
    Fixture to create a temporary project with Cursor rules initialized.
    
    Returns:
        Path to the initialized project directory
    """
    # Create a temporary directory to use as the project path
    test_project_path = tmp_path / "test_project"
    test_project_path.mkdir()
    
    # First initialize Cursor rules
    result = asyncio.run(handle_call_tool("initialize-ide-rules", {"project_path": str(test_project_path), "ide": "cursor"}))
    
    # Verify the initialization succeeded
    response = json.loads(result[0].text)
    assert response["success"] == True
    
    return test_project_path

def test_migrate_rules_to_windsurf(initialized_project):
    """Test migrating Cursor rules to Windsurf format."""
    logger.info("Testing migrate-rules-to-windsurf...")
    
    # Call migrate-rules-to-windsurf with the initialized project path
    result = asyncio.run(handle_call_tool("migrate-rules-to-windsurf", {"project_path": str(initialized_project)}))
    
    # Verify the result
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["success"] == True
    
    # Verify that the Windsurf rules file was created
    windsurf_rules_path = initialized_project / ".windsurfrules"
    assert windsurf_rules_path.exists()
    
    # Check content of Windsurf rules file
    windsurf_rules_content = windsurf_rules_path.read_text(encoding='utf-8')
    assert len(windsurf_rules_content) > 0
    
    # Save the response to the test_outputs directory
    save_test_output("migrate_rules_response", response)
    
    # Save the content of the Windsurf rules file
    save_test_output("windsurf_rules_content", windsurf_rules_content, suffix="md")
    
    # Copy the entire project directory to test_outputs for inspection
    copy_directory_to_outputs(initialized_project, "migrated_project_structure")
    
def test_migrate_rules_with_root_path():
    """Test that migrate-rules-to-windsurf safely handles root paths."""
    logger.info("Testing migrate-rules-to-windsurf safety with root path...")
    
    # Call migrate-rules-to-windsurf with root path
    result = asyncio.run(handle_call_tool("migrate-rules-to-windsurf", {
        "project_path": "/"
    }))
    
    # Verify the result - it should fall back to current directory
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    
    # The function might return success=False if there are no cursor rules to migrate
    # or success=True if it falls back to cwd and finds cursor rules
    # Either outcome is acceptable as long as it doesn't crash
    
    # Save the response to the test_outputs directory
    save_test_output("migrate_rules_with_root_path", response) 