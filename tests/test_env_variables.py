"""
Tests for the PROJECT_PATH environment variable functionality.

These tests verify that the environment variable PROJECT_PATH
is properly used by the MCP server tools.
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


def test_initialize_ide_rules_with_env_variable(temp_dir, env_cleanup):
    """Test that initialize-ide-rules works with PROJECT_PATH environment variable."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
    
    # Call the tool without project_path argument
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


def test_initialize_ide_rules_arg_override(temp_dir, env_cleanup):
    """Test that argument overrides the environment variable."""
    # Create a different temporary directory for the environment variable
    env_dir = tempfile.mkdtemp()
    
    try:
        # Set the environment variable to a different directory
        os.environ["PROJECT_PATH"] = env_dir
        print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
        print(f"Argument project_path set to: {temp_dir}")
        
        # Call the tool with project_path argument
        result = asyncio.run(handle_call_tool("initialize-ide-rules", {
            "project_path": temp_dir,
            "ide": "cursor"
        }))
        
        # Check the response
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Verify files were created in the argument directory, not the env directory
        cursor_dir_from_arg = os.path.join(temp_dir, ".cursor")
        cursor_dir_from_env = os.path.join(env_dir, ".cursor")
        
        assert os.path.exists(cursor_dir_from_arg)
        assert not os.path.exists(cursor_dir_from_env)
    
    finally:
        # Clean up the env_dir
        shutil.rmtree(env_dir)


def test_initialize_rules_with_env_variable(temp_dir, env_cleanup):
    """Test that initialize-rules works with PROJECT_PATH environment variable."""
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
    
    # Call the tool without project_path argument
    result = asyncio.run(handle_call_tool("initialize-rules", {}))
    
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


def test_migrate_rules_with_env_variable(temp_dir, env_cleanup):
    """Test that migrate-rules-to-windsurf works with PROJECT_PATH environment variable."""
    # First set up cursor rules to migrate
    cursor_dir = os.path.join(temp_dir, ".cursor", "rules")
    os.makedirs(cursor_dir, exist_ok=True)
    
    # Create a test cursor rule file
    with open(os.path.join(cursor_dir, "test.mdc"), "w") as f:
        f.write("# Test Rule\n\nThis is a test rule for migration.")
    
    # Set the environment variable
    os.environ["PROJECT_PATH"] = temp_dir
    print(f"\nPROJECT_PATH set to: {os.environ['PROJECT_PATH']}")
    
    # Call the migration tool
    result = asyncio.run(handle_call_tool("migrate-rules-to-windsurf", {}))
    
    # Check the response
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Verify the output file was created
    windsurf_rule_file = os.path.join(temp_dir, ".windsurfrules")
    assert os.path.exists(windsurf_rule_file)
    
    # Check the contents of the file
    with open(windsurf_rule_file, "r") as f:
        content = f.read()
        assert "Test Rule" in content


def test_migrate_rules_fallback_to_cwd(temp_dir, env_cleanup, monkeypatch):
    """Test that migrate-rules-to-windsurf falls back to cwd when no path is provided."""
    # Create a test cursor rule file in the temp dir
    cursor_dir = os.path.join(temp_dir, ".cursor", "rules")
    os.makedirs(cursor_dir, exist_ok=True)
    
    with open(os.path.join(cursor_dir, "test.mdc"), "w") as f:
        f.write("# Test Rule\n\nThis is a test rule for migration.")
    
    # Set the current working directory to the temp dir
    monkeypatch.chdir(temp_dir)
    print(f"\nCurrent working directory set to: {os.getcwd()}")
    
    # Call the migration tool without arguments or env variables
    if "PROJECT_PATH" in os.environ:
        del os.environ["PROJECT_PATH"]
        print("PROJECT_PATH environment variable removed")
    else:
        print("PROJECT_PATH environment variable not set")
    
    result = asyncio.run(handle_call_tool("migrate-rules-to-windsurf", {}))
    
    # Check the response
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Verify the output file was created
    windsurf_rule_file = os.path.join(temp_dir, ".windsurfrules")
    assert os.path.exists(windsurf_rule_file)
    
    # Check the contents of the file
    with open(windsurf_rule_file, "r") as f:
        content = f.read()
        assert "Test Rule" in content 