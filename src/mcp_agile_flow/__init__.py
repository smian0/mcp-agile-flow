"""
MCP Agile Flow - A package for agile project management tools.

This package provides tools for managing agile workflows, rules migration,
and knowledge management using the MCP (Model Context Protocol) framework.

Available tools:
- initialize-ide-rules: Initialize a project with rules for a specific IDE
- initialize-rules: Initialize a project with cursor rules and templates
- migrate-rules-to-windsurf: Migrate rules from Cursor to Windsurf
- add-note: Add a new note
- get-project-path: Returns the current project directory path
- debug-tools: Get debug information about recent tool invocations
"""

# Import version
__version__ = '0.1.0'

# Expose key modules for external use
from . import rules_migration
from . import memory_graph

# For simplified imports
from .memory_graph import KnowledgeGraphManager, Entity, Relation, KnowledgeGraph

__all__ = [
    'rules_migration',
    'memory_graph', 
    'KnowledgeGraphManager',
    'Entity',
    'Relation',
    'KnowledgeGraph'
]