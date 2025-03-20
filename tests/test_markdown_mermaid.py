#!/usr/bin/env python3
"""
Test the Markdown with Mermaid diagram functionality in the KnowledgeGraphManager.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mcp_agile_flow.memory_graph import KnowledgeGraphManager


@pytest.fixture
def temp_kg_manager(tmp_path):
    """Create a temporary KnowledgeGraphManager for testing."""
    # Create a test knowledge graph file in the temporary directory
    kg_path = tmp_path / "memory.json"
    manager = KnowledgeGraphManager(graph_path=str(kg_path))
    return manager


def test_update_markdown_with_mermaid(temp_kg_manager):
    """Test that update_markdown_with_mermaid creates a Markdown file with embedded Mermaid diagram."""
    manager = temp_kg_manager
    
    # Create a test entity
    entities = [
        {
            "name": "Test Entity",
            "entityType": "test",
            "observations": ["This is a test entity for Markdown with Mermaid diagram generation"]
        }
    ]
    created_entities = manager.create_entities(entities)
    assert len(created_entities) == 1
    assert created_entities[0].name == "Test Entity"
    
    # Create a test relation
    relations = [
        {
            "from": "Test Entity",
            "to": "Test Entity",
            "relationType": "self-reference"
        }
    ]
    created_relations = manager.create_relations(relations)
    assert len(created_relations) == 1
    assert created_relations[0].from_entity == "Test Entity"
    assert created_relations[0].to_entity == "Test Entity"
    
    # Update the Markdown file with Mermaid diagram
    markdown_content = manager.update_markdown_with_mermaid()
    
    # Check that the Markdown content contains the expected elements
    assert "```mermaid" in markdown_content
    assert "Test Entity" in markdown_content
    assert "self-reference" in markdown_content
    
    # Check that the Markdown file was created
    md_path = Path(manager.graph_path.replace(".json", ".md"))
    assert md_path.exists()
    
    # Read the Markdown file and verify it contains the Mermaid diagram
    with open(md_path, "r") as f:
        md_content = f.read()
    
    assert "```mermaid" in md_content
    assert "Test Entity" in md_content
    assert "self-reference" in md_content


def test_deprecated_methods(temp_kg_manager):
    """Test that deprecated methods correctly call the new method."""
    manager = temp_kg_manager
    
    # Create a test entity
    entities = [
        {
            "name": "Deprecated Test",
            "entityType": "test",
            "observations": ["Testing deprecated methods"]
        }
    ]
    manager.create_entities(entities)
    
    # Test the deprecated get_mermaid_diagram method
    md_content1 = manager.get_mermaid_diagram()
    assert "```mermaid" in md_content1
    assert "Deprecated Test" in md_content1
    
    # Test the deprecated update_mermaid_diagram method
    md_content2 = manager.update_mermaid_diagram()
    assert "```mermaid" in md_content2
    assert "Deprecated Test" in md_content2
    
    # Both should produce identical content
    assert md_content1 == md_content2


def test_markdown_file_content(temp_kg_manager):
    """Test that the Markdown file contains all expected sections."""
    manager = temp_kg_manager
    
    # Create multiple test entities with different types
    entities = [
        {
            "name": "Entity A",
            "entityType": "concept",
            "observations": ["First observation", "Second observation"]
        },
        {
            "name": "Entity B",
            "entityType": "file",
            "observations": ["File observation"]
        }
    ]
    manager.create_entities(entities)
    
    # Create relations between entities
    relations = [
        {
            "from": "Entity A",
            "to": "Entity B",
            "relationType": "references"
        }
    ]
    manager.create_relations(relations)
    
    # Update the Markdown file with Mermaid diagram
    markdown_content = manager.update_markdown_with_mermaid()
    
    # Check that the Markdown content contains all expected sections
    # The actual format doesn't have a title or Mermaid Diagram section header
    # It starts directly with the mermaid code block
    assert "```mermaid" in markdown_content
    assert "## Knowledge Graph Metadata" in markdown_content
    assert "```mermaid" in markdown_content
    assert "```" in markdown_content
    
    # Check for entity and relation information
    assert "Entity A" in markdown_content
    assert "Entity B" in markdown_content
    assert "concept" in markdown_content
    assert "file" in markdown_content
    assert "references" in markdown_content
    
    # Check that the file was saved
    md_path = Path(manager.graph_path.replace(".json", ".md"))
    assert md_path.exists()
