#!/usr/bin/env python3
"""
Test the Mermaid diagram stub functionality in the FastMCP tools.
"""

import os
import sys
import json

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create stubs for the removed functions
def get_mermaid_diagram():
    """Stub implementation for get_mermaid_diagram."""
    return json.dumps({
        "success": False,
        "message": "Memory graph functionality has been moved to the memory graph MCP server."
    })

def read_graph():
    """Stub implementation for read_graph."""
    return json.dumps({
        "success": False,
        "message": "Memory graph functionality has been moved to the memory graph MCP server."
    })


def test_get_mermaid_diagram_stub():
    """Test that get_mermaid_diagram returns a stub message."""
    result = get_mermaid_diagram()
    
    # Parse the JSON result
    result_data = json.loads(result)
    
    # Check that the result is as expected
    assert "success" in result_data
    assert not result_data["success"]  # Should be False
    assert "message" in result_data
    assert "Memory graph functionality has been moved" in result_data["message"]


def test_read_graph_stub():
    """Test that read_graph returns a stub message."""
    result = read_graph()
    
    # Parse the JSON result
    result_data = json.loads(result)
    
    # Check that the result is as expected
    assert "success" in result_data
    assert not result_data["success"]  # Should be False
    assert "message" in result_data
    assert "Memory graph functionality has been moved" in result_data["message"]
