# MCP Agile Flow

[![Coverage](https://github.com/yourusername/mcp-agile-flow/raw/main/badges/coverage.svg)](https://yourusername.github.io/mcp-agile-flow/)

A Model Context Protocol (MCP) server that enhances agile workflows with knowledge graph capabilities and project management tools.

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
      "autoApprove": ["initialize-ide-rules", "get-project-settings", "read_graph", "get_mermaid_diagram"],
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
      "autoApprove": ["initialize-ide-rules", "get-project-settings", "read_graph", "get_mermaid_diagram"],
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

- **Knowledge Graph Management**: Create, track, and visualize project entities and relationships
- **IDE Rules Integration**: Initialize and manage AI rules across different IDEs
- **Project Context Management**: Track project paths, settings, and documentation
- **MCP Configuration Migration**: Easily migrate MCP settings between different IDEs

### Available Tools

- `get-project-settings`: Returns project settings including paths and configuration
- `get-safe-project-path`: Get a safe, writable project path
- `get-project-info`: Get project type and metadata from the knowledge graph
- `get-mermaid-diagram`: Generate a Mermaid diagram of the knowledge graph
- `initialize-ide`: Initialize a project with rules for a specific IDE
- `initialize-ide-rules`: Initialize a project with rules for a specific IDE (specialized)
- `migrate-mcp-config`: Migrate MCP configuration between different IDEs
- `prime-context`: Analyze project AI documentation to build context

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