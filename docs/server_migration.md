# Server Implementation to FastMCP Migration Plan

This document outlines the plan for transitioning from the legacy `server.py` implementation to the new FastMCP-based implementation.

## Background

The project currently has two parallel implementations of the MCP server:

1. **Legacy Server Implementation** (`server.py`): Uses the standard MCP protocol over stdin/stdout.
2. **FastMCP Implementation** (`fastmcp_server.py`): Uses the FastMCP API from the official MCP SDK.

Both implementations currently perform the same functions, but the FastMCP implementation is more modern, has better error handling, and is easier to maintain. The goal is to gradually transition to using only the FastMCP implementation.

## Migration Strategy

We will use an incremental approach to migrate the tests and code from the legacy server implementation to the FastMCP implementation:

1. **Phase 1: Build Compatibility Layer**
   - Create a test adapter that can switch between implementations
   - Add comparison tests to verify equivalent behavior
   - Ensure all FastMCP implementations match server behavior

2. **Phase 2: Migrate Tests**
   - Create a parallel set of tests using the adapter
   - Run tests against both implementations to verify equivalence
   - Gradually deprecate tests that directly import from `server.py`

3. **Phase 3: Update Dependencies**
   - Identify all imports of `server.py` across the codebase
   - Replace direct imports with adapter usage or FastMCP imports
   - Update scripts that directly run `server.py`

4. **Phase 4: Deprecate Legacy Server**
   - Once all tests pass with both implementations, mark `server.py` as deprecated
   - Add deprecation warnings to `server.py` functions
   - Update documentation to recommend FastMCP usage

5. **Phase 5: Remove Legacy Server**
   - Once all dependencies are updated, remove `server.py`
   - Keep a simplified adapter for backward compatibility

## Test Adapter

We've created a test adapter (`test_adapter.py`) that provides a consistent interface for calling tools using either implementation. The adapter determines which implementation to use based on the `MCP_USE_FASTMCP` environment variable.

### Using the Test Adapter

```python
from src.mcp_agile_flow.test_adapter import call_tool

# Call a tool (will use either implementation based on the environment variable)
result = await call_tool("initialize-ide", {"project_path": "/path/to/project"})
```

To switch between implementations, set the `MCP_USE_FASTMCP` environment variable:

```bash
# Use the FastMCP implementation
export MCP_USE_FASTMCP=true

# Use the legacy server implementation (default)
export MCP_USE_FASTMCP=false
```

## Migration Progress

| Tool | FastMCP Implementation | Tests Migrated | Notes |
|------|----------------------|----------------|-------|
| get-project-settings | ✅ | ✅ | Already implemented in FastMCP, tests migrated |
| initialize-ide | ✅ | ✅ | Already implemented in FastMCP, tests migrated |
| initialize-ide-rules | ✅ | ✅ | Already implemented in FastMCP, tests migrated |
| prime-context | ✅ | ⚠️ | Already implemented in FastMCP, tests not migrated |
| migrate-mcp-config | ✅ | ⚠️ | Already implemented in FastMCP, tests not migrated |

Note: All memory graph-related functionality (create-entities, create-relations, etc.) has been moved to a separate memory graph MCP server and is no longer part of this codebase.

## Next Steps

1. Run and validate the adapter-based tests
2. Migrate tests for prime-context and migrate-mcp-config
3. Update all dependencies on `server.py`
4. Run tests using the FastMCP implementation only
5. Add deprecation warning to `server.py`
6. Remove `server.py` once all dependencies are updated 