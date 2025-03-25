---
description: Standards for MCP server development and testing with FastMCP
globs: "**/*.py"
alwaysApply: false
---
# MCP Server Development and Integration Testing

## Context
- When developing or extending MCP servers using FastMCP
- When implementing MCP tools and server-side Python functionality
- When creating integration tests for MCP tools
- When debugging or optimizing MCP server performance
- When validating tool interactions with the filesystem and environment
- When implementing new tools with MCP's built-in annotations

## Requirements
- Follow FastMCP conventions for tool registration and implementation
- Use type hints consistently for all function parameters and return values
- Implement proper error handling and logging
- Return properly formatted JSON responses
- Create comprehensive integration tests with direct tool invocation
- Set up proper test fixtures for clean testing
- Implement tool chain tests to validate workflows
- Ensure proper test cleanup for filesystem and environment changes
- Use MCP's built-in annotations as the standard approach for all tool implementations

## Server Implementation

### Core Components
- **Server Initialization**: Bootstrap FastMCP server with proper configuration
- **Tool Registration**: Register functions as MCP tools with appropriate naming
- **Tool Implementation**: Implement tool functions with proper typing and documentation
- **Error Handling**: Gracefully handle and report errors to clients
- **Logging**: Implement consistent logging throughout the application
- **Testing**: Create comprehensive test cases for all tools

### Project Structure
```
src/
├── your_package/
│   ├── __init__.py       # Package initialization
│   ├── __main__.py       # Entry point with FastMCP server setup
│   ├── version.py        # Version information
│   ├── utils.py          # Utility functions
│   ├── tools/            # Tool implementations
│   │   ├── __init__.py   # Tool exports
│   │   ├── tool_a.py     # Individual tool implementation
│   │   └── tool_b.py     # Individual tool implementation
│   └── config.py         # Configuration management
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures and configuration
└── test_*.py             # Test files for each module
```

### FastMCP Built-in Annotations

FastMCP provides several built-in annotations and type hints that form the foundation of MCP server development. These should be used as the primary building blocks for your server.

#### Core Decorators

1. **`@mcp.tool()`**
   - **Purpose**: Registers a function as an MCP tool available to the LLM
   - **Parameters**: Optional `name` to override the function name
   - **When to use**: For any Python function that should be exposed as a callable tool
   - **Example**:
     ```python
     @mcp.tool()  # Uses function name "add"
     def add(a: int, b: int) -> int:
         """Add two numbers"""
         return a + b
     
     @mcp.tool(name="subtract-numbers")  # Custom name
     def subtract(a: int, b: int) -> int:
         """Subtract b from a"""
         return a - b
     ```

2. **`@mcp.resource("uri://{param}")`**
   - **Purpose**: Registers a function as a resource provider
   - **Parameters**: URI template with optional parameters in curly braces
   - **When to use**: For functions that return data rather than performing actions
   - **Example**:
     ```python
     @mcp.resource("users://{user_id}/profile")
     def get_user_profile(user_id: str) -> dict:
         """Get a user's profile data"""
         return user_db.get_profile(user_id)
     
     @mcp.resource("config://system")
     def get_system_config() -> dict:
         """Get static system configuration"""
         return load_system_config()
     ```

3. **`@mcp.prompt()`**
   - **Purpose**: Registers a function that returns prompt templates
   - **Parameters**: Optional `name` to override the function name
   - **When to use**: For providing reusable prompt templates to the LLM
   - **Example**:
     ```python
     @mcp.prompt()
     def code_review(code: str) -> str:
         """Template for code review prompts"""
         return f"Please review this code:\n\n{code}"
     
     @mcp.prompt()
     def debug_help(error: str) -> list[Message]:
         """Structured message sequence for debugging"""
         from mcp.types import UserMessage, AssistantMessage
         return [
             UserMessage("I'm seeing this error:"),
             UserMessage(error),
             AssistantMessage("I'll help debug that. What have you tried so far?")
         ]
     ```

