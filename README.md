# MCP Agile Flow

A collection of Model Control Protocol (MCP) servers that enhance agile workflows in Cursor.

## For MCP Client Users

### Available Server

The MCP Agile Flow server provides natural language capabilities and essential tools:

- `hello-world`: Returns a greeting message
- `add-note`: Adds a note to the server's memory
- `get-project-path`: Returns current project paths
- `Hey Sho`: Process natural language commands
- `debug-tools`: Provides debugging information

### Available Tools Reference

#### Standard Tools (Both Servers)

1. **hello-world**
   ```json
   {
     "name": "hello-world",
     "arguments": {}
   }
   ```
   Returns: "Hello, World!"

2. **add-note**
   ```json
   {
     "name": "add-note",
     "arguments": {
       "name": "meeting-notes",
       "content": "Discuss project timeline"
     }
   }
   ```
   Returns: Confirmation that the note was added

3. **get-project-path**
   ```json
   {
     "name": "get-project-path",
     "arguments": {}
   }
   ```
   Returns: Current directory paths

#### Simple Server Special Tools

4. **Hey Sho**
   ```json
   {
     "name": "Hey Sho",
     "arguments": {
       "message": "Hey Sho, get project path"
     }
   }
   ```
   Example messages:
   - "Hey Sho, hello world"
   - "Hey Sho, add a note called todo with content Fix the bug"
   - "Hey Sho, get project path"

5. **debug-tools**
   ```json
   {
     "name": "debug-tools",
     "arguments": {
       "count": 10
     }
   }
   ```
   Returns: Recent tool invocations (count is optional, defaults to 5)

### Viewing Available Tools

To see all available tools:

1. In Cursor, open Command Palette (Cmd+Shift+P or Ctrl+Shift+P)
2. Type "MCP: List Tools" and select it
3. Choose your configured server
4. You should see all registered tools with descriptions

Alternatively, when running the server manually:
```bash
python run_mcp_server.py
```
Server logs should show tool registration during startup.

### Setup and Usage

1. Clone and set up the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-agile-flow.git
   cd mcp-agile-flow
   make install
   ```

2. Configure Cursor:
   - Open Cursor settings
   - Navigate to the MCP section
   - Edit your `~/.cursor/mcp.json` file with this configuration:

```json
{
  "mcp-agile-flow": {
    "command": "/absolute/path/to/your/venv/python",
    "args": [
      "/absolute/path/to/mcp-agile-flow/run_mcp_server.py"
    ],
    "autoApprove": [
      "hello-world",
      "add-note",
      "get-project-path"
    ],
    "disabled": false
  },
  "mcp-agile-flow-simple": {
    "command": "/absolute/path/to/your/venv/python",
    "args": [
      "/absolute/path/to/mcp-agile-flow/simple_server.py"
    ],
    "autoApprove": [
      "hello-world",
      "add-note",
      "get-project-path",
      "Hey Sho",
      "debug-tools"
    ],
    "disabled": false
  }
}
```

⚠️ **Important**: 
- Use **absolute paths** for both Python and script locations
- Make sure Python path points to the virtual environment's Python
- Restart Cursor after making changes

### Verifying Server Connection

You can manually test the servers:

```bash
# Test standard server
python run_mcp_server.py

# Test simple server
python simple_server.py
```

The server should start and show debug output. If connected properly in Cursor:
1. Select the server in Cursor settings
2. Try using a tool command:
   ```json
   {"name": "hello-world", "arguments": {}}
   ```

### Using Hey Sho Commands

With the Simple MCP Server, you can use natural language:

```json
{
  "name": "Hey Sho",
  "arguments": {
    "message": "Hey Sho, get project path"
  }
}
```

### Troubleshooting

If the server is not connecting:

1. Check server logs at `~/.mcp-agile-flow/mcp-server.log` or `~/.mcp-agile-flow/simple-mcp-server.log`
2. Verify absolute paths in your `~/.cursor/mcp.json` configuration
3. Make sure your virtual environment is activated when testing manually
4. Restart Cursor after updating the configuration
5. Verify server script permissions are executable (`chmod +x *.py`)

#### Common Issues

- **Missing Tool List**: Try using "MCP: List Tools" from Command Palette
- **Server Not Running**: Check logs for startup errors
- **Path Problems**: Ensure all paths are absolute and correct
- **Environment Issues**: Run `which python` in your activated environment to get the correct path

## For Developers

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-agile-flow.git
cd mcp-agile-flow

# Create environment and install dependencies
make install-dev
```

All development tasks are managed through the `Makefile`. Check the `Makefile` for available commands like testing, running servers, and code formatting.

### Project Structure

- `src/mcp_agile_flow/`
  - `simple_server.py`: MCP server implementation with Hey Sho capabilities
- `docs/`: Documentation
- `tests/`: Test suite

## Documentation

- [Simple Server Usage](docs/simple_server_usage.md)

## License

MIT License - See [LICENSE](LICENSE) file for details.