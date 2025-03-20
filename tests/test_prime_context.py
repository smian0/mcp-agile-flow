"""
Integration tests for the prime-context tool in MCP Agile Flow.

This module tests the prime-context tool, which analyzes project AI documentation
to provide contextual understanding.
"""
import asyncio
import json
import sys
import pytest
import os
import logging
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

# Create logger
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

def setup_test_data(test_dir: str) -> str:
    """Set up test data for the prime-context tool."""
    logger.info(f"Test data set up in: {test_dir}")
    
    # Create necessary directories
    ai_docs_dir = os.path.join(test_dir, "ai-docs")
    os.makedirs(ai_docs_dir, exist_ok=True)
    epics_dir = os.path.join(ai_docs_dir, "epics")
    os.makedirs(epics_dir, exist_ok=True)
    
    # Create a README.md file in the project root
    root_readme_path = os.path.join(test_dir, "README.md")
    with open(root_readme_path, 'w') as f:
        f.write("""# Test Project README

## Overview
This is a test project for evaluating the prime-context tool.

## Installation
1. Clone the repository
2. Install dependencies
3. Run the application

## Status
Active
""")
    
    # Create a Makefile in the project root
    makefile_path = os.path.join(test_dir, "Makefile")
    with open(makefile_path, 'w') as f:
        f.write("""# Test Project Makefile

.PHONY: test build run clean lint deploy

test:
	pytest tests/

build:
	pip install -e .

run:
	python run_server.py

clean:
	rm -rf build/ dist/ *.egg-info

lint:
	flake8 src/ tests/

deploy:
	python setup.py sdist bdist_wheel
	twine upload dist/*
""")
    
    # Create a PRD file
    prd_path = os.path.join(ai_docs_dir, "prd.md")
    with open(prd_path, 'w') as f:
        f.write("""# Test Project

## Status
In Progress

## Overview
This is a test project for evaluating the prime-context tool.

## Project Goals
- Goal 1
- Goal 2
- Goal 3

## User Stories
- Story 1
- Story 2
""")
    
    # Create an architecture document
    arch_path = os.path.join(ai_docs_dir, "architecture.md")
    with open(arch_path, 'w') as f:
        f.write("""# Architecture Document

## Status
In Progress

## Overview
This is the architecture document for the test project.

## Component Design
- Component 1
- Component 2
""")
    
    # Create a test epic
    epic_dir = os.path.join(epics_dir, "epic-1-test")
    os.makedirs(epic_dir, exist_ok=True)
    stories_dir = os.path.join(epic_dir, "stories")
    os.makedirs(stories_dir, exist_ok=True)
    
    # Create an epic file
    epic_path = os.path.join(epic_dir, "epic.md")
    with open(epic_path, 'w') as f:
        f.write("""# Test Epic

## Status
In Progress

## Overview
This is a test epic for evaluating the prime-context tool.

## Stories
- Story 1
- Story 2
""")
    
    # Create story files
    story1_path = os.path.join(stories_dir, "story-1.md")
    with open(story1_path, 'w') as f:
        f.write("""# Test Story 1

## Status
Complete

## Overview
This is a completed test story.

## Tasks
- [x] Task 1
- [x] Task 2
""")
    
    story2_path = os.path.join(stories_dir, "story-2.md")
    with open(story2_path, 'w') as f:
        f.write("""# Test Story 2

## Status
In Progress

## Overview
This is an in-progress test story.

## Tasks
- [x] Task 1
- [ ] Task 2
- [ ] Task 3
""")
    
    return test_dir

@pytest.fixture
def test_project_dir():
    """Fixture to create and clean up a test project directory."""
    # Create a temporary test directory
    test_dir = tempfile.mkdtemp(prefix="mcp_prime_context_test_")
    
    # Set up the test data
    setup_test_data(test_dir)
    
    # Set PROJECT_PATH environment variable to test directory
    original_project_path = os.environ.get("PROJECT_PATH")
    os.environ["PROJECT_PATH"] = test_dir
    
    yield test_dir
    
    # Clean up
    shutil.rmtree(test_dir)
    
    # Restore original PROJECT_PATH
    if original_project_path:
        os.environ["PROJECT_PATH"] = original_project_path
    else:
        os.environ.pop("PROJECT_PATH", None)

