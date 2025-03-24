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

### Other Changes

- Archived and then removed legacy test files
- Created backup system for archived files
- Updated documentation
- Simplified project structure
- Migrated memory graph functionality to a separate MCP server
- Refactored code to align with official FastMCP implementation examples

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