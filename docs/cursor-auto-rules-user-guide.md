# MCP Automatic Rules Generation with Agile Workflow
# User Guide

## Introduction

Welcome to the MCP Automatic Rules Generation with Agile Workflow system! This guide will help you understand how to use this local MCP server for managing your Agile development process and automatically generating documentation stored directly in your project.

## Getting Started

### Prerequisites

- Python 3.9 or later
- UVX (MCP server installer) - install with `pip install uvx`
- Git (recommended for version control)
- An AI-powered IDE (Cursor, WindSurfer, VS Code with GitHub Copilot, etc.)
- Virtual environment tool (recommended: venv or conda)

### Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install UVX if you don't have it already
pip install uvx

# Install the MCP server using UVX
uvx install mcp-agile-flow
```

### Project Setup

#### For New Projects

```bash
# Create a new directory for your project
mkdir my-project
cd my-project

# Initialize the Agile project structure
uvx run mcp-agile-flow init

# Generate IDE-specific rules file
uvx run mcp-agile-flow rules generate-ide --type=cursor
```

This will create the basic directory structure:
```
my-project/
├── ai-docs/
│   ├── prd.md                # Product Requirements Document
│   ├── architecture.md       # Architecture Document
│   ├── epics/                # Epic documentation
│   ├── stories/              # Story documentation
│   ├── rules/                # AI behavior rules
│   └── progress.md           # Project progress tracking
├── .cursor/
│   └── rules/
│       └── mcp-agile-workflow.mdc  # Cursor IDE integration rules
└── ... (your project files)
```

#### For Existing Projects

```bash
# Navigate to your existing project
cd existing-project

# Initialize the Agile structure in this directory
uvx run mcp-agile-flow init

# Generate IDE-specific rules file
uvx run mcp-agile-flow rules generate-ide --type=cursor
```

### Starting the Server

```bash
# Start the MCP server in your project directory
cd my-project
uvx run mcp-agile-flow start

# The server will start on localhost:3000 by default
# You should see output like:
# MCP Agile Server running at http://localhost:3000
```

## IDE Integration

### Generating IDE Rules

The MCP server can generate IDE-specific rules files that enable your IDE to communicate with the server and understand the Agile workflow:

```bash
# For Cursor IDE
uvx run mcp-agile-flow rules generate-ide --type=cursor

# For WindSurfer IDE
uvx run mcp-agile-flow rules generate-ide --type=windsurfer

# For VS Code with GitHub Copilot
uvx run mcp-agile-flow rules generate-ide --type=copilot

# For CLIne
uvx run mcp-agile-flow rules generate-ide --type=cline

# For a generic IDE
uvx run mcp-agile-flow rules generate-ide --type=generic
```

Each command creates a rules file in the appropriate location for that IDE:

- Cursor: `.cursor/rules/mcp-agile-workflow.mdc`
- WindSurfer: `.windsurfer/rules/mcp-agile-workflow.mds`
- GitHub Copilot: `.github/copilot/mcp-agile-workflow.yml`
- CLIne: `.cline/rules/mcp-agile-workflow.clr`
- VS Code: `.vscode/mcp-agile-workflow.json`
- Generic: `ai-docs/rules/mcp-agile-workflow.md`

### Future IDE Rule Migration

In future versions, the MCP server will support rule migration between different IDE formats. This planned feature will:

- Allow seamless conversion of rules from one IDE format to another
- Enable developers to switch between their preferred IDEs without losing customizations
- Support automatic synchronization of rules across multiple IDEs
- Provide a unified interface for managing rules across all supported environments

This enhancement will make the MCP server truly IDE-agnostic, ensuring that your Agile workflow can be managed through any AI-powered development environment.

### IDE Rules File Content

The generated IDE rules file contains:

1. **Server Configuration**: Connection details for the MCP server
2. **Command Documentation**: Available commands and how to use them
3. **Project Structure**: Layout of the documentation directory
4. **Workflow Process**: Steps for planning and implementation phases
5. **Critical Rules**: Important guidelines for using the system

### Using with Specific IDEs

#### Cursor IDE

1. Open your project in Cursor
2. Cursor will automatically load the rules from `.cursor/rules/mcp-agile-workflow.mdc`
3. You can now use Cursor's AI features to manage your Agile workflow:

```
// Example conversation with Cursor AI
User: Create a new epic for user authentication
AI: I'll use the MCP server to create that epic.
    Running: uvx run mcp-agile-flow epic create "User Authentication" --description="Implement secure user authentication system"
    Epic created successfully. Would you like to add stories to this epic now?
