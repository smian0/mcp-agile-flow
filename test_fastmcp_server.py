"""
Test script for verifying FastMCP server functionality.

This script tests the FastMCP server implementation by directly 
calling functions from fastmcp_tools.py.
"""

import json
import sys


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
    
    # Run the direct test
    direct_test = run_direct_test()
    
    # Summarize results
    print("\nTest Summary:")
    print("============")
    print(f"Direct Function Test: {'PASSED ✅' if direct_test else 'FAILED ❌'}")
    
    # Return exit code based on test results
    return 0 if direct_test else 1


if __name__ == "__main__":
    sys.exit(main()) 