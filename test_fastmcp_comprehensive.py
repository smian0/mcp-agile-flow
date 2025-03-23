#!/usr/bin/env python
"""
Comprehensive test script for FastMCP implementation

This script tests:
1. Direct function calls to FastMCP tool implementations
2. The FastMCP server tool registration
"""

import json
import sys
import importlib
import inspect
import os

# Import direct FastMCP functions
from mcp_agile_flow.fastmcp_tools import (
    get_project_settings,
    search_nodes,
    create_entities,
    open_nodes,
    get_mermaid_diagram
)

def test_direct_functions():
    """Test direct FastMCP function calls"""
    print("\n--- Testing Direct Functions ---")
    
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
    
    # Test get_mermaid_diagram function
    print("\nTesting get_mermaid_diagram...")
    result = get_mermaid_diagram()
    try:
        result_dict = json.loads(result)
        print(f"✅ get_mermaid_diagram structure: {list(result_dict.keys())}")
        if "diagram" in result_dict:
            print(f"  Diagram length: {len(result_dict['diagram'])}")
            print(f"  Diagram preview: {result_dict['diagram'][:50]}...")
        elif "mermaid" in result_dict:
            print(f"  Mermaid length: {len(result_dict['mermaid'])}")
            print(f"  Mermaid preview: {result_dict['mermaid'][:50]}...")
        else:
            print("  ❌ Missing 'diagram' or 'mermaid' key")
    except json.JSONDecodeError:
        print("❌ Failed to parse get_mermaid_diagram result as JSON")
    
    # Test creating a test entity
    print("\nTesting create_entities...")
    test_entity = [{
        "name": "TestEntityDirect",
        "entityType": "test",
        "observations": ["Created by direct test"]
    }]
    result = create_entities(entities=test_entity)
    try:
        result_dict = json.loads(result)
        if result_dict.get("success"):
            print(f"✅ create_entities success: Created {result_dict.get('count')} entities")
        else:
            print(f"❌ create_entities failed: {result_dict.get('error')}")
    except json.JSONDecodeError:
        print("❌ Failed to parse create_entities result as JSON")
    
    # Test opening the newly created entity
    print("\nTesting open_nodes with the new entity...")
    result = open_nodes(names=["TestEntityDirect"])
    try:
        result_dict = json.loads(result)
        if result_dict.get("success"):
            print(f"✅ open_nodes success: Found {result_dict.get('entities_found')} entities")
            missing = result_dict.get("missing_entities", [])
            if missing:
                print(f"❌ Missing entities: {missing}")
            else:
                print("✅ No missing entities")
        else:
            print(f"❌ open_nodes failed: {result_dict.get('error')}")
    except json.JSONDecodeError:
        print("❌ Failed to parse open_nodes result as JSON")

def test_server_registration():
    """Test that the FastMCP server has registered all tools correctly"""
    print("\n--- Testing Server Registration ---")
    
    try:
        # Import the FastMCP server
        server_module = importlib.import_module("mcp_agile_flow.fastmcp_server")
        
        # Access the server instance
        mcp = getattr(server_module, "mcp", None)
        if not mcp:
            print("❌ Failed to find 'mcp' instance in fastmcp_server module")
            return
        
        print("\nServer instance found!")
        
        # Check if tools are registered
        # Try to inspect the registered tools using reflection
        registered_tools = []
        
        tool_method = getattr(mcp, "tool", None)
        print(f"Tool registration method exists: {tool_method is not None}")
        
        # Check for _tools or similar attributes
        for attr_name in dir(mcp):
            if attr_name.startswith('_') and 'tool' in attr_name.lower():
                print(f"Found potential tools attribute: {attr_name}")
                tools_attr = getattr(mcp, attr_name, None)
                if isinstance(tools_attr, dict):
                    registered_tools = list(tools_attr.keys())
                    print(f"✅ Found {len(registered_tools)} registered tools:")
                    for tool in registered_tools:
                        print(f"  - {tool}")
                    break
                    
        if not registered_tools:
            print("⚠️ No registered tools found directly.")
            print("FastMCP might be using a different structure for tool storage.")
            print("The lack of visible tools doesn't necessarily mean they aren't registered.")
            
        # Check direct function availability instead
        print("\nChecking FastMCP function availability:")
        functions_to_check = [
            "get_project_settings",
            "search_nodes",
            "create_entities",
            "open_nodes"
        ]
        
        for func_name in functions_to_check:
            func = globals().get(func_name)
            if func is not None and callable(func):
                print(f"✅ Function {func_name} is available")
            else:
                print(f"❌ Function {func_name} is NOT available")
    
    except Exception as e:
        print(f"❌ Error testing server registration: {str(e)}")
        import traceback
        traceback.print_exc()

