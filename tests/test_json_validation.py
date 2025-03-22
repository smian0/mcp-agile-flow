#!/usr/bin/env python3
"""
Test the JSON validation in the simple_server.py file.
"""
import os
import sys
import json
import pytest
import pytest_asyncio
import tempfile
import asyncio
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import directly from the module
from src.mcp_agile_flow.simple_server import handle_call_tool, create_text_response
import src.mcp_agile_flow.memory_graph as memory_graph
import src.mcp_agile_flow.simple_server as simple_server

class TestJsonValidation:
    """Test the JSON validation in the simple_server.py file."""

    @pytest.fixture(autouse=True)
    def setup_memory_manager(self):
        """Set up a real memory manager with a temporary file for testing."""
        # Create a temporary file for the knowledge graph
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            self.temp_file_path = tmp.name
        
        # Create a real KnowledgeGraphManager with the temporary file
        manager = memory_graph.KnowledgeGraphManager(self.temp_file_path)
        
        # Store the original memory_manager to restore later
        self.original_memory_manager = simple_server.memory_manager
        
        # Set the memory_manager directly in the simple_server module
        simple_server.memory_manager = manager
        
        yield
        
        # Cleanup
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
        
        # Restore original memory_manager
        simple_server.memory_manager = self.original_memory_manager

    @pytest.mark.asyncio
    async def test_create_entities_missing_entities(self):
        """Test create_entities with missing entities field."""
        # Test with missing entities field
        result = await handle_call_tool("create_entities", {})
        assert result[0].isError is True
        assert "Missing 'entities' field" in result[0].text

    @pytest.mark.asyncio
    async def test_create_entities_entities_not_list(self):
        """Test create_entities with entities not a list."""
        # Test with entities not a list
        result = await handle_call_tool("create_entities", {"entities": "not a list"})
        assert result[0].isError is True
        assert "'entities' must be a list" in result[0].text

    @pytest.mark.asyncio
    async def test_create_entities_missing_required_fields(self):
        """Test create_entities with missing required fields."""
        # Test with missing name field
        result = await handle_call_tool("create_entities", {
            "entities": [{"entityType": "test"}]
        })
        assert result[0].isError is True
        assert "missing required 'name' field" in result[0].text
        
        # Test with missing entityType field
        result = await handle_call_tool("create_entities", {
            "entities": [{"name": "Test Entity"}]
        })
        assert result[0].isError is True
        assert "missing required 'entityType' field" in result[0].text

    @pytest.mark.asyncio
    async def test_create_entities_observations_not_list(self):
        """Test create_entities with observations not a list."""
        # Test with observations not a list
        result = await handle_call_tool("create_entities", {
            "entities": [{"name": "Test Entity", "entityType": "test", "observations": "not a list"}]
        })
        assert result[0].isError is True
        assert "'observations' for entity 'Test Entity' must be a list" in result[0].text

    @pytest.mark.asyncio
    async def test_create_entities_valid(self):
        """Test create_entities with valid arguments."""
        # Test with valid arguments
        result = await handle_call_tool("create_entities", {
            "entities": [{"name": "Test Entity", "entityType": "test", "observations": ["test"]}]
        })
        
        # Check that the call was successful
        assert result[0].isError is False
        
        # Parse the JSON response
        response_data = json.loads(result[0].text)
        
        # Verify entity was created
        assert isinstance(response_data, list)
        assert len(response_data) > 0
        assert "name" in response_data[0]
        assert response_data[0]["name"] == "Test Entity"
        assert response_data[0]["entityType"] == "test"
        assert "observations" in response_data[0]
        
        # Verify entity exists in the graph by searching for it
        search_result = await handle_call_tool("search_nodes", {"query": "Test Entity"})
        assert search_result[0].isError is False
        search_data = json.loads(search_result[0].text)
        
        # Check that the entity was found in the search results
        assert "entities" in search_data
        assert any(entity["name"] == "Test Entity" for entity in search_data["entities"])

    @pytest.mark.asyncio
    async def test_create_relations_missing_relations(self):
        """Test create_relations with missing relations field."""
        # Test with missing relations field
        result = await handle_call_tool("create_relations", {})
        assert result[0].isError is True
        assert "Missing 'relations' field" in result[0].text

    @pytest.mark.asyncio
    async def test_create_relations_relations_not_list(self):
        """Test create_relations with relations not a list."""
        # Test with relations not a list
        result = await handle_call_tool("create_relations", {"relations": "not a list"})
        assert result[0].isError is True
        assert "'relations' must be a list" in result[0].text

    @pytest.mark.asyncio
    async def test_create_relations_missing_required_fields(self):
        """Test create_relations with missing required fields."""
        # Test with missing from field
        result = await handle_call_tool("create_relations", {
            "relations": [{"to": "Test Entity 2", "relationType": "test"}]
        })
        assert result[0].isError is True
        assert "missing required 'from' field" in result[0].text
        
        # Test with missing to field
        result = await handle_call_tool("create_relations", {
            "relations": [{"from": "Test Entity", "relationType": "test"}]
        })
        assert result[0].isError is True
        assert "missing required 'to' field" in result[0].text
        
        # Test with missing relationType field
        result = await handle_call_tool("create_relations", {
            "relations": [{"from": "Test Entity", "to": "Test Entity 2"}]
        })
        assert result[0].isError is True
        assert "missing required 'relationType' field" in result[0].text

    @pytest.mark.asyncio
    async def test_create_relations_valid(self):
        """Test create_relations with valid arguments."""
        # First create entities that can be related
        await handle_call_tool("create_entities", {
            "entities": [
                {"name": "Source Entity", "entityType": "test", "observations": ["source"]},
                {"name": "Target Entity", "entityType": "test", "observations": ["target"]}
            ]
        })
        
        # Test with valid arguments
        result = await handle_call_tool("create_relations", {
            "relations": [{"from": "Source Entity", "to": "Target Entity", "relationType": "test"}]
        })
        
        # Check that the call was successful
        assert result[0].isError is False
        
        # Parse the JSON response
        response_data = json.loads(result[0].text)
        
        # Verify relation was created
        assert isinstance(response_data, list)
        assert len(response_data) > 0
        assert "from" in response_data[0]
        assert response_data[0]["from"] == "Source Entity"
        assert response_data[0]["to"] == "Target Entity"
        assert response_data[0]["relationType"] == "test"
        
    @pytest.mark.asyncio
    async def test_add_observations_missing_observations(self):
        """Test add_observations with missing observations field."""
        # Test with missing observations field
        result = await handle_call_tool("add_observations", {})
        assert result[0].isError is True
        assert "Missing 'observations' field" in result[0].text

    @pytest.mark.asyncio
    async def test_add_observations_observations_not_list(self):
        """Test add_observations with observations not a list."""
        # Test with observations not a list
        result = await handle_call_tool("add_observations", {"observations": "not a list"})
        assert result[0].isError is True
        assert "'observations' must be a list" in result[0].text

    @pytest.mark.asyncio
    async def test_add_observations_missing_required_fields(self):
        """Test add_observations with missing required fields."""
        # Test with missing entityName field
        result = await handle_call_tool("add_observations", {
            "observations": [{"contents": ["test"]}]
        })
        assert result[0].isError is True
        assert "missing required 'entityName' field" in result[0].text
        
        # Test with missing contents field
        result = await handle_call_tool("add_observations", {
            "observations": [{"entityName": "Test Entity"}]
        })
        assert result[0].isError is True
        assert "missing required 'contents' field" in result[0].text

    @pytest.mark.asyncio
    async def test_add_observations_contents_not_list(self):
        """Test add_observations with contents not a list."""
        # Test with contents not a list
        result = await handle_call_tool("add_observations", {
            "observations": [{"entityName": "Test Entity", "contents": "not a list"}]
        })
        assert result[0].isError is True
        assert "'contents' for entity 'Test Entity' must be a list" in result[0].text

    @pytest.mark.asyncio
    async def test_add_observations_valid(self):
        """Test add_observations with valid arguments."""
        # First create an entity
        await handle_call_tool("create_entities", {
            "entities": [{"name": "Observation Entity", "entityType": "test", "observations": ["initial"]}]
        })
        
        # Test with valid arguments
        result = await handle_call_tool("add_observations", {
            "observations": [{"entityName": "Observation Entity", "contents": ["new observation"]}]
        })
        
        # Check that the call was successful
        assert result[0].isError is False
        
        # Parse the JSON response
        response_data = json.loads(result[0].text)
        
        # Verify observation was added
        assert isinstance(response_data, list)
        assert len(response_data) > 0
        assert "entityName" in response_data[0]
        assert response_data[0]["entityName"] == "Observation Entity"
        assert "addedObservations" in response_data[0]
        assert "new observation" in response_data[0]["addedObservations"]
