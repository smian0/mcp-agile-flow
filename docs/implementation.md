# MCP Agile Flow Implementation Plan

This document outlines the implementation plan for the Python-based MCP Agile Flow server.

## Server Structure

```
mcp-agile-flow/
├── server.py              # Main entry point for MCP server
├── agile_flow/            # Core package
│   ├── __init__.py
│   ├── config.py          # Configuration handling
│   ├── mcp/               # MCP protocol handling
│   │   ├── __init__.py
│   │   ├── protocol.py    # Standard I/O communication
│   │   └── tools.py       # Tool registration and handling
│   ├── storage/           # File storage
│   │   ├── __init__.py
│   │   └── file_manager.py # Manages agile-docs directory
│   ├── tools/             # Tool implementations
│   │   ├── __init__.py
│   │   ├── project.py     # Project management tools
│   │   ├── epic.py        # Epic management tools
│   │   ├── story.py       # Story management tools
│   │   ├── task.py        # Task management tools
│   │   ├── docs.py        # Documentation tools
│   │   └── ide_rules.py   # IDE rules generation tools
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── logger.py      # Logging setup
├── pyproject.toml         # Package configuration
├── README.md              # Project documentation
└── docs/                  # Documentation files
```

## Key Implementation Components

### 1. MCP Protocol Handler

- Reads JSON requests from standard input
- Validates tool parameters
- Routes to appropriate tool handlers
- Writes JSON responses to standard output
- Handles errors according to MCP protocol

### 2. File Storage Manager

- Creates and manages the `agile-docs` directory structure
- Reads and writes markdown files
- Ensures file naming consistency

### 3. Tool Implementations

- Implements all tools specified in the documentation
- Follows the structure in tools.md
- Includes parameter validation

### 4. IDE Rules Generator

- Generates IDE-specific rules in appropriate formats
- Places rules in IDE-specific directories

### 5. Configuration Handler

- Manages environment variables
- Uses project root as default if PROJECT_PATH not specified
- Handles DEBUG flag for logging

## Implementation Approach

1. **Core Server First**
   - Implement basic MCP communication
   - Setup project structure and configuration

2. **Storage Layer**
   - Implement file structure management
   - Create initial setup for agile-docs

3. **Tool Implementation**
   - Start with project management tools
   - Implement epic, story, and task management
   - Add documentation tools
   - Finish with IDE rules generation

4. **Testing**
   - Create tests for each component
   - Ensure tool validation works correctly

5. **Packaging**
   - Setup proper Python packaging with pyproject.toml
   - Configure for installation via uvx

## IDE Rules Generation

Based on research, the following are the default locations for IDE rules files:

### IDE Rules Locations

| IDE | Rules Location | Format |
|-----|----------------|--------|
| Cursor | `.cursor/rules/` | `.mdc` files |
| GitHub Copilot | `.github/copilot-instructions.md` | Markdown (`.md`) |
| WindSurf | `.windsurfrules` | Single file (no directory) |
| VS Code | `.vscode/` | Markdown (`.md`) files |

### Rules Generation Strategy

1. **Cursor IDE**
   - Generate `.mdc` files in `.cursor/rules/` directory
   - Follow the Cursor rules format with context and requirements

2. **GitHub Copilot**
   - Generate a single `.github/copilot-instructions.md` file
   - Follow GitHub Copilot instructions format

3. **WindSurf IDE**
   - Generate a single `.windsurfrules` file in the project root
   - Keep content within the 6,000 character limit

4. **VS Code**
   - Generate Markdown files in `.vscode/rules/` directory
   - Follow standard Markdown format

Each IDE will have its own template format, but all will contain the same core information about the Agile workflow structure.

## Implementation Timeline

### Phase 1: Core Infrastructure

**Milestones:**
- Setup MCP protocol communication
- Implement configuration handling
- Create file storage manager

**Acceptance Criteria:**
- The server can be started and accepts MCP protocol commands
- The server properly reads and applies environment variables
- The server can create and initialize the `agile-docs` directory structure
- End users can verify by:
  - Installing and starting the server without errors
  - Checking that the `agile-docs` directory is created in their project root
  - Verifying that the server responds to a basic ping or status command

### Phase 2: Basic Tools

**Milestones:**
- Implement project management tools
- Implement epic management tools
- Implement story management tools

**Acceptance Criteria:**
- Users can create and initialize a new Agile project
- Users can create, list, and update epics
- Users can create, list, and update stories
- All created items are properly stored as markdown files
- End users can verify by:
  - Creating a new project and checking the initial structure
  - Creating epics and stories and verifying they appear in the appropriate directories
  - Updating the status of epics and stories and verifying the changes are saved
  - Listing epics and stories and verifying the output matches what was created

### Phase 3: Advanced Tools

**Milestones:**
- Implement task management tools
- Implement documentation tools
- Implement IDE rules generation

**Acceptance Criteria:**
- Users can create, list, and update tasks
- Users can generate, view, and update documentation
- Users can generate IDE-specific rules
- End users can verify by:
  - Creating and managing tasks within stories
  - Generating project documentation and verifying its contents
  - Generating IDE rules for different IDEs and verifying they appear in the correct locations
  - Verifying that generated IDE rules contain the proper Agile workflow information

### Phase 4: Testing and Refinement

**Milestones:**
- Add comprehensive tests
- Refine tool implementations
- Create Python package distribution

**Acceptance Criteria:**
- All components have unit tests with high coverage
- The server handles error conditions gracefully
- The package can be installed via uvx
- End users can verify by:
  - Installing the package via uvx
  - Testing edge cases like invalid parameters, missing directories, etc.
  - Checking that proper error messages are displayed when expected
  - Verifying that all tools function correctly in a complete workflow

## Development Practices

- Follow PEP 8 for Python code style
- Use type hints throughout the codebase
- Write comprehensive docstrings
- Implement unit tests for all components
- Ensure error handling is consistent and informative 