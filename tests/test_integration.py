"""
Integration tests for the MCP Agile Flow server.

Basic tests to validate that the server works correctly.
"""
import asyncio
import subprocess
import json
import sys
import pytest
import pytest_asyncio
from pathlib import Path
import os
import logging
import aiohttp
import shutil
import time
import uuid
from datetime import datetime
import tempfile

# Create loggers
logger = logging.getLogger(__name__)
server_logger = logging.getLogger('mcp_agile_flow.server')

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import from the main package
from src.mcp_agile_flow.simple_server import mcp

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

def test_server_imports():
    """Test that the server module can be imported."""
    logger.info("Testing server imports...")
    assert mcp is not None

def test_server_handle_call_tool():
    """Test the server's handle_call_tool function."""
    logger.info("Testing server handle_call_tool...")
    
    # Import the handler function
    from src.mcp_agile_flow.simple_server import handle_call_tool
    
    # Test get-project-settings
    result = asyncio.run(handle_call_tool("get-project-settings", {}))
    assert result[0].type == "text"
    settings_data = json.loads(result[0].text)
    assert "project_path" in settings_data

def test_initialize_ide_rules_with_custom_path(tmp_path):
    """Test the initialize-ide-rules tool with a custom project path."""
    logger.info("Testing initialize-ide-rules with custom project path...")
    
    # Import the handler function
    from src.mcp_agile_flow.simple_server import handle_call_tool
    
    # Create a single temporary directory to use as the project path
    test_project_path = tmp_path / "test_ide_project"
    test_project_path.mkdir()
    
    # Test different IDE values on the same project directory
    for ide in ["cursor", "windsurf", "cline", "copilot"]:
        # Call initialize-ide-rules with the same project path
        result = asyncio.run(handle_call_tool("initialize-ide-rules", {
            "ide": ide,
            "project_path": str(test_project_path)
        }))
        
        # Verify the result
        assert result[0].type == "text"
        response = json.loads(result[0].text)
        assert response["success"] == True
        
        # Save the response to the test_outputs directory
        save_test_output(f"initialize_{ide}_rules_response", response)
        
        # Verify that the ai-templates directory exists regardless of which IDE is used
        templates_dir = test_project_path / ".ai-templates"
        assert templates_dir.exists(), f"Templates directory not created for {ide}"
        
        # Handle IDE-specific path verification
        if ide == "cursor":
            # For Cursor, verify the multi-file rules
            rules_dir = test_project_path / ".cursor" / "rules"
            
            assert rules_dir.exists()
            
            # Verify that rule files were copied
            rule_files = list(rules_dir.glob("*"))
            assert len(rule_files) > 0
        else:
            # For other IDEs, check for their rule files
            if ide == "copilot":
                # Copilot stores rules in .github/copilot-instructions.md
                github_dir = test_project_path / ".github"
                rule_file = github_dir / "copilot-instructions.md"
            else:
                # For windsurf and cline, check for their rule files
                rule_file_name = f".{ide}rules"
                rule_file = test_project_path / rule_file_name
            
            # Assert that the rule file exists
            assert rule_file.exists(), f"Rule file {rule_file} does not exist"
            
            if rule_file.exists():
                # Extract and save the content of the rule file
                rule_content = rule_file.read_text(encoding='utf-8')
                save_test_output(f"{ide}_rules_content", rule_content)
    
    # After all IDEs have been set up, copy the entire project directory to test_outputs for inspection
    copy_directory_to_outputs(test_project_path, "unified_project_structure")

def test_initialize_ide_rules_with_root_path():
    """Test that initialize-ide-rules safely handles root paths."""
    logger.info("Testing initialize-ide-rules safety with root path...")
    
    # Import the handler function
    from src.mcp_agile_flow.simple_server import handle_call_tool
    
    # Call initialize-ide-rules with root path
    result = asyncio.run(handle_call_tool("initialize-ide-rules", {
        "ide": "cursor",
        "project_path": "/"
    }))
    
    # Verify the result - it should fall back to current directory
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["success"] == True
    
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
                copy_directory_to_outputs(cursor_dir, "ide_rules_root_test")
            
            # Clean up
            shutil.rmtree(os.path.join(current_dir, ".cursor"))