```

#### VS Code

1. Install the VS Code extension (if available):
   ```
   code --install-extension mcp-agile-workflow
   ```

2. Open your project in VS Code
3. VS Code will read the rules from `.vscode/mcp-agile-workflow.json`
4. Access the MCP Agile panel from the sidebar
5. Use the panel to manage epics, stories, and tasks

#### Other IDEs

For other IDEs, refer to their specific documentation on how to load and use the generated rules files.

### Directly Editing Files

Since all documentation is stored directly in your project as Markdown files, you can edit them directly in any code editor:

1. Navigate to the `ai-docs` directory
2. Open and edit the relevant Markdown files
3. The MCP server will detect changes and update its internal state

## Using the MCP Server

### Managing Epics

Epics are large, self-contained features that can be broken down into stories.

#### Creating an Epic

```bash
# Using the CLI
uvx run mcp-agile-flow epic create "User Authentication System"

# This creates:
# - ai-docs/epics/user-authentication-system.md
```

You can also create epics via the API:
```
POST http://localhost:3000/api/workflow/epics
Content-Type: application/json

{
  "name": "User Authentication System",
  "description": "Implement secure user authentication"
}
```

#### Viewing Epics

```bash
# List all epics
uvx run mcp-agile-flow epic list

# View details of a specific epic
uvx run mcp-agile-flow epic show "User Authentication System"
```

### Managing Stories

Stories are implementable work units that belong to an epic.

#### Creating a Story

```bash
# Using the CLI
uvx run mcp-agile-flow story create "Login Form" --epic="User Authentication System"

# This creates:
# - ai-docs/stories/login-form.md
```

Via the API:
```
POST http://localhost:3000/api/workflow/stories
Content-Type: application/json

{
  "name": "Login Form",
  "epicId": "user-authentication-system",
  "description": "Create a user login form with email and password"
}
```

#### Updating Story Status

```bash
# Mark a story as in-progress
uvx run mcp-agile-flow story update "Login Form" --status="in-progress"

# Mark a story as completed
uvx run mcp-agile-flow story update "Login Form" --status="completed"
```

### Managing Tasks

Tasks are smaller work items that make up a story.

```bash
# Create a task for a story
uvx run mcp-agile-flow task create "Design login form UI" --story="Login Form"

# Update task status
uvx run mcp-agile-flow task update "Design login form UI" --status="completed"
```

### Creating Rules

Rules help define how AI should assist with your project.

```bash
# Create a rule
uvx run mcp-agile-flow rule create "typescript-formatting" \
  --description="FORMAT TypeScript WITH proper indentation" \
  --content="Always use 2 spaces for indentation in TypeScript files"

# This creates:
# - ai-docs/rules/typescript-formatting.md
```

### Generating Documentation

```bash
# Generate or update PRD
uvx run mcp-agile-flow docs generate --type=prd

# Generate architecture document
uvx run mcp-agile-flow docs generate --type=architecture

# Generate progress report
uvx run mcp-agile-flow docs generate --type=progress
```

## Workflow Phases

### Planning Phase

During the planning phase, focus on:
1. Defining the Product Requirements Document
2. Creating the Architecture Document
3. Identifying epics and stories
4. Prioritizing work items

```bash
# Generate initial documentation
uvx run mcp-agile-flow docs generate --type=prd
uvx run mcp-agile-flow docs generate --type=architecture

# Create epics and stories
uvx run mcp-agile-flow epic create "Feature X"
uvx run mcp-agile-flow story create "Story 1" --epic="Feature X"
```

### Implementation Phase

During implementation:
1. Update story and task statuses
2. Document progress
3. Generate updated documentation

```bash
# Update status
uvx run mcp-agile-flow story update "Story 1" --status="in-progress"
uvx run mcp-agile-flow task update "Task 1" --status="completed"

# Generate progress report
uvx run mcp-agile-flow docs generate --type=progress
```

## Best Practices

### File Organization

- Keep the `ai-docs` directory under version control
- Update documentation regularly to reflect current status
- Use meaningful names for epics and stories

### IDE Integration

- Generate the appropriate rules file for your IDE
- Ensure your IDE can access the rules file
- Verify the MCP server is running when using IDE integration
- Use IDE AI features to manage your workflow through natural language commands

### Documentation Standards

- Follow a consistent format in all documentation
- Include acceptance criteria for stories
- Link related stories and tasks together

### Workflow Management

- Focus on one epic at a time
- Break stories into manageable tasks
- Update status regularly to keep progress tracking accurate

### Python Environment

- Use virtual environments to isolate dependencies
- Keep UVX up-to-date with `pip install -U uvx`
- For deployment in team environments, ensure all members have UVX installed
- Consider using Docker for containerized deployment in production environments

## Troubleshooting

### Server Issues

- **Server won't start**: Check if the port is already in use
  ```bash
  # Change the port
  uvx run mcp-agile-flow start --port=3001
  ```

- **Can't connect to server**: Ensure server is running and accessible
  ```bash
  # Check server status
  uvx run mcp-agile-flow status
  ```

- **UVX installation issues**: Make sure you have the latest version
  ```bash
  # Update UVX
  pip install -U uvx
  ```

### IDE Integration Issues

- **IDE not recognizing rules file**: Check if the rules file was generated in the correct location
  ```bash
  # Regenerate the rules file
  uvx run mcp-agile-flow rules generate-ide --type=cursor
  ```

- **IDE not connecting to server**: Verify server URL in rules file matches running server
  ```bash
  # Check the rules file
  cat .cursor/rules/mcp-agile-workflow.mdc
  ```

### File Issues

- **File not updating**: Check file permissions and ensure the server has write access
- **Documents not generating**: Verify that templates exist in the server installation

## Command Reference

```bash
# Server commands
uvx run mcp-agile-flow start [--port=PORT]
uvx run mcp-agile-flow stop
uvx run mcp-agile-flow status

