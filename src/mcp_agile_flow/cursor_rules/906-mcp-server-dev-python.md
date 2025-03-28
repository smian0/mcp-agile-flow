---
description: Standards for MCP server development and testing with FastMCP
globs: **/*.py, **/pyproject.toml
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
- When integrating MCP servers with other Python applications

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
- Provide proper integration patterns for external applications

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

### External Client Integration Strategies

When integrating an MCP server with external Python applications, there are two primary approaches, each with specific benefits and use cases:

#### 1. Official MCP Client API (Recommended)

The official `mcp` package provides a high-level client API that can programmatically start and interact with MCP servers:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    # Configure server parameters
    server_params = StdioServerParameters(
        command="uv",  # Use UV for Python execution
        args=["run", "-m", "your_server_module", "--mode", "stdio"],
        env=None  # Optional environment variables
    )
    
    # Start server and create session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            
            # Call a tool
            result = await session.call_tool("tool-name", {"param": "value"})
            
            # Read a resource
            content, mime_type = await session.read_resource("resource://uri")
```

**Benefits:**
- Clean async interface
- Proper protocol handling 
- Automatic server lifecycle management
- Standardized error handling
- Resilience against protocol changes

#### 2. Custom STDIO Client

For specialized needs, a custom STDIO client provides more control:

```python
class CustomMCPClient:
    def __init__(self, server_script="server.py", mode="stdio"):
        self.server_script = server_script
        self.mode = mode
        self.process = subprocess.Popen(
            [sys.executable, self.server_script, "--mode", self.mode],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,  # Unbuffered
        )
        self.request_id = 0
        self.initialize()
    
    def initialize(self):
        # Initialize the server with JSON-RPC protocol
        initialize_request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0",
                "capabilities": {},
                "clientInfo": {
                    "name": "custom-client",
                    "version": "1.0.0"
                }
            }
        }
        self.request_id += 1
        response = self.send_request(initialize_request)
        
        # Send initialized notification
        self.send_notification({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        })
        
        return response
    
    def send_request(self, request):
        # Implementation details here
        pass
        
    def call_tool(self, tool_name, params=None):
        # Implementation details here
        pass
```

#### 3. Package Dependency Approach

For tight coupling, directly integrating the MCP server as a Python package:

```python
# In pyproject.toml of the client application
[project]
dependencies = [
    "your-mcp-server @ git+https://github.com/org/your-mcp-server.git",
]

# In client code
from your_mcp_server import get_data_function

# Direct function call without MCP protocol
result = get_data_function(param1, param2)
```

#### 4. Integrating with MCP Servers from Another Application

For integrating with any MCP server from another Python program, use the official MCP client API approach for best results. Here's a generic pattern followed by a specific example:

**Generic Pattern:**
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_mcp_client(module_name, tool_calls):
    """
    Generic function to run any MCP server and make tool calls
    
    Args:
        module_name: The Python module name of the MCP server
        tool_calls: List of (tool_name, params) tuples to execute
    """
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="uv",  # Best practice: Use UV for Python execution
        args=["run", "-m", module_name, "--mode", "stdio"],
        env=None  # Optional environment variables
    )
    
    # Start server and create client session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Execute each tool call
            results = []
            for tool_name, params in tool_calls:
                result = await session.call_tool(tool_name, params)
                results.append(result)
            
            return results

if __name__ == "__main__":
    # Example usage with any MCP server
    tool_calls = [
        ("example_tool", {"param1": "value1"}),
        ("another_tool", {"param2": 42})
    ]
    asyncio.run(run_mcp_client("your_mcp_module", tool_calls))
```

**Real-World Example with MCP Stock Data:**
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_stock_data_client():
    """Example using the MCP Stock Data server"""
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="uv",  # Using UV as recommended
        args=["run", "-m", "fastmcp_server", "--mode", "stdio"],
        env=None  # Optional environment variables
    )
    
    # Start server and create client session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")
            
            # Get a stock metric (e.g., Apple's current price)
            result = await session.call_tool("get_stock_metric", 
                                           {"symbol": "AAPL", "metric": "shortName"})
            print(f"Apple name: {result}")
            
            # Get historical stock data
            history = await session.call_tool("get_historical_data", 
                                            {"symbol": "MSFT", "period": "1mo"})
            print(f"Microsoft history: {history}")
            
            # Get latest news for a stock
            news = await session.call_tool("get_stock_news", 
                                         {"symbol": "TSLA", "limit": 3})
            print(f"Tesla news: {news}")

