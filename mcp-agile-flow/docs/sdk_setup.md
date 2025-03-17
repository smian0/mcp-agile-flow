# MCP Agile Flow - SDK Setup Guide

This guide explains how to set up the MCP Agile Flow server using the simplified SDK implementation. The new implementation leverages the Model Context Protocol (MCP) Python SDK, which provides a much more straightforward approach to creating and using MCP servers.

## Prerequisites

- Python 3.10+
- uv (Python package installer)
- Cline (Claude desktop app) installed

## Installation

### Step 1: Install the MCP SDK

First, install the MCP Python SDK in your environment:

```bash
uv pip install "mcp[cli]"
```

This installs both the MCP SDK library and command-line interface tools.

### Step 2: Install the Agile Flow Server in Cline

The MCP CLI provides a simple command to install servers directly into Cline:

```bash
# Navigate to the project directory
cd /path/to/mcp-agile-flow

# Install the SDK server
mcp install agile_flow_sdk.py
```

The `mcp install` command automatically:
1. Identifies your Claude app configuration location
2. Adds the server to the configuration file
3. Uses the correct path and parameters

### Alternative: Manual Configuration

If you prefer to manually configure Cline, add the following to your Cline configuration file:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "python3",
      "args": ["/path/to/mcp-agile-flow/agile_flow_sdk.py"],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Development and Testing

The MCP CLI provides tools for development and testing without needing to connect to Cline:

```bash
# Run the server in development mode with the MCP Inspector
mcp dev agile_flow_sdk.py
```

This launches an interactive web-based MCP Inspector that allows you to:
- Browse available tools and resources
- Execute tools directly
- View tool documentation
- Test server functionality

## Available Features

The SDK implementation provides:

### Tools
- `create_project` - Create a new Agile project
- `list_projects` - List available projects
- `generate_cursor_rules` - Generate Cursor IDE rules
- `generate_cline_rules` - Generate Cline IDE rules
- `generate_all_rules` - Generate rules for all supported IDEs

### Resources
- `agile-flow://config` - Get server configuration
- `agile-flow://project` - Get project information
- `agile-flow://progress` - Get progress information
- `agile-flow://epic/{epic_name}` - Get epic information

## Advantages of the SDK Implementation

The SDK implementation offers several advantages:

1. **Simplified Code** - Much less boilerplate code compared to the manual implementation
2. **Decorator-based API** - Clean, intuitive API with function decorators
3. **Built-in CLI Tools** - Development and installation tools included
4. **Type Safety** - Better type checking and validation
5. **Resource Templates** - Simple path parameter support for dynamic resources
6. **Documentation Generation** - Automatic generation of documentation from docstrings

## Troubleshooting

If you encounter issues:

1. Verify the MCP SDK is installed:
   ```bash
   uv pip list | grep mcp
   ```

2. Check the server works in development mode:
   ```bash
   mcp dev agile_flow_sdk.py
   ```

3. Check the Cline logs for error messages:
   - macOS: `~/Library/Logs/Claude/main.log`
   - Windows: `%USERPROFILE%\AppData\Roaming\Claude\logs\main.log`
   - Linux: `~/.config/Claude/logs/main.log`

4. Use the MCP CLI to diagnose issues:
   ```bash
   mcp list
   mcp status
   ```
