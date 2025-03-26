"""
Tests for the Think Tool functionality in MCP Agile Flow.

These tests verify that the think tool correctly records, retrieves, and manages thoughts.
"""

import asyncio
from pathlib import Path
import pytest
from typing import Dict, Any

from src.mcp_agile_flow.think_tool import (
    think,
    get_thoughts,
    clear_thoughts,
    get_thought_stats,
    detect_thinking_directive,
    think_more
)

# Clear thoughts before each test
@pytest.fixture(autouse=True)
def clear_existing_thoughts():
    clear_thoughts()

def test_think():
    """Test recording a thought."""
    result = think("This is a test thought.")
    
    assert result["success"] is True
    assert "Thought recorded" in result["message"]
    
    # Verify thought was stored
    thoughts = get_thoughts()
    assert thoughts["success"] is True
    assert len(thoughts["thoughts"]) == 1
    assert thoughts["thoughts"][0]["thought"] == "This is a test thought."

def test_get_thoughts_empty():
    """Test getting thoughts when none exist."""
    result = get_thoughts()
    
    assert result["success"] is True
    assert "No thoughts have been recorded yet" in result["message"]
    assert result["thoughts"] == []

def test_get_thoughts():
    """Test getting thoughts when some exist."""
    # Record thoughts
    think("First thought")
    think("Second thought")
    
    # Get the thoughts
    result = get_thoughts()
    
    assert result["success"] is True
    assert len(result["thoughts"]) == 2
    assert result["thoughts"][0]["thought"] == "First thought"
    assert result["thoughts"][1]["thought"] == "Second thought"
    assert result["thoughts"][0]["index"] == 1
    assert result["thoughts"][1]["index"] == 2

def test_clear_thoughts():
    """Test clearing thoughts."""
    # Record thoughts
    think("A thought to clear")
    think("Another thought to clear")
    
    # Get stats before clearing
    stats = get_thought_stats()
    assert stats["success"] is True
    assert stats["stats"]["total_thoughts"] == 2
    
    # Clear thoughts
    result = clear_thoughts()
    
    assert result["success"] is True
    assert "Cleared 2 recorded thoughts" in result["message"]
    
    # Verify they were cleared
    stats = get_thought_stats()
    assert stats["success"] is True
    assert stats["stats"]["total_thoughts"] == 0

def test_get_thought_stats_empty():
    """Test getting stats when no thoughts exist."""
    result = get_thought_stats()
    
    assert result["success"] is True
    assert "No thoughts have been recorded yet" in result["message"]
    assert result["stats"]["total_thoughts"] == 0

def test_get_thought_stats():
    """Test getting stats when thoughts exist."""
    # Record thoughts
    think("A short thought")
    think("A much longer thought that has more characters and should be the longest")
    think("Medium length thought")
    
    # Get stats
    result = get_thought_stats()
    
    assert result["success"] is True
    assert result["stats"]["total_thoughts"] == 3
    assert result["stats"]["longest_thought_index"] == 2  # 1-indexed
    assert result["stats"]["longest_thought_length"] > 20

def test_multiple_thoughts_session():
    """Test a more complex session with multiple operations."""
    # Record initial thoughts
    think("Initial problem analysis")
    think("Breaking down sub-problems")
    
    # Get thoughts
    result1 = get_thoughts()
    assert len(result1["thoughts"]) == 2
    
    # Add another thought
    think("Potential solution approach")
    
    # Get updated thoughts
    result2 = get_thoughts()
    assert len(result2["thoughts"]) == 3
    
    # Get stats
    stats = get_thought_stats()
    assert stats["stats"]["total_thoughts"] == 3
    
    # Clear thoughts
    clear_thoughts()
    
    # Verify cleared
    result3 = get_thoughts()
    assert len(result3["thoughts"]) == 0

def test_think_with_category():
    """Test recording a thought with a category."""
    result = think("A categorized thought", category="test-category")
    
    assert result["success"] is True
    assert "test-category" in result["message"]
    
    thoughts = get_thoughts(category="test-category")
    assert len(thoughts["thoughts"]) == 1
    assert thoughts["thoughts"][0]["category"] == "test-category"

def test_think_with_depth():
    """Test recording thoughts with different depths."""
    result1 = think("Initial thought", depth=1)
    
    assert result1["success"] is True
    assert "deeper" not in result1["message"]
    
    result2 = think("Deeper thought", depth=2)
    
    assert result2["success"] is True
    assert "deeper" in result2["message"]

def test_get_thoughts_with_depth_chain():
    """Test retrieving thoughts with depth chain organization."""
    # Create chain of thoughts
    first = think("First thought")
    second = think("Second thought", depth=2, previous_thought_id=first["thought_id"])
    third = think("Third thought", depth=3, previous_thought_id=second["thought_id"])
    
    # Get organized thoughts
    result = get_thoughts(include_depth_chain=True)
    
    assert result["success"] is True
    assert result["organized_by_depth"] is True
    assert len(result["thoughts"]) == 1  # One root thought
    
    root = result["thoughts"][0]
    assert root["depth"] == 1
    assert len(root["deeper_thoughts"]) == 1
    
    level2 = root["deeper_thoughts"][0]
    assert level2["depth"] == 2
    assert len(level2["deeper_thoughts"]) == 1
