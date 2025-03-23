"""
MCP Agile Flow - FastMCP Server Implementation

This module implements the MCP server with tools for agile workflow.
It uses the FastMCP API from the official MCP SDK.
"""

import logging
import os
from typing import Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP

# Import all FastMCP tool implementations
from mcp_agile_flow.fastmcp_tools import (
    get_project_settings,
    get_mermaid_diagram,
    read_graph,
    initialize_ide,
    prime_context,
    migrate_mcp_config,
    initialize_ide_rules,
    create_entities,
    create_relations,
    add_observations,
    delete_entities,
    delete_observations,
    delete_relations,
    search_nodes,
    open_nodes,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create the FastMCP server instance
mcp = FastMCP("agile-flow")  # Must match the name in client configuration


# Register FastMCP tools using the decorator pattern
@mcp.tool(name="get-project-settings")
def get_project_settings_tool(proposed_path: Optional[str] = None) -> Dict:
    """Returns comprehensive project settings including project path, knowledge graph directory, AI docs directory, 
    project type, metadata, and other configuration."""
    logger.info(f"Calling get-project-settings with proposed_path: {proposed_path}")
    return get_project_settings(proposed_path)


@mcp.tool(name="get-mermaid-diagram")
def get_mermaid_diagram_tool() -> Dict:
    """Get a Mermaid diagram representation of the knowledge graph"""
    logger.info("Calling get-mermaid-diagram")
    return get_mermaid_diagram()


@mcp.tool(name="read-graph")
def read_graph_tool() -> Dict:
    """Read the entire knowledge graph"""
    logger.info("Calling read-graph")
    return read_graph()


@mcp.tool(name="initialize-ide")
def initialize_ide_tool(ide: str = "cursor", project_path: Optional[str] = None) -> Dict:
    """Initialize a project with rules for a specific IDE"""
    logger.info(f"Calling initialize-ide with ide: {ide}, project_path: {project_path}")
    return initialize_ide(ide=ide, project_path=project_path)


@mcp.tool(name="initialize-ide-rules")
def initialize_ide_rules_tool(ide: str = "cursor", project_path: Optional[str] = None) -> Dict:
    """Initialize a project with rules for a specific IDE"""
    logger.info(f"Calling initialize-ide-rules with ide: {ide}, project_path: {project_path}")
    return initialize_ide_rules(ide=ide, project_path=project_path)


@mcp.tool(name="prime-context")
def prime_context_tool(
    depth: str = "standard", 
    focus_areas: Optional[List[str]] = None, 
    project_path: Optional[str] = None
) -> Dict:
    """Analyzes project's AI documentation to build contextual understanding"""
    logger.info(f"Calling prime-context with depth: {depth}, focus_areas: {focus_areas}, project_path: {project_path}")
    return prime_context(depth=depth, focus_areas=focus_areas, project_path=project_path)


@mcp.tool(name="migrate-mcp-config")
def migrate_mcp_config_tool(
    from_ide: str, 
    to_ide: str, 
    backup: bool = True, 
    conflict_resolutions: Optional[Dict[str, bool]] = None
) -> Dict:
    """Migrate MCP configuration between different IDEs with smart merging and conflict resolution"""
    logger.info(f"Calling migrate-mcp-config with from_ide: {from_ide}, to_ide: {to_ide}")
    return migrate_mcp_config(from_ide=from_ide, to_ide=to_ide, backup=backup, conflict_resolutions=conflict_resolutions)


@mcp.tool(name="create-entities")
def create_entities_tool(entities: List[Dict]) -> Dict:
    """Create multiple new entities in the knowledge graph"""
    logger.info(f"Calling create-entities with {len(entities)} entities")
    return create_entities(entities=entities)


@mcp.tool(name="create-relations")
def create_relations_tool(relations: List[Dict]) -> Dict:
    """Create multiple new relations between entities in the knowledge graph"""
    logger.info(f"Calling create-relations with {len(relations)} relations")
    return create_relations(relations=relations)


@mcp.tool(name="add-observations")
def add_observations_tool(observations: List[Dict]) -> Dict:
    """Add new observations to existing entities in the knowledge graph"""
    logger.info(f"Calling add-observations with observations for {len(observations)} entities")
    return add_observations(observations=observations)


@mcp.tool(name="delete-entities")
def delete_entities_tool(entityNames: List[str]) -> Dict:
    """Delete multiple entities and their associated relations from the knowledge graph"""
    logger.info(f"Calling delete-entities with {len(entityNames)} entities")
    return delete_entities(entityNames=entityNames)


@mcp.tool(name="delete-observations")
def delete_observations_tool(deletions: List[Dict]) -> Dict:
    """Delete specific observations from entities in the knowledge graph"""
    logger.info(f"Calling delete-observations with deletions for {len(deletions)} entities")
    return delete_observations(deletions=deletions)


@mcp.tool(name="delete-relations")
def delete_relations_tool(relations: List[Dict]) -> Dict:
    """Delete multiple relations from the knowledge graph"""
    logger.info(f"Calling delete-relations with {len(relations)} relations")
    return delete_relations(relations=relations)


@mcp.tool(name="search-nodes")
def search_nodes_tool(query: str) -> Dict:
    """Search for nodes in the knowledge graph based on a query"""
    logger.info(f"Calling search-nodes with query: {query}")
    return search_nodes(query=query)


@mcp.tool(name="open-nodes")
def open_nodes_tool(names: List[str]) -> Dict:
    """Open specific nodes in the knowledge graph by their names"""
    logger.info(f"Calling open-nodes with {len(names)} names")
    return open_nodes(names=names)


def run():
    """Entry point for running the server."""
    logger.info("Starting MCP Agile Flow server (FastMCP mode)")
    print("Starting MCP Agile Flow server...", file=os.sys.stderr)
    
    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    # Configure logging when run directly
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    run() 