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

# Create loggers
logger = logging.getLogger(__name__)
server_logger = logging.getLogger('mcp_agile_flow.server')

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import from the main package
from src.mcp_agile_flow.simple_server import notes, mcp

def test_server_imports():
    """Test that the server module can be imported."""
    logger.info("Testing server imports...")
    assert mcp is not None

def test_notes_functionality():
    """Test that the notes dictionary works correctly."""
    logger.info("Testing notes functionality...")
    
    # Clear notes
    notes.clear()
    
    # Add a note
    note_name = "test-note"
    note_content = "This is a test note."
    notes[note_name] = note_content
    
    logger.info(f"Added note: {note_name}")
    
    # Check the note was added
    assert note_name in notes
    assert notes[note_name] == note_content

def test_get_project_path_tool():
    """Test the get-project-path tool functionality directly."""
    logger.info("Testing get-project-path tool...")
    
    # Import the handler function
    from src.mcp_agile_flow.simple_server import handle_call_tool
    
    logger.info("Running tool handler...")
    
    # Run the async function and get the result
    result = asyncio.run(handle_call_tool("get-project-path", {}))
    
    # Verify we got a text response
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Get the text content and parse the JSON
    path_info = result[0].text
    path_data = json.loads(path_info)
    
    # Log the paths
    logger.info("\nProject paths from tool:")
    for line in path_info.splitlines():
        logger.info(line)
    
    # Basic verification of the JSON response
    assert "project_path" in path_data
    assert "current_directory" in path_data
    assert os.path.isdir(path_data["project_path"])
    assert os.path.isdir(path_data["current_directory"])

def test_server_handle_call_tool():
    """Test the server's handle_call_tool function."""
    logger.info("Testing server handle_call_tool...")
    
    # Import the handler function
    from src.mcp_agile_flow.simple_server import handle_call_tool, notes
    
    # Clear notes
    notes.clear()
    
    # Test add-note
    result = asyncio.run(handle_call_tool("add-note", {"name": "test-note", "content": "Test content"}))
    assert result[0].type == "text"
    assert "successfully" in result[0].text
    assert notes["test-note"] == "Test content"
    
    # Test get-project-path
    result = asyncio.run(handle_call_tool("get-project-path", {}))
    assert result[0].type == "text"
    path_data = json.loads(result[0].text)
    assert "project_path" in path_data
    
    # Test debug-tools
    result = asyncio.run(handle_call_tool("debug-tools", {}))
    assert result[0].type == "text"
    assert "tool invocations" in result[0].text.lower() 