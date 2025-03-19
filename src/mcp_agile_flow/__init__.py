"""
MCP Agile Flow - MCP server implementations.

This package provides an MCP server implementation for agile workflows.

Simple MCP Server:
- Extended MCP server with natural language capabilities
- Includes tools:
  - add-note: Add a new note with a name and content
  - hello-world: Returns a simple greeting
  - get-project-path: Returns information about project paths
  - Hey Sho: Process natural language commands
  - debug-tools: Get debug information about recent tool invocations

Usage:
    To run the server:
    ```
    python run_mcp_server.py
    ```
    
    To use in integration tests:
    ```python
    from mcp_agile_flow.simple_server import notes, mcp, run
    ```
"""

# Import from simple_server
from .simple_server import notes, mcp, run

# Expose important variables at package level
__all__ = [
    'notes',
    'mcp',
    'run'
]

"""
MCP Agile Flow package

This package provides MCP server implementations for agile workflow.
"""

__version__ = "0.1.0"