# MCP Agile Flow Server Migration

## Status: Migration Complete

The migration from `server.py` to `FastMCP` implementation is now complete. The `server.py` module has been removed, and all functionality is now available through the adapter interface that uses the FastMCP implementation.

## Architecture

The MCP Agile Flow server architecture has been simplified:

1. The `adapter.py` module now serves as the main interface to the FastMCP implementation.
2. The `fastmcp_tools.py` module provides all the tool implementations.
3. The `adapter.py` module exposes both synchronous and asynchronous interfaces for compatibility.

## Usage

All clients should use the `adapter.py` interface:

```python
from mcp_agile_flow.adapter import call_tool, call_tool_sync

# Asynchronous usage
result = await call_tool("get-project-settings", {})

# Synchronous usage
result = call_tool_sync("get-project-settings", {})
```

## Tests

We've updated all tests to use the adapter interface. Legacy test files that depended on the server.py implementation have been moved to the `tests/archive/legacy/` directory.

## Future Development

Future development should focus on enhancing the FastMCP implementation with additional features and improvements, while maintaining the simple adapter interface for backward compatibility.

## Legacy modules

The following legacy modules have been archived and are no longer maintained:

1. `server.py` - Removed in favor of FastMCP implementation
2. `scripts/check_tools.py` - Legacy server utility
3. `scripts/run_mcp_server.py` - Legacy server runner
4. Several test files that directly imported the server module 