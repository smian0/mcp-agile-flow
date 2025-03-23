# MCP Agile Flow: FastMCP Implementation

This project has been migrated to use the official MCP SDK's FastMCP implementation, providing a modern, resource-based API with RESTful principles.

## Overview

The MCP Agile Flow project now uses a resource-based approach with FastMCP from the official MCP SDK, focusing on:

- **RESTful API Design** - Clean, intuitive resource URIs for data access
- **Resource-First Architecture** - Optimized for data retrieval and state representation
- **Action-Oriented Tools** - Tools used only for operations that modify state

## Benefits of the Resource-Based Implementation

- **Intuitive API Structure** - Resources organized in a RESTful hierarchy
- **Simplified Integration** - Direct mapping to resource URIs
- **Improved Caching** - Resources can be cached by clients
- **Reduced Complexity** - Separation of query operations from action operations
- **Better Performance** - Optimized for data access patterns

## Using the FastMCP Server

### In MCP Client Configuration

Update your MCP client configuration to use the FastMCP server:

```json
{
    "name": "mcp-agile-flow",
    "server": {
        "type": "module",
        "module": "mcp_agile_flow.fastmcp_server",
        "entry_point": "run"
    }
}
```

### Command Line Usage

You can also run the FastMCP server directly from the command line:

```bash
# Using the entry point
mcp-agile-flow-fastmcp

# Using Python
python -m mcp_agile_flow.fastmcp_server
```

### Using the `mcp` CLI Tool

The MCP SDK provides a CLI tool for working with MCP servers:

```bash
# Install the server in Claude Desktop
mcp install mcp_agile_flow.fastmcp_server

# Run the server in development mode
mcp run mcp_agile_flow.fastmcp_server
```

## RESTful Resources API

The server provides a comprehensive resource-based API following RESTful principles:

### Project Settings Resources

| Resource URI | Description |
|--------------|-------------|
| `settings://project` | Get project settings with default configuration |
| `settings://project/{path}` | Get project settings for a specific path |

### Knowledge Graph Resources

| Resource URI | Description |
|--------------|-------------|
| `graph://` | Get the entire knowledge graph |
| `graph://mermaid` | Get Mermaid diagram representation of the graph |
| `entities://` | List all entities in the knowledge graph |
| `entities/{name}` | Get a specific entity by name |
| `entities/search/{query}` | Search for entities matching the query |

### Resource Usage Examples

Using the MCP client:

```bash
# Get project settings
mcp resource mcp_agile_flow.fastmcp_server "settings://project"

# Get entity by name
mcp resource mcp_agile_flow.fastmcp_server "entities/MyEntity"

# Search for entities
mcp resource mcp_agile_flow.fastmcp_server "entities/search/concept"
```

Using direct Python code:

```python
from mcp.client import Client

client = Client("mcp-agile-flow")

# Get project settings
settings = client.resource("settings://project")

# Get entity by name
entity = client.resource("entities/MyEntity")

# Search for entities
search_results = client.resource("entities/search/concept")
```

## Action-Oriented Tools

For operations that modify state, the server provides action-oriented tools:

| Tool Name | Description |
|-----------|-------------|
| `initialize-ide` | Initialize a project with rules for a specific IDE |
| `initialize-ide-rules` | Initialize IDE-specific rules for a project |
| `prime-context` | Analyze project AI documentation to build context |
| `migrate-mcp-config` | Migrate MCP configuration between IDEs |
| `create-entities` | Create new entities in the knowledge graph |
| `create-relations` | Create new relations between entities |
| `add-observations` | Add observations to existing entities |
| `delete-entities` | Delete entities and their associated relations |
| `delete-observations` | Delete specific observations from entities |
| `delete-relations` | Delete relations from the knowledge graph |

## Direct API Usage

You can also use the FastMCP tools directly in your Python code:

```python
# For action-oriented operations
from mcp_agile_flow.fastmcp_tools import create_entities

# Create an entity
result = create_entities(entities=[
    {
        "name": "MyEntity",
        "entityType": "concept",
        "observations": ["An important concept"]
    }
])

# For data retrieval operations, use resources directly
from mcp_agile_flow.fastmcp_server import project_settings_resource, get_entity

# Get project settings
settings = project_settings_resource()

# Get entity by name
entity = get_entity("MyEntity")
```

## Testing

A comprehensive test script is provided to verify the implementation:

```bash
python test_fastmcp_comprehensive.py
```

## Resource-First Implementation

### RESTful Design Principles

The resource-based API follows key RESTful principles:

1. **Resource-Oriented** - Data is organized around resources
2. **Standard HTTP Semantics** - Though not using HTTP directly, follows standard URL patterns
3. **Stateless** - Each request contains all information needed
4. **Hierarchical** - Resources organized in a logical hierarchy

### Implementation Details

Resources are implemented in `fastmcp_server.py` with clear URI patterns:

```python
@mcp.resource("entities/{name}")
def get_entity(name: str) -> dict:
    """Resource for accessing a specific entity in the knowledge graph."""
    logger.info(f"Resource access: entities/{name}")
    
    result_json = open_nodes(names=[name])
    result_data = json.loads(result_json)
    
    entities = result_data.get("entities", [])
    return entities[0] if entities else None
```

Each resource:
1. Has a clear, descriptive URI
2. Accepts path or query parameters when needed
3. Returns JSON-compatible Python objects (dicts, lists)
4. Includes proper error handling and logging

## Implementation Benefits

### Resource-First Approach

The resource-based implementation provides:

1. **Cleaner API Design** - URIs map directly to resources
2. **Better API Discoverability** - Logical resource hierarchy
3. **Enhanced Caching** - Resources can be cached by clients
4. **Separation of Concerns** - Action tools vs. resource endpoints

### When to Use Resources vs. Tools

| Use Case | Recommendation |
|----------|----------------|
| Retrieving data | Resources |
| Reading state | Resources |
| Creating data | Tools |
| Updating state | Tools |
| Deleting data | Tools |
| Performing operations | Tools |

### Testing

The implementation is tested with a comprehensive test suite that verifies both resource endpoints and action-oriented tools:

```bash
# Run the comprehensive test
python test_fastmcp_comprehensive.py
``` 