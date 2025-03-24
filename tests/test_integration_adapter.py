"""
Integration tests for the MCP Agile Flow server using the test adapter.

This file adapts the original integration tests to work with both the legacy server
and the FastMCP implementation through the test adapter.
"""

import asyncio
import json
import logging
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
import pytest

# Create loggers
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import the test adapter
from src.mcp_agile_flow.test_adapter import call_tool

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
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
    else:
        with open(output_path, "w") as f:
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


@pytest.mark.asyncio
async def test_available_tools():
    """Test that basic tools are available through the adapter."""
    logger.info("Testing basic tool availability through adapter...")

    # Test get-project-settings
    result = await call_tool("get-project-settings", {})
    assert "project_path" in result
    
    # Save the result for inspection
    save_test_output("adapter_basic_tools_get_project_settings", result)
    
    # Test initialize-ide-rules
    with tempfile.TemporaryDirectory() as temp_dir:
        result = await call_tool("initialize-ide-rules", {
            "ide": "cursor", 
            "project_path": temp_dir
        })
        assert "success" in result
        assert result["success"] is True
        
        # Check that files were created
        templates_dir = Path(temp_dir) / ".ai-templates"
        assert templates_dir.exists()
        
        # Save the result for inspection
        save_test_output("adapter_basic_tools_initialize_ide_rules", result)
    
    # Test prime-context
    with tempfile.TemporaryDirectory() as temp_dir:
        result = await call_tool("prime-context", {
            "project_path": temp_dir,
            "depth": "minimal"
        })
        assert "context" in result
        assert "summary" in result
        
        # Save the result for inspection
        save_test_output("adapter_basic_tools_prime_context", result)
    
    # Test unknown tool behavior
    try:
        result = await call_tool("unknown-tool", {"random_string": "test"})
        assert "error" in result
        assert "not supported" in result["error"]
    except Exception as e:
        # If it raises an exception instead of returning an error dict, that's also acceptable
        assert "unknown-tool" in str(e).lower() or "not supported" in str(e).lower()


def test_adapter_get_project_settings():
    """Test the adapter with get-project-settings tool."""
    logger.info("Testing adapter with get-project-settings...")

    # Test get-project-settings
    result = asyncio.run(call_tool("get-project-settings", {}))
    assert result is not None
    assert "project_path" in result
    
    # Log the result
    logger.info(f"get-project-settings result: {result}")
    
    # Save the result for inspection
    save_test_output("adapter_get_project_settings", result)


def test_initialize_ide_rules_with_custom_path(tmp_path):
    """Test the initialize-ide-rules tool with a custom project path using the adapter."""
    logger.info("Testing initialize-ide-rules with custom project path through adapter...")

    # Create a single temporary directory to use as the project path
    test_project_path = tmp_path / "test_ide_project"
    test_project_path.mkdir()

    # Test different IDE values on the same project directory
    for ide in ["cursor", "windsurf", "cline", "copilot"]:
        # Call initialize-ide-rules with the same project path
        result = asyncio.run(
            call_tool(
                "initialize-ide-rules",
                {"ide": ide, "project_path": str(test_project_path)},
            )
        )

        # Verify the result
        assert result["success"] is True

        # Save the response to the test_outputs directory
        save_test_output(f"adapter_initialize_{ide}_rules_response", result)

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
                rule_content = rule_file.read_text(encoding="utf-8")
                save_test_output(f"adapter_{ide}_rules_content", rule_content)

    # After all IDEs have been set up, copy the entire project directory to test_outputs for inspection
    copy_directory_to_outputs(test_project_path, "adapter_unified_project_structure")


def test_initialize_ide_rules_with_root_path():
    """Test that initialize-ide-rules safely handles root paths using the adapter."""
    logger.info("Testing initialize-ide-rules safety with root path through adapter...")

    # Call initialize-ide-rules with root path
    result = asyncio.run(
        call_tool("initialize-ide-rules", {"ide": "cursor", "project_path": "/"})
    )

    # Verify the result - it should fall back to current directory
    assert result["success"] is True
    save_test_output("adapter_initialize_ide_rules_root_path", result)


def test_initialize_ide_rules_with_env_root_path():
    """
    Test that initialize-ide-rules safely handles root paths in environment variables
    using the adapter.
    """
    logger.info("Testing initialize-ide-rules with env root path through adapter...")

    # Save the current PROJECT_PATH environment variable
    original_project_path = os.environ.get("PROJECT_PATH")

    try:
        # Set PROJECT_PATH to the root directory
        os.environ["PROJECT_PATH"] = "/"

        # Call initialize-ide-rules (no project_path argument, it should use PROJECT_PATH)
        result = asyncio.run(
            call_tool("initialize-ide-rules", {"ide": "cursor"})
        )

        # Verify the result - it should fall back to current directory
        assert result["success"] is True
        save_test_output("adapter_initialize_ide_rules_env_root_path", result)

    finally:
        # Restore the original PROJECT_PATH
        if original_project_path is not None:
            os.environ["PROJECT_PATH"] = original_project_path
        else:
            os.environ.pop("PROJECT_PATH", None)


def test_get_project_settings_tool_with_proposed_path():
    """Test the get-project-settings tool with a proposed path using the adapter."""
    logger.info("Testing get-project-settings with proposed path through adapter...")

    # Test with current directory
    result1 = asyncio.run(call_tool("get-project-settings", {}))
    assert "project_path" in result1
    current_path = result1["project_path"]
    logger.info(f"Current project path: {current_path}")

    # Test with parent directory as proposed path
    parent_dir = str(Path(current_path).parent)
    result2 = asyncio.run(
        call_tool("get-project-settings", {"proposed_path": parent_dir})
    )
    assert "project_path" in result2
    assert result2["project_path"] == parent_dir
    logger.info(f"Project path with proposed parent: {result2['project_path']}")

    # Test with root directory as proposed path (should be rejected)
    root_dir = "/"
    result3 = asyncio.run(
        call_tool("get-project-settings", {"proposed_path": root_dir})
    )
    # The result should still be successful but should not use the root directory
    assert "project_path" in result3
    assert result3["project_path"] != root_dir
    logger.info(f"Project path with proposed root: {result3['project_path']}")

    # Save the results
    save_test_output("adapter_get_project_settings_results", {
        "current": result1,
        "parent": result2,
        "root": result3
    })


