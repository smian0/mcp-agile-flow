# Epic-5: MCP Configuration Migration Tool
# Story-1: Implement MCP Configuration Migration Tool Call

## Story

**As a** developer using multiple IDEs
**I want** to use a tool call to migrate my MCP configuration files between different IDEs
**so that** I can maintain consistent AI tools across development environments

## Status

✅ Completed

## Context

Previously, MCP configurations were IDE-specific and stored in different locations for each IDE. The implemented tool call now enables seamless migration of configurations between IDEs, with smart merging of existing configurations and user-guided conflict resolution.

## Estimation

Story Points: 3
Implementation Time Estimates:
- Human Development: 3 days
- AI-Assisted Development: ~30 minutes
  - Core Migration Tool: ~20 minutes
  - Integration Tests: ~10 minutes

## Tasks

1. - [x] Implement Core Migration Tool
   1. - [x] Create migrate-mcp-config tool call with parameters:
      ```python
      {
        "from_ide": {"type": "string", "enum": ["cursor", "windsurf", "windsurf-next", "cline", "roo"]},
        "to_ide": {"type": "string", "enum": ["cursor", "windsurf", "windsurf-next", "cline", "roo"]},
        "backup": {"type": "boolean", "default": true}
      }
      ```
   2. - [x] Implement IDE path resolution for known config locations:
      - Cursor: `~/.cursor/mcp.json`
      - Windsurf Next: `~/.codeium/windsurf-next/mcp_config.json`
      - Windsurf: `~/.codeium/windsurf/mcp_config.json`
      - Cline: `~/Library/Application Support/Code - Insiders/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
      - Roo: `~/Library/Application Support/Code - Insiders/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`
   3. - [x] Add environment variable override support (e.g., `MCP_CURSOR_PATH`)
   4. - [x] Implement smart JSON merging with conflict detection
   5. - [x] Add user prompting for conflict resolution

2. - [x] Implement Integration Tests
   1. - [x] Create test fixtures with sample MCP configurations
   2. - [x] Test basic migration between IDEs
   3. - [x] Test conflict detection and resolution
   4. - [x] Test environment variable overrides
   5. - [x] Verify backup creation
   6. - [x] Add integration test class:
   ```python
   def test_mcp_migration_tool():
       """Test the MCP migration tool functionality."""
       # Set up test data
       test_configs = create_test_configurations()

       # Test migration with no conflicts
       result = handle_call_tool("migrate-mcp-config", {
           "from_ide": "cursor",
           "to_ide": "windsurf"
       })
       assert result.success == True

       # Test migration with conflicts
       result = handle_call_tool("migrate-mcp-config", {
           "from_ide": "cursor",
           "to_ide": "cline"
       })
       assert "conflicts_detected" in result
       assert result.user_action_required == True
   ```

## Implementation Details

The MCP migration functionality has been fully implemented and includes:

- Support for all major IDEs (Cursor, Windsurf, Cline, Roo)
- Smart JSON merging with conflict detection and resolution
- Automatic creation of backups before modifications
- Environment variable overrides for custom configuration paths
- Comprehensive test suite verifying all functionality

All tests for this feature are now passing, indicating full functionality. The implementation follows the design constraints and provides a robust solution for cross-IDE configuration management.

## Structure
```
src/mcp_server/tools/
  └── migration_tool.py    # Tool implementation & IDE paths
tests/
  └── test_mcp_config_migration.py    # Integration tests
```

## Constraints

- Must maintain backward compatibility with existing MCP configuration format
- Must provide error messages that clearly indicate any issues
- Must be cross-platform compatible (Windows, macOS, Linux)
- Must never overwrite conflicting MCP server configurations without user approval
- Must create backups before modifying configurations

## Dev Notes

- Used existing MCP server tool call structure
- Smart merging preserves both configurations where possible
- User must approve overwriting of conflicting MCP server entries
- Creates backups before modifying any existing configurations
- Cross-platform support for different IDE config paths
- Follows existing testing patterns from test_integration.py

## Chat Command Log

- User: I'd like to create a new story that allows me to migrate over MCP JSON files from one IDE to another
- Assistant: Creating a story for the MCP migration functionality
- User: This is purely another tool call in this same mcp server so modify the requirements to reflect that
- Assistant: Updating the story to reflect implementation as a tool call within the MCP server
- User: If you already find an existing MCP server JSON, your requirements will be to do a smart merging of your existing IDE's MCP JSON, and then merge it into the other JSON. If there is any conflict, just let the user know how to resolve the conflict whether the same MCP server should be overwritten or not. Make sure that the user is involved whenever there's a conflict in the MCP server JSON that you're writing to.
- Assistant: Adding smart merging and conflict resolution requirements to the story
