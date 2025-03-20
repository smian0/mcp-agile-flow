"""
Tests for Business Requirements Document functionality.
"""

import os
import pytest
import datetime
import tempfile
import shutil
from pathlib import Path

from src.mcp_agile_flow.simple_server import create_brd, update_document_status, add_to_brd_section

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(temp_dir)
    
    # Create .ai-templates directory and copy the template
    templates_dir = os.path.join(temp_dir, ".ai-templates")
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create a minimal BRD template for testing
    template_content = """# Business Requirements Document (BRD) for {project-name}

## Document Control
- **Status:** Draft
- **Created:** {date}
- **Last Updated:** {date}
- **Version:** 0.1

## Executive Summary
[Brief overview of the business need and proposed solution]

## Business Objectives
- [Primary business goal 1]
- [Primary business goal 2]

## Market Problem Analysis
- [Problem 1]
- [Problem 2]

## Success Metrics
| Metric | Current Value | Target Value | Measurement Method |
|--------|--------------|-------------|-------------------|
| [Metric 1] | [Value] | [Target] | [Method] |

## Customer Needs
- [Need 1]
- [Need 2]

## Business Constraints
- [Constraint 1]
- [Constraint 2]

## Assumptions
- [Assumption 1]
- [Assumption 2]

## Stakeholders
| Role | Department | Responsibilities |
|------|------------|-----------------|
| [Role] | [Department] | [Responsibilities] |

## Related Documents
- [PRD Link]
- [Other Document Link]
"""
    
    template_path = os.path.join(templates_dir, "template-brd.md")
    with open(template_path, "w") as f:
        f.write(template_content)
    
    yield temp_dir
    
    # Clean up
    os.chdir(cwd)
    shutil.rmtree(temp_dir)

def test_create_brd(temp_dir):
    """Test creating a BRD document."""
    project_name = "Test Project"
    result = create_brd(project_name)
    
    # Check result message
    assert "Created Business Requirements Document" in result
    assert project_name in result
    
    # Check file was created
    brd_path = os.path.join(temp_dir, "ai-docs", "brd.md")
    assert os.path.exists(brd_path)
    
    # Check file content
    with open(brd_path, "r") as f:
        content = f.read()
    
    assert f"# Business Requirements Document (BRD) for {project_name}" in content
    assert "## Document Control" in content
    assert "**Status:** Draft" in content
    
    # Check date was inserted
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    assert f"**Created:** {today}" in content
    assert f"**Last Updated:** {today}" in content

def test_update_brd_status(temp_dir):
    """Test updating the status of a BRD document."""
    # First create a BRD
    project_name = "Test Project"
    create_brd(project_name)
    
    # Now update the status
    new_status = "In Review"
    result = update_document_status("brd", new_status)
    
    # Check result message
    assert "Updated BRD status to" in result
    assert new_status in result
    
    # Check file was updated
    brd_path = os.path.join(temp_dir, "ai-docs", "brd.md")
    with open(brd_path, "r") as f:
        content = f.read()
    
    assert f"**Status:** {new_status}" in content

def test_add_to_brd_section(temp_dir):
    """Test adding content to a BRD section."""
    # First create a BRD
    project_name = "Test Project"
    create_brd(project_name)
    
    # Add a business objective
    objective = "Increase revenue by 20% within the next fiscal year"
    result = add_to_brd_section("Business Objectives", objective)
    
    # Check result message
    assert "Added" in result
    assert "Business Objectives" in result
    assert objective in result
    
    # Check file was updated
    brd_path = os.path.join(temp_dir, "ai-docs", "brd.md")
    with open(brd_path, "r") as f:
        content = f.read()
    
    assert f"- {objective}" in content
    
    # Add a market problem
    problem = "Current solution has poor mobile compatibility"
    result = add_to_brd_section("Market Problem Analysis", problem)
    
    # Check file was updated with both changes
    with open(brd_path, "r") as f:
        content = f.read()
    
    assert f"- {objective}" in content
    assert f"- {problem}" in content

def test_error_handling(temp_dir):
    """Test error handling in BRD functions."""
    # Test updating non-existent BRD
    result = update_document_status("brd", "Approved")
    assert "Error" in result
    assert "not found" in result
    
    # Test adding to non-existent BRD
    result = add_to_brd_section("Business Objectives", "Test objective")
    assert "Error" in result
    assert "Create a BRD first" in result
    
    # Create a BRD and test adding to non-existent section
    create_brd("Test Project")
    result = add_to_brd_section("Invalid Section", "Test content")
    assert "Error" in result
    assert "Section 'Invalid Section' not found" in result 