"""
Configuration handling for the Agile Flow MCP server.
"""

import os
import logging
from typing import Optional


class Config:
    """Configuration handler for the MCP Agile Flow server."""

    def __init__(self):
        """Initialize configuration with environment variables."""
        def is_valid_project_dir(path: str) -> bool:
            """Check if a directory is a valid project root."""
            if not os.path.isdir(path):
                return False
            # Look for common project files/directories that indicate a project root
            project_indicators = [
                ".git",           # Git repository
                "package.json",   # Node.js project
                "setup.py",       # Python project
                "pyproject.toml", # Modern Python project
                "Cargo.toml",     # Rust project
                "pom.xml",        # Maven project
                "build.gradle",   # Gradle project
                ".vscode",        # VSCode project settings
                ".idea",          # IntelliJ project
                "README.md",      # Project documentation
            ]
            return any(os.path.exists(os.path.join(path, indicator)) for indicator in project_indicators)

        # Try PROJECT_PATH from environment first
        project_path = os.environ.get("PROJECT_PATH")
        
        if project_path:
            if "${PROJECT_PATH}" in project_path or "#{PROJECT_PATH}" in project_path:
                project_path = None
                logging.warning("PROJECT_PATH contains placeholder, will try to detect project root")
            elif project_path == "/" or not project_path:
                project_path = None
                logging.warning("PROJECT_PATH is root or empty, will try to detect project root")
            elif not is_valid_project_dir(project_path):
                logging.warning(f"PROJECT_PATH {project_path} doesn't appear to be a valid project root")
                project_path = None

        # If PROJECT_PATH is not valid, try to detect project root
        if not project_path:
            # Start with current directory and walk up until we find a project root
            current_dir = os.getcwd()
            while current_dir != "/" and current_dir != "":
                if is_valid_project_dir(current_dir):
                    project_path = current_dir
                    logging.info(f"Found project root at: {project_path}")
                    break
                # Move up one directory
                parent = os.path.dirname(current_dir)
                if parent == current_dir:  # We've reached the root
                    break
                current_dir = parent
            
            if not project_path:
                # If we still haven't found a project root, use current directory
                project_path = os.getcwd()
                logging.warning(f"Could not find project root, defaulting to current directory: {project_path}")

        # Validate the project path
        if not os.path.isdir(project_path):
            err_msg = (
                "\nError: Invalid project directory"
                f"\nDirectory not found: {project_path}"
                "\n\nPlease either:"
                "\n1. Open this project in VSCode, or"
                "\n2. Add a valid PROJECT_PATH to your MCP configuration:"
                f'\n   "env": {{'
                f'\n     "PROJECT_PATH": "/path/to/valid/directory"'
                f"\n   }}"
            )
            logging.error(err_msg)
            raise ValueError(err_msg)

        self.project_path = project_path
        logging.info(f"Using directory: {self.project_path}")
        
        # Final safety check - if path is problematic, use home directory
        if self.project_path == "/" or not self.project_path:
            self.project_path = os.path.expanduser("~/mcp-agile-flow")
            logging.warning(f"Using fallback home directory: {self.project_path}")
            os.makedirs(self.project_path, exist_ok=True)
            
        # Debug mode - default to true during development
        self.debug = os.environ.get("DEBUG", "true").lower() == "true"
        
        # Log level based on debug mode
        self.log_level = logging.DEBUG
        
        # Agile documentation directory - always relative to project path
        self.agile_docs_dir = os.path.join(self.project_path, "agile-docs")
        
        # Log configuration
        logging.debug(f"Configuration initialized with project_path: {self.project_path}")
        logging.debug(f"Agile docs directory: {self.agile_docs_dir}")
        
    def get_project_path(self) -> str:
        """Get the configured project path."""
        return self.project_path
    
    def get_agile_docs_path(self) -> str:
        """Get the path to the agile-docs directory."""
        return self.agile_docs_dir
    
    def get_log_level(self) -> int:
        """Get the configured log level."""
        return self.log_level
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug
