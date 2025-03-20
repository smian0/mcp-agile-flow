#!/usr/bin/env python3
"""

Test the JSON validation in the simple_server.py file.
"""
import os
import sys
import json
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_agile_flow.simple_server import handle_call_tool, create_text_response


class TestJsonValidation:
    """Test the JSON validation in the simple_server.py file."""

    @pytest.fixture
    def mock_memory_manager(self):
        """Create a mock memory manager."""
        mock = MagicMock()
        mock.create_entities.return_value = [MagicMock()]
        mock.create_relations.return_value = [MagicMock()]
        mock.add_observations.return_value = [{"entityName": "Test", "addedObservations": ["test"]}]
        return mock

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_create_entities_missing_entities(self, mock_memory_manager_global, mock_memory_manager):
        """Test create_entities with missing entities field."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with missing entities field
        result = await handle_call_tool("create_entities", {})
        assert result[0].isError is True
        assert "Missing 'entities' field" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_create_entities_entities_not_list(self, mock_memory_manager_global, mock_memory_manager):
        """Test create_entities with entities not being a list."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with entities not being a list
        result = await handle_call_tool("create_entities", {"entities": "not a list"})
        assert result[0].isError is True
        assert "'entities' must be a list" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_create_entities_missing_required_fields(self, mock_memory_manager_global, mock_memory_manager):
        """Test create_entities with entity missing required fields."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with entity missing entityType
        result = await handle_call_tool("create_entities", {"entities": [{"name": "Test Entity"}]})
        assert result[0].isError is True
        assert "missing required 'entityType' field" in result[0].text
        
        # Test with entity missing name
        result = await handle_call_tool("create_entities", {"entities": [{"entityType": "test"}]})
        assert result[0].isError is True
        assert "missing required 'name' field" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_create_entities_observations_not_list(self, mock_memory_manager_global, mock_memory_manager):
        """Test create_entities with observations not being a list."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with observations not being a list
        result = await handle_call_tool("create_entities", {
            "entities": [{"name": "Test Entity", "entityType": "test", "observations": "not a list"}]
        })
        assert result[0].isError is True
        assert "'observations' for entity 'Test Entity' must be a list" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_create_entities_valid(self, mock_memory_manager_global, mock_memory_manager):
        """Test create_entities with valid arguments."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with valid arguments
        result = await handle_call_tool("create_entities", {
            "entities": [{"name": "Test Entity", "entityType": "test", "observations": ["test"]}]
        })
        assert result[0].isError is False
        assert "entities created successfully" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_create_relations_missing_relations(self, mock_memory_manager_global, mock_memory_manager):
        """Test create_relations with missing relations field."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with missing relations field
        result = await handle_call_tool("create_relations", {})
        assert result[0].isError is True
        assert "Missing 'relations' field" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_create_relations_relations_not_list(self, mock_memory_manager_global, mock_memory_manager):
        """Test create_relations with relations not being a list."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with relations not being a list
        result = await handle_call_tool("create_relations", {"relations": "not a list"})
        assert result[0].isError is True
        assert "'relations' must be a list" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_create_relations_missing_required_fields(self, mock_memory_manager_global, mock_memory_manager):
        """Test create_relations with relation missing required fields."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with relation missing from
        result = await handle_call_tool("create_relations", {
            "relations": [{"to": "Test Entity", "relationType": "test"}]
        })
        assert result[0].isError is True
        assert "missing required 'from' field" in result[0].text
        
        # Test with relation missing to
        result = await handle_call_tool("create_relations", {
            "relations": [{"from": "Test Entity", "relationType": "test"}]
        })
        assert result[0].isError is True
        assert "missing required 'to' field" in result[0].text
        
        # Test with relation missing relationType
        result = await handle_call_tool("create_relations", {
            "relations": [{"from": "Test Entity", "to": "Test Entity 2"}]
        })
        assert result[0].isError is True
        assert "missing required 'relationType' field" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_create_relations_valid(self, mock_memory_manager_global, mock_memory_manager):
        """Test create_relations with valid arguments."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with valid arguments
        result = await handle_call_tool("create_relations", {
            "relations": [{"from": "Test Entity", "to": "Test Entity 2", "relationType": "test"}]
        })
        assert result[0].isError is False
        assert "relations created successfully" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_add_observations_missing_observations(self, mock_memory_manager_global, mock_memory_manager):
        """Test add_observations with missing observations field."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with missing observations field
        result = await handle_call_tool("add_observations", {})
        assert result[0].isError is True
        assert "Missing 'observations' field" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_add_observations_observations_not_list(self, mock_memory_manager_global, mock_memory_manager):
        """Test add_observations with observations not being a list."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with observations not being a list
        result = await handle_call_tool("add_observations", {"observations": "not a list"})
        assert result[0].isError is True
        assert "'observations' must be a list" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_add_observations_missing_required_fields(self, mock_memory_manager_global, mock_memory_manager):
        """Test add_observations with observation missing required fields."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with observation missing entityName
        result = await handle_call_tool("add_observations", {
            "observations": [{"contents": ["test"]}]
        })
        assert result[0].isError is True
        assert "missing required 'entityName' field" in result[0].text
        
        # Test with observation missing contents
        result = await handle_call_tool("add_observations", {
            "observations": [{"entityName": "Test Entity"}]
        })
        assert result[0].isError is True
        assert "missing required 'contents' field" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_add_observations_contents_not_list(self, mock_memory_manager_global, mock_memory_manager):
        """Test add_observations with contents not being a list."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with contents not being a list
        result = await handle_call_tool("add_observations", {
            "observations": [{"entityName": "Test Entity", "contents": "not a list"}]
        })
        assert result[0].isError is True
        assert "'contents' for entity 'Test Entity' must be a list" in result[0].text

    @pytest.mark.asyncio
    @patch("src.mcp_agile_flow.simple_server.memory_manager")
    async def test_add_observations_valid(self, mock_memory_manager_global, mock_memory_manager):
        """Test add_observations with valid arguments."""
        mock_memory_manager_global.return_value = mock_memory_manager
        
        # Test with valid arguments
        result = await handle_call_tool("add_observations", {
            "observations": [{"entityName": "Test Entity", "contents": ["test"]}]
        })
        assert result[0].isError is False
        assert "observations added to" in result[0].text
