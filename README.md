# MCP Agile Flow

[![Coverage](https://github.com/yourusername/mcp-agile-flow/raw/main/badges/coverage.svg)](https://yourusername.github.io/mcp-agile-flow/)

A comprehensive system for managing AI-assisted agile development workflows with a modern, resource-based API using FastMCP.

## Status

✅ **Migration Complete**: The migration from legacy server to FastMCP implementation is fully complete. All legacy code and tests have been removed.

## Overview

The MCP Agile Flow project uses a resource-based approach with FastMCP from the official MCP SDK, focusing on:

- **RESTful API Design** - Clean, intuitive resource URIs for data access
- **Resource-First Architecture** - Optimized for data retrieval and state representation
- **Action-Oriented Tools** - Tools used only for operations that modify state

## Key Features

- **Agile Documentation**: Generate and maintain comprehensive AI documentation
- **Project Structure**: Organize your project with AI-generated files and directories
- **IDE Integration**: Direct integration with various AI IDEs (Cursor, Windsurf, Cline)
- **Workflow Management**: Track agile stories and progress
- **Intuitive API Structure**: Resources organized in a RESTful hierarchy
- **Simplified Integration**: Direct mapping to resource URIs
- **Improved Performance**: Optimized for data access patterns

## Getting Started

To use MCP Agile Flow:

1. Install the package:
   ```
   pip install mcp-agile-flow
   ```

2. Import in your code:
   ```python
   from mcp_agile_flow import call_tool, call_tool_sync
   
   # Use async interface
   result = await call_tool("get-project-settings", {})
   
   # Or use sync interface
   result = call_tool_sync("get-project-settings", {})
   ```

## MCP Client Configuration

### Important: Configuration Update Required

If you had previously configured MCP Agile Flow, you need to update your configuration. The `fastmcp_server.py` module has been removed as part of code cleanup, and functionality has been consolidated into the main package.

Update your MCP client configuration from:

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

To:

```json
{
    "name": "mcp-agile-flow",
    "server": {
        "type": "module",
        "module": "mcp_agile_flow",
        "entry_point": "main"
    }
}
```

For Cursor users, also update the mcp.json file (typically at ~/.cursor/mcp.json):

```json
"mcp-agile-flow": {
  "command": "/path/to/python",
  "args": [
    "-m",
    "mcp_agile_flow"  // Updated from "mcp_agile_flow.fastmcp_server"
  ],
  "autoApprove": [
    // ...
  ]
}
```

### Command Line Usage

You can also run the server directly from the command line:

```bash
# Using Python
python -m mcp_agile_flow
```

## Available Tools

The MCP Agile Flow provides several tools:

- `get-project-settings`: Get project settings including paths and environment variables
- `initialize-ide`: Initialize project directory structure for specific IDEs
- `initialize-ide-rules`: Initialize AI rule files for specific IDEs
- `prime-context`: Analyze project documentation and build contextual understanding
- `migrate-mcp-config`: Migrate MCP configuration between different IDEs

## Development

To set up for development:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/mcp-agile-flow.git
   cd mcp-agile-flow
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```
   pytest
   ```

5. Common Makefile commands:
   ```
   make test         # Run tests
   make coverage     # Generate coverage report
   make clean        # Clean build artifacts
   make clean-all    # Clean everything including venv
   make clean-archived  # Remove archived legacy files
   ```

## License

This project is licensed under the MIT License - See [LICENSE](LICENSE) file for details.