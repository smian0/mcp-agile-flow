#!/usr/bin/env python3
"""
Test script for the ThoughtStorage singleton class.
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.mcp_agile_flow.think_tool import _storage, think, get_thoughts

def main():
    # Check if we should add a thought or get thoughts
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        # Add a thought
        thought_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Default test thought"
        result = think(thought_text)
        print(f"Added thought: {thought_text}")
        print(f"Result: {result}")
        print(f"Current thoughts count: {_storage.get_thought_count()}")
        print(f"Current thoughts: {_storage.get_thoughts()}")
    else:
        # Get thoughts
        result = get_thoughts()
        print(f"Get thoughts result: {result}")
        print(f"Current thoughts count: {_storage.get_thought_count()}")
        print(f"Memory ID of _storage: {id(_storage)}")

if __name__ == "__main__":
    main() 