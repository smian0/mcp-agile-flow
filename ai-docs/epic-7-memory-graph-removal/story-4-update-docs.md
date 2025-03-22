# Epic-7: Memory Graph Removal
# Story-4: Update Documentation to Reflect Memory Graph Removal

## Story

**As a** developer
**I want** to update all documentation to reflect the removal of the memory graph
**so that** the documentation accurately represents the current state of the application

## Status

Draft

## Context

After completely removing the memory graph functionality from the codebase, we need to update all documentation to reflect these changes. This includes the BRD, PRD, and Architecture documentation, which contain references to the memory graph functionality. The updates should clearly document that the memory graph functionality has been removed and will be available as a separate MCP server.

## Estimation

Story Points: 1

## Tasks

1. - [ ] Update Architecture documentation (arch.md)
   1. - [ ] Remove memory graph from component descriptions
   2. - [ ] Update architectural diagrams
   3. - [ ] Remove memory graph class models
   4. - [ ] Update implementation status section
   5. - [ ] Add note about memory graph being moved to separate MCP server

2. - [ ] Update Product Requirements Document (prd.md)
   1. - [ ] Update functional requirements to remove memory graph references
   2. - [ ] Update implementation status of affected components
   3. - [ ] Update planned future epics section
   4. - [ ] Add entry to changelog documenting the removal

3. - [ ] Update Business Requirements Document (brd.md) if needed
   1. - [ ] Check for memory graph references
   2. - [ ] Update if necessary

4. - [ ] Update READMEs and other documentation
   1. - [ ] Check main README.md for memory graph references
   2. - [ ] Update any developer guides or contribution guides

5. - [ ] Add new documentation for future memory graph MCP server
   1. - [ ] Create a basic README template for the future memory graph MCP server
   2. - [ ] Document migration path for those using memory graph functionality

## Constraints

- Documentation should clearly explain that memory graph removal is intentional
- Should provide guidance on how to access memory graph functionality in the future

## Dev Notes

Key documentation locations:

1. `ai-docs/arch.md`:
   - Contains detailed descriptions of the memory graph components
   - Includes class diagrams and architectural diagrams
   - Lists memory graph in the technology table

2. `ai-docs/prd.md`:
   - Includes memory graph as a functional requirement
   - Shows implementation status of memory graph features

Both documents need to be updated to reflect the removal of memory graph functionality, with notes indicating that this functionality will be available in a separate MCP server in the future.

## Chat Command Log

- User: Create a new epic to remove the memory graph from the MCP server
- AI: Created Epic-7-memory-graph-removal with story-4 for updating documentation 