#!/usr/bin/env python
"""
Simple entry point for MCP Agile Flow Simple Server

This script imports and runs the simple server from the correct module.
"""
import sys
import os

# Add the src directory to the path if it's not already there
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import and run the server
from mcp_agile_flow.simple_server import run

if __name__ == "__main__":
    run() 