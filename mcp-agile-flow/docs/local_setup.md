# Setting Up MCP Agile Flow on Your Local Machine

This guide provides specific configurations for using MCP Agile Flow on your local machine with different AI assistants that support the Model Context Protocol (MCP).

## Configuration Options

Depending on your preferences and environment setup, you can use one of the following configurations:

### Option 1: Using the Installed Entry Point (Recommended)

After installing the package with `uv pip install -e .`, you can use the installed entry point directly:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "/Users/smian/mcp-agile-flow/mcp-agile-flow/.venv/bin/mcp-agile-flow-start",
      "args": [],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

This is the most direct method, using the absolute path to the installed script.

### Option 2: Using Python with Full Path

You can use Python to run the server script directly:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "python3",
      "args": ["/Users/smian/mcp-agile-flow/mcp-agile-flow/server.py"],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Option 3: Using Activated Virtual Environment

If you have your virtual environment activated, you can use:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "/Users/smian/mcp-agile-flow/mcp-agile-flow/.venv/bin/python",
      "args": ["/Users/smian/mcp-agile-flow/mcp-agile-flow/server.py"],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Option 4: Using UV Run

If you prefer to use uv:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "uv",
      "args": ["run", "-m", "agile_flow.scripts.server"],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}",
        "PYTHONPATH": "/Users/smian/mcp-agile-flow/mcp-agile-flow"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Choosing the Right Option

- **Option 1** is generally the most reliable if you've installed the package in a virtual environment.
- **Option 2** is simple and works if Python can access the required modules.
- **Option 3** ensures the correct Python interpreter is used with all dependencies.
- **Option 4** is useful if you prefer to use uv's run command.

## Testing Your Configuration

After adding your chosen configuration:

1. Restart your AI assistant's client application
2. Ask it to use the MCP Agile Flow server to create a project:
   ```
   Could you create a new Agile project called "Test Project" with MCP Agile Flow?
   ```

If it responds that it's using the MCP Agile Flow server to create a project, your configuration is working correctly.

## Troubleshooting

If you encounter issues:

1. Check that the paths in your configuration match your actual file locations
2. Verify that the Python environment has all required dependencies
3. Try running the server manually to see if there are any errors:
   ```bash
   /Users/smian/mcp-agile-flow/mcp-agile-flow/.venv/bin/mcp-agile-flow-start
   ```
4. Check the AI assistant's logs for error messages related to the MCP server
