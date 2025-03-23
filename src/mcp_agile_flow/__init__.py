"""
MCP Agile Flow Tools

Primary tools:
- get-project-settings: Returns project settings including paths and configuration
- get-safe-project-path: Get a safe, writable project path
- get-project-info: Get project type and metadata from the knowledge graph
- get-mermaid-diagram: Generate a Mermaid diagram of the knowledge graph
- initialize-ide: Initialize a project with rules for a specific IDE
- initialize-ide-rules: Initialize a project with rules for a specific IDE (specialized)
- migrate-mcp-config: Migrate MCP configuration between different IDEs
- prime-context: Analyze project AI documentation to build context

Knowledge graph tools:
- create-entities: Create multiple new entities in the knowledge graph
- create-relations: Create multiple new relations between entities
- add-observations: Add new observations to existing entities
- delete-entities: Delete multiple entities and their associated relations
- delete-observations: Delete specific observations from entities
- delete-relations: Delete multiple relations from the knowledge graph
- read-graph: Read the entire knowledge graph
- search-nodes: Search for nodes in the knowledge graph based on a query
- open-nodes: Open specific nodes in the knowledge graph by their names
"""

# Import version
__version__ = "0.9.1"

# Expose key modules for external use
from . import memory_graph, initialize_ide_rules

# For simplified imports
from .memory_graph import Entity, KnowledgeGraph, KnowledgeGraphManager, Relation

__all__ = [
    "initialize_ide_rules",
    "memory_graph",
    "KnowledgeGraphManager",
    "Entity",
    "Relation",
    "KnowledgeGraph",
]