4. **`@asynccontextmanager` (for lifespan management)**
   - **Purpose**: Manages application lifecycle and dependencies
   - **When to use**: For setting up and cleaning up resources used by your server
   - **Example**:
     ```python
     from contextlib import asynccontextmanager
     
     @asynccontextmanager
     async def app_lifespan():
         """Manage application lifecycle with a type-safe context"""
         # Setup: Initialize database connection
         db = await Database.connect()
         
         try:
             # Yield the initialized resources to the app
             yield {"db": db}
         finally:
             # Cleanup: Close the database connection
             await db.close()
     
     # Pass the lifespan to the server
     mcp = FastMCP("DatabaseApp", lifespan=app_lifespan)
     ```

#### Type Annotations

1. **`Context` Parameter Type**
   - **Purpose**: Provides access to MCP capabilities within tool/resource functions
   - **When to use**: When tools need to report progress, log information, or access resources
   - **Example**:
     ```python
     from mcp import Context
     
     @mcp.tool()
     async def process_files(files: list[str], ctx: Context) -> str:
         """Process multiple files with progress tracking"""
         for i, file in enumerate(files):
             # Log information about current operation
             ctx.info(f"Processing {file}")
             
             # Report progress to the client
             await ctx.report_progress(i, len(files))
             
             # Access another resource if needed
             file_data = await ctx.read_resource(f"file://{file}")
             process_data(file_data)
             
         return "Processing complete"
     ```

2. **`Image` Return Type**
   - **Purpose**: Handles returning images from tools and resources
   - **When to use**: For tools that generate or process images
   - **Example**:
     ```python
     from mcp import Image
     from PIL import Image as PILImage
     
     @mcp.tool()
     def create_thumbnail(image_path: str, size: int = 100) -> Image:
         """Create a thumbnail from an image"""
         img = PILImage.open(image_path)
         img.thumbnail((size, size))
         
         # FastMCP handles conversion and MIME types
         return Image(data=img.tobytes(), format="png")
     
     @mcp.resource("images://{path}")
     def get_image(path: str) -> Image:
         """Load an image by path"""
         return Image(path=path)  # Automatic format detection
     ```

### Tool Implementation Pattern

#### Recommended Pattern

```python
import json
import logging
from typing import Optional, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

@mcp.tool(name="get-project-settings")
def get_project_settings(project_path: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    Returns project settings and configuration details.
    
    Args:
        project_path: Optional path to the project. If not provided,
                     uses current working directory.
        ctx: MCP context for logging
    
    Returns:
        Dictionary containing project settings
    """
    try:
        if ctx:
            ctx.info(f"Getting project settings for path: {project_path}")
        else:
            logger.info(f"Getting project settings for path: {project_path}")
        
        # Determine project path
        actual_path = project_path or os.getcwd()
        
        # Validate path exists
        if not os.path.exists(actual_path):
            return {
                "success": False,
                "error": f"Project path does not exist: {actual_path}",
                "message": "Please provide a valid project path"
            }
        
        # Collect project settings
        settings = {
            "success": True,
            "project_path": actual_path,
            "project_name": os.path.basename(actual_path),
            "ai_docs_path": os.path.join(actual_path, "ai-docs"),
            "templates_path": os.path.join(actual_path, ".ai-templates"),
            "has_makefile": os.path.exists(os.path.join(actual_path, "Makefile")),
        }
        
        return settings
    except Exception as e:
        if ctx:
            ctx.error(f"Error getting project settings: {str(e)}")
        else:
            logger.error(f"Error getting project settings: {str(e)}")
        
        return {
            "success": False,
            "error": str(e),
            "message": "An error occurred while fetching project settings"
        }
```

#### Using Context for Progress and Logging

```python
@mcp.tool(name="process-files")
async def process_files(file_paths: list[str], ctx: Context) -> Dict[str, Any]:
    """
    Process multiple files with progress reporting.
    
    Args:
        file_paths: List of files to process
        ctx: MCP context for progress reporting
    
    Returns:
        Dictionary with operation results
    """
    try:
        results = []
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            # Log progress
            ctx.info(f"Processing file {i+1}/{total_files}: {file_path}")
            
            # Report progress
            await ctx.report_progress(i, total_files)
            
            # Process file
            file_result = process_single_file(file_path)
            results.append(file_result)
            
        return {
            "success": True,
            "processed_count": len(results),
            "results": results
        }
    except Exception as e:
        ctx.error(f"Error processing files: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "An error occurred while processing files"
        }
```

## Testing Approach

### Test Infrastructure

```python
import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path

import pytest

# Add project to Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

# Import MCP-related functions
from src.your_package import call_tool, call_tool_sync
```

