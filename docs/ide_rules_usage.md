# IDE Rules Usage

This guide explains how to use the `initialize-ide-rules` tool to set up rule files for different IDEs.

## Overview

The MCP Agile Flow server provides a unified way to initialize rule files for multiple IDEs, currently supporting:

- **Cursor**: Uses multiple `.mdc` files in a `.cursor/rules` directory
- **Windsurf**: Uses a single `.windsurfrules` file in the project root

Instead of manually migrating rules between formats, this tool lets you initialize specific IDE formats directly from standardized templates.

## IDE-Specific Rule Formats

### Cursor Rules Format

Cursor uses individual `.mdc` files in the `.cursor/rules` directory, with each file having YAML frontmatter and Markdown content:

```md
---
description: Use when handling database operations
globs: src/db/**/*.ts
alwaysApply: false
---

# Database Operations

## Context
- When implementing database operations
- When designing schemas

## Requirements
...
```

### Windsurf Rules Format

Windsurf uses a single `.windsurfrules` file in the project root, with HTML comments for metadata and all rules in one file:

```md
<!-- 
description: Windsurf Rules Template
version: 1.0.0
-->

# Windsurf Rules

## 000-cursor-rules

### Context
- When creating or updating rule files
...

## 001-emoji-communication

### Context
...
```

## Using the Tool

### Initialize Cursor Rules

```json
{
  "name": "initialize-ide-rules",
  "arguments": {
    "project_path": "/path/to/your/project",
    "ide": "cursor",
    "backup_existing": true
  }
}
```

This will:
1. Create a `.cursor/rules` directory if it doesn't exist
2. Create a `.cursor/templates` directory if it doesn't exist
3. Copy all template rule files to the rules directory
4. Copy all template files to the templates directory
5. Back up any existing files if requested

### Initialize Windsurf Rules

```json
{
  "name": "initialize-ide-rules",
  "arguments": {
    "project_path": "/path/to/your/project",
    "ide": "windsurf",
    "backup_existing": true
  }
}
```

This will:
1. Create a `.windsurfrules` file in the project root
2. Populate it with the complete set of rules in Windsurf format
3. Back up any existing file if requested

## Important Considerations

1. **Backup Option**
   - Set `backup_existing: true` to create `.back` files of any existing rules
   - Set `backup_existing: false` to overwrite existing files without backup

2. **Format Differences**
   - Cursor: Multiple files with YAML frontmatter
   - Windsurf: Single file with HTML comments for metadata

3. **Managing Changes**
   - The tool does not synchronize between formats
   - When updating rules, update for each IDE separately
   - Prefer using this tool instead of manually migrating between formats

## Examples

### From Python Code

```python
import asyncio
from mcp_agile_flow.simple_server import handle_call_tool

async def init_both_rules(project_path):
    # Initialize Cursor rules
    await handle_call_tool("initialize-ide-rules", {
        "project_path": project_path,
        "ide": "cursor"
    })
    
    # Initialize Windsurf rules
    await handle_call_tool("initialize-ide-rules", {
        "project_path": project_path,
        "ide": "windsurf"
    })
    
    print(f"Rules initialized for both IDEs in {project_path}")

# Run the async function
asyncio.run(init_both_rules("/path/to/project"))
```

### From Command Line

You can run the MCP server and use a JSON file to send the request:

```json
// init-cursor.json
{
  "name": "initialize-ide-rules",
  "arguments": {
    "project_path": "/path/to/your/project",
    "ide": "cursor"
  }
}
```

```bash
# Start the server
python simple_server.py

# In another terminal, send the request
cat init-cursor.json | nc localhost 7777
```

## Troubleshooting

- **Missing Directories**: The tool will create required directories if they don't exist
- **File Permissions**: Ensure the tool has write permissions to the project directory
- **Backup Issues**: If backup fails, check disk space and file permissions 