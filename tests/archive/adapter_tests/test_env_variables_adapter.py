"""
Tests for the PROJECT_PATH environment variable functionality with the test adapter.

These tests verify that the environment variable PROJECT_PATH
is properly used by both implementations of MCP.
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
async def test_initialize_ide_rules_with_env_variable(temp_dir, env_cleanup):
    """Test that initialize-ide-rules works with PROJECT_PATH environment variable."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")

    # Call the initialize-ide-rules tool with IDE set to windsurf
    result = await call_tool("initialize-ide-rules", {"ide": "windsurf"})

    # Check the response
    assert result["success"] is True

    # Verify the windsurf rules file was created
    windsurf_rule_file = os.path.join(temp_dir, ".windsurfrules")
    assert os.path.exists(windsurf_rule_file)


@pytest.mark.asyncio
async def test_initialize_ide_rules_fallback_to_cwd(temp_dir, env_cleanup, monkeypatch):
    """Test that initialize-ide-rules falls back to cwd when no path is provided."""
    # Set the current working directory to the temp dir
    monkeypatch.chdir(temp_dir)
    print(f"\nCurrent working directory set to: {os.getcwd()}")

    # Call the initialize-ide-rules tool without project_path and with IDE set to windsurf
    if "PROJECT_PATH" in os.environ:
        del os.environ["PROJECT_PATH"]
        print("PROJECT_PATH environment variable removed")
    else:
        print("PROJECT_PATH environment variable not set")

    result = await call_tool("initialize-ide-rules", {"ide": "windsurf"})

    # Check the response
    assert result["success"] is True

    # Verify the windsurf rules file was created in the current directory
    windsurf_rule_file = os.path.join(os.getcwd(), ".windsurfrules")
    assert os.path.exists(windsurf_rule_file)


@pytest.mark.asyncio
async def test_initialize_ide_cursor_with_env_variable(temp_dir, env_cleanup):
    """Test that initialize-ide-rules with cursor IDE works with PROJECT_PATH environment variable."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")

    # Call the initialize-ide-rules tool with IDE set to cursor
    result = await call_tool("initialize-ide-rules", {"ide": "cursor"})

    # Check the response
    assert result["success"] is True

    # Verify the cursor rules directory was created
    cursor_rules_dir = os.path.join(temp_dir, ".cursor", "rules")
    assert os.path.exists(cursor_rules_dir)


@pytest.mark.asyncio
async def test_initialize_ide_rules_arg_override(temp_dir, env_cleanup):
    """Test that arguments override environment variables for project path."""
    # Create a different temporary directory for the environment variable
    env_dir = tempfile.mkdtemp()

    try:
        # Set the environment variable to a different directory
        os.environ["PROJECT_PATH"] = env_dir
        print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
        print(f"Argument project_path set to: {temp_dir}")

        # Call the tool with project_path argument
        result = await call_tool(
            "initialize-ide-rules", {"project_path": temp_dir, "ide": "cursor"}
        )

        # Check the response
        assert result["success"] is True

        # Verify files were created in the argument directory, not the env directory
        cursor_dir_from_arg = os.path.join(temp_dir, ".cursor")
        cursor_dir_from_env = os.path.join(env_dir, ".cursor")

        assert os.path.exists(cursor_dir_from_arg)
        assert not os.path.exists(cursor_dir_from_env)

    finally:
        # Clean up the env_dir
        shutil.rmtree(env_dir) 