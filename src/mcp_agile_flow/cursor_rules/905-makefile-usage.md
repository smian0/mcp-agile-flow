---
description: Use when working with projects that have Makefiles for automating build, test, and deployment processes
globs: Makefile, makefile, *.mk, pyproject.toml, package.json
alwaysApply: true
---

# Makefile Usage Standards

## Context
- When working with projects that have build, test, or deployment automation
- When setting up a new project that requires task automation
- When executing project commands or workflows
- When maintaining or updating build processes
- When documenting project setup and usage

## Requirements
- Always look for and use existing Makefiles for project commands
- Follow proper Makefile syntax and conventions
- Document all Makefile targets clearly with comments
- Organize targets by category (build, test, run, clean, deploy)
- Maintain backward compatibility when updating Makefiles
- Ensure all commands are properly escaped and portable
- Provide descriptive help targets for self-documentation

## Makefile Structure

### Core Components
- **Variables**: Define reusable variables at the top of the file
- **Phony Targets**: Mark non-file targets as .PHONY to avoid conflicts
- **Default Target**: The first target is the default when running `make` without arguments
- **Dependencies**: Clearly specify target dependencies
- **Help Documentation**: Include a help target that lists available commands
- **Comments**: Document each target's purpose with comments

### Standard Target Categories
- **Build**: Compilation, installation, and setup (`build`, `install`, `setup`)
- **Testing**: Test execution and coverage (`test`, `pytest`, `check`)
- **Running**: Execution of the project (`run`, `start`, `serve`, `dev`)
- **Cleaning**: Removal of temporary files (`clean`, `clear`, `reset`)
- **Deployment**: Publishing and releasing (`deploy`, `publish`, `release`)
- **Linting**: Code formatting and style checking (`lint`, `format`, `style`)

### Common Project Targets
- `all`: Build everything needed
- `clean`: Remove build artifacts
- `test`: Run tests
- `install`: Install dependencies
- `build`: Compile/build the project
- `run`/`start`: Execute the project
- `lint`: Check code style and format
- `help`: Show available commands
- `deploy`: Deploy to hosting/production

## Commands

- "look for and use the Makefile": Examines project Makefile for relevant commands
- "add a Makefile target for {operation}": Creates a new target in the Makefile
- "update the Makefile with {command}": Modifies existing Makefile targets
- "show available Makefile commands": Lists all targets in the Makefile
- "run make {target}": Executes the specified Makefile target

## Examples

<example>
User: "How do I run the project tests?"

AI Action:
1. Checks for a Makefile in the project root
2. Finds a 'test' target in the Makefile
3. Responds: "You can run the tests using the Makefile command: `make test`"

User: "What build commands are available in this project?"

AI Action:
1. Examines the Makefile
2. Identifies build-related targets
3. Responds: "The project Makefile includes these build commands:
   - `make build`: Compiles the project
   - `make install`: Installs dependencies
   - `make setup-dev`: Sets up the development environment"
</example>

<example type="invalid">
User: "How do I run the project?"

AI Action:
Suggests a direct command without checking if a Makefile target exists for running the project.

User: "Add a test command to the project"

AI Action:
Creates a new script file rather than adding an appropriate target to the existing Makefile.
</example>

## Critical Rules
- Always check for the existence of a Makefile before suggesting command-line instructions
- Use `make` commands instead of direct shell commands when equivalent targets exist
- When adding functionality, extend the Makefile rather than creating separate scripts
- Preserve existing Makefile structure and conventions when making updates
- Document all Makefile changes clearly with comments
- Ensure Makefile targets are properly categorized
- Use tab indentation (not spaces) for command lines
- Keep commands portable across environments (avoid system-specific commands)
- Ensure all targets have clear, descriptive names that reflect their purpose 