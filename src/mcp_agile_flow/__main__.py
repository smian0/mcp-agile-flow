"""
Main entry point for the MCP Agile Flow server.
This module runs the FastMCP server implementation.
"""

import sys
import logging
import argparse
from typing import Optional

from .version import __version__

# Import all tools directly
from .fastmcp_tools import (
    mcp,
)

# SUPPORTED_TOOLS list for natural language processing
SUPPORTED_TOOLS = [
    "get_project_settings",
    "initialize_ide",
    "initialize_ide_rules",
    "prime_context",
    "migrate_mcp_config",
    "think",
    "get_thoughts",
    "clear_thoughts",
    "get_thought_stats",
]


def configure_logging(quiet: bool = True) -> None:
    """Configure logging for the MCP server.

    Args:
        quiet: Whether to disable all logging output
    """
    if quiet:
        # Disable all logging
        logging.disable(logging.CRITICAL)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(stream=sys.stderr)],
        )


def main(debug: bool = False, quiet: bool = True, verbose: bool = False) -> Optional[int]:
    """
    Run the MCP Agile Flow server using FastMCP implementation.

    Args:
        debug: Whether to run in debug mode with verbose logging
        quiet: Whether to disable all logging output
        verbose: Whether to enable normal (INFO) logging

    Returns:
        Exit code or None if successful
    """
    # Configure logging
    if debug:
        # Enable debug logging
        configure_logging(quiet=False)
        logging.getLogger().setLevel(logging.DEBUG)
        # Allow MCP's internal logging in debug mode
        logging.getLogger("mcp").setLevel(logging.DEBUG)
    elif verbose:
        # Enable normal logging
        configure_logging(quiet=False)
        # Set MCP's internal logging to INFO level
        logging.getLogger("mcp").setLevel(logging.INFO)
    else:
        # Disable all logging by default
        configure_logging(quiet=True)
        # Disable MCP's internal logging
        logging.getLogger("mcp").setLevel(logging.CRITICAL)

    # All tools are registered via decorators in fastmcp_tools.py
    # Use the server instance created there

    try:
        # Run the server
        mcp.run()
        return None
    except KeyboardInterrupt:
        if not quiet:
            logging.info("Server stopped by user")
        return 0
    except Exception as e:
        if not quiet:
            logging.error(f"Server error: {str(e)}")
        return 1


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MCP Agile Flow Server")
    parser.add_argument(
        "--debug", action="store_true", help="Run in debug mode with verbose logging"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable logging output (less verbose than debug)"
    )
    parser.add_argument(
        "--version", "-v", action="store_true", help="Show version information and exit"
    )
    parser.add_argument("--server", action="store_true", help="Run as server")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Check if version flag is provided
    if args.version:
        print(f"MCP Agile Flow v{__version__}")
        sys.exit(0)

    if args.server:
        # Run as server
        from .server import start_server

        start_server()
    else:
        # Run the server and exit with the returned code if any
        exit_code = main(
            debug=args.debug, quiet=not (args.debug or args.verbose), verbose=args.verbose
        )
        if exit_code is not None:
            sys.exit(exit_code)
