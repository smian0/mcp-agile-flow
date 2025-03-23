# MCP Agile Flow: FastMCP Implementation

This project has been migrated to use the official MCP SDK's FastMCP implementation, providing a cleaner, more maintainable codebase with simplified tool registration.

## Overview

The MCP Agile Flow project now offers two server implementations:

1. **Legacy Server** (`mcp_agile_flow.server`) - The original implementation with manual protocol handling
2. **FastMCP Server** (`mcp_agile_flow.fastmcp_server`) - A modern implementation using FastMCP from the official MCP SDK

## Benefits of the FastMCP Implementation

- **Simplified Tool Registration** - Tools are registered using decorators instead of complex handler functions
- **Reduced Boilerplate** - Eliminates repetitive code blocks for handling tool calls
- **Improved Type Safety** - Better type annotations for parameters and return values
- **Standardized Error Handling** - Consistent error handling across all tools
- **Easier Maintenance** - Code is more modular and easier to understand
- **Integration with MCP SDK** - Uses the officially supported FastMCP implementation

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

# Test the server with a tool call
mcp call mcp_agile_flow.fastmcp_server get-project-settings
```

## Available Tools

All tools have been migrated to the FastMCP implementation:

- **Project Tools**
  - `get-project-settings` - Returns comprehensive project settings
  - `initialize-ide` - Initialize a project with rules for a specific IDE
  - `initialize-ide-rules` - Initialize IDE-specific rules for a project
  - `prime-context` - Analyze project AI documentation to build context
  - `migrate-mcp-config` - Migrate MCP configuration between IDEs

- **Knowledge Graph Tools**
  - `get-mermaid-diagram` - Generate a Mermaid diagram of the knowledge graph
  - `read-graph` - Read the entire knowledge graph
  - `create-entities` - Create new entities in the knowledge graph
  - `create-relations` - Create new relations between entities
  - `add-observations` - Add observations to existing entities
  - `delete-entities` - Delete entities and their associated relations
  - `delete-observations` - Delete specific observations from entities
  - `delete-relations` - Delete relations from the knowledge graph
  - `search-nodes` - Search for nodes in the knowledge graph
  - `open-nodes` - Open specific nodes in the knowledge graph

## Direct API Usage

You can also use the FastMCP tools directly in your Python code:

```python
from mcp_agile_flow.fastmcp_tools import get_project_settings, create_entities

# Get project settings
settings = get_project_settings()

# Create an entity
result = create_entities(entities=[
    {
        "name": "MyEntity",
        "entityType": "concept",
        "observations": ["An important concept"]
    }
])
```

## Testing

A test script is provided to verify the FastMCP implementation:

```bash
python test_fastmcp_server.py
``` 