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
       "project_path": "/path/to/project",
       "ide": "cursor",
       "backup_existing": true
     }
   }
   ```
   Returns: Success status and details about initialized files

2. **initialize-rules**
   ```json
   {
     "name": "initialize-rules",
     "arguments": {
       "project_path": "/path/to/project",
       "backup_existing": true
     }
   }
   ```
   Returns: Success status and details about initialized files

3. **migrate-rules-to-windsurf**
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

4. **add-note**
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

5. **get-project-path**
   ```json
   {
     "name": "get-project-path",
     "arguments": {
       "random_string": "dummy-value"
     }
   }
   ```
   Returns: Current project paths

6. **debug-tools**
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

1. Initialize Cursor Rules:
   ```json
   {
     "name": "initialize-rules",
     "arguments": {
       "project_path": "/path/to/project",
       "backup_existing": true
     }
   }
   ```

2. Add a Note:
   ```json
   {
     "name": "add-note",
     "arguments": {
       "name": "todo",
       "content": "Fix the bug"
     }
   }
   ```

3. Get Project Path:
   ```json
   {
     "name": "get-project-path",
     "arguments": {
       "random_string": "dummy"
     }
   }
   ```

4. Migrate to Windsurf:
   ```json
   {
     "name": "migrate-rules-to-windsurf",
     "arguments": {
       "project_path": "/path/to/project"
     }
   }
   ```
   This creates a single `.windsurfrules` file in your project root that contains all rules in a Windsurf-compatible format.

5. Debug Tool Invocations:
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