# MCP Agile Flow

[![Coverage](https://github.com/yourusername/mcp-agile-flow/raw/main/badges/coverage.svg)](https://yourusername.github.io/mcp-agile-flow/)

A Model Context Protocol (MCP) server that enhances agile workflows with project management tools and standardized documentation across different IDEs.

## Getting Started

### Prerequisites
- Python 3.10+
- uv (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/smian0/mcp-agile-flow.git
   cd mcp-agile-flow
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv .venv
   uv pip install -e .
   ```

### Quick Installation (One-Line)

You can install MCP Agile Flow directly from GitHub using our installation script:

```bash
# Using curl
curl -fsSL https://raw.githubusercontent.com/smian0/mcp-agile-flow/main/install.sh | bash

# Or using wget
wget -O- https://raw.githubusercontent.com/smian0/mcp-agile-flow/main/install.sh | bash
```

This script will:
1. Install MCP Agile Flow from GitHub (with SSH or HTTPS authentication)
2. Automatically detect your IDEs (Cursor, VS Code, Windsurf, Cline)
3. Configure MCP for all detected IDEs
4. Create a convenient command-line shortcut

No manual configuration needed - just run and restart your IDE!

### MCP Configuration

Generic MCP Configuration:
```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "/path/to/python",
      "args": ["-m", "mcp_agile_flow.server"],
      "disabled": false,
      "autoApprove": ["initialize-ide-rules", "get-project-settings"],
      "timeout": 30
    }
  }
}
```

Alternative MCP Configuration using UVX directly:
```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "uvx",
      "args": ["run", "-m", "mcp_agile_flow.server"],
      "disabled": false,
      "autoApprove": ["initialize-ide-rules", "get-project-settings"],
      "timeout": 30
    }
  }
}
```

### Installing from a Private GitHub Repository

You can install this MCP client directly from a private GitHub repository using UVX:

```bash
# Using SSH (recommended if you have SSH keys configured)
uv pip install git+ssh://git@github.com/username/mcp-agile-flow.git

# Using HTTPS with personal access token
uv pip install git+https://username:token@github.com/username/mcp-agile-flow.git

# Specify a branch, tag, or commit
uv pip install git+ssh://git@github.com/username/mcp-agile-flow.git@main
```

This method leverages your local Git configuration and authentication methods, so as long as you can access the repository via Git commands, UVX can install the package from it.

## Using the MCP Server

After installation, you can use the MCP tools through any compatible MCP client.

### Key Features

- **IDE Rules Integration**: Initialize and manage AI rules across different IDEs
- **Project Context Management**: Track project paths, settings, and documentation
- **MCP Configuration Migration**: Easily migrate MCP settings between different IDEs
- **Fast MCP Tools**: Enhanced Pythonic interface for tools with simplified registration

### Available Tools

- `get-project-settings`: Returns project settings including paths and configuration
- `get-safe-project-path`: Get a safe, writable project path
- `get-project-info`: Get project type and metadata
- `initialize-ide`: Initialize a project with rules for a specific IDE
- `initialize-ide-rules`: Initialize a project with rules for a specific IDE (specialized)
- `migrate-mcp-config`: Migrate MCP configuration between different IDEs
- `prime-context`: Analyze project AI documentation to build context

## Note on Knowledge Graph Functionality

The knowledge graph functionality (entity and relationship tracking, contextual awareness of documentation connections, and semantic search capabilities) has been moved to a separate MCP server. This decision was made to simplify the core MCP Agile Flow implementation and provide better separation of concerns. The core functionality of MCP Agile Flow continues to work without the knowledge graph.

**Status Update (Epic 7)**: Memory Graph Removal has been successfully completed. All integration tests have been updated to work correctly without memory graph dependencies. For testing purposes, the affected integration tests have been moved to the scripts directory, allowing the main test suite to run reliably without external dependencies.

## FastMCP Integration

We've implemented a streamlined FastMCP server that offers a more elegant approach to MCP tools integration:

### Key Features

- **Simplified Architecture**: Direct registration of tool functions without wrapper layers
- **Reduced Code Volume**: Eliminated ~1,400 lines of boilerplate code
- **Improved Maintainability**: Consistent patterns for all tools
- **Better Type Safety**: Proper type hints for parameters and return values

### Usage

You can run the FastMCP server with:

```bash
# Using the module directly
python -m mcp_agile_flow.fastmcp_server

# Using the console script
mcp-agile-flow-fastmcp
```

### Direct API Access

You can also use the FastMCP tools directly in your Python code:

```python
from mcp_agile_flow.fastmcp_tools import search_nodes, get_project_settings

# Get project settings
settings_json = get_project_settings()
settings = json.loads(settings_json)

# Search for nodes
results_json = search_nodes(query="TestEntity")
results = json.loads(results_json)
```

For more detailed information, see [README-FastMCP.md](README-FastMCP.md).

## FastMCP Migration Status

We are in the process of migrating from the legacy server implementation to a more maintainable FastMCP-based implementation. This allows for better integration with the MCP ecosystem and improves maintainability.

### Migrated and Tested Tools

The following tools have been successfully migrated and tested with both implementations:

- `initialize-ide`
- `initialize-ide-rules`
- `prime-context`
- `migrate-mcp-config`
- `get-project-settings`
- Environment variables handling (PROJECT_PATH)

### Migration Testing

Adapter tests have been created for each tool, which allow running the tests against both implementations to ensure they behave consistently. The test adapter is located at `src/mcp_agile_flow/test_adapter.py`.

To run tests for both implementations and verify equivalence:

```bash
./scripts/migrate_server_tests.sh -f tests/test_<tool>_adapter.py -v
```

### Remaining Tests to Migrate

The following tests still need to be migrated to use the adapter:

- `test_fastmcp_tools.py`
- `test_integration.py`

## Troubleshooting

### Common Issues

1. **Connection Error**: If you see an error like "ModuleNotFoundError: No module named...", check your MCP configuration. Make sure you're using:
   - The correct Python path (from your virtual environment)
   - The correct module path (`-m mcp_agile_flow.server`) 
   - No `.py` extension in the module name when using `-m`

2. **Permission Issues**: Ensure your Python virtual environment has the necessary permissions to run.

3. **Missing Modules**: If modules are missing, try reinstalling the package with:
   ```bash
   uv pip install -e .
   ```

## Debugging

You can use the MCP inspector to debug the server:

```bash
# For standard installations
npx @modelcontextprotocol/inspector python -m mcp_agile_flow.server

# For UVX installations 
npx @modelcontextprotocol/inspector uvx --with-editable . python -m mcp_agile_flow.server

# If you've installed from a private repository
GIT_SSH_COMMAND="ssh -i ~/.ssh/your_key" npx @modelcontextprotocol/inspector uvx --with mcp-agile-flow python -m mcp_agile_flow.server
```

## License

This project is licensed under the MIT License - See [LICENSE](LICENSE) file for details.