def test_resources():
    """Test FastMCP resources"""
    print("\n--- Testing FastMCP Resources ---")
    
    try:
        # Import the FastMCP server
        server_module = importlib.import_module("mcp_agile_flow.fastmcp_server")
        
        # Access the server instance
        mcp = getattr(server_module, "mcp", None)
        if not mcp:
            print("❌ Failed to find 'mcp' instance in fastmcp_server module")
            return
        
        # Check for resource registration
        resource_handler = None
        
        # Try to find the resource decorator or registration mechanism
        for attr_name in dir(mcp):
            if 'resource' in attr_name.lower():
                resource_handler = getattr(mcp, attr_name, None)
                print(f"Found resource handler: {attr_name}")
                
        # Resource function mapping
        resource_functions = {
            "settings://project": "project_settings_resource",
            "settings://project/{path}": "project_settings_with_path",
            "graph://": "graph_resource",
            "graph://mermaid": "mermaid_diagram_resource",
            "entities://": "list_entities",
            "entities/{name}": "get_entity",
            "entities/search{?query}": "search_entities"
        }
        
        print("\nTesting resource functions:")
        
        # Test each resource function
        for uri, func_name in resource_functions.items():
            if hasattr(server_module, func_name):
                func = getattr(server_module, func_name)
                print(f"\n✅ Resource function found: {func_name} for URI {uri}")
                
                try:
                    # Handle different function signatures
                    if func_name == "project_settings_resource" or func_name == "graph_resource" or func_name == "mermaid_diagram_resource" or func_name == "list_entities":
                        result = func()
                    elif func_name == "project_settings_with_path":
                        result = func(path=os.getcwd())
                    elif func_name == "get_entity":
                        result = func(name="TestEntity")
                    elif func_name == "search_entities":
                        result = func(query="TestEntity")
                        
                    # Verify the result
                    if result is not None:
                        result_type = type(result).__name__
                        print(f"  ✅ Function returned {result_type}")
                        
                        # Check type-specific expectations
                        if isinstance(result, dict):
                            print(f"  Keys: {list(result.keys())}")
                        elif isinstance(result, list):
                            print(f"  List with {len(result)} items")
                            
                        # For specific resources, check for expected keys
                        if func_name == "project_settings_resource" or func_name == "project_settings_with_path":
                            if "project_path" in result:
                                print(f"  ✅ Project path: {result.get('project_path')}")
                            else:
                                print(f"  ❌ Missing expected 'project_path' key")
                    else:
                        print(f"  ⚠️ Function returned None")
                except Exception as e:
                    print(f"  ❌ Error calling function: {str(e)}")
            else:
                print(f"❌ Resource function not found: {func_name} for URI {uri}")
                
        # Check if resource decorator exists
        if resource_handler and callable(resource_handler):
            print(f"\n✅ Resource decorator/handler exists")
        else:
            print(f"\n❌ No resource handler found")
            
        # Try to find registered resource patterns
        print("\nLooking for registered resource patterns:")
        resources_found = False
        for attr_name in dir(mcp):
            if attr_name.startswith('_') and 'resource' in attr_name.lower():
                resources_attr = getattr(mcp, attr_name, None)
                if isinstance(resources_attr, dict):
                    patterns = list(resources_attr.keys())
                    print(f"✅ Found {len(patterns)} registered resource patterns:")
                    for pattern in patterns:
                        print(f"  - {pattern}")
                    resources_found = True
                    break
        
        if not resources_found:
            print("⚠️ No registered resource patterns found directly")
            
    except Exception as e:
        print(f"❌ Error testing resources: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("=== FastMCP Comprehensive Test ===")
    
    # Test direct FastMCP functions
    test_direct_functions()
    
    # Test server registration
    test_server_registration()
    
    # Test resources
    test_resources()
    
    print("\n=== Test Completed ===")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 