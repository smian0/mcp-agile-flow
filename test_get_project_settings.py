#!/usr/bin/env python
"""
Test script for the get-project-settings tool in the MCP Agile Flow Simple Server.
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

async def test_get_project_settings():
    """Test the get-project-settings tool."""
    # Test with specific directories for knowledge graph and AI docs
    test_kg_dir = os.path.join(PROJECT_ROOT, "ai-kngr")
    test_docs_dir = os.path.join(PROJECT_ROOT, "ai-docs")
    
    # Create the directories if they don't exist
    os.makedirs(test_kg_dir, exist_ok=True)
    os.makedirs(test_docs_dir, exist_ok=True)
    
    try:
        # Test with PROJECT_PATH set
        os.environ["PROJECT_PATH"] = PROJECT_ROOT
        
        # Call the tool
        response = await handle_call_tool("get-project-settings", None)
        
        # Print the response
        print("Response with PROJECT_PATH set:")
        for item in response:
            print(item.text)
        
        # Parse the JSON response
        data = json.loads(response[0].text)
        
        # Verify the response format
        assert "project_path" in data, "project_path is missing from the response"
        assert "current_directory" in data, "current_directory is missing from the response"
        assert "is_project_path_manually_set" in data, "is_project_path_manually_set flag is missing from the response"
        assert "knowledge_graph_directory" in data, "knowledge_graph_directory is missing from the response"
        assert "ai_docs_directory" in data, "ai_docs_directory is missing from the response"
        
        assert data["project_path"] == PROJECT_ROOT, "project_path value is incorrect"
        assert data["current_directory"] == os.getcwd(), "current_directory should be the current working directory"
        assert data["is_project_path_manually_set"] is True, "is_project_path_manually_set should be True when PROJECT_PATH is set"
        assert data["knowledge_graph_directory"] == test_kg_dir, "knowledge_graph_directory value is incorrect"
        assert data["ai_docs_directory"] == test_docs_dir, "ai_docs_directory value is incorrect"
        
        # Test without PROJECT_PATH set
        os.environ.pop("PROJECT_PATH", None)
        
        # Call the tool again
        response = await handle_call_tool("get-project-settings", None)
        
        # Print the response
        print("\nResponse without PROJECT_PATH set:")
        for item in response:
            print(item.text)
        
        # Parse the JSON response
        data = json.loads(response[0].text)
        
        # Verify the response format
        assert "project_path" in data, "project_path is missing from the response"
        assert "current_directory" in data, "current_directory is missing from the response"
        assert "is_project_path_manually_set" in data, "is_project_path_manually_set flag is missing from the response"
        assert "knowledge_graph_directory" in data, "knowledge_graph_directory is missing from the response"
        assert "ai_docs_directory" in data, "ai_docs_directory is missing from the response"
        
        assert data["project_path"] == os.getcwd(), "project_path should default to current working directory"
        assert data["current_directory"] == os.getcwd(), "current_directory should be the current working directory"
        assert data["is_project_path_manually_set"] is False, "is_project_path_manually_set should be False when PROJECT_PATH is not set"
        
        # Now test with directories removed
        # Remove the test directories
        for test_dir in [test_kg_dir, test_docs_dir]:
            try:
                if os.path.exists(test_dir):
                    for file in os.listdir(test_dir):
                        file_path = os.path.join(test_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    os.rmdir(test_dir)
            except Exception as e:
                print(f"Warning: Could not remove test directory {test_dir}: {e}")
        
        # Call the tool again with directories removed
        response = await handle_call_tool("get-project-settings", None)
        
        # Print the response
        print("\nResponse with directories removed:")
        for item in response:
            print(item.text)
        
        # Parse the JSON response
        data = json.loads(response[0].text)
        
        # Verify that proper directory paths with suffixes are used
        expected_kg_dir = os.path.join(PROJECT_ROOT, "ai-kngr")
        assert data["knowledge_graph_directory"] == expected_kg_dir, "knowledge_graph_directory should have ai-kngr suffix"
        
        # Check if the docs directory exists in the project root
        docs_dir = os.path.join(PROJECT_ROOT, "docs")
        if os.path.exists(docs_dir):
            assert data["ai_docs_directory"] == docs_dir, "ai_docs_directory should use existing docs directory"
        else:
            expected_docs_dir = os.path.join(PROJECT_ROOT, "ai-docs")
            assert data["ai_docs_directory"] == expected_docs_dir, "ai_docs_directory should have ai-docs suffix"
        
        print("\nTest passed! The get-project-settings tool returns comprehensive project settings with appropriate defaults.")
    
    finally:
        # Clean up test directories
        try:
            # Remove any files in the test directories
            for test_dir in [test_kg_dir, test_docs_dir]:
                if os.path.exists(test_dir):
                    for file in os.listdir(test_dir):
                        file_path = os.path.join(test_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    os.rmdir(test_dir)
        except Exception as e:
            print(f"Warning: Could not clean up test directories: {e}")

if __name__ == "__main__":
    asyncio.run(test_get_project_settings())
