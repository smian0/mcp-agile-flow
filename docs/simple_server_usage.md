# Simple MCP Server Usage

The Simple MCP Server extends the standard MCP server with natural language processing capabilities through the "Hey Sho" tool.

## Getting Started

Run the simple server:

```bash
python simple_server.py
```

Or use the script:

```bash
python run_simple_mcp_server.py
```

## Available Tools

### Standard Tools

- `hello-world`: Returns a simple greeting message
- `add-note`: Adds a note to the server's memory
- `get-project-path`: Returns information about the current project paths

### Special Tools

#### Hey Sho

The `Hey Sho` tool allows natural language interactions with the server. You can use it to perform various tasks using conversational language.

Usage:

```json
{
  "name": "Hey Sho",
  "arguments": {
    "message": "Hey Sho, get the project path"
  }
}
```

Example commands:

- "Hey Sho, get project path" - Returns project path information
- "Hey Sho, add a note called 'meeting' with content 'Discuss project status'" - Creates a new note
- "Hey Sho, show me all notes" - Lists all stored notes
- "Hey Sho, help" - Shows help information

#### Debug Tools

The `debug-tools` tool provides information about the server's internal state and recent tool invocations.

Usage:

```json
{
  "name": "debug-tools", 
  "arguments": {}
}
```

This will return:
- A list of recent tool calls
- Memory usage statistics
- Number of stored notes
- Server uptime

## Using with Cursor

After running the setup script:

```bash
python setup_cursor_mcp.py
```

The server will be registered with Cursor as "mcp-agile-flow-simple".

You can then use the server in Cursor by selecting it from the MCP server dropdown in the settings panel. 