if __name__ == "__main__":
    asyncio.run(run_stock_data_client())
```

Make sure to install both the specific MCP server package and the MCP client library:

```bash
# Install the MCP server package (example with Stock Data)
uv pip install git+https://github.com/owner/mcp-server-repo.git

# Install the MCP client library
uv pip install mcp
```

### Integration Best Practices

1. **Dependency Management**:
   - Ensure all package modules are included in pyproject.toml:
   ```toml
   [tool.setuptools]
   py-modules = [
       "server",
       "fastmcp_server",
       "models"  # Include ALL modules
   ]
   ```

2. **Error Handling**: 
   - Implement robust error handling in clients
   - Handle connection failures gracefully
   - Provide meaningful error messages

3. **Documentation**:
   - Document integration patterns in README
   - Include example code for different integration approaches
   - Specify required dependencies

4. **Testing**:
   - Create integration tests that validate client-server interactions
   - Test in both development and production environments
   - Validate handling of edge cases

## Testing Approach

### Test Infrastructure

```python
import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
import subprocess
import sys
from typing import Dict, Any, Optional, List

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

### STDIO Mode Integration Testing

STDIO mode integration testing is crucial for validating MCP servers intended to be used as AI assistant tools. This testing approach uses real subprocess communication to closely match how AI assistants will interact with your server.

#### FastMCPClient for STDIO Testing

```python
class FastMCPClient:
    """A client for interacting with a FastMCP server over STDIO."""
    
    def __init__(self, debug: bool = False):
        """Initialize the client with debugging options.
        
        Args:
            debug: Whether to print debug information
        """
        self.debug = debug
        self.request_id = 0
        self.process = None
        self.initialized = False
    
    def start_server(self, server_module: str) -> None:
        """Start the server as a subprocess.
        
        Args:
            server_module: Python module path to the server
        """
        if self.debug:
            print(f"Starting server using module: {server_module}")
        
        self.process = subprocess.Popen(
            [sys.executable, "-m", server_module, "--mode", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        if self.debug:
            print(f"Server started with PID: {self.process.pid}")
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the server with standard parameters."""
        if self.debug:
            print("Initializing server...")
        
        init_response = self.send_request("initialize", {
            "rootUri": "file:///tmp/test",
            "capabilities": {},
            "clientInfo": {
                "name": "Test Client",
                "version": "1.0.0"
            },
            "locale": "en-US"
        })
        
        # Send initialized notification
        self.send_notification("notifications/initialized", {})
        
        self.initialized = True
        return init_response
    
    def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the server.
        
        Args:
            method: The method name
            params: The parameters to pass
            
        Returns:
            The server's response
        """
        if not self.process:
            raise RuntimeError("Server not started")
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        if self.debug:
            print(f"Sending request: {json.dumps(request, indent=2)}")
        
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        
        response_text = self.process.stdout.readline().strip()
        
        if not response_text:
            raise RuntimeError("No response received from server")
        
        try:
            response = json.loads(response_text)
            if self.debug:
                print(f"Received response: {json.dumps(response, indent=2)}")
            return response
        except json.JSONDecodeError:
            raise RuntimeError(f"Failed to parse response: {response_text}")
    
    def send_notification(self, method: str, params: Dict[str, Any]) -> None:
        """Send a notification to the server (no response expected).
        
        Args:
            method: The notification method name
            params: The parameters to pass
        """
        if not self.process:
            raise RuntimeError("Server not started")
        
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        if self.debug:
            print(f"Sending notification: {json.dumps(notification, indent=2)}")
        
        self.process.stdin.write(json.dumps(notification) + "\n")
        self.process.stdin.flush()
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        if not self.initialized:
            raise RuntimeError("Server not initialized")
        
        return self.send_request("tools/list", {})
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool with the given parameters.
        
        Args:
            tool_name: The name of the tool to call
            parameters: The parameters to pass to the tool
            
        Returns:
            The tool's response
        """
        if not self.initialized:
            raise RuntimeError("Server not initialized")
        
        if parameters is None:
            parameters = {}
        
        return self.send_request("tools/call", {
            "name": tool_name,
            "parameters": parameters
        })
    
    def list_resources(self) -> Dict[str, Any]:
        """List available resources."""
        if not self.initialized:
            raise RuntimeError("Server not initialized")
        
        return self.send_request("resources/list", {})
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource by URI.
        
        Args:
            uri: The URI of the resource to read
            
        Returns:
            The resource content
        """
        if not self.initialized:
            raise RuntimeError("Server not initialized")
        
        return self.send_request("resources/read", {
            "uri": uri
        })
    
    def shutdown(self) -> None:
        """Shutdown the server gracefully."""
        if not self.process:
            return
        
        try:
            if self.initialized:
                self.send_request("shutdown", {})
            self.process.stdin.close()
            self.process.wait(timeout=5)
        except Exception as e:
            if self.debug:
                print(f"Error during shutdown: {e}")
            self.process.kill()
        
        if self.debug:
            print("Server shut down")
        
        self.process = None
        self.initialized = False
    
    def __del__(self):
        """Clean up resources when the object is garbage collected."""
        self.shutdown()
```

