#!/usr/bin/env python3
"""
Test script for the MCP Agile Flow server.
"""

import json
import subprocess
import time
import sys
from typing import Dict, Any, List, Optional


def send_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Send a request to the MCP server and get the response.
    
    Args:
        request: The JSON-RPC request to send.
        
    Returns:
        The JSON-RPC response, or None if there was an error.
    """
    try:
        # Serialize request to JSON
        request_json = json.dumps(request)
        
        # Start the server process
        server_process = subprocess.Popen(
            ["python3", "server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the request
        server_process.stdin.write(request_json + "\n")
        server_process.stdin.flush()
        
        # Read the response
        response_json = server_process.stdout.readline()
        
        # Close the server
        server_process.terminate()
        server_process.wait()
        
        # Parse the response
        if response_json:
            return json.loads(response_json)
        return None
        
    except Exception as e:
        print(f"Error sending request: {str(e)}")
        return None


def test_list_tools() -> None:
    """Test the list_tools method."""
    request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "list_tools"
    }
    
    print("Testing list_tools...")
    response = send_request(request)
    
    if response and "result" in response and "tools" in response["result"]:
        tools = response["result"]["tools"]
        print(f"Server has {len(tools)} tools:")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")
    else:
        print("Error: Failed to get tools list")
        print(f"Response: {response}")


def test_create_project() -> None:
    """Test the create_project tool."""
    request = {
        "jsonrpc": "2.0",
        "id": "2",
        "method": "call_tool",
        "params": {
            "name": "create_project",
            "arguments": {
                "name": "Test Project",
                "description": "A test project for MCP Agile Flow."
            }
        }
    }
    
    print("\nTesting create_project...")
    response = send_request(request)
    
    if response and "result" in response and "project" in response["result"]:
        project = response["result"]["project"]
        print(f"Created project: {project['name']}")
        print(f"Description: {project['description']}")
        print(f"Documents:")
        for doc in project["documents"]:
            print(f"- {doc['type']}: {doc['path']}")
    else:
        print("Error: Failed to create project")
        print(f"Response: {response}")


if __name__ == "__main__":
    test_list_tools()
    # Test project creation (will create agile-docs directory)
    test_create_project()
