"""
Tests for the initialize-ide tool functionality using the adapter.

These tests verify that the initialize-ide tool correctly handles project paths
and creates the necessary files and directories using the adapter that can switch
between server and FastMCP implementations.
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Add the src directory to the Python path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from our adapter instead of directly from server
from src.mcp_agile_flow.test_adapter import call_tool


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def env_cleanup():
    """Clean up environment variables after tests."""
    # Save the original values
    original_project_path = os.environ.get("PROJECT_PATH")

    # Run the test
    yield

    # Restore or remove the environment variables
    if original_project_path is not None:
        os.environ["PROJECT_PATH"] = original_project_path
    else:
        os.environ.pop("PROJECT_PATH", None)


def test_initialize_ide_with_explicit_path(temp_dir, env_cleanup):
    """Test initialize-ide with an explicit project path."""
    # Call the tool with an explicit project path
    arguments = {"project_path": temp_dir, "ide": "cursor"}

    result = asyncio.run(call_tool("initialize-ide", arguments))

    # Verify the command executed successfully
    assert result["success"] is True

    # Check that the directories were created
    cursor_dir = os.path.join(temp_dir, ".cursor")
    rules_dir = os.path.join(cursor_dir, "rules")
    templates_dir = os.path.join(temp_dir, ".ai-templates")

    assert os.path.exists(cursor_dir)
    assert os.path.exists(rules_dir)
    assert os.path.exists(templates_dir)

    # Check that the rules directory contains files
    rule_files = os.listdir(rules_dir)
    assert len(rule_files) > 0

    # Verify that all rule files have .mdc extension for Cursor
    for rule_file in rule_files:
        assert rule_file.endswith(
            ".mdc"
        ), f"Rule file {rule_file} does not have .mdc extension"

    # Check that templates directory contains files
    assert len(os.listdir(templates_dir)) > 0


def test_initialize_ide_with_env_variable(temp_dir, env_cleanup):
    """Test initialize-ide with PROJECT_PATH environment variable."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir

    # Call the tool without a project path
    arguments = {"ide": "cursor"}

    result = asyncio.run(call_tool("initialize-ide", arguments))

    # Verify the command executed successfully
    assert result["success"] is True

    # Verify that rules_directory and templates_directory are returned
    assert "rules_directory" in result
    assert "templates_directory" in result
    assert "initialized_rules" in result
    assert "initialized_templates" in result

    # Get the rules directory path
    rules_dir = result["rules_directory"]
    assert os.path.exists(rules_dir)

    # Check the initialized rules
    initialized_rules = result.get("initialized_rules", [])
    assert len(initialized_rules) > 0

    # Verify that all initialized rules have .mdc extension
    for rule_file in initialized_rules:
        assert rule_file.endswith(
            ".mdc"
        ), f"Rule file {rule_file} does not have .mdc extension"

    # Also verify the files on disk
    rule_files = os.listdir(rules_dir)
    for rule_file in rule_files:
        assert rule_file.endswith(
            ".mdc"
        ), f"Rule file {rule_file} on disk does not have .mdc extension"


def test_initialize_ide_windsurf(temp_dir, env_cleanup):
    """Test initialize-ide with Windsurf IDE option."""
    # Call the tool with an explicit project path
    arguments = {"project_path": temp_dir, "ide": "windsurf"}

    result = asyncio.run(call_tool("initialize-ide", arguments))

    # Verify the command executed successfully
    assert result["success"] is True
    assert result.get("initialized_windsurf") is True

    # Check that the files were created
    windsurf_rule_file = os.path.join(temp_dir, ".windsurfrules")
    templates_dir = os.path.join(temp_dir, ".ai-templates")

    assert os.path.exists(windsurf_rule_file)
    assert os.path.exists(templates_dir)

    # Check that templates directory contains files
    assert len(os.listdir(templates_dir)) > 0


def test_initialize_ide_without_arguments():
    """Test initialize-ide without any arguments - should default to current directory."""
    # Call the tool without any arguments
    result = asyncio.run(call_tool("initialize-ide", {}))

    # Check the response is successful (uses current directory by default)
    assert result["success"] is True
    assert "rules_directory" in result
    assert "templates_directory" in result


def test_initialize_ide_cline(temp_dir, env_cleanup):
    """Test initialize-ide with cline IDE option."""
    # Call the tool with an explicit project path
    arguments = {"project_path": temp_dir, "ide": "cline"}

    result = asyncio.run(call_tool("initialize-ide", arguments))

    # Verify the command executed successfully
    assert result["success"] is True
    
    # Check that the files were created
    cline_rule_file = os.path.join(temp_dir, ".clinerules")
    templates_dir = os.path.join(temp_dir, ".ai-templates")

    assert os.path.exists(cline_rule_file)
    assert os.path.exists(templates_dir)

    # Verify that the rules file has content
    with open(cline_rule_file, "r") as f:
        content = f.read()
        assert len(content) > 0

    # Check that templates directory contains files
    assert len(os.listdir(templates_dir)) > 0 