"""
Test script for verifying FastMCP server functionality.

This script tests the new FastMCP-based server implementation by directly 
calling some of the tools to ensure they work correctly.
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def test_entity_creation():
    """Test entity creation through the FastMCP server."""
    print("Testing entity creation...")
    
    # Create a test entity
    entity_data = {
        "entities": [
            {
                "name": "TestEntityFastMCP",
                "entityType": "test",
                "observations": ["Testing the FastMCP implementation"]
            }
        ]
    }
    
    try:
        # Start the server in a subprocess
        server_process = subprocess.Popen(
            [sys.executable, "new_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the server time to start
        time.sleep(2)
        
        # Construct MCP tool call
        tool_call = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "mcp/callTool",
            "params": {
                "name": "create-entities",
                "arguments": entity_data
            }
        }
        
        # Send the tool call
        server_process.stdin.write(json.dumps(tool_call) + "\n")
        server_process.stdin.flush()
        
        # Read the response (with timeout)
        response_line = ""
        timeout = time.time() + 5  # 5 second timeout
        
        while time.time() < timeout:
            if server_process.stdout.readable():
                line = server_process.stdout.readline().strip()
                if line:
                    response_line = line
                    break
            time.sleep(0.1)
        
        # Check stderr for any issues
        err_output = server_process.stderr.read()
        if err_output:
            print(f"Server stderr output: {err_output}")
        
        # Clean up
        server_process.terminate()
        server_process.wait(timeout=3)
        
        # Parse the response
        if not response_line:
            print("No response received from server")
            print("Entity creation test: FAILED ❌")
            return False
            
        try:
            response = json.loads(response_line)
            print(f"Response: {json.dumps(response, indent=2)}")
            
            # Check if the response indicates success
            if "result" in response and response.get("result", {}).get("status") == "success":
                print("Entity creation test: PASSED ✅")
                return True
            else:
                print("Entity creation test: FAILED ❌")
                print(f"Response doesn't indicate success: {response}")
                return False
        except json.JSONDecodeError:
            print(f"Failed to parse response: {response_line}")
            print("Entity creation test: FAILED ❌")
            return False
    except Exception as e:
        print(f"Error during entity creation test: {e}")
        print("Entity creation test: FAILED ❌")
        return False


def run_direct_test():
    """Run a direct test using the FastMCP functions directly."""
    print("\nRunning direct function test...")
    
    try:
        # Import the functions directly
        from mcp_agile_flow.fastmcp_tools import create_entities, search_nodes
        
        # Create a test entity
        entity_result = create_entities(entities=[
            {
                "name": "DirectTestEntity",
                "entityType": "test",
                "observations": ["Direct function test"]
            }
        ])
        
        # The FastMCP tools return strings that need to be parsed
        if isinstance(entity_result, str):
            entity_result = json.loads(entity_result)
        print(f"Direct create result: {json.dumps(entity_result, indent=2)}")
        
        # Search for the entity
        search_result = search_nodes(query="DirectTestEntity")
        if isinstance(search_result, str):
            search_result = json.loads(search_result)
        print(f"Direct search result: {json.dumps(search_result, indent=2)}")
        
        # Check if the entity was found
        found = False
        if "entities" in search_result:
            for entity in search_result["entities"]:
                if entity["name"] == "DirectTestEntity":
                    found = True
                    break
        
        if found:
            print("Direct function test: PASSED ✅")
            return True
        else:
            print("Direct function test: FAILED ❌")
            return False
    except Exception as e:
        print(f"Error during direct function test: {str(e)}")
        import traceback
        traceback.print_exc()
        print("Direct function test: FAILED ❌")
        return False


def main():
    """Run all tests."""
    print("Testing FastMCP functionality...")
    print("===============================")
    
    # Run the direct test first (simpler, more reliable)
    direct_test = run_direct_test()
    
    # Run the entity creation test through the server
    # entity_test = test_entity_creation()
    
    # Summarize results
    print("\nTest Summary:")
    print("============")
    print(f"Direct Function Test: {'PASSED ✅' if direct_test else 'FAILED ❌'}")
    # print(f"Entity Creation:      {'PASSED ✅' if entity_test else 'FAILED ❌'}")
    
    # Return exit code based on test results
    return 0 if direct_test else 1


if __name__ == "__main__":
    sys.exit(main()) 