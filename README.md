# MCP Agile Flow

A simple MCP server implementation for managing agile workflow rules and templates.

### Available Server
- `run_mcp_server.py`: Consolidated MCP server implementation with agile workflow capabilities

### Available Tools Reference

1. **initialize-ide-rules**
   ```json
   {
     "name": "initialize-ide-rules",
     "arguments": {
       "ide": "cursor",
       "project_path": "/path/to/project"
     }
   }
   ```
   Returns: Success status and details about initialized files

2. **initialize-rules**
   ```json
   {
     "name": "initialize-rules",
     "arguments": {
       "project_path": "/path/to/project"
     }
   }
   ```
   Returns: Success status and details about initialized files

3. **get-safe-project-path**
   ```json
   {
     "name": "get-safe-project-path",
     "arguments": {
       "proposed_path": "/optional/path/to/check"
     }
   }
   ```
   Returns: Safe project path or error requesting user input
   - If proposed path is writable, returns that path
   - If proposed path is not provided, checks PROJECT_PATH environment variable
   - If current directory is not root, uses it as fallback for safety
   - If current directory is root, returns error requesting user to provide a specific path
   - Never allows operations in the root directory
   - Always prompts for explicit path instead of using unsafe defaults

4. **migrate-rules-to-windsurf**
   ```json
   {
     "name": "migrate-rules-to-windsurf",
     "arguments": {
       "project_path": "/path/to/project",
       "specific_file": "optional-file-name",
       "verbose": false,
       "no_truncate": false
     }
   }
   ```
   Returns: Migration status and details

5. **add-note**
   ```json
   {
     "name": "add-note",
     "arguments": {
       "name": "note-name",
       "content": "note content"
     }
   }
   ```
   Returns: Success status

6. **get-project-settings**
   ```json
   {
     "name": "get-project-settings",
     "arguments": {
       "random_string": "dummy-value"
     }
   }
   ```
   Returns: Current project paths, including the active project directory (from PROJECT_PATH environment variable or fallback to user's home directory)

7. **debug-tools**
   ```json
   {
     "name": "debug-tools",
     "arguments": {
       "count": 5
     }
   }
   ```
   Returns: Debug information about recent tool invocations

### Viewing Available Tools

To see all available tools:

```python
from src.mcp_agile_flow.simple_server import get_tool_definitions
tools = get_tool_definitions()
for tool in tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
    print("---")
```

### Example Usage

1. Initialize Cursor Rules (with path check):
   ```json
   # First, check if the path is safe and writable
   {
     "name": "get-safe-project-path",
     "arguments": {}
   }
   # Then use the returned safe path in the initialize-rules command
   {
     "name": "initialize-rules",
     "arguments": {
       "project_path": "/path/from/previous/step"
     }
   }
   ```

2. Initialize Rules for a specific IDE:
   ```json
   {
     "name": "initialize-ide-rules",
     "arguments": {
       "ide": "windsurf",
       "project_path": "/path/to/project"
     }
   }
   ```

3. Add a Note:
   ```json
   {
     "name": "add-note",
     "arguments": {
       "name": "todo",
       "content": "Fix the bug"
     }
   }
   ```

4. Get Project Path:
   ```json
   {
     "name": "get-project-path",
     "arguments": {
       "random_string": "dummy"
     }
   }
   ```

5. Migrate to Windsurf:
   ```json
   {
     "name": "migrate-rules-to-windsurf",
     "arguments": {
       "project_path": "/path/to/project"
     }
   }
   ```
   This creates a single `.windsurfrules` file in your project root that contains all rules in a Windsurf-compatible format.

6. Debug Tool Invocations:
   ```json
   {
     "name": "debug-tools",
     "arguments": {
       "count": 5
     }
   }
   ```

### Development

#### Prerequisites
- Python 3.8+
- pip

#### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```

#### Running Tests
```bash
python -m pytest
```

#### Development Tasks
All development tasks are managed through the `Makefile`. Check the `Makefile` for available commands like testing, running servers, and code formatting.

### Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### License
MIT License - See [LICENSE](LICENSE) file for details.

### Authors
- Your Name - Initial work