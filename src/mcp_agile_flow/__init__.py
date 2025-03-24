"""
MCP Agile Flow - A package for enhancing agile workflows with AI-assisted tools.

This package provides tools for managing project structure, documentation, and IDE integration
using the Model Context Protocol (MCP).

Primary tools:
- get-project-settings: Returns project settings including paths and configuration
- initialize-ide: Initialize a project with rules for a specific IDE
- initialize-ide-rules: Initialize a project with rules for a specific IDE (specialized)
- migrate-mcp-config: Migrate MCP configuration between different IDEs
- prime-context: Analyze project AI documentation to build context

The knowledge graph functionality has been migrated to a separate MCP server.
"""

from .version import __version__, get_version
from .adapter import call_tool, call_tool_sync

__all__ = ["__version__", "get_version", "call_tool", "call_tool_sync"]
