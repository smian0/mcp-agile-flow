# Project Initialization with MCP Agile Flow

The MCP Agile Flow server provides a tool called `initialize_project` that allows you to set up a project with Cursor rule templates. This document explains how to use this tool.

## What it does

The `initialize_project` tool:

1. Automatically detects your project root based on common project markers (like .git, package.json, etc.)
2. Creates the necessary directory structure:
   - `.cursor/rules`: Contains the rule files that provide context to Cursor AI
   - `.cursor/templates`: For template files
   - `.ai`: Directory for AI-generated content
   - `docs`: For project documentation
3. Copies the default set of Cursor rule templates to the `.cursor/rules` directory
4. Creates a workflow documentation file (`docs/workflow-rules.md`)
5. Updates or creates a `.gitignore` file to ignore user-specific rule files

## Using the tool via MCP

To use this tool through the MCP protocol:

```json
{
  "name": "initialize_project",
  "arguments": {
    // Both parameters are optional
    "target_directory": "/path/to/your/project",  // Optional: If not provided, auto-detects project root
    "project_name": "your-project-name"           // Optional: If not provided, extracted from directory or project files
  }
}
```

The tool will return:

```json
{
  "project_root": "/detected/project/root",
  "project_name": "detected-project-name",
  "created_files": [
    "/path/to/created/file1",
    "/path/to/created/file2",
    ...
  ],
  "created_dirs": [
    "/path/to/created/dir1",
    "/path/to/created/dir2",
    ...
  ]
}
```

## Smart Detection Features

The tool includes the following smart detection capabilities:

### Project Root Detection

The tool will search for common project markers to determine the project root:

- Version control directories (`.git`)
- Package files (`package.json`, `pyproject.toml`)
- Configuration files (`go.mod`, `Cargo.toml`)
- IDE configuration (`.vscode`)
- Other common project markers

If no markers are found, it will use the current working directory.

### Project Name Detection

The tool will try to extract the project name from:

1. `package.json` (for Node.js projects)
2. `pyproject.toml` (for Python projects)
3. If no project files are found, it will use the name of the project directory

## Examples

### Initialize the current project with auto-detection

```json
{
  "name": "initialize_project",
  "arguments": {}
}
```

### Initialize a specific project with a custom name

```json
{
  "name": "initialize_project",
  "arguments": {
    "target_directory": "/path/to/specific/project",
    "project_name": "custom-project-name"
  }
}
```

## Benefits

- Provides a standardized way to initialize projects with Cursor rules
- Eliminates the need to manually create directories and files
- Ensures all necessary rule files are copied over consistently
- Automates the setup process that was previously done via the apply-rules.sh script
- Smart detection reduces the need for user input