#### STDIO Test Fixtures

```python
@pytest.fixture
def fastmcp_client():
    """Fixture that provides a FastMCPClient."""
    client = FastMCPClient(debug=False)
    yield client
    client.shutdown()

@pytest.fixture
def initialized_client(fastmcp_client):
    """Fixture that provides an initialized FastMCPClient."""
    server_module = "your_package.server"  # Adjust to your module path
    fastmcp_client.start_server(server_module)
    fastmcp_client.initialize()
    yield fastmcp_client
```

#### STDIO Mode Test Patterns

Below are essential patterns for testing MCP servers in STDIO mode:

```python
def test_list_resources(initialized_client):
    """Test that resources can be listed."""
    response = initialized_client.list_resources()
    
    # Validate response structure
    assert "id" in response
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "resources" in response["result"]
    
    # Validate that there's at least one resource
    resources = response["result"]["resources"]
    assert isinstance(resources, list)
    assert len(resources) > 0

def test_list_tools(initialized_client):
    """Test that tools can be listed."""
    response = initialized_client.list_tools()
    
    # Validate response structure
    assert "id" in response
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "tools" in response["result"]
    
    # Validate that there's at least one tool
    tools = response["result"]["tools"]
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    # Validate tool structure
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool

def test_call_health_check(initialized_client):
    """Test the health check tool."""
    response = initialized_client.call_tool("health_check")
    
    # Validate response structure
    assert "id" in response
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "content" in response["result"]
    assert "isError" in response["result"]
    
    # Validate content and error status
    assert not response["result"]["isError"]
    assert len(response["result"]["content"]) > 0
    
    # Parse the content as JSON
    content_text = response["result"]["content"][0]["text"]
    content_json = json.loads(content_text)
    
    # Validate the content
    assert "status" in content_json
    assert content_json["status"] == "ok"

def test_call_specific_tool(initialized_client):
    """Test a tool with specific parameters."""
    response = initialized_client.call_tool("your_tool_name", {
        "param1": "value1",
        "param2": 42
    })
    
    # Validate response structure
    assert "id" in response
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    
    # Check for successful result (not an error)
    assert "isError" in response["result"]
    assert not response["result"]["isError"]
    
    # Validate tool-specific response content
    assert "content" in response["result"]
    content = response["result"]["content"]
    
    # You can add more specific validation based on your tool's expected output
```

#### Error Handling in STDIO Tests

```python
def test_call_nonexistent_tool(initialized_client):
    """Test calling a tool that doesn't exist."""
    response = initialized_client.call_tool("nonexistent_tool")
    
    # Validate error response
    assert "id" in response
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    
    # Check for error result
    assert "result" in response
    assert "isError" in response["result"]
    assert response["result"]["isError"]
    
    # Validate error content
    assert "content" in response["result"]
    content = response["result"]["content"]
    assert len(content) > 0
    assert "text" in content[0]
    assert "error" in content[0]["text"].lower()

def test_call_tool_with_invalid_parameters(initialized_client):
    """Test calling a tool with invalid parameters."""
    response = initialized_client.call_tool("valid_tool_name", {
        "invalid_param": "value"
    })
    
    # Validate response structure for parameter validation errors
    assert "id" in response
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    
    # Expect an error result for invalid parameters
    assert "result" in response
    assert "isError" in response["result"]
    assert response["result"]["isError"]
```

