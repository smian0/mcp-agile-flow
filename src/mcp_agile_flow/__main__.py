"""
Main entry point for running the MCP Agile Flow server.

This file allows the server to be executed using:
    python -m src.mcp_agile_flow
"""

import os
import warnings

# Check if we should use the legacy server implementation
USE_LEGACY = os.environ.get("MCP_USE_LEGACY", "false").lower() in ("true", "1", "yes")

if USE_LEGACY:
    # Show deprecation warning
    warnings.warn(
        "Using the legacy server implementation which is deprecated and will be removed in a future version. "
        "Please migrate to the FastMCP implementation by removing the MCP_USE_LEGACY environment variable.",
        DeprecationWarning,
        stacklevel=2
    )
    # Import and run the legacy server
    from .server import run
else:
    # Import and run the FastMCP server (default)
    from .fastmcp_server import run

if __name__ == "__main__":
    run()