def test_initialize_ide_rules_with_env_root_path():
    """Test that initialize-ide-rules safely handles environment variables pointing to root."""
    logger.info("Testing initialize-ide-rules safety with environment variable pointing to root...")
    
    # Import the handler function
    from src.mcp_agile_flow.simple_server import handle_call_tool
    
    # Save the original PROJECT_PATH environment variable
    original_project_path = os.environ.get("PROJECT_PATH")
    
    try:
        # Set environment variable to root
        os.environ["PROJECT_PATH"] = "/"
        
        # Call initialize-ide-rules without a project_path (should use environment variable which points to root)
        result = asyncio.run(handle_call_tool("initialize-ide-rules", {
            "ide": "cursor"
        }))
        
        # Verify the result - it should fall back to current directory
        assert result[0].type == "text"
        response = json.loads(result[0].text)
        assert response["success"] == True
        
        # Save the response to the test_outputs directory
        save_test_output("initialize_ide_rules_with_env_root_path", response)
        
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
                    copy_directory_to_outputs(cursor_dir, "ide_rules_env_root_test")
                
                # Clean up
                shutil.rmtree(os.path.join(current_dir, ".cursor"))
    finally:
        # Restore the original PROJECT_PATH or remove it if it wasn't set
        if original_project_path is not None:
            os.environ["PROJECT_PATH"] = original_project_path
        else:
            os.environ.pop("PROJECT_PATH", None)

def test_get_safe_project_path_tool():
    """Test the get-safe-project-path tool functionality."""
    logger.info("Testing get-safe-project-path tool...")
    
    # Import the handler function
    from src.mcp_agile_flow.simple_server import handle_call_tool
    import os
    
    # Test with no proposed path (should use current directory)
    result = asyncio.run(handle_call_tool("get-safe-project-path", {}))
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    
    # Save the response to the test_outputs directory
    save_test_output("get_safe_project_path_no_path", response)
    
    # Current directory is not root in test environment, so should work
    current_dir = os.getcwd()
    if current_dir != '/':
        assert "safe_path" in response
        assert response["safe_path"] == current_dir
        assert response["is_writable"] == True
    else:
        # Special case for when tests are run in root directory (unlikely)
        assert "error" in response
        assert response["needs_user_input"] == True
    
    # Test with root path explicitly
    result = asyncio.run(handle_call_tool("get-safe-project-path", {"proposed_path": "/"}))
    assert result[0].type == "text"
    
    # Save the response to the test_outputs directory
    response_root = json.loads(result[0].text)
    save_test_output("get_safe_project_path_root", response_root)
    
    # If current directory is not root, should fall back to it
    if current_dir != '/':
        assert response_root["safe_path"] == current_dir
        assert "root" in response_root["source"].lower()
    else:
        # If current directory is root, should ask for user input
        assert response_root["needs_user_input"] == True
        assert "error" in response_root
    
    # Test with a valid path (parent directory)
    parent_dir = os.path.dirname(current_dir)
    
    # Only test if parent_dir is writable and not root
    if parent_dir != '/' and os.access(parent_dir, os.W_OK):
        result = asyncio.run(handle_call_tool("get-safe-project-path", {"proposed_path": parent_dir}))
        assert result[0].type == "text"
        response_parent = json.loads(result[0].text)
        
        # Save the response to the test_outputs directory
        save_test_output("get_safe_project_path_parent", response_parent)
        
        # Should use the provided path
        assert response_parent["safe_path"] == parent_dir
        assert response_parent["is_writable"] == True
    
    # Test with a temporary directory to simulate real non-writable paths 
    # instead of using mocking
    
    # Create a temporary file that we'll use as a non-writable path
    with tempfile.NamedTemporaryFile() as temp_file:
        # Create a path that definitely doesn't exist
        non_existent_path = os.path.join(
            os.path.dirname(temp_file.name), 
            f"non_existent_dir_{uuid.uuid4().hex}"
        )
        
        # Test with non-existent path
        result = asyncio.run(handle_call_tool("get-safe-project-path", {"proposed_path": non_existent_path}))
        assert result[0].type == "text"
        response_real = json.loads(result[0].text)
        
        # Save the response to the test_outputs directory
        save_test_output("get_safe_project_path_real_non_existent", response_real)
        
        # The path doesn't exist, so we expect either:
        # 1. is_writable is False if non-existent paths are allowed but marked non-writable
        # 2. we've fallen back to current directory 
        # 3. an error is returned
        valid_response = (
            ("safe_path" in response_real and response_real["safe_path"] == non_existent_path and response_real.get("is_writable") == False) or
            ("safe_path" in response_real and response_real["safe_path"] == current_dir) or
            "error" in response_real
        )
        assert valid_response, f"Unexpected response for non-existent path: {response_real}"

# === Tests for MCP Config Migration have been moved to test_mcp_config_migration.py ===
# The following tests were moved:
# - test_migrate_mcp_config_with_conflicts
# - test_migrate_mcp_config_resolve_conflicts
# - test_migrate_mcp_config_invalid_resolutions 

# === Tests for initialize-rules have been moved to test_initialize_rules.py ===
# The following tests were moved:
# - test_initialize_rules_with_custom_path
# - test_initialize_rules_with_root_path

# === Tests for migrate-rules-to-windsurf have been moved to test_rules_migration.py ===

# === Tests for get-project-settings have been moved to test_project_settings.py ===
# The following tests were moved:
# - test_get_project_settings_tool 