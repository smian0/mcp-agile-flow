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

# FastMCP Migration Guide

This document describes the migration process from the legacy server implementation to the FastMCP-based implementation.

## Overview

The MCP Agile Flow project is transitioning from a custom server implementation to the FastMCP framework to improve maintainability, performance, and compatibility with the wider MCP ecosystem. This migration involves:

1. Creating FastMCP-compatible implementations of all tools
2. Testing each tool with both implementations to ensure equivalence
3. Updating documentation and guides

## Migration Architecture

### Test Adapter

A key component of the migration is the test adapter, which allows tests to run against either implementation:

```python
# src/mcp_agile_flow/test_adapter.py
import os
import json
from typing import Dict, Any

# Use this env var to control which implementation is used
USE_FASTMCP = os.environ.get("MCP_USE_FASTMCP", "false").lower() in ("true", "1", "yes")

async def call_tool(name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call a tool using either the legacy or FastMCP implementation based on environment variable."""
    if USE_FASTMCP:
        # Use the FastMCP implementation
        return await _call_fastmcp_tool(name, arguments or {})
    else:
        # Use the legacy server implementation
        return await _call_server_tool(name, arguments or {})
```

This adapter dynamically selects the implementation based on the `MCP_USE_FASTMCP` environment variable, allowing tests to verify both implementations with the same test code.

### Migration Testing Script

A script is provided to run tests against both implementations and compare results:

```bash
# scripts/migrate_server_tests.sh
#!/bin/bash
# Run tests with both server implementations to verify equivalence

# First run with legacy implementation
export MCP_USE_FASTMCP=false
python -m pytest $TEST_FILES -v

# Then run with FastMCP implementation
export MCP_USE_FASTMCP=true
python -m pytest $TEST_FILES -v
```

## Migrated Tools

The following tools have been successfully migrated and tested with both legacy and FastMCP implementations:

### 1. `initialize-ide`

**Status**: Fully migrated and tested

This tool initializes a project with the necessary directory structure for a specific IDE.

**Implementation**: 
- Legacy: Using `handle_initialize_ide` in `server.py`
- FastMCP: Using `initialize_ide` in `fastmcp_tools.py`

### 2. `initialize-ide-rules`

**Status**: Fully migrated and tested

This tool creates IDE-specific rules files for a project.

**Implementation**:
- Legacy: Using `handle_initialize_ide_rules` in `server.py`
- FastMCP: Using `initialize_ide_rules` in `fastmcp_tools.py`

### 3. `prime-context`

**Status**: Fully migrated and tested

This tool analyzes project AI documentation to build contextual understanding.

**Implementation**:
- Legacy: Using `handle_prime_context` in `server.py`
- FastMCP: Using `prime_context` in `fastmcp_tools.py`

### 4. `migrate-mcp-config`

**Status**: Fully migrated and tested

This tool migrates MCP configuration between different IDEs.

**Implementation**:
- Legacy: Using `handle_migrate_mcp_config` in `server.py` 
- FastMCP: Using `migrate_mcp_config` in `fastmcp_tools.py`

### 5. `get-project-settings`

**Status**: Fully migrated and tested

This tool returns project settings including paths and configuration.

**Implementation**:
- Legacy: Using `handle_get_project_settings` in `server.py`
- FastMCP: Using `get_project_settings` in `fastmcp_tools.py`

### 6. Environment Variables Handling

**Status**: Fully migrated and tested

This functionality ensures consistent project path resolution via the PROJECT_PATH environment variable.

**Implementation**:
- Legacy: Using various tools in `server.py` and `utils.py`
- FastMCP: Using equivalent functionality in `fastmcp_tools.py` and `utils.py`

## Remaining Tools

The following tools still need to be migrated to FastMCP:

1. **`test_fastmcp_tools.py`** - Various tools specific to FastMCP
2. **`test_integration.py`** - Integration tests for multiple tools
3. **`tests/archive/path_tests/test_root_tool.py`** - Tests for path handling

## Testing Approach

To verify that a tool's FastMCP implementation is equivalent to its legacy implementation:

1. Create adapter tests that run the same test code against both implementations
2. Use the migration script to run tests with both implementations
3. Compare results and address any discrepancies
4. Document any intentional differences between the implementations

## Migration Roadmap

### Current Phase

- Migrating core tools with adapter tests for each
- Testing both implementations to ensure equivalence
- Updating documentation to reflect migration progress

### Next Phase

- Complete migration of remaining tools
- Enhance test coverage for complex scenarios
- Update all integration tests to work with both implementations

### Final Phase

- Complete retirement of legacy server code
- Full transition to FastMCP for all functionality
- Comprehensive documentation and guides for the new implementation

## Contributing to Migration

To help with the migration process:

1. Create FastMCP implementations of tools in `fastmcp_tools.py`
2. Create adapter tests that run against both implementations
3. Use the `./scripts/migrate_server_tests.sh` script to verify equivalence
4. Document any implementation differences or special considerations

## Testing Command Reference

Run tests with both implementations:

```bash
# Test a specific adapter
./scripts/migrate_server_tests.sh -f tests/test_initialize_ide_adapter.py -v

# Test multiple adapters
./scripts/migrate_server_tests.sh -f "tests/test_*_adapter.py" -v

# Test with increased verbosity
./scripts/migrate_server_tests.sh -f tests/test_initialize_ide_adapter.py -vv
```

### Migration Progress

#### Migrated Tools

1. **initialize-ide** - Fully migrated and tested
   - Legacy: `src/mcp_agile_flow/tools.py`
   - FastMCP: `src/mcp_agile_flow/fastmcp_tools.py`
   - Testing: `tests/test_initialize_ide_adapter.py`

2. **initialize-ide-rules** - Fully migrated and tested
   - Legacy: `src/mcp_agile_flow/tools.py`
   - FastMCP: `src/mcp_agile_flow/fastmcp_tools.py`
   - Testing: `tests/test_initialize_ide_rules_adapter.py`

3. **prime-context** - Fully migrated and tested
   - Legacy: `src/mcp_agile_flow/tools.py`
   - FastMCP: `src/mcp_agile_flow/fastmcp_tools.py`
   - Testing: `tests/test_prime_context_adapter.py`

4. **migrate-mcp-config** - Fully migrated and tested
   - Legacy: `src/mcp_agile_flow/tools.py`
   - FastMCP: `src/mcp_agile_flow/fastmcp_tools.py`
   - Testing: `tests/test_mcp_config_migration_adapter.py`

5. **get-project-settings** - Fully migrated and tested
   - Legacy: `src/mcp_agile_flow/tools.py`
   - FastMCP: `src/mcp_agile_flow/fastmcp_tools.py`
   - Testing: `tests/test_project_configuration_adapter.py`

6. **Environment variables handling (PROJECT_PATH)** - Fully migrated and tested
   - Legacy: `src/mcp_agile_flow/tools.py`
   - FastMCP: `src/mcp_agile_flow/utils.py`
   - Testing: `tests/test_env_variables_adapter.py`

7. **get-safe-project-path (replaced with get-project-settings)** - Migration complete
   - Legacy: This tool was deprecated in the legacy server
   - FastMCP: Functionality covered by `get-project-settings` in `src/mcp_agile_flow/fastmcp_tools.py`
   - Testing: `tests/test_integration_adapter.py::test_archive_path_tests`

#### Remaining Tests to Migrate

- `test_fastmcp_tools.py`
- `test_integration.py` 