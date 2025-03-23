"""
Tests for the initialize-ide-rules tool functionality.

Tests the ability to initialize a project with specific IDE rules, focusing on Cursor rules.
"""

import asyncio
import json
import logging
import os
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Create loggers
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import from the main package
from src.mcp_agile_flow.server import handle_call_tool

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
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
    else:
        with open(output_path, "w") as f:
            f.write(str(output_data))

    logger.info(f"Saved test output to {output_path}")
    return output_path


def test_initialize_ide_rules_with_custom_path(tmp_path):
    """Test the initialize-ide-rules tool with a custom project path."""
    logger.info("Testing initialize-ide-rules with custom project path...")

    # Create a temporary directory to use as the project path
    test_project_path = tmp_path / "test_project"
    test_project_path.mkdir()

    # Call initialize-ide-rules with the custom project path
    result = asyncio.run(
        handle_call_tool(
            "initialize-ide-rules",
            {"project_path": str(test_project_path), "ide": "cursor"},
        )
    )

    # Verify the result
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["success"] is True

    # Verify that the rules directory was created in the custom path
    rules_dir = test_project_path / ".cursor" / "rules"
    templates_dir = test_project_path / ".ai-templates"

    assert rules_dir.exists()
    assert templates_dir.exists()

    # Verify that rules files were copied
    rule_files = list(rules_dir.glob("*"))
    assert len(rule_files) > 0

    # Verify that template files were copied
    template_files = list(templates_dir.glob("*"))
    assert len(template_files) > 0

    # Copy the created rules directory to test_outputs for inspection
    cursor_dir = test_project_path / ".cursor"
    copy_directory_to_outputs(cursor_dir, "cursor_rules")

    # Copy the entire project directory to test_outputs for inspection
    copy_directory_to_outputs(test_project_path, "project_structure")

    # Save the response to the test_outputs directory
    save_test_output("initialize_ide_rules_response", response)


def test_initialize_ide_rules_with_root_path():
    """Test that initialize-ide-rules safely handles root paths."""
    logger.info("Testing initialize-ide-rules safety with root path...")

    # Call initialize-ide-rules with root path
    result = asyncio.run(
        handle_call_tool("initialize-ide-rules", {"project_path": "/", "ide": "cursor"})
    )

    # Verify the result - it should fall back to current directory
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["success"] is True

    # Save the response to the test_outputs directory
    save_test_output("initialize_ide_rules_with_root_path", response)

    # The rules should be created in the current directory
    current_dir = os.getcwd()

    # Check if the path in the response is not the root directory
    assert response["rules_directory"].startswith(current_dir)
    assert not response["rules_directory"].startswith("/.")

    # Clean up created files if they exist in cwd
    rules_dir = os.path.join(current_dir, ".cursor", "rules")
    if os.path.exists(rules_dir):
        # Only clean up if in a test environment
        if "pytest" in sys.modules:
            # Copy the files to test_outputs before cleaning
            cursor_dir = os.path.join(current_dir, ".cursor")
            if os.path.exists(cursor_dir):
                copy_directory_to_outputs(cursor_dir, "cursor_rules_root_test")

            # Clean up
            shutil.rmtree(os.path.join(current_dir, ".cursor"))


def test_initialize_ide_rules_cline(tmp_path):
    """Test initialize-ide-rules with the cline IDE option."""
    logger.info("Testing initialize-ide-rules with cline IDE option...")

    # Create a test project directory
    test_project_path = tmp_path / "test_cline_project"
    test_project_path.mkdir()

    # Call initialize-ide-rules with cline option
    result = asyncio.run(
        handle_call_tool(
            "initialize-ide-rules",
            {"project_path": str(test_project_path), "ide": "cline"},
        )
    )

    # Verify the result
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["success"] is True

    # Verify that the rules file was created
    cline_rules_file = test_project_path / ".clinerules"
    templates_dir = test_project_path / ".ai-templates"

    assert cline_rules_file.exists()
    assert templates_dir.exists()

    # Verify that the rules file has content
    with open(cline_rules_file, "r") as f:
        content = f.read()
        assert len(content) > 0

    # Verify that template files were copied
    template_files = list(templates_dir.glob("*"))
    assert len(template_files) > 0

    # Copy the created rules file to test_outputs for inspection
    copy_directory_to_outputs(test_project_path, "cline_rules")

    # Save the response to the test_outputs directory
    save_test_output("initialize_ide_rules_cline_response", response)

    # Verify response contains the correct rule file path and no directory
    assert response.get("rules_file") == str(cline_rules_file)
    assert response.get("rules_directory") is None
    assert "initialized_windsurf" not in response
