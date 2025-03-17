# MCP Agile Flow Server Configuration Options

Based on testing, here are working configuration options for the MCP Agile Flow server.

## Option 1: Shell Script Wrapper (Recommended)

This is a robust solution that handles potential path issues:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "/Users/smian/mcp-agile-flow/run_server.sh",
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

The shell script (`run_server.sh`) handles:
1. Finding the Python interpreter
2. Setting up the correct PYTHONPATH
3. Changing to the correct directory
4. Running the server with proper environment

## Option 2: Using System Python with Full Path

For a more direct approach:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "python3",
      "args": ["/Users/smian/mcp-agile-flow/mcp-agile-flow/agile_flow_sdk.py"],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}",
        "PYTHONPATH": "/Users/smian/mcp-agile-flow:/Users/smian/mcp-agile-flow/mcp-agile-flow"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Option 3: Using MCP CLI

If you have the MCP CLI installed and in your PATH:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "mcp",
      "args": ["run", "/Users/smian/mcp-agile-flow/mcp-agile-flow/agile_flow_sdk.py"],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Testing Your Configuration

After adding your configuration to your MCP client (like Claude Desktop):

1. Restart the client
2. Try a simple command like "List available MCP tools" or "Create a new Agile project"
3. Watch for any error messages in the client's logs

## Debugging Tips

If you experience issues:

1. Try running the server directly from the command line to see if there are any errors:
   ```bash
   /Users/smian/mcp-agile-flow/run_server.sh
   ```

2. Check your IDE or MCP client logs for detailed error messages
   
3. Verify all file paths exist and are accessible

4. Ensure Python and the required dependencies are installed:
   ```bash
   pip list | grep mcp
   ```