def test_prime_context_standard_depth(test_project_dir):
    """Test the prime-context tool with standard depth."""
    logger.info("Testing prime-context with standard depth...")
    
    # Define arguments
    arguments = {
        "project_path": test_project_dir,
        "depth": "standard"
    }
    
    # Call the prime-context tool
    result = asyncio.run(handle_call_tool("prime-context", arguments))
    
    # Verify we got a text response
    assert result[0].type == "text"
    
    # Get the text content and parse the JSON
    response_text = result[0].text
    response_data = json.loads(response_text)
    
    # Save the response to the test_outputs directory
    save_test_output("prime_context_standard", response_data)
    
    # Basic verification
    assert "context" in response_data
    assert "summary" in response_data
    
    # Context validation
    context = response_data["context"]
    assert "project" in context
    assert "architecture" in context
    assert "epics" in context
    assert "progress" in context
    
    # Project details validation
    assert context["project"]["name"] == "Test Project"  # From PRD title
    assert context["project"]["status"] == "In Progress"  # From PRD status
    
    # Verify both PRD and README information is included
    assert "readme" in context["project"]
    assert context["project"]["readme"] is not None
    assert "Test Project README" in context["project"]["readme"]
    
    # Verify PRD information is stored
    assert "prd_title" in context["project"]
    assert "prd_status" in context["project"]
    assert "prd_overview" in context["project"]
    
    # README should be included in the summary
    assert "From Project README" in response_data["summary"]
    
    # Epic validation
    assert context["epics"][0]["name"] == "Test Epic"
    assert context["epics"][0]["status"] == "In Progress"
    assert len(context["epics"][0]["stories"]) == 0  # standard depth doesn't include stories

    # Should not include comprehensive detail like task completion percentages
    if "current_story" in context and context["current_story"] is not None:
        assert "completion" in context["current_story"]

def test_prime_context_minimal_depth(test_project_dir):
    """Test the prime-context tool with minimal depth."""
    logger.info("Testing prime-context with minimal depth...")
    
    # Define arguments
    arguments = {
        "project_path": test_project_dir,
        "depth": "minimal"
    }
    
    # Call the prime-context tool
    result = asyncio.run(handle_call_tool("prime-context", arguments))
    
    # Verify we got a text response
    assert result[0].type == "text"
    
    # Get the text content and parse the JSON
    response_text = result[0].text
    response_data = json.loads(response_text)
    
    # Save the response to the test_outputs directory
    save_test_output("prime_context_minimal", response_data)
    
    # Verify minimal depth provides less content
    standard_result = asyncio.run(handle_call_tool("prime-context", {
        "project_path": test_project_dir,
        "depth": "standard"
    }))
    standard_data = json.loads(standard_result[0].text)
    
    # Minimal should be shorter than standard
    assert len(response_data["summary"]) < len(standard_data["summary"])

def test_prime_context_focus_areas(test_project_dir):
    """Test the prime-context tool with focus areas."""
    logger.info("Testing prime-context with focus areas...")
    
    # Define arguments to focus only on project information
    arguments = {
        "project_path": test_project_dir,
        "depth": "standard",
        "focus_areas": ["project"]
    }
    
    # Call the prime-context tool
    result = asyncio.run(handle_call_tool("prime-context", arguments))
    
    # Verify we got a text response
    assert result[0].type == "text"
    
    # Get the text content and parse the JSON
    response_text = result[0].text
    response_data = json.loads(response_text)
    
    # Save the response to the test_outputs directory
    save_test_output("prime_context_focus", response_data)
    
    # Verify only project data is returned
    assert "context" in response_data
    assert "project" in response_data["context"]
    
    # Should only have the project field, not architecture, epics, etc.
    assert len(response_data["context"]) == 1
    
    # Project details validation
    assert response_data["context"]["project"]["name"] == "Test Project"  # From PRD title
    assert response_data["context"]["project"]["status"] == "In Progress"

def test_prime_context_comprehensive_depth(test_project_dir):
    """Test the prime-context tool with comprehensive depth."""
    logger.info("Testing prime-context with comprehensive depth...")
    
    # Define arguments
    arguments = {
        "project_path": test_project_dir,
        "depth": "comprehensive"
    }
    
    # Call the prime-context tool
    result = asyncio.run(handle_call_tool("prime-context", arguments))
    
    # Verify we got a text response
    assert result[0].type == "text"
    
    # Get the text content and parse the JSON
    response_text = result[0].text
    response_data = json.loads(response_text)
    
    # Save the response to the test_outputs directory
    save_test_output("prime_context_comprehensive", response_data)
    
    # Verify comprehensive depth provides more content
    standard_result = asyncio.run(handle_call_tool("prime-context", {
        "project_path": test_project_dir,
        "depth": "standard"
    }))
    standard_data = json.loads(standard_result[0].text)
    
    # Comprehensive should be longer than standard
    assert len(response_data["summary"]) >= len(standard_data["summary"])

def test_prime_context_missing_docs(tmp_path):
    """Test the prime-context tool with missing documentation."""
    logger.info("Testing prime-context with missing documentation...")
    
    # Create an empty directory with no AI docs
    test_dir = tmp_path / "empty_project"
    test_dir.mkdir()
    
    # Define arguments
    arguments = {
        "project_path": str(test_dir),
        "depth": "standard"
    }
    
    # Call the prime-context tool
    result = asyncio.run(handle_call_tool("prime-context", arguments))
    
    # Verify we got an error response
    assert result[0].type == "text"
    assert result[0].isError == True
    
    # Error message should mention missing AI docs directory
    assert "AI docs directory not found" in result[0].text 

