# Epic-7: Memory Graph Removal
# Story-3: Remove Memory Graph Tests

## Story

**As a** developer
**I want** to remove the memory graph tests and update the test suite
**so that** the test suite remains clean and focused after removing the memory graph functionality

## Status

Draft

## Context

After removing the core memory graph implementation and its server integration, we need to update the test suite to reflect these changes. This involves removing the dedicated memory graph tests and updating any other tests that might reference the memory graph functionality. This ensures that the test suite remains relevant and passes after the changes.

## Estimation

Story Points: 1

## Tasks

1. - [ ] Remove dedicated memory graph test files
   1. - [ ] Remove `test_memory_graph.py`
   2. - [ ] Archive a copy for reference if needed

2. - [ ] Update integration tests
   1. - [ ] Identify memory graph references in `test_integration.py`
   2. - [ ] Remove or modify tests that depend on memory graph

3. - [ ] Update mock server tests
   1. - [ ] Identify memory graph references in `test_json_validation.py`
   2. - [ ] Update the setup code to remove memory graph references
   3. - [ ] Remove memory graph-specific test cases

4. - [ ] Update API tests
   1. - [ ] Check `test_mcp_via_agno_agent.py` for memory graph usage
   2. - [ ] Remove or update relevant tests

5. - [ ] Update test utilities and fixtures
   1. - [ ] Check for memory graph-related fixtures
   2. - [ ] Update any helper functions that use memory graph

6. - [ ] Run the updated test suite
   1. - [ ] Verify all tests pass without memory graph
   2. - [ ] Fix any regressions caused by the removal

## Constraints

- Must maintain test coverage for remaining functionality
- May need to update test fixtures that previously relied on memory graph

## Dev Notes

Key test files to check:

1. `test_memory_graph.py` - This file will be removed entirely
2. `test_json_validation.py` - Contains setup code that uses the memory manager
3. `test_integration.py` - May include integration tests that use memory graph
4. `test_mcp_via_agno_agent.py` - May test memory graph tools via agent

The setup code in `test_json_validation.py` specifically creates a memory manager instance and attaches it to the simple server:

```python
def setup_memory_manager(self):
    # Create a temporary file for the knowledge graph
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        self.temp_file_path = tmp.name
    
    # Create a real KnowledgeGraphManager with the temporary file
    manager = memory_graph.KnowledgeGraphManager(self.temp_file_path)
    
    # Store the original memory_manager to restore later
    self.original_memory_manager = server.memory_manager
    
    # Set the memory_manager directly in the server module
    server.memory_manager = manager
```

This setup code will need to be removed or modified.

## Chat Command Log

- User: Create a new epic to remove the memory graph from the MCP server
- AI: Created Epic-7-memory-graph-removal with story-3 for removing tests 