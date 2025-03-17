"""
MCP Agile Flow - A lightweight Python MCP server for Agile project lifecycle management.
"""

import os
import sys
from typing import Dict, Any

# Package version
__version__ = "0.1.0"

def main() -> None:
    """
    Main entry point for the MCP Agile Flow server when installed as a package.
    This is called by the console_script entry point.
    """
    # Add the current directory to the path so that the server.py
    # can be imported when running from the installed package
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(script_dir))
    
    # Import and run the server
    from server import main as server_main
    server_main()

if __name__ == "__main__":
    main()
