"""
Main entry point for the MCP Agile Flow server.
This module runs the FastMCP server implementation.
"""
import sys
import logging
from typing import Optional

from fastmcp.server import FastMCP
from .version import __version__


def configure_logging() -> None:
    """Configure logging for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(stream=sys.stderr)],
    )


def main(debug: bool = False) -> Optional[int]:
    """
    Run the MCP Agile Flow server using FastMCP implementation.
    
    Args:
        debug: Whether to run in debug mode with verbose logging
    
    Returns:
        Exit code or None if successful
    """
    # Check if version flag is provided
    if "--version" in sys.argv or "-v" in sys.argv:
        print(f"MCP Agile Flow v{__version__}")
        return 0
        
    # Configure logging
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        configure_logging()
    
    # Create and run the server
    server = FastMCP(name="mcp-agile-flow")
    
    # Import all tools directly and register them with the server
    from .fastmcp_tools import (
        get_project_settings,
        initialize_ide,
        initialize_ide_rules,
        prime_context,
        migrate_mcp_config
    )
    
    # Register tools with the server
    server.tool(name="get-project-settings")(get_project_settings)
    server.tool(name="initialize-ide")(initialize_ide)
    server.tool(name="initialize-ide-rules")(initialize_ide_rules)
    server.tool(name="prime-context")(prime_context)
    server.tool(name="migrate-mcp-config")(migrate_mcp_config)
    
    try:
        server.run()
        return None
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        return 0
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        return 1


if __name__ == "__main__":
    # Set debug mode if --debug flag is provided
    debug_mode = "--debug" in sys.argv
    
    # Run the server and exit with the returned code if any
    exit_code = main(debug=debug_mode)
    if exit_code is not None:
        sys.exit(exit_code)
