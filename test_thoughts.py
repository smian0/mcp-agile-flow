#!/usr/bin/env python3
"""
Simple test script for the thoughts functionality.
"""
import json
from src.mcp_agile_flow.think_tool import think, get_thoughts, clear_thoughts, get_thought_stats

def main():
    # Clear any existing thoughts
    clear_result = clear_thoughts()
    print("Clear thoughts result:", clear_result)
    
    # Add a thought
    think_result = think("This is a test thought from the direct script.")
    print("Think result:", think_result)
    
    # Get thoughts
    get_result = get_thoughts()
    print("Get thoughts result:", get_result)
    
    # Get stats
    stats_result = get_thought_stats()
    print("Get stats result:", stats_result)

if __name__ == "__main__":
    main() 