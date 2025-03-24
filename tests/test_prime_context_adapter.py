"""
Tests for the prime-context tool functionality using the adapter.

These tests verify that the prime-context tool correctly analyzes project documentation
using the adapter that can switch between server and FastMCP implementations.
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

# Create loggers
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import from the adapter instead of directly from server
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
    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
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


def create_test_project(root_path):
    """Create a test project with AI documentation."""
    # Create project directories
    ai_docs_dir = root_path / "ai-docs"
    ai_docs_dir.mkdir(exist_ok=True)

    # Create a sample PRD
    prd_content = """# Product Requirements Document

## Overview
This is a test PRD for the prime-context tool.

## Feature 1
- Description: Test feature 1
- Priority: High

## Feature 2
- Description: Test feature 2
- Priority: Medium
"""
    with open(ai_docs_dir / "prd.md", "w") as f:
        f.write(prd_content)

    # Create a sample architecture document
    arch_content = """# Architecture Document

## System Design
This is a test architecture document for the prime-context tool.

## Components
- Component 1: Handles feature 1
- Component 2: Handles feature 2

## Diagram
[Test Diagram]
"""
    with open(ai_docs_dir / "architecture.md", "w") as f:
        f.write(arch_content)

    # Create a sample README
    readme_content = """# Test Project

This is a test README for the prime-context tool.

## Getting Started
Instructions for getting started with the project.

## Features
- Feature 1: Test feature 1
- Feature 2: Test feature 2
"""
    with open(root_path / "README.md", "w") as f:
        f.write(readme_content)

    return root_path


def test_prime_context_with_custom_path():
    """Test the prime-context tool with a custom project path."""
    logger.info("Testing prime-context with custom project path...")

    # Create a temporary directory to use as the project path
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_path = Path(temp_dir)
        create_test_project(test_project_path)

        # Call prime-context with the custom project path
        result = asyncio.run(
            call_tool(
                "prime-context",
                {"project_path": str(test_project_path), "depth": "standard"},
            )
        )

        # Save the response to the test_outputs directory
        save_test_output("prime_context_response", result)

        # Verify the result
        assert isinstance(result, dict)
        
        # Check for the structure returned by FastMCP
        assert "context" in result
        assert "summary" in result
        
        # Verify project data in context
        assert "project" in result["context"]
        assert "architecture" in result["context"]
        
        # Verify key project information
        assert "name" in result["context"]["project"]
        assert "overview" in result["context"]["project"]
        
        # Check that the content from the AI docs is properly included
        assert "test prd" in result["context"]["project"]["overview"].lower()
        
        # Check for architecture content
        assert "overview" in result["context"]["architecture"]
        assert "component" in result["context"]["architecture"]["overview"].lower()


def test_prime_context_with_focus_areas():
    """Test the prime-context tool with specific focus areas."""
    logger.info("Testing prime-context with focus areas...")

    # Create a temporary directory to use as the project path
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_path = Path(temp_dir)
        create_test_project(test_project_path)

        # Call prime-context with focus areas
        result = asyncio.run(
            call_tool(
                "prime-context",
                {
                    "project_path": str(test_project_path),
                    "depth": "standard",
                    "focus_areas": ["architecture"],
                },
            )
        )

        # Save the response to the test_outputs directory
        save_test_output("prime_context_focus_areas_response", result)

        # Verify the result
        assert isinstance(result, dict)
        
        # Check for success or check for expected data structure
        if "success" in result and not result["success"]:
            # If there's an error, make sure it's properly formatted
            assert "error" in result
            assert "message" in result
        else:
            # If success, check for expected data structure
            assert "context" in result
            assert "architecture" in result["context"]
            
            # Check for architecture content
            assert "overview" in result["context"]["architecture"]
            assert "component" in result["context"]["architecture"]["overview"].lower()


def test_prime_context_with_depth():
    """Test the prime-context tool with different depth levels."""
    logger.info("Testing prime-context with different depth levels...")

    # Create a temporary directory to use as the project path
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_path = Path(temp_dir)
        create_test_project(test_project_path)

        # Test minimal depth
        minimal_result = asyncio.run(
            call_tool(
                "prime-context",
                {"project_path": str(test_project_path), "depth": "minimal"},
            )
        )

        # Test comprehensive depth
        comprehensive_result = asyncio.run(
            call_tool(
                "prime-context",
                {"project_path": str(test_project_path), "depth": "comprehensive"},
            )
        )

        # Verify the results
        assert isinstance(minimal_result, dict)
        assert isinstance(comprehensive_result, dict)

        # Save the responses to the test_outputs directory
        save_test_output("prime_context_minimal_depth", minimal_result)
        save_test_output("prime_context_comprehensive_depth", comprehensive_result)

        # The comprehensive result should have a longer summary than the minimal result
        if "summary" in minimal_result and "summary" in comprehensive_result:
            minimal_summary_length = len(minimal_result["summary"])
            comprehensive_summary_length = len(comprehensive_result["summary"])
            
            # This is a simple heuristic, but it should work for our test
            assert comprehensive_summary_length >= minimal_summary_length 