### Essential Test Fixtures

```python
@pytest.fixture(scope="function", autouse=True)
def setup_logging():
    """Configure logging for all tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
    )
    yield

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def env_cleanup():
    """Clean up environment variables after tests."""
    # Store original environment variables
    original_env = {}
    for key in ["PROJECT_PATH", "WORKSPACE_DIRECTORY"]:
        if key in os.environ:
            original_env[key] = os.environ[key]
    
    yield
    
    # Restore original environment
    for key in ["PROJECT_PATH", "WORKSPACE_DIRECTORY"]:
        if key in original_env:
            os.environ[key] = original_env[key]
        elif key in os.environ:
            del os.environ[key]
```

### Tool Chain Testing Pattern

```python
@pytest.mark.asyncio
async def test_tool_chain_integration():
    """Test a full chain of tool interactions together."""
    with tempfile.TemporaryDirectory() as project_dir:
        # 1. Initialize project structure
        init_result = await call_tool("initialize-ide", {
            "ide": "cursor", 
            "project_path": project_dir
        })
        assert init_result["success"] is True
        
        # 2. Create test content
        story_content = "# Test Story\n\nThis is a test story."
        story_file = Path(project_dir) / "ai-docs" / "story-test.md"
        story_file.parent.mkdir(exist_ok=True)
        with open(story_file, "w") as f:
            f.write(story_content)
        
        # 3. Call subsequent tool
        prime_result = await call_tool("prime-context", {
            "project_path": project_dir,
            "depth": "minimal"
        })
        
        # 4. Verify results
        assert prime_result["success"] is True
        assert "Test Story" in str(prime_result["context"])
```

## Examples

<example>
# Tool Implementation Pattern

```python
import json
import logging
import os
from typing import Dict, Any, Optional
from mcp import Context

logger = logging.getLogger(__name__)

@mcp.tool(name="get-project-settings")
def get_project_settings(project_path: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    Returns project settings and configuration details.
    
    Args:
        project_path: Optional path to the project. If not provided,
                     uses current working directory.
        ctx: MCP context for logging
    
    Returns:
        Dictionary containing project settings
    """
    try:
        if ctx:
            ctx.info(f"Getting project settings for path: {project_path}")
        else:
            logger.info(f"Getting project settings for path: {project_path}")
        
        # Determine project path
        actual_path = project_path or os.getcwd()
        
        # Validate path exists
        if not os.path.exists(actual_path):
            return {
                "success": False,
                "error": f"Project path does not exist: {actual_path}",
                "message": "Please provide a valid project path"
            }
        
        # Collect project settings
        settings = {
            "success": True,
            "project_path": actual_path,
            "project_name": os.path.basename(actual_path),
            "ai_docs_path": os.path.join(actual_path, "ai-docs"),
            "templates_path": os.path.join(actual_path, ".ai-templates"),
            "has_makefile": os.path.exists(os.path.join(actual_path, "Makefile")),
        }
        
        return settings
    except Exception as e:
        if ctx:
            ctx.error(f"Error getting project settings: {str(e)}")
        else:
            logger.error(f"Error getting project settings: {str(e)}")
        
        return {
            "success": False,
            "error": str(e),
            "message": "An error occurred while fetching project settings"
        }
```

# Resource Implementation

```python
import os
from typing import Dict, Any
from pathlib import Path
from mcp import Context

@mcp.resource("file://{file_path}")
async def get_file_content(file_path: str, ctx: Context = None) -> str:
    """
    Get the content of a file.
    
    Args:
        file_path: Path to the file to read
        ctx: MCP context for logging
    
    Returns:
        String containing the file content
    """
    if ctx:
        ctx.info(f"Reading file: {file_path}")
    
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
```

# Lifespan Management

```python
from contextlib import asynccontextmanager
import sqlite3
from mcp import FastMCP

@asynccontextmanager
async def app_lifespan():
    """Set up and tear down database connection for our app."""
    # Setup: Create database connection
    db = sqlite3.connect("app.db")
    
    try:
        # Initialize the database if needed
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        db.commit()
        
        # Yield resources to be available during app lifetime
        yield {"db": db}
    finally:
        # Cleanup: Close database connection
        db.close()

# Create MCP server with lifespan
mcp = FastMCP("DatabaseApp", lifespan=app_lifespan)

@mcp.tool()
def add_user(name: str, ctx: Context) -> Dict[str, Any]:
    """Add a user to the database."""
    try:
        # Access the database from context
        db = ctx.resources["db"]
        
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        db.commit()
        
        return {
            "success": True,
            "user_id": cursor.lastrowid,
            "message": f"User {name} added successfully"
        }
    except Exception as e:
        ctx.error(f"Error adding user: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add user to database"
        }
```

