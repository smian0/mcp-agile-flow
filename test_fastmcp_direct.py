#!/usr/bin/env python
"""
Test script to verify the streamlined FastMCP server implementation
"""

import json
import sys
from mcp_agile_flow.fastmcp_tools import search_nodes, get_project_settings

def main():
    """Test direct FastMCP function calls"""
    print("Testing direct FastMCP functions...")
    
    # Test search_nodes function
    print("\nTesting search_nodes with query 'TestEntity'...")
    result = search_nodes(query="TestEntity")
    try:
        result_dict = json.loads(result)
        if result_dict.get("success"):
            print(f"✅ search_nodes success: Found {result_dict.get('entities_found')} entities")
            for entity in result_dict.get("entities", []):
                print(f"  - Entity: {entity.get('name')}")
        else:
            print(f"❌ search_nodes failed: {result_dict.get('error')}")
    except json.JSONDecodeError:
        print("❌ Failed to parse search_nodes result as JSON")
    
    # Test get_project_settings function
    print("\nTesting get_project_settings...")
    result = get_project_settings()
    try:
        result_dict = json.loads(result)
        print(f"✅ get_project_settings success: Project path is {result_dict.get('project_path')}")
    except json.JSONDecodeError:
        print("❌ Failed to parse get_project_settings result as JSON")
    
    print("\nDirect function test completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 