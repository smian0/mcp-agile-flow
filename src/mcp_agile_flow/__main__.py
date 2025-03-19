"""
Main entry point for running the MCP Agile Flow server.

This file allows the server to be executed using:
    python -m src.mcp_agile_flow
"""
from .simple_server import run

if __name__ == "__main__":
    run() 