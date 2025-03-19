#!/usr/bin/env python3
"""
Test script to verify the default memory file path in the KnowledgeGraphManager.
"""

from src.mcp_agile_flow.memory_graph import KnowledgeGraphManager

# Create a manager with default path
manager = KnowledgeGraphManager()

# Print the default path
print(f"Default memory file path: {manager.memory_file_path}")

# Create some test data
test_entities = [
    {"name": "DefaultPathTest", "entityType": "test", "observations": ["Testing default path"]}
]

# Save to default location
manager.create_entities(test_entities)

print("Test entity created at default location.")
print("Check the file contents with: cat ai-kngr/memory.json") 