# Project commands
uvx run mcp-agile-flow init
uvx run mcp-agile-flow status

# IDE integration
uvx run mcp-agile-flow rules generate-ide --type=<ide-type> [--output=<path>]

# Epic commands
uvx run mcp-agile-flow epic create NAME [--description=DESC]
uvx run mcp-agile-flow epic list
uvx run mcp-agile-flow epic show NAME
uvx run mcp-agile-flow epic update NAME [--status=STATUS]

# Story commands
uvx run mcp-agile-flow story create NAME --epic=EPIC [--description=DESC]
uvx run mcp-agile-flow story list [--epic=EPIC]
uvx run mcp-agile-flow story show NAME
uvx run mcp-agile-flow story update NAME [--status=STATUS]

# Task commands
uvx run mcp-agile-flow task create NAME --story=STORY [--description=DESC]
uvx run mcp-agile-flow task list [--story=STORY]
uvx run mcp-agile-flow task update NAME [--status=STATUS]

# Documentation commands
uvx run mcp-agile-flow docs generate --type=TYPE
uvx run mcp-agile-flow docs list
```

## Python MCP SDK Integration

The MCP Agile Flow is built using the Python MCP SDK, which provides:

- MCP tool definitions for AI model interactions
- Request handling and routing
- State management for complex workflows
- File operations for documentation management
- Natural language processing capabilities

For developers looking to extend the MCP server functionality, familiarity with the Python MCP SDK is recommended. The SDK documentation provides detailed information on creating custom tools and handlers.

## Using with MCP Clients

### MCP Configuration

The MCP Agile Flow server can be used with any MCP-compatible client by adding it to your client's configuration file. Most MCP clients follow the standard JSON configuration format introduced by Claude Desktop.

#### Standard Configuration Format

Create a JSON configuration file (e.g., `.mcp-config.json`) with the following structure:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "uvx",
      "args": [
        "run",
        "mcp-agile-flow",
        "start"
      ],
      "env": {
        "PROJECT_PATH": "/path/to/your/project"
      }
    }
  }
}
```

You can place this file in:
- Your project root directory for project-specific configuration
- Your home directory (`~/.mcp-config.json`) for global configuration
- A location specified by your MCP client application

#### Claude Desktop Configuration

To use with Claude Desktop:

1. Open Claude Desktop
2. Go to Settings > MCP
3. Edit the configuration file or use the UI to add a new server
4. Add the mcp-agile-flow configuration as shown above
5. Restart Claude Desktop

#### Cursor IDE Configuration

To use with Cursor IDE:

1. Open Cursor settings
2. Navigate to the MCP section
3. Click "Add MCP Server"
4. Enter the following details:
   - **Name**: `agile-flow`
   - **Command**: `uvx`
   - **Arguments**: `run mcp-agile-flow start`

#### Other MCP Clients

For other MCP clients, consult your client's documentation for the specific location and method to add the server configuration.

### Using MCP Tools

Once configured, the MCP server provides tools that can be used by AI assistants and other MCP clients:

```
// Example conversation with an AI assistant
User: Show me all epics in my project
AI: I'll use the MCP server to retrieve your epics.
    [Executing list_epics tool from agile-flow server]
    Here are your epics:
    1. User Authentication (In Progress)
    2. Dashboard Interface (Planned)
    3. Reporting Module (Completed)

User: Create a new story for the Authentication epic
AI: [Executing create_story tool from agile-flow server]
    Story "Login Page Design" created successfully in the "User Authentication" epic.
```

### Environment Variables

You can customize the MCP server behavior using environment variables in your configuration:

- `PROJECT_PATH`: Path to your project directory
- `DEBUG`: Set to `true` to enable detailed logging
- `PORT`: Set a custom port if the default is in use

## Conclusion

The MCP Automatic Rules Generation with Agile Workflow provides a lightweight but powerful way to manage your Agile development process with documentation stored directly in your project. By using this system and integrating it with your preferred IDE, you can maintain better project organization, track progress effectively, and ensure that your documentation always reflects the current state of your project. 