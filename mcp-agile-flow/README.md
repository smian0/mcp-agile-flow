# MCP Agile Flow Server

A lightweight Python MCP server for Agile project lifecycle management and documentation.

## Overview

MCP Agile Flow provides tools for managing Agile workflows through the Model Context Protocol (MCP). It enables AI assistants to help with:

- Agile documentation in markdown files
- Managing epics, stories, and tasks
- Project progress tracking
- IDE-specific rule generation

All documentation is stored locally in your project root for easy versioning.

## Quick Start

### Prerequisites

- Python 3.10+
- uv (Python package installer)

### Installation

```bash
# Install using uv
uv pip install -e /path/to/mcp-agile-flow
```

Or install directly from GitHub (when available):

```bash
uv pip install git+https://github.com/modelcontextprotocol/mcp-agile-flow.git
```

### MCP Client Configuration

Add to your client's MCP configuration:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "uv",
      "args": ["run", "mcp-agile-flow", "start"],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}"
      }
    }
  }
}
```

The server automatically uses the current project directory if `PROJECT_PATH` is not specified.

For client-specific instructions, see [Setup Guide](docs/setup.md).

## Development

To run the server directly from the source code without installing:

```bash
# From the root of the mcp-agile-flow directory
python server.py
```

## Key Features

- **Document Management**: Store and manage Agile documentation
- **Workflow Management**: Track epics, stories, and tasks
- **IDE Integration**: Generate IDE-specific rules for AI assistants
- **Local Storage**: All data stored as markdown files in the `agile-docs` directory

## Tools Overview

| Category | Tools |
|----------|-------|
| Project | `create_project`, `list_projects`, `set_active_project` |
| Epics | `create_epic`, `list_epics`, `update_epic` |
| Stories | `create_story`, `list_stories`, `update_story` |
| Tasks | `create_task`, `list_tasks`, `update_task` |
| Docs | `generate_prd`, `generate_architecture`, `generate_progress` |
| IDE Rules | `generate_cursor_rules`, `generate_cline_rules`, `generate_all_rules` |

For complete documentation of all available tools, see [Tool Reference](docs/tools.md).

## Documentation

- [Setup Guide](docs/setup.md) - Installation and configuration
- [User Guide](docs/user-guide.md) - How to use the MCP server
- [Tool Reference](docs/tools.md) - Available MCP tools
- [Technical Overview](docs/technical.md) - Architecture details
- [Implementation Plan](docs/implementation.md) - Development plan and structure

## Contributing

Contributions are welcome! This is an early version with basic functionality. Future versions will implement the remaining tools and add more features.

## License

This project is licensed under the MIT License.
