def register_memory_tools(mcp_server):
    """Register memory graph tools with the MCP server.

    Args:
        mcp_server: The MCP server instance to register tools with

    Returns:
        A tuple of (memory_tools, manager) where memory_tools is a list of Tool objects
        and manager is the KnowledgeGraphManager instance.
    """
    # Create a singleton KnowledgeGraphManager to handle all operations
    manager = KnowledgeGraphManager()

    # Define memory graph tools to be added to the handle_list_tools function
    memory_tools = [
        Tool(
            name="create_entities",
            description="Create multiple new entities in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "The name of the entity",
                                },
                                "entityType": {
                                    "type": "string",
                                    "description": "The type of the entity",
                                },
                                "observations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "An array of observation contents associated with the entity",
                                },
                            },
                            "required": ["name", "entityType"],
                        },
                    }
                },
                "required": ["entities"],
            },
        ),
        Tool(
            name="create_relations",
            description="Create multiple new relations between entities in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from": {
                                    "type": "string",
                                    "description": "The name of the entity where the relation starts",
                                },
                                "to": {
                                    "type": "string",
                                    "description": "The name of the entity where the relation ends",
                                },
                                "relationType": {
                                    "type": "string",
                                    "description": "The type of the relation",
                                },
                            },
                            "required": ["from", "to", "relationType"],
                        },
                    }
                },
                "required": ["relations"],
            },
        ),
        Tool(
            name="add_observations",
            description="Add new observations to existing entities in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "observations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entityName": {
                                    "type": "string",
                                    "description": "The name of the entity to add the observations to",
                                },
                                "contents": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "An array of observation contents to add",
                                },
                            },
                            "required": ["entityName", "contents"],
                        },
                    }
                },
                "required": ["observations"],
            },
        ),
        Tool(
            name="delete_entities",
            description="Delete multiple entities and their associated relations from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "entityNames": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of entity names to delete",
                    }
                },
                "required": ["entityNames"],
            },
        ),
        Tool(
            name="delete_observations",
            description="Delete specific observations from entities in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "deletions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entityName": {
                                    "type": "string",
                                    "description": "The name of the entity containing the observations",
                                },
                                "observations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "An array of observations to delete",
                                },
                            },
                            "required": ["entityName", "observations"],
                        },
                    }
                },
                "required": ["deletions"],
            },
        ),
        Tool(
            name="delete_relations",
            description="Delete multiple relations from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from": {
                                    "type": "string",
                                    "description": "The name of the entity where the relation starts",
                                },
                                "to": {
                                    "type": "string",
                                    "description": "The name of the entity where the relation ends",
                                },
                                "relationType": {
                                    "type": "string",
                                    "description": "The type of the relation",
                                },
                            },
                            "required": ["from", "to", "relationType"],
                        },
                        "description": "An array of relations to delete",
                    }
                },
                "required": ["relations"],
            },
        ),
        Tool(
            name="read_graph",
            description="Read the entire knowledge graph",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="search_nodes",
            description="Search for nodes in the knowledge graph based on a query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to match against entity names, types, and observation content",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="open_nodes",
            description="Open specific nodes in the knowledge graph by their names",
            inputSchema={
                "type": "object",
                "properties": {
                    "names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of entity names to retrieve",
                    }
                },
                "required": ["names"],
            },
        ),
    ]

    # Export the memory tools and manager for use in server.py
    return memory_tools, manager
