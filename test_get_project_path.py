#!/usr/bin/env python
"""
Test script for the get-project-path tool in the MCP Agile Flow Simple Server.
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# Ensure the src directory is in the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    sys.path.insert(0, SRC_DIR)

# Import the handle_call_tool function
from mcp_agile_flow.simple_server import handle_call_tool

async def test_get_project_path():
    """Test the get-project-path tool."""
    # Test with PROJECT_PATH set
    os.environ["PROJECT_PATH"] = "/test/project/path"
    
    # Call the tool
    response = await handle_call_tool("get-project-path", None)
    
    # Print the response
    print("Response with PROJECT_PATH set:")
    for item in response:
        print(item.text)
    
    # Parse the JSON response
    data = json.loads(response[0].text)
    
    # Verify the response format
    assert "project_path" in data, "project_path is missing from the response"
    assert "current_directory" in data, "current_directory is missing from the response"
    assert "is_manually_set" in data, "is_manually_set flag is missing from the response"
    assert data["project_path"] == "/test/project/path", "project_path value is incorrect"
    assert data["current_directory"] == os.getcwd(), "current_directory should be the current working directory"
    assert data["is_manually_set"] is True, "is_manually_set should be True when PROJECT_PATH is set"
    
    # Test without PROJECT_PATH set
    os.environ.pop("PROJECT_PATH", None)
    
    # Call the tool again
    response = await handle_call_tool("get-project-path", None)
    
    # Print the response
    print("\nResponse without PROJECT_PATH set:")
    for item in response:
        print(item.text)
    
    # Parse the JSON response
    data = json.loads(response[0].text)
    
    # Verify the response format
    assert "project_path" in data, "project_path is missing from the response"
    assert "current_directory" in data, "current_directory is missing from the response"
    assert "is_manually_set" in data, "is_manually_set flag is missing from the response"
    assert data["project_path"] == os.getcwd(), "project_path should default to current working directory"
    assert data["current_directory"] == os.getcwd(), "current_directory should be the current working directory"
    assert data["is_manually_set"] is False, "is_manually_set should be False when PROJECT_PATH is not set"
    
    print("\nTest passed! The get-project-path tool now returns project_path, current_directory, and is_manually_set flag.")

if __name__ == "__main__":
    asyncio.run(test_get_project_path())
