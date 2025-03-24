# MCP Agile Flow

[![Coverage](https://github.com/yourusername/mcp-agile-flow/raw/main/badges/coverage.svg)](https://yourusername.github.io/mcp-agile-flow/)

A comprehensive system for managing AI-assisted agile development workflows.

## Status

✅ **Migration Complete**: The migration from legacy server to FastMCP implementation is fully complete. All legacy code and tests have been removed.

## Key Features

- **Agile Documentation**: Generate and maintain comprehensive AI documentation
- **Project Structure**: Organize your project with AI-generated files and directories
- **IDE Integration**: Direct integration with various AI IDEs (Cursor, Windsurf, Cline)
- **Workflow Management**: Track agile stories and progress

## Getting Started

To use MCP Agile Flow:

1. Install the package:
   ```
   pip install mcp-agile-flow
   ```

2. Import in your code:
   ```python
   from mcp_agile_flow.adapter import call_tool, call_tool_sync
   
   # Use async interface
   result = await call_tool("get-project-settings", {})
   
   # Or use sync interface
   result = call_tool_sync("get-project-settings", {})
   ```

## Available Tools

The MCP Agile Flow provides several tools:

- `get-project-settings`: Get project settings including paths and environment variables
- `initialize-ide`: Initialize project directory structure for specific IDEs
- `initialize-ide-rules`: Initialize AI rule files for specific IDEs
- `prime-context`: Analyze project documentation and build contextual understanding
- `migrate-mcp-config`: Migrate MCP configuration between different IDEs

## Development

To set up for development:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/mcp-agile-flow.git
   cd mcp-agile-flow
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```
   pytest
   ```

5. Common Makefile commands:
   ```
   make test         # Run tests
   make coverage     # Generate coverage report
   make clean        # Clean build artifacts
   make clean-archived  # Remove archived legacy files
   ```

## License

This project is licensed under the MIT License - See [LICENSE](LICENSE) file for details.