@pytest.mark.asyncio
async def test_archive_path_tests():
    """Test adapter for the legacy test_root_tool.py file.
    
    This test replaces the deprecated get-safe-project-path tool with get-project-settings
    which is the modern equivalent.
    """
    # Test with no arguments (should use current directory)
    result = await call_tool("get-project-settings", {})
    
    # Log the result
    logger.info(f"get-project-settings with no args result: {result}")
    
    # Check that we got a project path back
    assert "project_path" in result
    assert result["project_path"] is not None
    assert Path(result["project_path"]).exists()
    
    # Test with valid path
    valid_path = os.getcwd()
    result = await call_tool("get-project-settings", {
        "proposed_path": valid_path
    })
    
    # Log the result
    logger.info(f"get-project-settings with valid path result: {result}")
    
    # Check that we got a project path back
    assert "project_path" in result
    assert result["project_path"] == valid_path
    assert Path(result["project_path"]).exists()
    
    # Test with root path, which should be rejected
    result = await call_tool("get-project-settings", {
        "proposed_path": "/"
    })
    
    # Log the result
    logger.info(f"get-project-settings with root path result: {result}")
    
    # Check that the response contains expected fields
    assert "project_path" in result
    assert "is_root" in result
    
    # Check if the root path was rejected and a fallback was used
    assert "source" in result
    assert "fallback" in result["source"].lower()
    
    # Ensure the path was actually safe
    assert result["project_path"] != "/"

@pytest.mark.asyncio
async def test_prime_context_depth_levels():
    """Test prime-context with different depth levels using the adapter."""
    logger.info("Testing prime-context with different depth levels...")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create ai-docs directory
        ai_docs_dir = Path(temp_dir) / "ai-docs"
        ai_docs_dir.mkdir()
        
        # Create a sample PRD file
        prd_content = """# Product Requirements Document

## Overview
Test PRD for prime-context depth testing.

## Features
- Feature 1: Example feature
- Feature 2: Another example feature

## Status
Planning
"""
        
        with open(ai_docs_dir / "prd.md", "w") as f:
            f.write(prd_content)
        
        # Test minimal depth
        minimal_result = await call_tool("prime-context", {
            "depth": "minimal",
            "project_path": temp_dir
        })
        
        # Test standard depth
        standard_result = await call_tool("prime-context", {
            "depth": "standard",
            "project_path": temp_dir
        })
        
        # Test comprehensive depth
        comprehensive_result = await call_tool("prime-context", {
            "depth": "comprehensive",
            "project_path": temp_dir
        })
        
        # Log the results
        logger.info(f"prime-context minimal depth summary length: {len(minimal_result['summary'])}")
        logger.info(f"prime-context standard depth summary length: {len(standard_result['summary'])}")
        logger.info(f"prime-context comprehensive depth summary length: {len(comprehensive_result['summary'])}")
        
        # Verify that increasing depth provides more detailed analysis
        assert len(minimal_result["summary"]) <= len(standard_result["summary"])
        assert len(standard_result["summary"]) <= len(comprehensive_result["summary"])
        
        # Check that PRD content is analyzed at all depths
        assert "project" in minimal_result["context"]
        assert "name" in minimal_result["context"]["project"]
        assert "status" in minimal_result["context"]["project"]
        assert "prd_title" in minimal_result["context"]["project"]
        
        # Verify PRD data is present
        assert minimal_result["context"]["project"]["name"] == "Product Requirements Document"
        assert minimal_result["context"]["project"]["status"] == "Planning"
        assert "Test PRD for prime-context depth testing" in minimal_result["context"]["project"]["overview"]
        
        # Save the results for inspection
        save_test_output("adapter_prime_context_depth_comparison", {
            "minimal": minimal_result,
            "standard": standard_result,
            "comprehensive": comprehensive_result
        })

@pytest.mark.asyncio
async def test_server_imports():
    """Test that server imports succeed and basic functionality works."""
    # Verify handle_call_tool import works
    from src.mcp_agile_flow.server import handle_call_tool
    assert handle_call_tool is not None
    
    # Test module loading
    from src.mcp_agile_flow import server
    assert server is not None
    
    # Test utils import
    from src.mcp_agile_flow import utils
    assert utils is not None
    
    # Test existence of key functions
    assert callable(handle_call_tool)

@pytest.mark.asyncio
async def test_server_handle_call_tool():
    """Test the server's handle_call_tool functionality using the adapter."""
    # Test calling tool with an unknown tool
    unknown_response = await call_tool("unknown-tool", {})
    
    # Check for error response - different implementations have different error patterns
    assert "error" in unknown_response
    # The error could be either "Unknown tool" (server) or "not supported by this adapter" (adapter)
    assert ("Unknown tool" in unknown_response["error"] or 
            "not supported by this adapter" in unknown_response["error"])
    
    # Test calling get-project-settings
    settings_response = await call_tool("get-project-settings", {})
    
    assert "project_path" in settings_response
    assert "current_directory" in settings_response
    assert "ai_docs_directory" in settings_response
    
    # Log the response for debugging
    logger.info(f"get-project-settings response: {settings_response}") 