#### Integration with Real External Services

For comprehensive testing, it's important to test your MCP server with real external services rather than mocks:

```python
def test_integration_with_external_service(initialized_client):
    """Test integration with a real external service."""
    # Use a well-known stable test case
    response = initialized_client.call_tool("get_data_from_service", {
        "query": "test_query",
        "limit": 5
    })
    
    # Validate successful response
    assert "id" in response
    assert "jsonrpc" in response
    assert "result" in response
    assert not response["result"]["isError"]
    
    # Validate real data from the service
    content = response["result"]["content"]
    assert len(content) > 0
    
    # Parse the content and validate service-specific data
    data = json.loads(content[0]["text"])
    assert "results" in data
    assert len(data["results"]) <= 5  # Respects the limit
```

#### Testing Common Failure Modes

```python
def test_handle_service_timeout(initialized_client):
    """Test handling of service timeouts."""
    # Use a parameter known to trigger slow response
    response = initialized_client.call_tool("get_data_with_timeout", {
        "simulate_timeout": True
    })
    
    # Validate timeout handling
    assert "result" in response
    assert "isError" in response["result"]
    assert response["result"]["isError"]
    
    # Check for timeout error message
    content = response["result"]["content"]
    error_text = content[0]["text"]
    assert "timeout" in error_text.lower() or "timed out" in error_text.lower()

def test_handle_rate_limiting(initialized_client):
    """Test handling of rate limiting from external services."""
    # Make multiple rapid requests to trigger rate limiting
    for _ in range(5):
        initialized_client.call_tool("rate_limited_tool")
    
    # The final request should detect and handle rate limiting
    response = initialized_client.call_tool("rate_limited_tool")
    
    # Validate rate limit handling
    content = response["result"]["content"]
    data = json.loads(content[0]["text"])
    
    assert "rate_limited" in data or "retry_after" in data
```

### STDIO Tool Chain Testing Pattern

```python
def test_tool_chain_in_stdio_mode(initialized_client):
    """Test a sequence of tool calls in STDIO mode."""
    # Step 1: Initialize or set up test data
    setup_response = initialized_client.call_tool("setup_test_data", {
        "test_id": "chain_test"
    })
    assert not setup_response["result"]["isError"]
    
    # Extract a value from the response for use in the next step
    setup_data = json.loads(setup_response["result"]["content"][0]["text"])
    test_resource_id = setup_data["resource_id"]
    
    # Step 2: Process the resource
    process_response = initialized_client.call_tool("process_resource", {
        "resource_id": test_resource_id,
        "action": "transform"
    })
    assert not process_response["result"]["isError"]
    
    # Extract results for verification
    process_data = json.loads(process_response["result"]["content"][0]["text"])
    assert process_data["status"] == "transformed"
    
    # Step 3: Verify the final state
    verify_response = initialized_client.call_tool("verify_resource_state", {
        "resource_id": test_resource_id,
        "expected_state": "transformed"
    })
    assert not verify_response["result"]["isError"]
    
    # Final verification
    verification = json.loads(verify_response["result"]["content"][0]["text"])
    assert verification["verified"] is True
```

## Examples

<example>
# STDIO Integration Test Example

```python
import json
import pytest
from my_project.tests.common import FastMCPClient

@pytest.fixture
def client():
    """Provide an initialized FastMCP client."""
    client = FastMCPClient(debug=True)
    client.start_server("my_package.server")
    client.initialize()
    yield client
    client.shutdown()

def test_get_stock_info(client):
    """Test getting stock information through STDIO mode."""
    # Call the tool to get stock information
    response = client.call_tool("get_stock_metric", {
        "symbol": "AAPL",
        "metric": "marketCap"
    })
    
    # Validate response structure
    assert "id" in response
    assert "jsonrpc" in response
    assert "result" in response
    assert "content" in response["result"]
    assert not response["result"]["isError"]
    
    # Validate content
    content = response["result"]["content"]
    assert len(content) > 0
    assert "text" in content[0]
    
    # Parse the text content as JSON
    data = json.loads(content[0]["text"])
    
    # Validate the data
    assert "symbol" in data
    assert data["symbol"] == "AAPL"
    assert "metric" in data
    assert data["metric"] == "marketCap"
    assert "value" in data
    assert isinstance(data["value"], (int, float))
    assert data["value"] > 0  # Market cap should be positive
```

