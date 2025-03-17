"""
File storage management for Agile Flow documentation.
"""

import os
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

from ..utils.logger import setup_logger

logger = setup_logger("agile_flow.storage")


class FileManager:
    """
    Manages file operations for the agile-docs directory.
    """
    
    def __init__(self, agile_docs_path: str):
        """
        Initialize the FileManager with the path to the agile-docs directory.
        
        Args:
            agile_docs_path: Path to the agile-docs directory.
        """
        # Safety check for root-level paths
        if agile_docs_path == '/agile-docs' or agile_docs_path == '/':
            # This is a dangerous path at the filesystem root, redirect to home directory
            home_dir = os.path.expanduser("~")
            self.agile_docs_path = os.path.join(home_dir, "agile-docs")
            logger.warning(f"Detected root-level path: {agile_docs_path}. Redirecting to: {self.agile_docs_path}")
        else:
            self.agile_docs_path = agile_docs_path
        
        # Additional sanity check
        if self.agile_docs_path.startswith('/') and self.agile_docs_path.count('/') == 1:
            # This is a direct child of root (e.g., '/some-dir'), which is likely a mistake
            home_dir = os.path.expanduser("~")
            old_path = self.agile_docs_path
            self.agile_docs_path = os.path.join(home_dir, self.agile_docs_path.lstrip('/'))
            logger.warning(f"Detected root child path: {old_path}. Redirecting to: {self.agile_docs_path}")
        
    def ensure_directory_structure(self) -> None:
        """
        Create the agile-docs directory structure if it doesn't exist.
        """
        try:
            # Create main agile-docs directory
            os.makedirs(self.agile_docs_path, exist_ok=True)
            
            # Create subdirectories
            os.makedirs(os.path.join(self.agile_docs_path, "epics"), exist_ok=True)
            os.makedirs(os.path.join(self.agile_docs_path, "stories"), exist_ok=True)
            os.makedirs(os.path.join(self.agile_docs_path, "tasks"), exist_ok=True)
            
            logger.debug(f"Ensured directory structure at {self.agile_docs_path}")
        except PermissionError as e:
            logger.error(f"Permission error creating directories: {e}")
            # Try to create in a user-writable location instead
            home_dir = os.path.expanduser("~")
            new_agile_docs_path = os.path.join(home_dir, "agile-docs")
            logger.warning(f"Falling back to home directory: {new_agile_docs_path}")
            
            # Update the path
            self.agile_docs_path = new_agile_docs_path
            
            # Try again with the new path
            os.makedirs(self.agile_docs_path, exist_ok=True)
            os.makedirs(os.path.join(self.agile_docs_path, "epics"), exist_ok=True)
            os.makedirs(os.path.join(self.agile_docs_path, "stories"), exist_ok=True)
            os.makedirs(os.path.join(self.agile_docs_path, "tasks"), exist_ok=True)
            
            logger.info(f"Created directory structure at fallback location: {self.agile_docs_path}")
        
    def write_markdown(self, path: str, content: str) -> None:
        """
        Write content to a markdown file within the agile-docs directory.
        
        Args:
            path: Relative path to the file (within agile-docs).
            content: Content to write to the file.
        """
        full_path = os.path.join(self.agile_docs_path, path)
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write content to file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        logger.debug(f"Wrote content to {full_path}")
        
    def read_markdown(self, path: str) -> str:
        """
        Read content from a markdown file within the agile-docs directory.
        
        Args:
            path: Relative path to the file (within agile-docs).
            
        Returns:
            Content of the file as a string.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        full_path = os.path.join(self.agile_docs_path, path)
        
        if not os.path.exists(full_path):
            logger.error(f"File not found: {full_path}")
            raise FileNotFoundError(f"File not found: {path}")
        
        # Read content from file
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        logger.debug(f"Read content from {full_path}")
        return content
        
    def list_files(self, directory: str) -> List[str]:
        """
        List markdown files in a subdirectory of agile-docs.
        
        Args:
            directory: Relative path to the directory (within agile-docs).
            
        Returns:
            List of filenames (without paths).
        """
        full_path = os.path.join(self.agile_docs_path, directory)
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            logger.warning(f"Directory not found: {full_path}")
            return []
        
        # List files in directory
        files = [f for f in os.listdir(full_path) if f.endswith(".md")]
        logger.debug(f"Listed {len(files)} files in {full_path}")
        return files
        
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists within the agile-docs directory.
        
        Args:
            path: Relative path to the file (within agile-docs).
            
        Returns:
            True if the file exists, False otherwise.
        """
        full_path = os.path.join(self.agile_docs_path, path)
        return os.path.exists(full_path) and os.path.isfile(full_path)
        
    def get_markdown_metadata(self, content: str) -> Dict[str, str]:
        """
        Extract metadata from markdown content.
        
        Args:
            content: Markdown content.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        metadata = {}
        
        # Extract metadata from lines like "- Key: Value"
        for line in content.split('\n'):
            match = re.match(r'^\s*-\s+([^:]+):\s+(.+)$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                metadata[key] = value
                
        return metadata
        
    def get_title_from_markdown(self, content: str) -> Optional[str]:
        """
        Extract the title (first heading) from markdown content.
        
        Args:
            content: Markdown content.
            
        Returns:
            The title (without the heading marker) or None if not found.
        """
        # Look for the first heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
