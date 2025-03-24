"""
Tests for the Think Tool functionality in MCP Agile Flow.

These tests verify that the think tool correctly records, retrieves, and manages thoughts.
"""

import asyncio
import json
import sys
from pathlib import Path

import pytest

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import MCP-related functions
from src.mcp_agile_flow import call_tool
from src.mcp_agile_flow.think_tool import _storage

@pytest.fixture(scope="function", autouse=True)
def clear_thoughts_storage():
    """Clear thoughts storage before and after each test."""
    # Clear before test
    _storage.clear_thoughts()
    yield
    # Clear after test
    _storage.clear_thoughts()

@pytest.mark.asyncio
async def test_think():
    """Test the think tool."""
    # Record a thought
    result = await call_tool("think", {"thought": "This is a test thought."})
    assert result["success"] is True
    assert "Thought recorded" in result["message"]
    
    # Verify the thought was stored
    assert _storage.get_thought_count() == 1
    assert _storage.get_thoughts()[0]["thought"] == "This is a test thought."

@pytest.mark.asyncio
async def test_get_thoughts_empty():
    """Test getting thoughts when none are stored."""
    result = await call_tool("get-thoughts")
    assert result["success"] is True
    assert "No thoughts have been recorded yet" in result["message"]
    assert result["thoughts"] == []

@pytest.mark.asyncio
async def test_get_thoughts():
    """Test getting thoughts when some are stored."""
    # Record some thoughts
    await call_tool("think", {"thought": "First thought"})
    await call_tool("think", {"thought": "Second thought"})
    
    # Get the thoughts
    result = await call_tool("get-thoughts")
    assert result["success"] is True
    assert "Retrieved 2 thoughts" in result["message"]
    assert len(result["thoughts"]) == 2
    assert result["thoughts"][0]["thought"] == "First thought"
    assert result["thoughts"][1]["thought"] == "Second thought"
    assert result["thoughts"][0]["index"] == 1
    assert result["thoughts"][1]["index"] == 2

@pytest.mark.asyncio
async def test_clear_thoughts():
    """Test clearing thoughts."""
    # Record some thoughts
    await call_tool("think", {"thought": "A thought to be cleared"})
    await call_tool("think", {"thought": "Another thought to be cleared"})
    
    # Verify thoughts were stored
    assert _storage.get_thought_count() == 2
    
    # Clear the thoughts
    result = await call_tool("clear-thoughts")
    assert result["success"] is True
    assert "Cleared 2 recorded thoughts" in result["message"]
    
    # Verify thoughts were cleared
    assert _storage.get_thought_count() == 0

@pytest.mark.asyncio
async def test_get_thought_stats_empty():
    """Test getting thought stats when none are stored."""
    result = await call_tool("get-thought-stats")
    assert result["success"] is True
    assert "No thoughts have been recorded yet" in result["message"]
    assert result["stats"]["total_thoughts"] == 0

@pytest.mark.asyncio
async def test_get_thought_stats():
    """Test getting thought stats when some are stored."""
    # Record some thoughts
    await call_tool("think", {"thought": "A short thought"})
    await call_tool("think", {"thought": "A much longer thought that has more characters and should be the longest"})
    await call_tool("think", {"thought": "Medium length thought"})
    
    # Get thought stats
    result = await call_tool("get-thought-stats")
    assert result["success"] is True
    assert "Retrieved statistics" in result["message"]
    assert result["stats"]["total_thoughts"] == 3
    assert result["stats"]["longest_thought_index"] == 2  # 1-indexed
    assert result["stats"]["longest_thought_length"] > 20

@pytest.mark.asyncio
async def test_multiple_thoughts_session():
    """Test a more complex session with multiple operations."""
    # Record some thoughts
    await call_tool("think", {"thought": "Initial problem analysis"})
    await call_tool("think", {"thought": "Breaking down sub-problems"})
    
    # Get thoughts
    result1 = await call_tool("get-thoughts")
    assert len(result1["thoughts"]) == 2
    
    # Add another thought
    await call_tool("think", {"thought": "Potential solution approach"})
    
    # Get updated thoughts
    result2 = await call_tool("get-thoughts")
    assert len(result2["thoughts"]) == 3
    
    # Get stats
    stats = await call_tool("get-thought-stats")
    assert stats["stats"]["total_thoughts"] == 3
    
    # Clear thoughts
    await call_tool("clear-thoughts")
    
    # Verify thoughts were cleared
    result3 = await call_tool("get-thoughts")
    assert len(result3["thoughts"]) == 0 