# Tool Chain Integration Test Example

```python
def test_data_processing_workflow(client):
    """Test a complete data processing workflow."""
    # Step 1: Fetch historical data
    history_response = client.call_tool("get_historical_data", {
        "symbol": "MSFT",
        "period": "1mo"
    })
    assert not history_response["result"]["isError"]
    
    # Parse history data
    history_data = json.loads(history_response["result"]["content"][0]["text"])
    assert "symbol" in history_data
    assert "data" in history_data
    assert len(history_data["data"]) > 0
    
    # Step 2: Calculate a moving average
    ma_response = client.call_tool("calculate_moving_average", {
        "symbol": "MSFT",
        "period": "20d",
        "data_source": "cached"  # Use data we just cached
    })
    assert not ma_response["result"]["isError"]
    
    # Parse MA data
    ma_data = json.loads(ma_response["result"]["content"][0]["text"])
    assert "symbol" in ma_data
    assert "moving_average" in ma_data
    assert isinstance(ma_data["moving_average"], (int, float))
    
    # Step 3: Get recommendation based on MA
    rec_response = client.call_tool("get_recommendation", {
        "symbol": "MSFT",
        "metric": "moving_average",
        "current_value": ma_data["moving_average"]
    })
    assert not rec_response["result"]["isError"]
    
    # Validate recommendation
    rec_data = json.loads(rec_response["result"]["content"][0]["text"])
    assert "symbol" in rec_data
    assert "recommendation" in rec_data
    assert rec_data["recommendation"] in ["buy", "sell", "hold"]
```
</example>

<example type="invalid">
# Skipping STDIO Testing

```python
# Only testing HTTP mode and not STDIO mode
def test_http_only():
    """Test only HTTP mode, ignoring STDIO mode."""
    client = HttpClient("http://localhost:8000")
    response = client.get("/tools")
    assert response.status_code == 200
```

# Using Mocks Instead of Real Processes

```python
def test_with_mocks():
    """Using mocks defeats the purpose of integration testing."""
    with mock.patch("subprocess.Popen") as mock_popen:
        mock_process = mock.MagicMock()
        mock_process.stdout.readline.return_value = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"success": True}
        })
        mock_popen.return_value = mock_process
        
        client = FastMCPClient()
        client.start_server("my_package.server")
        # Rest of test with mocked responses
```

# Not Properly Shutting Down

```python
def test_without_cleanup():
    """Not properly cleaning up the subprocess."""
    client = FastMCPClient()
    client.start_server("my_package.server")
    client.initialize()
    
    response = client.list_tools()
    assert "result" in response
    
    # No shutdown, leaving process running
```

# Not Validating Response Structure

```python
def test_minimal_validation():
    """Only checking for success without validating structure."""
    client = FastMCPClient()
    client.start_server("my_package.server")
    client.initialize()
    
    response = client.call_tool("get_data")
    
    # Only checking basic success, not validating structure
    assert "result" in response
    assert not response["result"]["isError"]
    # Missing validation of content structure and data
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

### STDIO Mode Testing Rules
- Always use a reusable client class for STDIO communication
- Test with real subprocess for authentic behavior
- Always properly initialize and shutdown the server
- Validate the complete JSON-RPC response structure
- Test the full lifecycle: initialization, tool listing, tool calls, shutdown
- Include tests for error scenarios like invalid parameters and nonexistent tools
- Test tool chains that involve multiple sequential calls
- Prefer real external service calls over mocks when possible
- Validate response content structure and data correctness
- Ensure proper cleanup of subprocesses
- Include tests for common failure modes like timeouts and rate limiting
- Set up clear test fixtures for STDIO testing
- Include testing for both resources and tools
- Use proper debugging options for troubleshooting test failures
- Test all supported transport modes (HTTP and STDIO)

### External Client Integration Strategies
- Always implement proper error reporting with complete error details and suggested fixes
- Use type hints consistently throughout all code
- Verify all MCP servers work in both HTTP and STDIO modes
- Document all tools with clear descriptions and parameter information
- Provide integration guidance for external applications in documentation
- Include all modules in pyproject.toml to prevent import errors
- Prefer the official MCP client API for external Python integrations