# MCP Agile Flow

A Model Context Protocol (MCP) server that enhances agile workflows with knowledge graph capabilities and project management tools.

## Getting Started

### Prerequisites
- Python 3.10+
- uv (Python package manager)
- Cursor IDE

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-agile-flow.git
   cd mcp-agile-flow
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv .venv
   uv pip install -e .
   ```

3. Set up the MCP server in Cursor:
   ```bash
   python setup_cursor_mcp.py
   ```

4. Alternatively, manually configure the MCP server in your `~/.cursor/mcp.json` file:
   ```json
   {
     "mcpServers": {
       "mcp-agile-flow": {
         "command": "/path/to/mcp-agile-flow/.venv/bin/python",
         "args": [
           "-m",
           "mcp_agile_flow.simple_server"
         ],
         "disabled": false,
         "autoApprove": [
           "initialize-ide-rules",
           "initialize-rules",
           "get-project-path",
           "get-project-settings",
           "create_entities",
           "create_relations",
           "read_graph",
           "debug-tools",
           "get_mermaid_diagram",
           "add_observations",
           "delete_entities",
           "get-safe-project-path",
           "initialize-ide"
         ],
         "timeout": 30
       }
     }
   }
   ```

## Using the MCP Server

After installation, you can use the MCP tools directly in Cursor through Claude or other supporting AI assistants.

### Key Features

- **Knowledge Graph Management**: Create, track, and visualize project entities and relationships
- **IDE Rules Integration**: Initialize and manage AI rules across different IDEs
- **Project Context Management**: Track project paths, settings, and documentation
- **MCP Configuration Migration**: Easily migrate MCP settings between different IDEs

### Available Tools

#### Primary Tools

- `get-project-settings`: Returns project settings including paths and configuration
- `get-safe-project-path`: Get a safe, writable project path
- `get-project-info`: Get project type and metadata from the knowledge graph
- `get-mermaid-diagram`: Generate a Mermaid diagram of the knowledge graph
- `initialize-ide`: Initialize a project with rules for a specific IDE
- `initialize-ide-rules`: Initialize a project with rules for a specific IDE (specialized)
- `migrate-mcp-config`: Migrate MCP configuration between different IDEs
- `prime-context`: Analyze project AI documentation to build context

#### Knowledge Graph Management

1. **create_entities**
   ```json
   {
     "name": "create_entities",
     "arguments": {
       "entities": [
         {
           "name": "Login Feature",
           "entityType": "Feature",
           "observations": ["Required for user authentication"]
         }
       ]
     }
   }
   ```
   Creates new entities in the knowledge graph.

2. **create_relations**
   ```json
   {
     "name": "create_relations",
     "arguments": {
       "relations": [
         {
           "from": "Login Feature",
           "relationType": "dependsOn",
           "to": "User Database"
         }
       ]
     }
   }
   ```
   Creates relationships between entities.

3. **read_graph**
   ```json
   {
     "name": "read_graph",
     "arguments": {}
   }
   ```
   Returns the entire knowledge graph.

4. **get_mermaid_diagram**
   ```json
   {
     "name": "get_mermaid_diagram",
     "arguments": {}
   }
   ```
   Returns a Mermaid.js diagram visualization of the knowledge graph.

#### MCP Configuration Management

1. **migrate-mcp-config**
   ```json
   {
     "name": "migrate-mcp-config",
     "arguments": {
       "from_ide": "cursor",        // Source IDE
       "to_ide": "windsurf",        // Target IDE
       "backup": true,              // Create backups before modifying
       "conflict_resolutions": {    // Optional conflict resolutions
         "server-name": true        // true = use source, false = keep target
       }
     }
   }
   ```
   Migrates MCP configuration between different IDEs with smart merging.

   Supported IDEs:
   - `cursor`: Cursor IDE (~/.cursor/mcp.json)
   - `windsurf`: Windsurf IDE (~/.codeium/windsurf/mcp_config.json)
   - `windsurf-next`: Windsurf Next IDE (~/.codeium/windsurf-next/mcp_config.json)
   - `cline`: Cline IDE (VSCode extension)
   - `roo`: Roo IDE (VSCode extension)
   - `claude-desktop`: Claude Desktop app (~/Library/Application Support/Claude/claude_desktop_config.json)

## Troubleshooting

### Common Issues

1. **Connection Error**: If you see an error like "ModuleNotFoundError: No module named...", check your MCP configuration. Make sure you're using:
   - The correct Python path (from your virtual environment)
   - The correct module path (`-m mcp_agile_flow.simple_server`) 
   - No `.py` extension in the module name when using `-m`

2. **Permission Issues**: Ensure your Python virtual environment has the necessary permissions to run.

3. **Missing Modules**: If modules are missing, try reinstalling the package with:
   ```bash
   uv pip install -e .
   ```

## License

This project is licensed under the MIT License - See [LICENSE](LICENSE) file for details.