def test_prime_context_readme_fallback(test_project_dir):
    """Test the prime-context tool with README when no PRD exists."""
    logger.info("Testing prime-context with README when no PRD...")

    # Remove the PRD file
    prd_path = os.path.join(test_project_dir, "ai-docs", "prd.md")
    if os.path.exists(prd_path):
        os.remove(prd_path)

    # Define arguments
    arguments = {
        "project_path": test_project_dir,
        "depth": "standard"
    }

    # Call the prime-context tool
    result = asyncio.run(handle_call_tool("prime-context", arguments))

    # Verify we got a text response
    assert result[0].type == "text"

    # Get the text content and parse the JSON
    response_text = result[0].text
    response_data = json.loads(response_text)

    # Save the response to the test_outputs directory
    save_test_output("prime_context_readme_fallback", response_data)

    # Project details validation
    context = response_data["context"]

    # Should use README content as overview when PRD is missing
    assert context["project"]["readme"] is not None
    assert context["project"]["overview"] == context["project"]["readme"]
    assert "Test Project README" in context["project"]["overview"]

    # Should extract status from README
    assert context["project"]["status"] == "Active"

    # Should have created a reasonable summary
    assert "summary" in response_data
    assert "Test Project README" in response_data["summary"]

def test_prime_context_ai_docs_readme_priority(test_project_dir):
    """Test that both PRD and README contribute to project information."""
    logger.info("Testing PRD and README contribution...")

    # First test with the PRD present
    # Define arguments
    arguments = {
        "project_path": test_project_dir,
        "depth": "standard"
    }

    # Call the prime-context tool
    result = asyncio.run(handle_call_tool("prime-context", arguments))
    
    # Get the text content and parse the JSON
    response_text = result[0].text
    response_data = json.loads(response_text)
    
    # Verify with PRD present - both sources should be included
    context = response_data["context"]
    assert context["project"]["name"] == "Test Project"  # From PRD
    assert context["project"]["status"] == "In Progress"  # From PRD
    assert "readme" in context["project"]  # Should have README
    assert "prd_title" in context["project"]  # Should have PRD title stored
    assert "prd_status" in context["project"]  # Should have PRD status stored
    assert "prd_overview" in context["project"]  # Should have PRD overview stored
    
    # Save the response
    save_test_output("prime_context_prd_priority", response_data)
    
    # Remove the PRD file and test again
    prd_path = os.path.join(test_project_dir, "ai-docs", "prd.md")
    os.remove(prd_path)
    
    # Call the prime-context tool again
    result = asyncio.run(handle_call_tool("prime-context", arguments))
    response_text = result[0].text
    response_data = json.loads(response_text)
    
    # Verify behavior with no PRD
    context = response_data["context"]
    
    # README should be used for project info when no PRD
    assert context["project"]["readme"] is not None
    assert context["project"]["name"] == "Test Project README"  # From README
    assert context["project"]["status"] == "Active"  # From README
    assert context["project"]["overview"] == context["project"]["readme"]
    
    # The summary should contain the README
    assert "From Project README" in response_data["summary"] 

def test_prime_context_makefile_extraction(test_project_dir):
    """Test that the prime-context tool extracts and categorizes Makefile commands."""
    logger.info("Testing Makefile command extraction...")
    
    # Define arguments
    arguments = {
        "project_path": test_project_dir,
        "depth": "standard"
    }
    
    # Call the prime-context tool
    result = asyncio.run(handle_call_tool("prime-context", arguments))
    
    # Verify we got a text response
    assert result[0].type == "text"
    
    # Get the text content and parse the JSON
    response_text = result[0].text
    response_data = json.loads(response_text)
    
    # Save the response to the test_outputs directory
    save_test_output("prime_context_makefile", response_data)
    
    # Verify Makefile commands are extracted and categorized
    context = response_data["context"]
    assert "project" in context
    assert "makefile_commands" in context["project"]
    
    makefile_commands = context["project"]["makefile_commands"]
    
    # Verify the categorization of common command types
    assert "testing" in makefile_commands
    assert "build" in makefile_commands
    assert "run" in makefile_commands
    assert "clean" in makefile_commands
    assert "lint" in makefile_commands
    assert "deploy" in makefile_commands
    
    # Verify the commands are correctly extracted
    assert makefile_commands["testing"][0]["target"] == "test"
    assert "pytest tests/" in makefile_commands["testing"][0]["command"]
    
    assert makefile_commands["build"][0]["target"] == "build"
    assert "pip install" in makefile_commands["build"][0]["command"]
    
    assert makefile_commands["run"][0]["target"] == "run"
    assert "python run_server.py" in makefile_commands["run"][0]["command"]
    
    # Verify Makefile commands appear in the summary
    summary = response_data["summary"]
    assert "Project Commands (from Makefile)" in summary
    assert "Testing Commands" in summary
    assert "Build Commands" in summary
    assert "Run Commands" in summary 