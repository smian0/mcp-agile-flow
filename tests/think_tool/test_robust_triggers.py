"""
Test module for the enhanced think tool functionality.

This tests the new features of the think tool, including thought categories,
templates, and self-assessment mechanism.
"""

import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from mcp_agile_flow.think_tool import (
    think, 
    get_thoughts, 
    clear_thoughts, 
    get_thought_stats, 
    get_thought_template,
    should_think
)


class TestThinkTool(unittest.TestCase):
    """Test cases for the enhanced think tool functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear any existing thoughts before each test
        clear_thoughts()
    
    def test_think_with_category(self):
        """Test recording a thought with a category."""
        result = think("This is a test thought", "test-category")
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertIn("test-category", result_json["message"])
        
        # Verify the thought was recorded with the category
        thoughts = json.loads(get_thoughts())
        self.assertEqual(len(thoughts["thoughts"]), 1)
        self.assertEqual(thoughts["thoughts"][0]["category"], "test-category")
    
    def test_get_thoughts_filtered_by_category(self):
        """Test retrieving thoughts filtered by category."""
        # Add thoughts with different categories
        think("Thought 1", "category-1")
        think("Thought 2", "category-2")
        think("Thought 3", "category-1")
        
        # Get thoughts for category-1
        result = get_thoughts("category-1")
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertEqual(len(result_json["thoughts"]), 2)
        self.assertEqual(result_json["thoughts"][0]["category"], "category-1")
        self.assertEqual(result_json["thoughts"][1]["category"], "category-1")
    
    def test_clear_thoughts_by_category(self):
        """Test clearing thoughts of a specific category."""
        # Add thoughts with different categories
        think("Thought 1", "category-1")
        think("Thought 2", "category-2")
        think("Thought 3", "category-1")
        
        # Clear thoughts for category-1
        result = clear_thoughts("category-1")
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertEqual(result_json["message"], "Cleared 2 recorded thoughts in category 'category-1'.")
        
        # Verify only category-1 thoughts were cleared
        thoughts = json.loads(get_thoughts())
        self.assertEqual(len(thoughts["thoughts"]), 1)
        self.assertEqual(thoughts["thoughts"][0]["category"], "category-2")
    
    def test_get_thought_stats_with_category(self):
        """Test getting thought statistics for a specific category."""
        # Add thoughts with different categories
        think("Thought 1", "category-1")
        think("Thought 2", "category-2")
        think("Long thought in category 1 " + "x" * 100, "category-1")
        
        # Get stats for category-1
        result = get_thought_stats("category-1")
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertEqual(result_json["stats"]["total_thoughts"], 2)
        # The longest thought should be the third one
        self.assertTrue(result_json["stats"]["longest_thought_length"] > 100)
    
    def test_get_thought_template(self):
        """Test retrieving thought templates."""
        # Test valid template type
        result = get_thought_template("problem-decomposition")
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertIn("Problem Statement", result_json["template"])
        self.assertEqual(result_json["template_type"], "problem-decomposition")
        
        # Test invalid template type
        result = get_thought_template("invalid-template")
        result_json = json.loads(result)
        
        self.assertFalse(result_json["success"])
        self.assertIn("not found", result_json["message"])
        self.assertTrue(len(result_json["available_templates"]) > 0)
    
    def test_should_think_high_complexity(self):
        """Test self-assessment with high complexity query."""
        query = "Please help me optimize our system architecture to balance performance, cost, and security requirements."
        result = should_think(query)
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertTrue(result_json["should_think"])
        self.assertEqual(result_json["confidence"], "high")
        self.assertTrue(len(result_json["detected_indicators"]) > 0)
    
    def test_should_think_medium_complexity(self):
        """Test self-assessment with medium complexity query."""
        query = "How do I implement this feature following our coding standards?"
        result = should_think(query)
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertTrue(result_json["should_think"])
        # Could be low or medium confidence depending on exact implementation
        self.assertIn(result_json["confidence"], ["low", "medium"])
    
    def test_should_think_low_complexity(self):
        """Test self-assessment with low complexity query."""
        query = "What is 2 + 2?"
        result = should_think(query)
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertFalse(result_json["should_think"])
        self.assertEqual(result_json["confidence"], "high")
    
    def test_should_think_with_context(self):
        """Test self-assessment with additional context."""
        query = "How should I proceed?"  # Ambiguous query alone
        context = "We need to balance multiple competing requirements while ensuring compliance with regulations."
        result = should_think(query, context)
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertTrue(result_json["should_think"])
        # Context should increase complexity score
        self.assertTrue(result_json["complexity_score"] > 0)


if __name__ == "__main__":
    unittest.main() 