# Integration Test

```python
@pytest.mark.asyncio
async def test_complete_workflow():
    """Test a complete workflow from project initialization to tool usage."""
    with tempfile.TemporaryDirectory() as test_project:
        # Step 1: Initialize project
        init_result = await call_tool("initialize-ide", {
            "ide": "cursor", 
            "project_path": test_project
        })
        assert init_result["success"] is True
        
        # Step 2: Get project settings
        settings_result = await call_tool("get-project-settings", {
            "proposed_path": test_project
        })
        assert settings_result["success"] is True
        assert settings_result["project_path"] == test_project
        
        # Step 3: Create sample content
        ai_docs_dir = Path(test_project) / "ai-docs"
        prd_file = ai_docs_dir / "prd.md"
        with open(prd_file, "w") as f:
            f.write("# Product Requirements Document\n\nTest PRD content.")
        
        # Step 4: Prime context to read content
        prime_result = await call_tool("prime-context", {
            "project_path": test_project,
            "depth": "standard"
        })
        assert prime_result["success"] is True
        assert "Product Requirements Document" in str(prime_result["context"])
```
</example>

<example type="invalid">
# Missing Type Hints

```python
@mcp.tool()
def my_tool(data):  # Missing type hints
    # Process the data
    result = process_data(data)
    return result  # No clear return type
```

# Missing Error Handling

```python
@mcp.tool()
def unsafe_file_read(path: str) -> str:
    # No error handling for file not found or permission issues
    with open(path, "r") as f:
        return f.read()  # Will raise exceptions to the client
```

# Inconsistent Response Format

```python
@mcp.tool()
def inconsistent_tool(query: str) -> Dict[str, Any]:
    if query == "special":
        # Missing success flag
        return {"data": process_special(query)}
    
    # Has success flag
    return {
        "success": True,
        "data": process_normal(query)
    }
```

# Using Mocks in Integration Tests

```python
@pytest.mark.asyncio
async def test_with_mocks():
    """Using mocks defeats the purpose of integration testing."""
    with mock.patch("src.mcp_agile_flow.call_tool") as mock_call:
        mock_call.return_value = {"success": True, "data": "mocked"}
        result = await call_tool("get-project-settings", {})
        assert result["success"] is True
```

# Not Using Context Parameter

```python
@mcp.tool()
def tool_without_context(file_paths: list[str]) -> Dict[str, Any]:
    """
    Process files without using Context for progress tracking
    or proper logging.
    """
    results = []
    for file_path in file_paths:
        # No progress reporting to client
        # No structured logging
        result = process_file(file_path)
        results.append(result)
    
    return {"success": True, "results": results}
```
</example>

## Critical Rules

### Development Rules
- Use proper type hints for all function parameters and return values
- Always add clear descriptive docstrings to all tool and resource functions
- Use the Context parameter in tools that perform long-running operations or need logging
- Implement consistent error handling in all tools and resources
- Use a standard response format with {"success": bool, ...} for all tool responses
- Return clear, user-friendly error messages
- Keep tools focused on a single responsibility
- Use lifespan management with asynccontextmanager for proper resource management
- Properly document any required parameters in tool docstrings
- Always validate input parameters before performing operations
- Use appropriate HTTP status codes for error responses
- Log at appropriate levels (debug, info, warning, error)
- Return detailed error information in development, but be cautious with sensitive info in production

### Testing Rules
- Never use mocks for integration tests - invoke actual MCP server tools directly
- Always use `tempfile.TemporaryDirectory()` for filesystem tests
- Clean up all environment variable changes after tests
- Test both synchronous and asynchronous versions of tools
- Include tests for both happy paths and error scenarios
- Create real test data and files for testing
- Implement tests for complete workflows that use multiple tools in sequence
- Test idempotence for all tools that modify state
- Validate the complete response structure for all tool calls
- Test error handling by providing invalid inputs 