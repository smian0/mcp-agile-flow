# MCP Automatic Rules Generation with Agile Workflow

## Documentation Overview

This directory contains documentation for the MCP Automatic Rules Generation with Agile Workflow system - a lightweight, local solution for managing Agile development workflows with all documentation stored directly in your project's root directory.

## Documents

| Document | Description |
|----------|-------------|
| [Executive Summary](cursor-auto-rules-summary.md) | High-level overview of the solution |
| [Architecture Document](mcp-auto-rules-architecture.md) | Simplified architecture and file structure |
| [User Guide](cursor-auto-rules-user-guide.md) | Step-by-step usage instructions |

## Key Features

### Local Documentation Storage

- All documentation stored in `ai-docs/` directory within your project
- Documentation versioned with your source code
- No external databases or complex infrastructure required

### Agile Workflow Management

- Structured organization of epics, stories, and tasks
- File-based tracking of project progress
- Command-line tools for workflow management

### IDE Integration

- Generates IDE-specific rules files for seamless integration
- Supports multiple IDEs (Cursor, WindSurfer, VS Code, etc.)
- Enables AI-powered workflow management through natural language
- Allows your IDE to communicate directly with the MCP server

### Python MCP SDK Implementation

- Built using the Python MCP SDK for AI model integration
- Lightweight server with minimal dependencies
- Easy extension through Python modules
- Seamless integration with AI models via MCP protocol
- Standardized installation through UVX, the universal MCP server manager

### Simple Setup and Use

- Straightforward installation via UVX
- Lightweight local server
- Direct access to documentation files in your preferred editor

## Getting Started

To get started with the MCP Automatic Rules Generation with Agile Workflow:

1. Install the server:
   ```bash
   # Install UVX if you don't have it already
   pip install uvx
   
   # Install the MCP server
   uvx install mcp-agile-flow
   ```

2. Initialize your project:
   ```bash
   cd your-project
   uvx run mcp-agile-flow init
   ```

3. Generate IDE-specific rules file:
   ```bash
   # For Cursor IDE
   uvx run mcp-agile-flow rules generate-ide --type=cursor
   
   # For WindSurfer IDE
   uvx run mcp-agile-flow rules generate-ide --type=windsurfer
   
   # For other supported IDEs
   uvx run mcp-agile-flow rules generate-ide --type=<ide-type>
   ```

4. Start the server:
   ```bash
   uvx run mcp-agile-flow start
   ```

5. Begin managing your project:
   ```bash
   # Create an epic
   uvx run mcp-agile-flow epic create "Feature X"
   
   # Create a story
   uvx run mcp-agile-flow story create "Story 1" --epic="Feature X"
   ```

## Project Structure

After initialization, your project will contain:

```
your-project/
├── ai-docs/
│   ├── prd.md                # Product Requirements Document
│   ├── architecture.md       # Architecture Document
│   ├── epics/                # Epic documentation
│   ├── stories/              # Story documentation
│   ├── rules/                # AI behavior rules
│   └── progress.md           # Project progress tracking
├── IDE-specific directories  # Based on generated rules
│   ├── .cursor/rules/        # Cursor IDE rules
│   ├── .windsurfer/rules/    # WindSurfer IDE rules 
│   └── ...                   # Other IDE integrations
└── ... (your project files)
```

## Workflow Commands

The MCP server provides a simple CLI for managing your workflow:

```bash
# Server commands
uvx run mcp-agile-flow start [--port=PORT]
uvx run mcp-agile-flow stop
uvx run mcp-agile-flow status

# Project commands
uvx run mcp-agile-flow init
uvx run mcp-agile-flow status

# IDE integration
uvx run mcp-agile-flow rules generate-ide --type=<ide-type> [--output=<path>]

# Documentation commands
uvx run mcp-agile-flow docs generate --type=prd
uvx run mcp-agile-flow docs generate --type=architecture
uvx run mcp-agile-flow docs generate --type=progress
```

For detailed information on all available commands, refer to the [User Guide](cursor-auto-rules-user-guide.md).

## IDE Integration

The MCP server can generate IDE-specific rules files that enable your IDE to communicate with the server:

### Supported IDEs

