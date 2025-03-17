# MCP Agile Flow User Guide

This guide explains how to use the Python-based MCP Agile Flow server for managing Agile projects.

## Getting Started

### Project Initialization

After installing and configuring the MCP server (see [Setup Guide](setup.md)), you can initialize a new Agile project:

```
Can you initialize a new Agile project for me using the MCP Agile Flow server?
```

This creates the following structure in your project:

```
project-root/
├── agile-docs/
│   ├── epics/
│   ├── stories/
│   ├── tasks/
│   ├── project.md
│   └── progress.md
└── .agile-flow.json
```

## Agile Workflow Management

### Managing Epics

**Creating an Epic:**
```
Please create a new epic called "User Authentication" with the description "Implement user login and registration" using the MCP server.
```

**Listing Epics:**
```
List all epics in the current project using the MCP server.
```

**Updating Epic Status:**
```
Update the status of the "User Authentication" epic to "in-progress" using the MCP server.
```

### Managing Stories

**Creating a Story:**
```
Create a new story called "Login Page" under the "User Authentication" epic with the description "Create a user login form" using the MCP server.
```

**Listing Stories:**
```
List all stories for the "User Authentication" epic using the MCP server.
```

**Updating Story Status:**
```
Update the status of the "Login Page" story to "completed" using the MCP server.
```

### Managing Tasks

**Creating a Task:**
```
Create a new task called "Design Login Form" under the "Login Page" story using the MCP server.
```

**Listing Tasks:**
```
List all tasks for the "Login Page" story using the MCP server.
```

**Updating Task Status:**
```
Update the status of the "Design Login Form" task to "completed" using the MCP server.
```

## Documentation Management

### Generating Documentation

```
Generate architecture documentation for the current project using the MCP server.
```

Available documentation types:
- `prd`: Product Requirements Document
- `architecture`: Technical Architecture Document
- `progress`: Project Progress Report

### Viewing Documentation

```
Show me the content of the architecture document using the MCP server.
```

### Updating Documentation

```
Update the architecture document with the following content: "..." using the MCP server.
```

## IDE Integration

### Generating IDE Rules

Generate rules files for specific IDEs:

```
Generate Cursor IDE rules using the MCP server.
```

This creates rule files that help AI assistants understand your project structure and workflows.

## Best Practices

1. **Consistent Naming**: Use consistent naming for epics, stories, and tasks
2. **Regular Updates**: Keep task and story statuses up to date
3. **Documentation First**: Create proper documentation before implementation
4. **Use Hierarchy**: Maintain the epic > story > task hierarchy
5. **Version Control**: Commit the agile-docs directory to keep track of changes

## Working with AI Assistants

When working with AI assistants, use natural language to interact with the MCP server:

```
I need to implement a user authentication system. Can you help me set up the epics, stories, and tasks using the MCP Agile Flow server?
```

The assistant will use the appropriate MCP tools to help you manage your Agile workflow. 