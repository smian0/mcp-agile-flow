#!/usr/bin/env python3
"""
Simple manual test script for the Memory Knowledge Graph implementation.

This script demonstrates the basic functionality of the KnowledgeGraphManager
without requiring pytest. It allows for quick manual testing and verification.

Run it directly: python test_memory_graph_manual.py
"""

import json
import os
import tempfile
from pathlib import Path

# Import the KnowledgeGraphManager from our package
from src.mcp_agile_flow.memory_graph import KnowledgeGraphManager


def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def format_json(obj):
    """Format an object as JSON."""
    def default_serializer(o):
        """Custom serializer for objects."""
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)
    
    return json.dumps(obj, default=default_serializer, indent=2)


def main():
    """Run a manual test of the KnowledgeGraphManager."""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        temp_file = tmp.name
    
    print(f"Using temporary file: {temp_file}")
    
    try:
        # Create a KnowledgeGraphManager
        manager = KnowledgeGraphManager(temp_file)
        
        print_separator("CREATING ENTITIES")
        entities = [
            {"name": "Python", "entityType": "language", "observations": ["A popular programming language"]},
            {"name": "TypeScript", "entityType": "language", "observations": ["JavaScript with types"]},
            {"name": "MCP", "entityType": "framework", "observations": ["Model Context Protocol"]},
        ]
        result = manager.create_entities(entities)
        print(f"Created {len(result)} entities:")
        print(format_json(result))
        
        print_separator("CREATING RELATIONS")
        relations = [
            {"from": "Python", "to": "MCP", "relationType": "implements"},
            {"from": "TypeScript", "to": "MCP", "relationType": "implements"},
        ]
        result = manager.create_relations(relations)
        print(f"Created {len(result)} relations:")
        print(format_json(result))
        
        print_separator("READING GRAPH")
        graph = manager.read_graph()
        print(f"Graph contains {len(graph.entities)} entities and {len(graph.relations)} relations:")
        print(format_json(graph))
        
        print_separator("ADDING OBSERVATIONS")
        observations = [
            {"entityName": "Python", "contents": ["Used for data science", "Has a large ecosystem"]},
            {"entityName": "TypeScript", "contents": ["Developed by Microsoft"]},
        ]
        result = manager.add_observations(observations)
        print("Added observations:")
        print(format_json(result))
        
        print_separator("SEARCHING NODES")
        query = "language"
        result = manager.search_nodes(query)
        print(f"Search for '{query}' found {len(result.entities)} entities:")
        print(format_json(result))
        
        print_separator("OPENING SPECIFIC NODES")
        names = ["Python", "MCP"]
        result = manager.open_nodes(names)
        print(f"Opening {names} found {len(result.entities)} entities and {len(result.relations)} relations:")
        print(format_json(result))
        
        print_separator("DELETING OBSERVATIONS")
        deletions = [{"entityName": "Python", "observations": ["Has a large ecosystem"]}]
        manager.delete_observations(deletions)
        print("After deleting observations:")
        entity = next(e for e in manager.read_graph().entities if e.name == "Python")
        print(format_json(entity))
        
        print_separator("DELETING RELATIONS")
        relations_to_delete = [{"from": "TypeScript", "to": "MCP", "relationType": "implements"}]
        manager.delete_relations(relations_to_delete)
        print("After deleting relations:")
        print(format_json(manager.read_graph().relations))
        
        print_separator("DELETING ENTITIES")
        manager.delete_entities(["TypeScript"])
        print("After deleting entities:")
        print(format_json(manager.read_graph().entities))
        
        print_separator("TESTING PERSISTENCE")
        # Create a new manager with the same file
        new_manager = KnowledgeGraphManager(temp_file)
        graph = new_manager.read_graph()
        print("Graph loaded from file:")
        print(format_json(graph))
        
        print_separator("TEST COMPLETE")
        print("All tests completed successfully!")
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
            print(f"Removed temporary file: {temp_file}")


if __name__ == "__main__":
    main() 