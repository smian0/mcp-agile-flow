# Testing the initialize_project MCP Tool

This document describes how to test the `initialize_project` MCP tool, which is used to bootstrap a project with Cursor rule templates.

## Overview

The `initialize_project` MCP tool:

1. Creates necessary directories (.cursor/rules, .cursor/templates, docs, .ai)
2. Copies cursor rule templates to the project
3. Creates workflow documentation
4. Updates or creates .gitignore file
5. Intelligently detects project name and root directory

## Running the Tests

We've created a pytest-based test suite that verifies all aspects of the tool's functionality.

### Prerequisites

- Python 3.6+
- pytest (`pip install pytest`)
- requests (`pip install requests`)

### Running Tests

To run the tests, use the provided script:

```bash
./run_initialize_tests.sh
```

This script:
1. Sets up the Python path correctly
2. Starts the MCP server if not already running
3. Runs the pytest tests with verbose output
4. Cleans up after test execution

### What the Tests Verify

The tests check:

1. **Basic Initialization**: Initializing a project with explicit parameters
2. **Project Name Detection**: Auto-detecting project name from package.json
3. **Gitignore Integration**: Proper creation or updating of .gitignore
4. **Multiple Initializations**: Handling multiple initializations of the same directory

## Manual Testing

You can also test the tool manually using curl:

```bash
# Start the MCP server
./run_server.sh

# In another terminal, use curl to call the tool
curl -X POST http://localhost:3000/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "call_tool",
    "params": {
      "name": "initialize_project",
      "arguments": {
        "target_directory": "/path/to/your/project",
        "project_name": "your-project-name"
      }
    }
  }'
```

## Extending the Tests

To add more test cases:

1. Add new test functions to `tests/test_initialize_mcp.py`
2. Use the existing fixtures and helper functions
3. Follow the pytest naming convention (`test_*`)

Example of adding a new test:

```python
def test_your_new_scenario(mcp_server, test_dir):
    """Description of your test."""
    # Setup any special conditions
    
    # Call the MCP tool
    response = call_mcp_tool("initialize_project", {
        "target_directory": test_dir,
        "project_name": "specific-test-name"
    })
    
    # Assert expected results
    assert "result" in response
    # More assertions...
```
