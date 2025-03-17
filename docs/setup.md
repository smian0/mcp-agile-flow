# MCP Agile Flow Setup Guide

This guide explains how to install and configure the Python-based MCP Agile Flow server.

## Installation

### Prerequisites

- Python 3.8 or higher
- `uvx` package manager

### Installing with uvx

The easiest way to install the MCP Agile Flow server is using `uvx`:

```bash
uvx install mcp-agile-flow
```

This will install the MCP Agile Flow server and all its dependencies.

### Installing from Source

Alternatively, you can install from source:

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-agile-flow.git

# Navigate to the project directory
cd mcp-agile-flow

# Install using uvx
uvx . install
```

## Configuration

### Basic Configuration

Create a `.mcp-config.json` file in your project root with the following content:

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

### Environment Variables

The MCP Agile Flow server supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_PATH` | Path to the project root | Current directory |
| `DEBUG` | Enable debug logging | `false` |

## Usage with IDEs

### Cursor IDE

In Cursor IDE, you can add the MCP server via the MCP configuration:

1. Open Cursor Settings
2. Navigate to AI > Claude > MCP
3. Add a new server with:
   - Name: Agile Flow
   - Command: uvx
   - Args: ["run", "mcp-agile-flow", "start"]
   - Environment: {"PROJECT_PATH": "${PROJECT_PATH}"}

### Claude Desktop

In Claude Desktop, create a `.mcp-config.json` file with:

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
        "PROJECT_PATH": "${workspaceFolder}"
      }
    }
  }
}
```

## Verifying Installation

To verify the installation:

```bash
uvx run mcp-agile-flow --version
```

This should display the version of the MCP Agile Flow server.

## Next Steps

After installation, refer to the [User Guide](user-guide.md) for information on how to use the MCP Agile Flow server to manage your Agile projects. 