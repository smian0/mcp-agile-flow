#!/usr/bin/env python3
"""
Tests for the Memory Knowledge Graph implementation.
"""

import json
import os
import tempfile
from pathlib import Path
import pytest

# Import only the core classes we need from memory_graph, avoiding the MCP integration
from mcp_agile_flow.memory_graph import KnowledgeGraphManager, Entity, Relation, KnowledgeGraph


@pytest.fixture
def temp_memory_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
    
    yield tmp_path
    
    # Cleanup
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def graph_manager(temp_memory_file):
    """Create a graph manager with a temporary file."""
    return KnowledgeGraphManager(temp_memory_file)


@pytest.fixture
def populated_graph(graph_manager):
    """Create a graph manager with some test data."""
    # Create test entities
    entities = [
        {"name": "Python", "entityType": "language", "observations": ["A popular programming language"]},
        {"name": "TypeScript", "entityType": "language", "observations": ["JavaScript with types"]},
        {"name": "MCP", "entityType": "framework", "observations": ["Model Context Protocol"]},
    ]
    graph_manager.create_entities(entities)
    
    # Create test relations
    relations = [
        {"from": "Python", "to": "MCP", "relationType": "implements"},
        {"from": "TypeScript", "to": "MCP", "relationType": "implements"},
    ]
    graph_manager.create_relations(relations)
    
    return graph_manager


class TestKnowledgeGraphManager:
    """Tests for the KnowledgeGraphManager class."""
    
    def test_create_entities(self, graph_manager):
        """Test creating entities."""
        entities = [
            {"name": "Entity1", "entityType": "test", "observations": ["Observation 1"]},
            {"name": "Entity2", "entityType": "test", "observations": ["Observation 2"]},
        ]
        
        result = graph_manager.create_entities(entities)
        assert len(result) == 2
        assert result[0].name == "Entity1"
        assert result[1].name == "Entity2"
        
        # Test duplicate prevention
        duplicate_result = graph_manager.create_entities(entities)
        assert len(duplicate_result) == 0
    
    def test_create_relations(self, graph_manager):
        """Test creating relations."""
        # First create entities
        entities = [
            {"name": "SourceEntity", "entityType": "test", "observations": []},
            {"name": "TargetEntity", "entityType": "test", "observations": []},
        ]
        graph_manager.create_entities(entities)
        
        # Then create relations
        relations = [
            {"from": "SourceEntity", "to": "TargetEntity", "relationType": "test_relation"},
        ]
        
        result = graph_manager.create_relations(relations)
        assert len(result) == 1
        assert result[0].from_entity == "SourceEntity"
        assert result[0].to_entity == "TargetEntity"
        
        # Test duplicate prevention
        duplicate_result = graph_manager.create_relations(relations)
        assert len(duplicate_result) == 0
    
    def test_add_observations(self, graph_manager):
        """Test adding observations to entities."""
        # First create an entity
        graph_manager.create_entities([{"name": "ObsEntity", "entityType": "test", "observations": ["Initial"]}])
        
        # Add observations
        observations = [{"entityName": "ObsEntity", "contents": ["New observation", "Another observation"]}]
        
        result = graph_manager.add_observations(observations)
        assert len(result) == 1
        assert result[0]["entityName"] == "ObsEntity"
        assert len(result[0]["addedObservations"]) == 2
        
        # Verify observations were added
        graph = graph_manager.read_graph()
        entity = next(e for e in graph.entities if e.name == "ObsEntity")
        assert len(entity.observations) == 3
        assert "Initial" in entity.observations
        assert "New observation" in entity.observations
        
        # Test adding the same observation again (should be ignored)
        repeat_result = graph_manager.add_observations(observations)
        assert len(repeat_result[0]["addedObservations"]) == 0
    
    def test_delete_entities(self, populated_graph):
        """Test deleting entities."""
        # Initial state should have 3 entities
        initial_graph = populated_graph.read_graph()
        assert len(initial_graph.entities) == 3
        
        # Delete one entity
        populated_graph.delete_entities(["Python"])
        
        # Should have 2 entities and 1 relation left
        updated_graph = populated_graph.read_graph()
        assert len(updated_graph.entities) == 2
        assert len(updated_graph.relations) == 1
        assert all(e.name != "Python" for e in updated_graph.entities)
        
        # Relations involving Python should be deleted
        assert all(r.from_entity != "Python" for r in updated_graph.relations)
        assert all(r.to_entity != "Python" for r in updated_graph.relations)
    
    def test_delete_observations(self, graph_manager):
        """Test deleting observations from entities."""
        # Create entity with multiple observations
        graph_manager.create_entities([
            {"name": "MultiObsEntity", "entityType": "test", 
             "observations": ["Obs1", "Obs2", "Obs3"]}
        ])
        
        # Delete one observation
        deletions = [{"entityName": "MultiObsEntity", "observations": ["Obs2"]}]
        graph_manager.delete_observations(deletions)
        
        # Check result
        graph = graph_manager.read_graph()
        entity = next(e for e in graph.entities if e.name == "MultiObsEntity")
        assert len(entity.observations) == 2
        assert "Obs1" in entity.observations
        assert "Obs2" not in entity.observations
        assert "Obs3" in entity.observations
    
    def test_delete_relations(self, populated_graph):
        """Test deleting relations."""
        # Initial state should have 2 relations
        initial_graph = populated_graph.read_graph()
        assert len(initial_graph.relations) == 2
        
        # Delete one relation
        relations_to_delete = [{"from": "Python", "to": "MCP", "relationType": "implements"}]
        populated_graph.delete_relations(relations_to_delete)
        
        # Should have 1 relation left
        updated_graph = populated_graph.read_graph()
        assert len(updated_graph.relations) == 1
        remaining = updated_graph.relations[0]
        assert remaining.from_entity == "TypeScript"
        assert remaining.to_entity == "MCP"
    
    def test_search_nodes(self, populated_graph):
        """Test searching for nodes."""
        # Search for languages
        language_graph = populated_graph.search_nodes("language")
        assert len(language_graph.entities) == 2
        assert {e.name for e in language_graph.entities} == {"Python", "TypeScript"}
        
        # Search for specific language
        python_graph = populated_graph.search_nodes("Python")
        assert len(python_graph.entities) == 1
        assert python_graph.entities[0].name == "Python"
        
        # Search in observations
        popular_graph = populated_graph.search_nodes("popular")
        assert len(popular_graph.entities) == 1
        assert popular_graph.entities[0].name == "Python"
    
    def test_open_nodes(self, populated_graph):
        """Test opening specific nodes."""
        # Open two specific nodes
        specific_graph = populated_graph.open_nodes(["Python", "MCP"])
        assert len(specific_graph.entities) == 2
        assert {e.name for e in specific_graph.entities} == {"Python", "MCP"}
        
        # Relations between these nodes should be included
        assert len(specific_graph.relations) == 1
        assert specific_graph.relations[0].from_entity == "Python"
        assert specific_graph.relations[0].to_entity == "MCP"
    
    def test_persistence(self, temp_memory_file):
        """Test that the graph persists between manager instances."""
        # Create a manager and add data
        manager1 = KnowledgeGraphManager(temp_memory_file)
        manager1.create_entities([{"name": "PersistentEntity", "entityType": "test", "observations": []}])
        
        # Create a new manager with the same file and verify data exists
        manager2 = KnowledgeGraphManager(temp_memory_file)
        graph = manager2.read_graph()
        assert len(graph.entities) == 1
        assert graph.entities[0].name == "PersistentEntity"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 