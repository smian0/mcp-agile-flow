# Epic-7: Memory Graph Removal
# Story-2: Remove Memory Graph Integration with Simple Server

## Story

**As a** developer
**I want** to remove all memory graph integration from the simple server
**so that** the server can run independently without any memory graph dependencies

## Status

Completed

## Context

After removing the core memory graph implementation in Story-1, we need to remove all integration points with the simple server. The memory graph functionality is currently integrated with the server in `server.py` and `run_mcp_server.py`. This includes tool registration, initialization, and handling of memory graph-related tool calls.

## Estimation

Story Points: 2

## Tasks

1. - [x] Update `server.py`
   1. - [x] Remove memory graph import statements
   2. - [x] Remove memory graph tool registration
   3. - [x] Remove memory graph tool handlers
   4. - [x] Remove memory graph global variables
   5. - [x] Clean up memory graph initialization in `run_server()`

2. - [x] Update `run_mcp_server.py`
   1. - [x] Remove memory graph import statements
   2. - [x] Remove memory graph initialization code
   3. - [x] Clean up any memory graph-related error handling

3. - [x] Remove memory graph tools from the tools list
   1. - [x] Remove memory graph tools from `handle_list_tools()`
   2. - [x] Remove memory graph tool handlers from `handle_call_tool()`

4. - [x] Update or remove any helper files related to memory graph
   1. - [x] Check `check_tools.py` for memory graph references
   2. - [x] Remove or update any other helper scripts

5. - [x] Test server startup and functionality
   1. - [x] Verify server starts without errors
   2. - [x] Verify non-memory-graph tools still work

## Constraints

- Must ensure that all other server functionality continues to work
- Must remove all references to memory graph to avoid runtime errors
- Should maintain backward compatibility with tools API where possible

## Dev Notes

Key integration points to remove:

1. In `server.py`:
   - Import statements: `from .memory_graph import register_memory_tools, KnowledgeGraphManager`
   - Global variables: `memory_tools = []` and `memory_manager = None`
   - Tool registration in `handle_list_tools()`
   - Tool handlers in `handle_call_tool()`
   - Memory graph initialization in `run_server()`

2. In `run_mcp_server.py`:
   - Import statements related to memory graph
   - Memory graph initialization in `run_server()`

After removal, ensure that the server starts correctly and other tools function as expected.

## Chat Command Log

- User: Create a new epic to remove the memory graph from the MCP server
- AI: Created Epic-7-memory-graph-removal with story-2 for removing server integration
- User: Remove memory graph from server integration
- AI: Removed memory graph integration from server files