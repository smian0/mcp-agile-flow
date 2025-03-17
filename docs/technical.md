# MCP Agile Flow Technical Overview

This document provides a technical overview of the Python-based MCP Agile Flow server architecture.

## Architecture Overview

MCP Agile Flow is built on a lightweight Python file-based architecture that follows the Model Context Protocol (MCP) standard. The server provides tools for Agile project management without requiring a database.

```
┌─────────────────┐      ┌───────────────┐      ┌───────────────┐
│    MCP Client   │──────│  MCP Server   │──────│ File Storage  │
│   (Any IDE)     │      │ (Agile Flow)  │      │  (agile-docs) │
└─────────────────┘      └───────────────┘      └───────────────┘
```

## Core Components

1. **MCP Server:** Handles requests from MCP clients and provides tools for Agile workflow management.

2. **File Storage:** Stores all project data as Markdown files in the project directory.

3. **Tool Handlers:** Process tool invocations from MCP clients and execute the corresponding actions.

4. **IDE Rules Generator:** Creates IDE-specific rules files to enhance AI interaction with the codebase.

## File Structure

All data is stored in the `agile-docs` directory within the project root:

```
agile-docs/
├── epics/                  # Epic documents
│   ├── epic-name-1.md
│   └── epic-name-2.md
├── stories/                # Story documents
│   ├── story-name-1.md
│   └── story-name-2.md
├── tasks/                  # Task documents
│   ├── task-name-1.md
│   └── task-name-2.md
├── project.md              # Project overview
└── progress.md             # Project progress
```

## Tool Implementation

Tools are implemented as Python functions that handle MCP protocol requests:

```python
def create_epic(name: str, description: str = None) -> dict:
    """Create a new epic document."""
    # Implementation...
    return {"success": True, "epic": {"name": name, "status": "planned"}}
```

## MCP Protocol Integration

The server follows the MCP protocol for communication with clients:

1. **Tool Registration:** The server registers available tools with their parameters during initialization.

2. **Request Handling:** When a request is received, the server validates parameters and routes to the appropriate handler.

3. **Response Format:** Responses follow the MCP protocol standard format:

```json
{
  "result": {
    "data": {
      "name": "User Authentication",
      "status": "planned",
      "description": "Implement user login system"
    }
  }
}
```

## Configuration

The server requires minimal configuration:

- **PROJECT_PATH**: Path to the project directory. Defaults to the current working directory if not specified.
- **DEBUG**: Flag to enable detailed logging. Defaults to false.

## IDE Rules Generation

The server can generate IDE-specific rule files:

```
.cursor/
└── rules/
    ├── 000-agile-workflow.mdc
    └── 001-project-structure.mdc
```

These rules help AI assistants understand the project structure and workflow.

## Security Considerations

1. **File Access:** Tools only access files within the project directory.
2. **Parameter Validation:** All parameters are validated before processing.
3. **No External Dependencies:** The server operates entirely within the local filesystem.

## Extending the Server

To add new tools:

1. Create a new handler function
2. Register the tool in the MCP server
3. Implement the tool's functionality
4. Add documentation for the new tool

## Error Handling

The server implements standardized error handling:

```json
{
  "error": {
    "message": "Epic 'User Authentication' already exists",
    "code": "duplicate_resource"
  }
}
```

## Logging

The server logs events to help with debugging:

- Tool invocations
- File operations
- Error conditions
- Request validation 