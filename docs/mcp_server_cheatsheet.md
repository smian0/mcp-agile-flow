# MCP Agile Flow Server Cheatsheet

This document provides a quick reference for using the MCP Agile Flow server, including setup instructions, available tools, and common usage patterns.

## Setup

### Installation

1. **With the MCP config file**:
   ```json
   {
     "mcpServers": {
       "agile-flow": {
         "command": "/path/to/run_server.sh",
         "args": [],
         "env": {},  // Empty env is fine - project path is auto-detected
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```

2. **With explicit project path** (optional):
   ```json
   {
     "mcpServers": {
       "agile-flow": {
         "command": "/path/to/run_server.sh",
         "args": [],
         "env": {
           "PROJECT_PATH": "/path/to/your/project"
         },
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```

## Available Tools

The server provides several tools for managing Agile documentation and IDE configurations:

### Project Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_project` | Creates a new project with basic Agile documentation | `name` (string): Project name<br>`description` (string): Project description |
| `add_epic` | Adds a new epic to the project | `name` (string): Epic name<br>`description` (string): Epic description<br>`priority` (string): Priority level |
| `add_story` | Adds a new user story to an epic | `epic` (string): Epic name<br>`title` (string): Story title<br>`description` (string): Story description<br>`points` (number): Story points |
| `add_task` | Adds a new task to a story | `story` (string): Story title<br>`title` (string): Task title<br>`description` (string): Task description |
| `update_status` | Updates the status of an epic, story, or task | `type` (string): "epic", "story", or "task"<br>`name` (string): Item name<br>`status` (string): New status |

### IDE Rules

| Tool | Description | Parameters |
|------|-------------|------------|
| `generate_cursor_rules` | Generates Cursor IDE rules from project documentation | None |
| `generate_cline_rules` | Generates Cline rules from project documentation | None |
| `generate_all_rules` | Generates rules for all supported IDEs | None |

### Documentation Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_projects` | Lists all available projects | None |
| `list_epics` | Lists all epics in a project | None |
| `list_stories` | Lists all stories in an epic | `epic` (string): Epic name |
| `list_tasks` | Lists all tasks in a story | `story` (string): Story title |
| `get_progress` | Gets project progress summary | None |

## How Project Path Detection Works

The server intelligently finds the correct project root:

1. **Environment Variable**: Uses `PROJECT_PATH` if provided and valid
2. **Project Detection**: Looks for project indicators (.git, package.json, etc.) in current directory
3. **Workspace Navigation**: If needed, walks up to find the nearest project root
4. **Fallback Mechanism**: Uses home directory when all else fails

## Troubleshooting

### Common Issues

1. **"Error: Could not determine project path"**
   - Solution: Explicitly set `PROJECT_PATH` in the MCP config

2. **"Error generating IDE rules"**
   - Solution: Check write permissions to the project directory
   - The server will now automatically use fallback locations if needed

3. **File Permission Issues**
   - Solution: The server now falls back to user's home directory when permission issues occur

## Example Usage

### Creating a Project Structure

```
create_project(
  name: "My New Project",
  description: "This is a sample project to demonstrate the Agile Flow MCP server."
)
```

### Adding an Epic

```
add_epic(
  name: "User Authentication",
  description: "Implement user authentication and authorization",
  priority: "High"
)
```

### Generating IDE Rules

```
generate_all_rules()
```

This will create:
- `.cursor/rules/` directory with Cursor rule files
- `.clinerules` file with Cline rules
