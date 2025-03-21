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

#### Project Setup and Management

1. **initialize-ide**
   ```json
   {
     "name": "initialize-ide",
     "arguments": {
       "ide": "cursor"  // Options: cursor, windsurf, cline, copilot
     }
   }
   ```
   Initializes a project with the appropriate rules for the specified IDE.

2. **get-project-settings**
   ```json
   {
     "name": "get-project-settings",
     "arguments": {}
   }
   ```
   Returns comprehensive project settings including paths and configuration.

3. **get-safe-project-path**
   ```json
   {
     "name": "get-safe-project-path",
     "arguments": {
       "proposed_path": "/optional/path/to/check"
     }
   }
   ```
   Returns a safe, writable project path for file operations.

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