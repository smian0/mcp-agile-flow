#!/usr/bin/env python3
"""
Test script for the MCP Agile Flow IDE rules generation.
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


def test_generate_cursor_rules() -> None:
    """Test the generate_cursor_rules tool."""
    request = {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "call_tool",
        "params": {
            "name": "generate_cursor_rules",
            "arguments": {}
        }
    }
    
    print("Testing generate_cursor_rules...")
    response = send_request(request)
    
    if response and "result" in response and "rules" in response["result"]:
        rules = response["result"]["rules"]
        print(f"Generated {len(rules)} Cursor rule files:")
        for rule in rules:
            print(f"- {rule}")
    else:
        print("Error: Failed to generate Cursor rules")
        print(f"Response: {response}")


def test_generate_cline_rules() -> None:
    """Test the generate_cline_rules tool."""
    request = {
        "jsonrpc": "2.0",
        "id": "4",
        "method": "call_tool",
        "params": {
            "name": "generate_cline_rules",
            "arguments": {}
        }
    }
    
    print("\nTesting generate_cline_rules...")
    response = send_request(request)
    
    if response and "result" in response and "rules" in response["result"]:
        rules = response["result"]["rules"]
        print(f"Generated {len(rules)} Cline rule files:")
        for rule in rules:
            print(f"- {rule}")
    else:
        print("Error: Failed to generate Cline rules")
        print(f"Response: {response}")


def test_generate_all_rules() -> None:
    """Test the generate_all_rules tool."""
    request = {
        "jsonrpc": "2.0",
        "id": "5",
        "method": "call_tool",
        "params": {
            "name": "generate_all_rules",
            "arguments": {}
        }
    }
    
    print("\nTesting generate_all_rules...")
    response = send_request(request)
    
    if response and "result" in response and "rules" in response["result"]:
        rules = response["result"]["rules"]
        print(f"Generated rules for {len(rules)} IDEs:")
        for ide, ide_rules in rules.items():
            print(f"- {ide}: {len(ide_rules)} rules")
    else:
        print("Error: Failed to generate all rules")
        print(f"Response: {response}")


if __name__ == "__main__":
    test_generate_cursor_rules()
    test_generate_cline_rules()
    test_generate_all_rules()
