from mcp_agile_flow.fastmcp_tools import search_nodes, open_nodes
import json

def main():
    # Test search_nodes function
    print("Testing search_nodes function")
    result = search_nodes("TestEntity")
    print(result)
    
    # Parse the JSON
    try:
        data = json.loads(result)
        if data.get('success'):
            print(f"\nSearch was successful!")
            print(f"Found {data.get('entities_found', 0)} entities and {data.get('relations_found', 0)} relations")
            for entity in data.get('entities', []):
                print(f"  - {entity['name']} ({entity['entity_type']}): {entity['observations']}")
        else:
            print(f"\nSearch failed: {data.get('error', 'unknown error')}")
    except json.JSONDecodeError:
        print("\nCould not parse response as JSON")
    
    # Test open_nodes function
    print("\nTesting open_nodes function")
    result = open_nodes(["TestEntity"])
    print(result)
    
    # Parse the JSON
    try:
        data = json.loads(result)
        if data.get('success'):
            print(f"\nOpen Nodes was successful!")
            print(f"Found {data.get('entities_found', 0)} entities and {data.get('relations_found', 0)} relations")
            for entity in data.get('entities', []):
                print(f"  - {entity['name']} ({entity['entity_type']}): {entity['observations']}")
        else:
            print(f"\nOpen Nodes failed: {data.get('error', 'unknown error')}")
    except json.JSONDecodeError:
        print("\nCould not parse response as JSON")

if __name__ == "__main__":
    main() 