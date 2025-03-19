#!/usr/bin/env python
"""
Test script for MCP server

This script simulates a client calling the MCP server's hello-world tool.
It communicates with the server over stdin/stdout.
"""
import asyncio
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional

# Unique message IDs
REQUEST_ID = 1

async def run_test():
    """Run the MCP server test."""
    # Start the server process
    server_process = subprocess.Popen(
        ["python", "run_simple_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": REQUEST_ID,
            "method": "initialize",
            "params": {
                "client_name": "MCP Test Client",
                "client_version": "1.0.0",
            }
        }
        
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        # Read initialization response
        init_response = json.loads(await asyncio.get_event_loop().run_in_executor(
            None, server_process.stdout.readline
        ))
        print("Initialization response:", json.dumps(init_response, indent=2))
        
        # Send list tools request
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": REQUEST_ID + 1,
            "method": "listTools",
            "params": {}
        }
        
        server_process.stdin.write(json.dumps(list_tools_request) + "\n")
        server_process.stdin.flush()
        
        # Read list tools response
        list_tools_response = json.loads(await asyncio.get_event_loop().run_in_executor(
            None, server_process.stdout.readline
        ))
        print("List tools response:", json.dumps(list_tools_response, indent=2))
        
        # Send call tool request for hello-world
        call_tool_request = {
            "jsonrpc": "2.0",
            "id": REQUEST_ID + 2,
            "method": "callTool",
            "params": {
                "name": "hello-world",
                "arguments": {}
            }
        }
        
        server_process.stdin.write(json.dumps(call_tool_request) + "\n")
        server_process.stdin.flush()
        
        # Read call tool response
        call_tool_response = json.loads(await asyncio.get_event_loop().run_in_executor(
            None, server_process.stdout.readline
        ))
        print("Call tool response:", json.dumps(call_tool_response, indent=2))

        # Test succeeded
        print("\n✅ Test succeeded! The server is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        # Print any error output from the server
        error_output = server_process.stderr.read()
        if error_output:
            print(f"Server error output: {error_output}")
        return False
        
    finally:
        # Terminate the server process
        server_process.terminate()
        try:
            server_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            server_process.kill()

if __name__ == "__main__":
    print("🔍 Testing MCP server...")
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1) 