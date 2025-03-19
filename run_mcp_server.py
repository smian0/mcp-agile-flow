#!/usr/bin/env python
"""
MCP Server runner script.

This script runs the MCP Agile Flow server and can be executed from any location.
It ensures the proper Python path is set up so that modules can be found.

IMPORTANT: This uses the standard MCP protocol over stdin/stdout,
which is required for Cursor MCP integration.
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging to a file for debugging
log_dir = Path.home() / ".mcp-agile-flow"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "mcp-server.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

try:
    # Import and run the server
    logger.info(f"Starting MCP server from {project_root}")
    logger.info(f"Logging to {log_file}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python path: {sys.path}")
    
    from src.mcp_agile_flow.simple_server import run
    
    logger.info("Successfully imported server module")
    logger.info("Running server (stdin/stdout mode)...")
    
    if __name__ == "__main__":
        run()
except Exception as e:
    logger.exception(f"Error starting MCP server: {str(e)}")
    sys.exit(1) 