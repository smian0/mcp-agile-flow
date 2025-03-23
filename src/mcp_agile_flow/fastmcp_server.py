"""
MCP Agile Flow - FastMCP Server Implementation

This module implements the MCP server with tools for agile workflow.
It uses the FastMCP API from the official MCP SDK.
"""

import logging
import os
import json

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

# Register all action-oriented tools (operations that modify state)
mcp.tool(name="initialize-ide")(initialize_ide)
mcp.tool(name="initialize-ide-rules")(initialize_ide_rules)
mcp.tool(name="prime-context")(prime_context)
mcp.tool(name="migrate-mcp-config")(migrate_mcp_config)
mcp.tool(name="create-entities")(create_entities)
mcp.tool(name="create-relations")(create_relations)
mcp.tool(name="add-observations")(add_observations)
mcp.tool(name="delete-entities")(delete_entities)
mcp.tool(name="delete-observations")(delete_observations)
mcp.tool(name="delete-relations")(delete_relations)

# Add resource-based API for data retrieval operations
# Project settings resources
@mcp.resource("settings://project")
def project_settings_resource() -> dict:
    """
    Resource representing the project settings.
    
    Returns the comprehensive project settings including project path, 
    knowledge graph directory, AI docs directory, project type, metadata, 
    and other configuration.
    
    Returns:
        Dict containing the project settings
    """
    logger.info("Resource access: settings://project")
    
    # Call the existing implementation but parse the JSON into a dict
    settings_json = get_project_settings()
    return json.loads(settings_json)

@mcp.resource("settings://project/{path}")
def project_settings_with_path(path: str) -> dict:
    """
    Resource representing the project settings for a specific path.
    
    Returns the comprehensive project settings for the specified path.
    
    Args:
        path: The project path to use
        
    Returns:
        Dict containing the project settings
    """
    logger.info(f"Resource access: settings://project/{path}")
    
    # Call the existing implementation but parse the JSON into a dict
    settings_json = get_project_settings(proposed_path=path)
    return json.loads(settings_json)

# Knowledge graph resources
@mcp.resource("graph://")
def graph_resource() -> dict:
    """
    Resource for accessing the entire knowledge graph.
    
    Returns:
        Dict containing the entire knowledge graph
    """
    logger.info("Resource access: graph://")
    
    # Call the existing implementation but parse the JSON into a dict
    graph_json = read_graph()
    return json.loads(graph_json)

@mcp.resource("graph://mermaid")
def mermaid_diagram_resource() -> dict:
    """
    Resource for accessing the Mermaid diagram representation of the knowledge graph.
    
    Returns:
        Dict containing the Mermaid diagram representation
    """
    logger.info("Resource access: graph://mermaid")
    
    # Call the existing implementation but parse the JSON into a dict
    diagram_json = get_mermaid_diagram()
    result = json.loads(diagram_json)
    
    # FastMCP resources should return dicts or lists directly, not strings
    # Make sure the result includes a 'mermaid' key with the diagram content
    if isinstance(result, dict) and "content" in result and not "mermaid" in result:
        # Create a standardized result format with 'mermaid' key
        return {"mermaid": result["content"], "success": result.get("success", True)}
    
    return result

@mcp.resource("entities://")
def list_entities() -> list:
    """
    Resource for listing all entities in the knowledge graph.
    
    Returns:
        List of entities in the knowledge graph
    """
    logger.info("Resource access: entities://")
    
    # Call the existing implementation but parse the JSON into a dict
    graph_json = read_graph()
    graph_data = json.loads(graph_json)
    
    # Return just the entities array
    return graph_data.get("entities", [])

@mcp.resource("entities/{name}")
def get_entity(name: str) -> dict:
    """
    Resource for accessing a specific entity in the knowledge graph.
    
    Args:
        name: The name of the entity to access
        
    Returns:
        Dict containing the entity data, or None if not found
    """
    logger.info(f"Resource access: entities/{name}")
    
    # Call the existing implementation but parse the JSON into a list
    result_json = open_nodes(names=[name])
    result_data = json.loads(result_json)
    
    # Get the entities list
    entities = result_data.get("entities", [])
    
    # Return the first entity if found, otherwise None
    return entities[0] if entities else None

@mcp.resource("entities/search/{query}")
def search_entities(query: str) -> dict:
    """
    Resource for searching entities in the knowledge graph.
    
    Args:
        query: The search query to match against entity names, types, and observation content
        
    Returns:
        Dict containing the search results
    """
    logger.info(f"Resource access: entities/search/{query}")
    
    # Call the existing implementation but parse the JSON into a dict
    result_json = search_nodes(query=query)
    return json.loads(result_json)

def run():
    """Entry point for running the server."""
    logger.info("Starting MCP Agile Flow server (FastMCP mode)")
    print("Starting MCP Agile Flow server...", file=os.sys.stderr)
    
    # Debug: Print registered resources
    resources = []
    for attr_name in dir(mcp):
        if attr_name.startswith('_') and 'resource' in attr_name.lower():
            resource_attr = getattr(mcp, attr_name, None)
            if isinstance(resource_attr, dict):
                resources = list(resource_attr.keys())
                break
    
    print(f"Registered resources: {resources}", file=os.sys.stderr)
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    # Configure logging when run directly
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    run() 