# MCP Agile Flow Server

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

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
# Install from PyPI
pip install mcp-agile-flow

# Or install from GitHub
pip install git+https://github.com/modelcontextprotocol/mcp-agile-flow.git
```

For development setup:
```bash
# Clone the repository
git clone https://github.com/modelcontextprotocol/mcp-agile-flow.git
cd mcp-agile-flow

# Install dependencies with uv
uv pip install -e .
```

### MCP Client Configuration

Add to your MCP configuration file:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "/path/to/run_server.sh",
      "args": [],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

The server now intelligently detects project paths:
1. Automatically detects the project root (looks for .git, package.json, etc.)
2. Falls back to the current working directory if needed
3. Supports explicit configuration via PROJECT_PATH if you prefer

For client-specific instructions, see [Setup Guide](docs/setup.md) or [MCP Server Cheatsheet](docs/mcp_server_cheatsheet.md).

## Key Features

- **Document Management**: Store and manage Agile documentation
- **Workflow Management**: Track epics, stories, and tasks
- **IDE Integration**: Generate IDE-specific rules for AI assistants
- **Local Storage**: All data stored as markdown files in the `agile-docs` directory
- **Smart Path Detection**: Automatically finds project root folder
- **Fault Tolerance**: Handles permission issues gracefully with fallbacks

## Tools Overview

| Category | Tools |
|----------|-------|
| Project | `create_project`, `list_projects`, `get_progress` |
| Epics | `add_epic`, `list_epics`, `update_status` |
| Stories | `add_story`, `list_stories`, `update_status` |
| Tasks | `add_task`, `list_tasks`, `update_status` |
| IDE Rules | `generate_cursor_rules`, `generate_cline_rules`, `generate_all_rules` |

For complete documentation of all available tools, see [Tool Reference](docs/tools.md) or [MCP Server Cheatsheet](docs/mcp_server_cheatsheet.md).

## Documentation

- [Setup Guide](docs/setup.md) - Installation and configuration
- [User Guide](docs/user-guide.md) - How to use the MCP server
- [Tool Reference](docs/tools.md) - Available MCP tools
- [MCP Server Cheatsheet](docs/mcp_server_cheatsheet.md) - Quick reference guide
- [Alternative Configurations](docs/alternative_configs.md) - Different setup options
- [Technical Overview](docs/technical.md) - Architecture details
- [Implementation Plan](docs/implementation.md) - Development plan and structure 

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for more information.

## License

This project is licensed under the [MIT License](LICENSE).

## Recent Improvements

- Smart project path detection to find the correct project root
- Permission error handling with fallback to user's home directory
- Fixed IDE rule generation to avoid root directory issues
- Improved configuration flexibility - environment variables now optional
- Enhanced error messaging with specific troubleshooting steps
