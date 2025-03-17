# MCP Agile Flow Tools Reference

This document outlines the available tools in the Python-based MCP Agile Flow server.

## Core Tools

### Project Management

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `create_project` | Creates a new Agile project | `name`, `description` |
| `list_projects` | Lists all available projects | - |
| `set_active_project` | Sets the active project | `name` |

### Epic Management

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `create_epic` | Creates a new epic | `name`, `description`, `priority` |
| `list_epics` | Lists all epics in the current project | - |
| `get_epic` | Gets details of a specific epic | `name` |
| `update_epic` | Updates an existing epic | `name`, `field`, `value` |

### Story Management

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `create_story` | Creates a new user story | `epic`, `name`, `description`, `points` |
| `list_stories` | Lists all stories for an epic | `epic` |
| `get_story` | Gets details of a specific story | `epic`, `name` |
| `update_story` | Updates an existing story | `epic`, `name`, `field`, `value` |

### Task Management

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `create_task` | Creates a new task | `epic`, `story`, `name`, `description` |
| `list_tasks` | Lists all tasks for a story | `epic`, `story` |
| `get_task` | Gets details of a specific task | `epic`, `story`, `name` |
| `update_task` | Updates an existing task | `epic`, `story`, `name`, `field`, `value` |

## Documentation Tools

### Document Generation

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `generate_prd` | Generates a PRD | - |
| `generate_architecture` | Generates architecture documentation | - |
| `generate_progress` | Generates progress report | - |

### Document Management

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `get_document` | Gets content of a document | `doc_type` |
| `update_document` | Updates a document | `doc_type`, `content` |

## IDE Integration Tools

### Rule Generation

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `generate_cursor_rules` | Generates Cursor IDE rules | - |
| `generate_windsurfer_rules` | Generates WindSurfer IDE rules | - |
| `generate_copilot_rules` | Generates GitHub Copilot rules | - |
| `generate_vscode_rules` | Generates VS Code rules | - |

## Configuration Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `get_config` | Gets current configuration | - |
| `set_config` | Updates configuration | `key`, `value` |

## Installation

The MCP Agile Flow server can be installed using `uvx`:

```bash
uvx install mcp-agile-flow
```

For more details on installation and setup, see the [Setup Guide](setup.md).

## Error Handling

The MCP server follows standard error handling protocols. Errors are returned in this format:

```json
{
  "error": {
    "message": "Error message",
    "code": "error_code",
    "details": {
      "additional": "information"
    }
  }
}
```

Common error codes:
- `not_found`: Resource not found
- `duplicate_resource`: Resource already exists
- `invalid_parameter`: Invalid parameter value 