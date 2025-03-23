#!/usr/bin/env python
"""
Resource API Testing Script for FastMCP implementation

This script tests:
1. Direct function calls to resource implementations
2. Simulated client requests to resource endpoints
"""

import json
import sys
import importlib
import inspect
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_resources():
    """Test direct calls to resource functions"""
    print("\n=== Testing Direct Resource Function Calls ===")
    
    # Import the FastMCP server module
    server_module = importlib.import_module("mcp_agile_flow.fastmcp_server")
    
    # Test project settings resources
    print("\n--- Project Settings Resources ---")
    
    if hasattr(server_module, "project_settings_resource"):
        print("\nTesting project_settings_resource (settings://project):")
        try:
            result = server_module.project_settings_resource()
            print(f"✅ Success - Project path: {result.get('project_path')}")
            print(f"  Keys: {', '.join(result.keys())}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        print("❌ Function not found: project_settings_resource")
    
    if hasattr(server_module, "project_settings_with_path"):
        print("\nTesting project_settings_with_path (settings://project/{path}):")
        try:
            current_dir = os.getcwd()
            result = server_module.project_settings_with_path(path=current_dir)
            print(f"✅ Success - Project path: {result.get('project_path')}")
            print(f"  Keys: {', '.join(result.keys())}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        print("❌ Function not found: project_settings_with_path")
    
    # Test knowledge graph resources
    print("\n--- Knowledge Graph Resources ---")
    
    if hasattr(server_module, "graph_resource"):
        print("\nTesting graph_resource (graph://):")
        try:
            result = server_module.graph_resource()
            entity_count = len(result.get("entities", []))
            relation_count = len(result.get("relations", []))
            print(f"✅ Success - {entity_count} entities, {relation_count} relations")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        print("❌ Function not found: graph_resource")
    
    if hasattr(server_module, "mermaid_diagram_resource"):
        print("\nTesting mermaid_diagram_resource (graph://mermaid):")
        try:
            result = server_module.mermaid_diagram_resource()
            if "mermaid" in result:
                mermaid_length = len(result["mermaid"])
                print(f"✅ Success - Mermaid diagram length: {mermaid_length} chars")
                # Print first 100 chars of the diagram
                print(f"  Preview: {result['mermaid'][:100]}...")
            else:
                print("❌ Missing 'mermaid' key in result")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        print("❌ Function not found: mermaid_diagram_resource")
    
    # Test entity resources
    print("\n--- Entity Resources ---")
    
    if hasattr(server_module, "list_entities"):
        print("\nTesting list_entities (entities://):")
        try:
            result = server_module.list_entities()
            print(f"✅ Success - Found {len(result)} entities")
            # Display the first few entities
            for i, entity in enumerate(result[:3]):
                if i >= 3:
                    break
                print(f"  - {entity.get('name')} ({entity.get('entityType')})")
            if len(result) > 3:
                print(f"  - ... and {len(result) - 3} more")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        print("❌ Function not found: list_entities")
    
    if hasattr(server_module, "get_entity"):
        print("\nTesting get_entity (entities/{name}):")
        try:
            # Try to get a known entity
            entity_name = "TestEntity"
            result = server_module.get_entity(name=entity_name)
            if result:
                print(f"✅ Success - Found entity: {result.get('name')}")
                obs_count = len(result.get('observations', []))
                print(f"  Entity has {obs_count} observations")
            else:
                print(f"⚠️ Entity '{entity_name}' not found")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        print("❌ Function not found: get_entity")
    
    if hasattr(server_module, "search_entities"):
        print("\nTesting search_entities (entities/search/{query}):")
        try:
            # Search for entities
            query = "Test"
            result = server_module.search_entities(query=query)
            entities_found = result.get('entities_found', 0)
            print(f"✅ Success - Found {entities_found} entities matching '{query}'")
            for entity in result.get('entities', [])[:3]:
                print(f"  - {entity.get('name')}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        print("❌ Function not found: search_entities")

def simulate_client_request(resource_uri, params=None):
    """Simulate a client request to a resource endpoint"""
    print(f"\nSimulating client request to: {resource_uri}")
    try:
        # Import the FastMCP server module
        server_module = importlib.import_module("mcp_agile_flow.fastmcp_server")
        
        # Simplified mapping from URI patterns to function names
        uri_to_function = {
            "settings://project": "project_settings_resource",
            "settings://project/{path}": "project_settings_with_path",
            "graph://": "graph_resource",
            "graph://mermaid": "mermaid_diagram_resource",
            "entities://": "list_entities",
            "entities/{name}": "get_entity",
            "entities/search/{query}": "search_entities"
        }
        
        # Find the best matching function
        function_name = None
        for uri_pattern, func_name in uri_to_function.items():
            # Check for literal match
            if resource_uri == uri_pattern:
                function_name = func_name
                break
            
            # Check for parameterized URIs by comparing path structure
            if "{" in uri_pattern:
                uri_parts = uri_pattern.split("/")
                res_parts = resource_uri.split("/")
                
                if len(uri_parts) == len(res_parts):
                    match = True
                    for i, (uri_part, res_part) in enumerate(zip(uri_parts, res_parts)):
                        if "{" in uri_part:  # it's a parameter
                            continue
                        if uri_part != res_part:
                            match = False
                            break
                    if match:
                        function_name = func_name
                        break
        
        if not function_name:
            print(f"❌ No matching function found for URI: {resource_uri}")
            print("Available resources:")
            for uri, func in uri_to_function.items():
                print(f"  - {uri} -> {func}")
            return None
        
        # Get the function
        if not hasattr(server_module, function_name):
            print(f"❌ Function '{function_name}' not found in server module")
            return None
        
        handler_function = getattr(server_module, function_name)
        print(f"✅ Found handler function: {function_name}")
        
        # Execute the function with the right parameters based on the URI pattern
        if params:
            result = handler_function(**params)
        else:
            result = handler_function()
        
        # Print the result summary
        if isinstance(result, dict):
            print(f"✅ Success - Response is a dictionary with {len(result)} keys")
            print(f"  Keys: {', '.join(list(result.keys())[:5])}")
        elif isinstance(result, list):
            print(f"✅ Success - Response is a list with {len(result)} items")
        else:
            print(f"✅ Success - Response type: {type(result).__name__}")
        
        return result
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_simulated_client():
    """Test resources using simulated client requests"""
    print("\n=== Testing Simulated Client Requests ===")
    
    # Test project settings resources
    simulate_client_request("settings://project")
    simulate_client_request("settings://project/{path}", {"path": os.getcwd()})
    
    # Test knowledge graph resources
    simulate_client_request("graph://")
    simulate_client_request("graph://mermaid")
    
    # Test entity resources
    simulate_client_request("entities://")
    simulate_client_request("entities/{name}", {"name": "TestEntity"})
    simulate_client_request("entities/search/{query}", {"query": "Test"})

def main():
    """Run all tests"""
    print("=== FastMCP Resource API Test ===")
    
    # Test direct resource functions
    test_direct_resources()
    
    # Test simulated client requests
    test_simulated_client()
    
    print("\n=== Test Completed ===")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 