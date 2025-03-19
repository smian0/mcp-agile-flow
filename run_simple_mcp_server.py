#!/usr/bin/env python
"""
Run script for the MCP Agile Flow Simple Server

This script sets up logging and runs the simple MCP server.
"""
import os
import sys
import logging
from pathlib import Path

# Ensure the src directory is in the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    sys.path.insert(0, SRC_DIR)

# Create logs directory if it doesn't exist
USER_HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(USER_HOME, ".mcp-agile-flow")
LOG_FILE = os.path.join(LOG_DIR, "simple-mcp-server.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(stream=sys.stderr)
    ]
)

# Get the main logger
logger = logging.getLogger(__name__)

# Log some system info
logger.info(f"Starting Simple MCP server from {PROJECT_ROOT}")
logger.info(f"Logging to {LOG_FILE}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python path: {sys.path}")

# Import and run the server directly with modified approach
try:
    # Run the simple server directly instead of using the imported run function
    import asyncio
    import json
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.server import stdio
    
    # Import just the MCP server instance from simple_server
    from mcp_agile_flow.simple_server import mcp as simple_mcp
    
    logger.info("Successfully imported simple_server module")
    logger.info("Running server (stdin/stdout mode)...")
    
    # Define our own run function to avoid compatibility issues
    async def run_server():
        """Run the simple server directly."""
        async with stdio.stdio_server() as (read_stream, write_stream):
            await simple_mcp.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="MCP Agile Flow - Simple",
                    server_version="0.1.0",
                    capabilities=simple_mcp.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    
    # Run the server
    print("Starting MCP Agile Flow Simple server...", file=sys.stderr)
    asyncio.run(run_server())
    
except Exception as e:
    logger.error(f"Failed to run server: {e}", exc_info=True)
    sys.exit(1) 