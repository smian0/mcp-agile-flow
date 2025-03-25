"""
Main entry point for the MCP Agile Flow server.
This module runs the FastMCP server implementation.
"""
import sys
import logging
import argparse
from typing import Optional, Dict, Any
import json

from mcp.server import FastMCP
from .version import __version__
from .utils import detect_mcp_command


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
    
    # Create and run the server
    server = FastMCP(name="mcp_agile_flow")
    
    # Import all tools directly and register them with the server
    from .fastmcp_tools import (
        get_project_settings,
        initialize_ide,
        initialize_ide_rules,
        prime_context,
        migrate_mcp_config,
        think,
        get_thoughts,
        clear_thoughts,
        get_thought_stats
    )
    
    # Register tools with the server
    server.tool(name="get_project_settings")(get_project_settings)
    server.tool(name="initialize_ide")(initialize_ide)
    server.tool(name="initialize_ide_rules")(initialize_ide_rules)
    server.tool(name="prime_context")(prime_context)
    server.tool(name="migrate_mcp_config")(migrate_mcp_config)
    server.tool(name="think")(think)
    server.tool(name="get_thoughts")(get_thoughts)
    server.tool(name="clear_thoughts")(clear_thoughts)
    server.tool(name="get_thought_stats")(get_thought_stats)
    
    # Add special natural language command processing endpoint
    @server.tool(name="process_natural_language")
    def process_natural_language(query: str) -> str:
        """
        Process natural language command and route to appropriate tool.
        
        Args:
            query: The natural language query to process
            
        Returns:
            JSON string with the result of the processed command or error
        """
        # Detect command in the query
        tool_name, arguments = detect_mcp_command(query)
        
        if not tool_name:
            # No command detected
            response = {
                "success": False,
                "error": "No command detected in the query",
                "message": "Please try a more specific command or check documentation for supported commands"
            }
            return json.dumps(response, indent=2)
        
        # Call the appropriate tool
        try:
            if tool_name == "get_project_settings":
                result = get_project_settings(**(arguments or {}))
            elif tool_name == "initialize_ide":
                result = initialize_ide(**(arguments or {}))
            elif tool_name == "initialize_ide_rules":
                result = initialize_ide_rules(**(arguments or {}))
            elif tool_name == "prime_context":
                result = prime_context(**(arguments or {}))
            elif tool_name == "migrate_mcp_config":
                result = migrate_mcp_config(**(arguments or {}))
            elif tool_name == "think":
                result = think(**(arguments or {}))
            elif tool_name == "get_thoughts":
                result = get_thoughts()
            elif tool_name == "clear_thoughts":
                result = clear_thoughts()
            elif tool_name == "get_thought_stats":
                result = get_thought_stats()
            else:
                response = {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "message": "The detected command could not be routed to a known tool"
                }
                return json.dumps(response, indent=2)
            
            # Check if the result is already a JSON string
            try:
                # Try to parse as JSON to see if it's already a JSON string
                parsed_result = json.loads(result)
                # If it's already JSON, just return it
                return result
            except (json.JSONDecodeError, TypeError):
                # If it's not a JSON string, return it directly
                return result
                
        except Exception as e:
            # Handle any errors during processing
            response = {
                "success": False,
                "error": f"Error processing command: {str(e)}",
                "message": "An error occurred while processing your command"
            }
            return json.dumps(response, indent=2)
    
    try:
        server.run()
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
    parser.add_argument("--debug", action="store_true", help="Run in debug mode with verbose logging")
    parser.add_argument("--verbose", action="store_true", help="Enable logging output (less verbose than debug)")
    parser.add_argument("--version", "-v", action="store_true", help="Show version information and exit")
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
        # Run a command via FastMCP
        from mcp.server import FastMCP
        import asyncio
        import os
        
        # Set up environment
        os.environ["MCP_TOOL_DEBUG"] = "1" if args.debug else "0"
        
        # Create FastMCP instance
        server = FastMCP(name="mcp_agile_flow")
        
        # Run the server and exit with the returned code if any
        exit_code = main(debug=args.debug, quiet=not (args.debug or args.verbose), verbose=args.verbose)
        if exit_code is not None:
            sys.exit(exit_code)
