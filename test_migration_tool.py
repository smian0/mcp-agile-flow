#!/usr/bin/env python
"""
Test script to call the migrate-rules-to-windsurf MCP tool directly.
"""
import os
import json
import asyncio
import shutil
from pathlib import Path
from src.mcp_agile_flow.simple_server import handle_call_tool

async def test_migration():
    """Test the migrate-rules-to-windsurf tool directly."""
    # Set up a test directory with cursor rules
    base_dir = os.getcwd()
    test_dir = os.path.join(base_dir, "test_migration")
    
    # Create test directory
    os.makedirs(test_dir, exist_ok=True)
    
    # Create cursor rules directory
    cursor_dir = os.path.join(test_dir, ".cursor")
    rules_dir = os.path.join(cursor_dir, "rules")
    os.makedirs(rules_dir, exist_ok=True)
    
    # Copy sample rules files
    source_rules = os.path.join(base_dir, "src", "mcp_agile_flow", "cursor_rules")
    print(f"Copying rules from {source_rules} to {rules_dir}")
    
    for rule_file in os.listdir(source_rules):
        if rule_file.endswith(".mdc"):
            source_path = os.path.join(source_rules, rule_file)
            dest_path = os.path.join(rules_dir, rule_file)
            shutil.copy2(source_path, dest_path)
            print(f"Copied {rule_file}")
    
    # Set up arguments
    arguments = {
        "project_path": test_dir,
        "verbose": True,
        "no_truncate": False
    }
    
    print(f"\nTesting migration with arguments: {json.dumps(arguments, indent=2)}")
    
    # Call the tool handler directly
    result = await handle_call_tool("migrate-rules-to-windsurf", arguments)
    
    # Print the result
    print("\nMigration result:")
    for item in result:
        print(f"Type: {item.type}")
        print(f"Content: {item.text}")
    
    # Check if the file was created
    windsurf_rules = os.path.join(test_dir, ".windsurfrules")
    if os.path.exists(windsurf_rules):
        print(f"\nWindsurf rules file created successfully: {windsurf_rules}")
        with open(windsurf_rules, "r") as f:
            content = f.read()
            print(f"\nFile size: {len(content.encode('utf-8'))} bytes")
            print(f"First 100 characters: {content[:100]}...")
    else:
        print(f"\nWindsurf rules file was not created.")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_migration()) 