# Changelog

## v2.0.0 (2023-09-18)

### Breaking Changes

- Removed legacy `server.py` implementation in favor of FastMCP
- Removed all direct imports from `server.py`
- Updated adapter to use FastMCP implementation only
- Changed import paths to remove `src.` prefix
- Deleted archived test files and legacy scripts
- Removed deprecated mermaid graph functionality stubs and tests
- Removed migration-related files and test scripts
- Removed `adapter.py` in favor of direct implementation in `__init__.py`
- MCP client configuration updated: references to `mcp_agile_flow.fastmcp_server` should be changed to `mcp_agile_flow`
- Updated Cursor MCP configuration in mcp.json to use `mcp_agile_flow` instead of `mcp_agile_flow.fastmcp_server`

### New Features

- Added version information and command-line version checking
- Improved error handling in the adapter
- Better synchronous and asynchronous support in the adapter
- Added `clean-archived` Makefile target for easy cleanup
- Simplified architecture by removing redundant adapter layer

### Fixes

- Updated tests to work with FastMCP implementation
- Fixed import paths in all modules
- Simplified server configuration
- Updated installation script to use new module path and remove deprecated tools
- Improved maintainability by following standard FastMCP patterns
- Renamed misleading test function to better reflect its purpose
- Fixed incompatible API usage in the CLI: replaced `server.start()` with `server.run()`
- Improved maintainability with consistent code style

### Other Changes

- Archived and then removed legacy test files
- Created backup system for archived files
- Updated documentation
- Simplified project structure
- Migrated memory graph functionality to a separate MCP server
- Refactored code to align with official FastMCP implementation examples
- Removed obsolete memory graph stub functions from fastmcp_tools.py
- Removed non-existent `get-safe-project-path` tool reference from supported tools list
- Removed redundant `fastmcp_server.py` file that duplicated functionality in `__main__.py`
- Refactored imports in `__init__.py` for better code organization and readability
- Documentation updates in README.md and docstrings
- Project structure simplification
- Removal of legacy files and redundant code
- Removed `adapter.py` and integrated functionality directly into `__init__.py`
- Removed redundant `fastmcp_server.py`
- Improved import structure in `__init__.py`
- Fixed asyncio deprecation warning in `call_tool_sync` function
- Updated Makefile test-core target to reference existing tests

## [Unreleased]

### Added
- Migration of `get-safe-project-path` functionality to `get-project-settings`
- Adapter test for `get-safe-project-path` as `test_archive_path_tests`
- Improved error handling in test adapter to support FastMCP migration

### Changed
- Updated README.md and README-FastMCP.md with latest migration status
- Enhanced test adapter to better handle differences between legacy and FastMCP implementations
- Fixed tests to properly support both implementations 

### Fixed
- Resolved issues with `migrate-mcp-config` parameter handling in adapter tests
- Improved test stability for FastMCP tool tests

## [0.1.0] - 2024-03-23

### Added
- Initial FastMCP migration for core tools
- Test adapter infrastructure
- Compatibility tests for both legacy and FastMCP implementations
- Documentation for migration process 