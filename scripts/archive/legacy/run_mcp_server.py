#!/usr/bin/env python
"""
MCP Agile Flow Server Runner

This script runs the MCP Agile Flow server with enhanced functionality:
- Proper Python path setup for module discovery
- Comprehensive logging configuration
- Environment variable detection and validation
- Standard MCP protocol over stdin/stdout for IDE integration

Usage: python run_mcp_server.py
"""
import os
import sys
import logging
import asyncio
import json
from pathlib import Path
import argparse

# Ensure the src directory is in the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    sys.path.insert(0, SRC_DIR)

# Create logs directory if it doesn't exist
USER_HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(USER_HOME, ".mcp-agile-flow")
LOG_FILE = os.path.join(LOG_DIR, "mcp-server.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG level for more detailed logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(stream=sys.stderr)
    ]
)

# Get the main logger
logger = logging.getLogger(__name__)

# Log system information
logger.info(f"Starting MCP Agile Flow server from {PROJECT_ROOT}")
logger.info(f"Logging to {LOG_FILE}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"PROJECT_PATH: {os.environ.get('PROJECT_PATH')}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python path: {sys.path}")

# Import and run the server
try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.server import stdio
    
    # Import necessary components from server
    from mcp_agile_flow.server import mcp
    
    logger.info("Successfully imported server modules")
    logger.info("Running server (stdin/stdout mode)...")
    
    async def run_server():
        """Run the MCP Agile Flow server."""
        logger.info("Starting MCP Agile Flow server")
        print("Starting MCP Agile Flow server...", file=sys.stderr)
        
        async with stdio.stdio_server() as (read_stream, write_stream):
            await mcp.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="MCP Agile Flow",
                    server_version="0.1.0",
                    capabilities=mcp.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    
    # Run the server if this script is executed directly
    if __name__ == "__main__":
        print("Starting MCP Agile Flow server...", file=sys.stderr)
        asyncio.run(run_server())
    
except Exception as e:
    logger.error(f"Failed to run server: {e}", exc_info=True)
    sys.exit(1)