- **Cursor**: `.cursor/rules/mcp-agile-workflow.mdc`
- **WindSurfer**: `.windsurfer/rules/mcp-agile-workflow.mds`
- **GitHub Copilot**: `.github/copilot/mcp-agile-workflow.yml`
- **CLIne**: `.cline/rules/mcp-agile-workflow.clr`
- **VS Code**: `.vscode/mcp-agile-workflow.json`
- **Generic**: `ai-docs/rules/mcp-agile-workflow.md`

### Future IDE Rule Migration

A planned feature for future versions is the ability to migrate rules between different IDE formats. This enhancement will allow developers to seamlessly switch between their preferred development environments while maintaining their customized rules and workflows. The MCP server will provide a unified interface for managing rules across all supported IDEs, further emphasizing its IDE-agnostic approach.

### Rules File Content

Each generated rules file contains:
- Connection details for the MCP server
- Available commands for workflow management
- Project structure information
- Workflow phase descriptions
- Critical rules for proper workflow

## Python MCP SDK

The system is built using the Python MCP SDK, which provides:

- Tool definitions for AI model interactions
- Request handling and routing framework
- State management for complex workflows
- File operations for documentation management
- Natural language processing capabilities

By leveraging the Python MCP SDK, the system provides a streamlined interface between AI models and your project documentation, enabling powerful natural language interactions for Agile workflow management.

## MCP Client Configuration

The MCP Agile Flow server can be used with any MCP-compatible client, including:

- Cursor IDE
- Claude Desktop
- VS Code (with Claude extension)
- WindSurfer IDE
- Command line tools

### Configuration Approaches

#### Approach 1: UVX Installation (Recommended)

This approach is recommended for production use and provides a standardized installation experience:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "uvx",
      "args": [
        "run",
        "mcp-agile-flow",
        "start"
      ],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}"
      }
    }
  }
}
```

#### Approach 2: Direct Script Execution

For development or custom setups, you can directly execute the Python script:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "python",
      "args": [
        "/absolute/path/to/mcp-agile-flow/server.py"
      ],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}",
        "TOKEN_LIMIT": "8000"
      }
    }
  }
}
```

Replace `/absolute/path/to/mcp-agile-flow/server.py` with the absolute path to the server.py file on your system.

For detailed configuration examples for specific platforms, see the [MCP Client Configuration Examples](../server/mcp-config-examples.md).

For the complete JSON schema of the configuration file, see the [MCP Configuration Schema](../server/schema.json).

### Environment Variables

You can customize the MCP server behavior using environment variables:

- `PROJECT_PATH`: Path to your project directory
- `DEBUG`: Set to `true` to enable debug logging
- `PORT`: Set a custom port (default: 3000)
- `TOKEN_LIMIT`: Maximum token limit for code extraction (default: 8000)

### IDE-Specific Configurations

#### Cursor IDE

If you're using Cursor IDE, you can add the MCP server to your Cursor MCP settings:

1. Open Cursor settings
2. Navigate to the MCP section
3. Click "Add MCP Server"
4. Enter the following details:
   - **Name**: `agile-flow`
   - **Command**: `uvx`
   - **Arguments**: `run mcp-agile-flow start`

#### Claude Desktop

For Claude Desktop, add the configuration to your Claude Desktop MCP configuration file:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "uvx",
      "args": [
        "run",
        "mcp-agile-flow",
        "start"
      ],
      "env": {
        "PROJECT_PATH": "${HOME}/projects/current-project"
      }
    }
  }
}
```

#### Other MCP Clients

Most MCP clients follow the same JSON configuration format. Refer to your specific client's documentation for where to place the configuration file.

### MCP Tools

The MCP Agile Flow server provides the following tools via the MCP protocol:

- `create_epic`: Create a new epic
- `list_epics`: List all epics
- `get_epic`: Get epic details
- `update_epic`: Update epic status
- `list_stories`: List stories for an epic
- `create_story`: Create a new story
- `update_story`: Update story status
- `list_tasks`: List tasks for a story
- `create_task`: Create a new task
- `update_task`: Update task status
- `generate_ide_rules`: Generate IDE-specific rules file

These tools can be accessed by any MCP-compatible client once the server is properly configured.

## Contributing

Contributions to this project are welcome. Please feel free to submit issues or pull requests to improve the functionality or documentation. 