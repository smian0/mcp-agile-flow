"""
Test module for the thinking directive detection and depth functionality.

This module tests the enhanced features that detect when a user asks to
think harder, deeper, more, or again, and the ability to build on previous thoughts.
"""

import json
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
    """Test cases for the thinking directive detection and depth functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear any existing thoughts before each test
        clear_thoughts()
    
    def test_detect_thinking_directive_deeper(self):
        """Test detection of 'think deeper' directive."""
        # Test exact match
        result = detect_thinking_directive("think deeper")
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "deeper")
        self.assertEqual(result["confidence"], "high")
        
        # Test in a sentence
        result = detect_thinking_directive("Could you think deeper about this problem?")
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "deeper")
        self.assertEqual(result["confidence"], "medium")
        
        # Test variant
        result = detect_thinking_directive("Can you go deeper in your analysis?")
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "deeper")
    
    def test_detect_thinking_directive_harder(self):
        """Test detection of 'think harder' directive."""
        result = detect_thinking_directive("think harder")
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "harder")
        
        result = detect_thinking_directive("I need you to think with more effort")
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "harder")
    
    def test_detect_thinking_directive_again(self):
        """Test detection of 'think again' directive."""
        result = detect_thinking_directive("think again")
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "again")
        
        result = detect_thinking_directive("Please reconsider your approach")
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "again")
    
    def test_detect_thinking_directive_more(self):
        """Test detection of 'think more' directive."""
        result = detect_thinking_directive("think more")
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "more")
        
        result = detect_thinking_directive("Please continue thinking about this")
        self.assertTrue(result["detected"])
        self.assertEqual(result["directive_type"], "more")
    
    def test_detect_thinking_directive_negative(self):
        """Test detection with text that doesn't contain a directive."""
        result = detect_thinking_directive("What's the weather like today?")
        self.assertFalse(result["detected"])
        self.assertIsNone(result["directive_type"])
    
    def test_think_with_depth(self):
        """Test recording a thought with a specific depth level."""
        # Create a thought with depth=2
        result = think("This is a deeper thought", depth=2)
        result_json = json.loads(result)
        
        self.assertTrue(result_json["success"])
        self.assertIn("deeper analysis", result_json["message"])
        
        # Verify the thought was recorded with the correct depth
        thoughts = json.loads(get_thoughts())
        self.assertEqual(len(thoughts["thoughts"]), 1)
        self.assertEqual(thoughts["thoughts"][0]["depth"], 2)
    
    def test_think_with_previous_thought(self):
        """Test recording a thought that builds on a previous thought."""
        # Create initial thought
        initial_result = think("Initial thought")
        initial_json = json.loads(initial_result)
        initial_id = initial_json["thought_id"]
        
        # Create thought that builds on the initial thought
        follow_up_result = think(
            "Building on the previous thought", 
            depth=2, 
            previous_thought_id=initial_id
        )
        follow_up_json = json.loads(follow_up_result)
        
        # Verify link is established
        thoughts = json.loads(get_thoughts())
        self.assertEqual(len(thoughts["thoughts"]), 2)
        self.assertEqual(thoughts["thoughts"][1]["previous_thought_id"], initial_id)
    
    def test_get_thoughts_depth_chain(self):
        """Test retrieving thoughts organized in depth chains."""
        # Create a chain of thoughts
        first_result = think("Root thought")
        first_json = json.loads(first_result)
        first_id = first_json["thought_id"]
        
        second_result = think("Deeper analysis", depth=2, previous_thought_id=first_id)
        second_json = json.loads(second_result)
        second_id = second_json["thought_id"]
        
        third_result = think("Even deeper analysis", depth=3, previous_thought_id=second_id)
        
        # Add another root thought
        think("Another root thought")
        
        # Get thoughts with depth chain organization
        result = get_thoughts(include_depth_chain=True)
        result_json = json.loads(result)
        
        # Verify structure
        self.assertTrue(result_json["organized_by_depth"])
        self.assertEqual(len(result_json["thoughts"]), 2)  # Two root thoughts
        
        # Check the first chain
        first_chain = result_json["thoughts"][0]
        self.assertEqual(first_chain["depth"], 1)
        self.assertEqual(len(first_chain["deeper_thoughts"]), 1)
        
        # Check second level
        second_level = first_chain["deeper_thoughts"][0]
        self.assertEqual(second_level["depth"], 2)
        self.assertEqual(len(second_level["deeper_thoughts"]), 1)
        
        # Check third level
        third_level = second_level["deeper_thoughts"][0]
        self.assertEqual(third_level["depth"], 3)
    
    def test_think_more(self):
        """Test the think_more function that provides guidance for deeper thinking."""
        # Create initial thought
        initial_result = think("Initial problem analysis")
        initial_json = json.loads(initial_result)
        thought_id = initial_json["thought_id"]
        
        # Test with different directives
        for directive in ["deeper", "harder", "again", "more"]:
            result = think_more(directive, thought_id)
            result_json = json.loads(result)
            
            self.assertTrue(result_json["success"])
            self.assertEqual(result_json["source_thought"]["id"], thought_id)
            self.assertEqual(result_json["suggested_depth"], 2)
            self.assertIn(directive, result_json["message"])
            self.assertIsNotNone(result_json["guidance"])
    
    def test_think_more_without_id(self):
        """Test think_more using the most recent thought."""
        # Create multiple thoughts
        think("First thought")
        think("Second thought")
        last_result = think("Last thought")
        last_json = json.loads(last_result)
        last_id = last_json["thought_id"]
        
        # Call think_more without specifying an ID
        result = think_more("deeper")
        result_json = json.loads(result)
        
        # Should use the most recent thought
        self.assertTrue(result_json["success"])
        self.assertEqual(result_json["source_thought"]["id"], last_id)
    
    def test_think_more_no_thoughts(self):
        """Test think_more when there are no thoughts."""
        # Clear thoughts
        clear_thoughts()
        
        # Call think_more
        result = think_more("deeper")
        result_json = json.loads(result)
        
        # Should fail gracefully
        self.assertFalse(result_json["success"])
        self.assertIn("No previous thoughts", result_json["message"])


if __name__ == "__main__":
    unittest.main() 