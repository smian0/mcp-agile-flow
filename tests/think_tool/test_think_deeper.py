"""
Test module for advanced thinking features.

This tests depth-related functionality like thinking deeper on previous thoughts
and detecting when deeper thinking is needed.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from mcp_agile_flow.think_tool import (
    think,
    get_thoughts,
    clear_thoughts,
    detect_thinking_directive,
    think_more
)

class TestThinkDeeper(unittest.TestCase):
    """Test cases for deeper thinking functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_thoughts()
    
    def test_detect_thinking_directive_deeper(self):
        """Test detecting 'think deeper' directives."""
        text = "Let's think deeper about this problem"
        result = detect_thinking_directive(text)
        
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "deeper")
        self.assertEqual(result["confidence"], "medium")
    
    def test_detect_thinking_directive_harder(self):
        """Test detecting 'think harder' directives."""
        text = "We need to think harder about this"
        result = detect_thinking_directive(text)
        
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "harder")
        self.assertEqual(result["confidence"], "medium")
    
    def test_detect_thinking_directive_again(self):
        """Test detecting 'think again' directives."""
        text = "Let's think about this again"
        result = detect_thinking_directive(text)
        
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "again")
        self.assertEqual(result["confidence"], "medium")
    
    def test_detect_thinking_directive_more(self):
        """Test detecting 'think more' directives."""
        text = "We should think more about this"
        result = detect_thinking_directive(text)
        
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "more")
        self.assertEqual(result["confidence"], "medium")
    
    def test_detect_thinking_directive_negative(self):
        """Test that non-directive text is not detected."""
        text = "Here's what I think"
        result = detect_thinking_directive(text)
        
        self.assertFalse(result["detected"])
        self.assertEqual(result["confidence"], "low")
    
    def test_think_with_depth(self):
        """Test recording thoughts with different depth levels."""
        result = think("Initial thought", depth=1)
        
        self.assertTrue(result["success"])
        self.assertNotIn("deeper analysis", result["message"])
        
        result = think("Deeper thought", depth=2)
        
        self.assertTrue(result["success"])
        self.assertIn("deeper analysis", result["message"])
        
        result = think("Much deeper thought", depth=3)
        
        self.assertTrue(result["success"])
        self.assertIn("much deeper", result["message"])
    
    def test_think_with_previous_thought(self):
        """Test linking thoughts with previous thought IDs."""
        initial_result = think("Initial thought")
        
        self.assertTrue(initial_result["success"])
        initial_id = initial_result["thought_id"]
        
        follow_up = think("Follow-up thought", depth=2, previous_thought_id=initial_id)
        
        self.assertTrue(follow_up["success"])
        self.assertNotEqual(follow_up["thought_id"], initial_id)
    
    def test_get_thoughts_depth_chain(self):
        """Test retrieving thoughts organized by depth chains."""
        # Create a chain of thoughts
        first_result = think("First thought")
        first_id = first_result["thought_id"]
        
        second_result = think("Second thought", depth=2, previous_thought_id=first_id)
        second_id = second_result["thought_id"]
        
        third_result = think("Third thought", depth=3, previous_thought_id=second_id)
        
        # Get thoughts with depth chain organization
        result = get_thoughts(include_depth_chain=True)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["organized_by_depth"])
        self.assertEqual(len(result["thoughts"]), 1)  # One root thought
        
        root = result["thoughts"][0]
        self.assertEqual(root["depth"], 1)
        self.assertEqual(len(root["deeper_thoughts"]), 1)
        
        level2 = root["deeper_thoughts"][0]
        self.assertEqual(level2["depth"], 2)
        self.assertEqual(len(level2["deeper_thoughts"]), 1)
        
        level3 = level2["deeper_thoughts"][0]
        self.assertEqual(level3["depth"], 3)
        self.assertEqual(len(level3["deeper_thoughts"]), 0)
    
    def test_think_more(self):
        """Test getting guidance for thinking more deeply."""
        # Record initial thought
        initial_result = think("Initial thought")
        thought_id = initial_result["thought_id"]
        
        # Get guidance for thinking deeper
        result = think_more("deeper", thought_id)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["source_thought"]["id"], thought_id)
        self.assertEqual(result["suggested_depth"], 2)
        self.assertTrue(len(result["guidance"]) > 0)
    
    def test_think_more_without_id(self):
        """Test getting guidance without specifying thought ID."""
        # Record some thoughts
        think("First thought")
        last_result = think("Last thought")
        
        # Get guidance without ID
        result = think_more("deeper")
        
        self.assertTrue(result["success"])
        # Should use the last thought
        self.assertEqual(result["source_thought"]["id"], last_result["thought_id"])
    
    def test_think_more_no_thoughts(self):
        """Test think more behavior when no thoughts exist."""
        # Ensure no thoughts exist
        clear_thoughts()
        
        result = think_more("deeper")
        
        self.assertFalse(result["success"])
        self.assertIn("No previous thoughts", result["message"])

if __name__ == "__main__":
    unittest.main()
