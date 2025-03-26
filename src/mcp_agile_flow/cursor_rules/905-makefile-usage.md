---
description: Use when working with projects that have Makefiles for automating build, test, and deployment processes
globs: Makefile, makefile, *.mk
alwaysApply: false
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
- Keep Makefiles concise and minimal with focused targets
- Prioritize developer convenience by combining related commands
- Use clear section headers to organize complex Makefiles
- Provide meaningful output with visual indicators (e.g., emojis)
- Combine related code quality tasks (lint, format, type check) into a single `quality` target

## Makefile Structure

### Core Components
- **Variables**: Define reusable variables at the top of the file
- **Phony Targets**: Mark non-file targets as .PHONY to avoid conflicts
- **Default Target**: The first target is the default when running `make` without arguments
- **Dependencies**: Clearly specify target dependencies
- **Help Documentation**: Include a help target that lists available commands
- **Comments**: Document each target's purpose with comments
- **Sections**: Use clear section headers to separate groups of related targets
- **Combined Targets**: Create convenience targets that combine multiple related operations

### Standard Target Categories
- **Build**: Compilation, installation, and setup (`build`, `install`, `setup`)
- **Testing**: Test execution and coverage (`test`, `pytest`, `check`)
- **Running**: Execution of the project (`run`, `start`, `serve`, `dev`)
- **Cleaning**: Removal of temporary files (`clean`, `clear`, `reset`)
- **Quality**: Code quality assurance (`quality`, `lint`, `format`, `type-check`)
- **Deployment**: Publishing and releasing (`deploy`, `publish`, `release`)
- **All-in-one**: Combined targets for common workflows (`all`, `setup-and-test`, `quick-start`)

### Common Project Targets
- `all`: Build everything needed (or combine setup and test)
- `clean`: Remove build artifacts
- `test`: Run tests
- `install`: Install dependencies
- `build`: Compile/build the project
- `run`/`start`: Execute the project
- `quality`: Run all code quality checks (linting, formatting, type checking)
- `lint`: Check code style
- `format`: Auto-format code
- `type-check`: Check type correctness
- `help`: Show available commands
- `deploy`: Deploy to hosting/production

## Commands

- "look for and use the Makefile": Examines project Makefile for relevant commands
- "add a Makefile target for {operation}": Creates a new target in the Makefile
- "update the Makefile with {command}": Modifies existing Makefile targets
- "show available Makefile commands": Lists all targets in the Makefile
- "run make {target}": Executes the specified Makefile target
- "make the Makefile more concise": Combines related targets and simplifies structure

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

User: "Can you make the Makefile more concise and convenient?"

AI Action:
1. Examines the existing Makefile
2. Identifies opportunities to combine targets and simplify structure
3. Updates the Makefile with:
   ```makefile
   # Combined convenient target
   all: setup test
      @echo "✅ Setup and tests completed successfully!"
   
   # Clear section headers
   #################################################
   # CORE TARGETS
   #################################################
   ```

User: "Add a way to check code quality"

AI Action:
1. Examines the existing Makefile
2. Creates a comprehensive quality target that combines related checks
3. Updates the Makefile with:
   ```makefile
   # Combined quality target
   .PHONY: quality
   quality: lint format type-check
      @echo "✅ All quality checks passed!"
   
   lint:
      @echo "Running linter..."
      $(LINTER) $(LINT_FLAGS) $(SRC_DIR)
   
   format:
      @echo "Running formatter..."
      $(FORMATTER) $(FORMAT_FLAGS) $(SRC_DIR)
   
   type-check:
      @echo "Running type checker..."
      $(TYPECHECKER) $(TYPECHECK_FLAGS) $(SRC_DIR)
   ```
</example>

<example type="invalid">
User: "How do I run the project?"

AI Action:
Suggests a direct command without checking if a Makefile target exists for running the project.

User: "Add a test command to the project"

AI Action:
Creates a new script file rather than adding an appropriate target to the existing Makefile.

User: "Make the Makefile simpler"

AI Action:
Removes important targets or functionality in the name of simplicity, breaking existing workflows.

User: "How do I check code quality?"

AI Action:
Suggests running individual linting, formatting, and type checking commands instead of creating or using a combined `quality` target in the Makefile.
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
- Minimize the number of targets while maximizing convenience
- Use combined targets for common workflows to reduce command complexity
- Add section headers to improve readability in larger Makefiles
- Prioritize developer convenience over strict target separation
- Add meaningful terminal output with visual indicators (emojis, colors)
- Combine code quality tasks (linting, formatting, type checking) into a single `quality` target 