# Epic-7: Memory Graph Removal
# Story-1: Remove Memory Graph Core Implementation

## Story

**As a** developer
**I want** to remove the core memory graph implementation
**so that** the MCP Agile Flow server is simplified and focused on its primary functionality

## Status

Completed

## Context

The memory graph functionality is currently integrated into the MCP Agile Flow server, but it has been decided to move this functionality to a separate MCP server. This story focuses on removing the core memory graph implementation, which is mainly contained in the `memory_graph.py` file. This includes the `Entity`, `Relation`, and `KnowledgeGraph` classes, as well as the `KnowledgeGraphManager` class.

## Estimation

Story Points: 1

## Tasks

1. - [x] Remove the `memory_graph.py` file
   1. - [x] Verify all imports and usage of this file to identify dependencies

2. - [x] Update package structure
   1. - [x] Remove references to memory graph in package imports and exports
   2. - [x] Update `__init__.py` if needed

3. - [x] Update build configuration
   1. - [x] Update `pyproject.toml` if needed
   2. - [x] Run linting to ensure no stray references

4. - [x] Verify removal
   1. - [x] Check that the package builds without errors
   2. - [x] Check for any residual artifacts

## Constraints

- Must not disrupt other core functionality when removing memory graph
- No backup needed as the code is already in git repository

## Dev Notes

The memory graph implementation is contained in `memory_graph.py` and includes:

- Data models: `Entity`, `Relation`, `KnowledgeGraph`
- Main class: `KnowledgeGraphManager` which handles all operations
- Registration function: `register_memory_tools` which registers tools with the MCP server

Since the file is stored in git, we don't need to create a separate backup.

## Chat Command Log

- User: Create a new epic to remove the memory graph from the MCP server
- AI: Created Epic-7-memory-graph-removal with first story for removing core implementation
- User: @story-1-remove-memory-graph-core.md No need to backup I already have that in the git repo
- AI: Updated story to remove backup step
- User: Implement removal of memory_graph.py
- AI: Removed memory_graph.py and all its references