"""
Think Tool for MCP Agile Flow

This module implements a thinking tool that allows LLMs to work through complex problems
in a structured way, storing thoughts and allowing reflection on previous thinking.
"""

import json
import datetime
import os
import tempfile
import logging
import mmap
import threading
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

class ThoughtStorage:
    """Singleton class to store thoughts in memory with cross-process sharing."""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThoughtStorage, cls).__new__(cls)
            cls._instance._init_storage()
        return cls._instance
    
    def _init_storage(self):
        """Initialize the cross-process shared storage."""
        self._thoughts = []
        # Create a temporary file for this session only
        # This will be automatically deleted when the process exits
        self._temp_fd, self._temp_path = tempfile.mkstemp(prefix="mcp_thoughts_", suffix=".tmp")
        logger.debug(f"Initialized thought storage using temporary file: {self._temp_path}")
        # Write empty array to initialize the file
        os.write(self._temp_fd, json.dumps([]).encode('utf-8'))
    
    def _read_thoughts(self):
        """Read thoughts from the shared memory file."""
        try:
            with self._lock:
                # Seek to the beginning of the file
                os.lseek(self._temp_fd, 0, os.SEEK_SET)
                # Read the entire content
                content = os.read(self._temp_fd, os.path.getsize(self._temp_path))
                if content:
                    return json.loads(content.decode('utf-8'))
                return []
        except Exception as e:
            logger.error(f"Error reading thoughts: {e}")
            return []
    
    def _write_thoughts(self, thoughts):
        """Write thoughts to the shared memory file."""
        try:
            with self._lock:
                # Convert to JSON and encode to bytes
                content = json.dumps(thoughts).encode('utf-8')
                # Truncate the file
                os.ftruncate(self._temp_fd, 0)
                # Seek to the beginning
                os.lseek(self._temp_fd, 0, os.SEEK_SET)
                # Write the new content
                os.write(self._temp_fd, content)
        except Exception as e:
            logger.error(f"Error writing thoughts: {e}")
    
    def add_thought(self, thought: str) -> None:
        """Add a thought to storage with current timestamp."""
        thoughts = self._read_thoughts()
        thoughts.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "thought": thought
        })
        self._write_thoughts(thoughts)
    
    def get_thoughts(self) -> List[Dict[str, Any]]:
        """Get all thoughts."""
        return self._read_thoughts()
    
    def clear_thoughts(self) -> int:
        """Clear all thoughts and return count of cleared thoughts."""
        thoughts = self._read_thoughts()
        count = len(thoughts)
        self._write_thoughts([])
        return count
    
    def get_thought_count(self) -> int:
        """Get the number of thoughts."""
        return len(self._read_thoughts())
    
    def __del__(self):
        """Clean up when the instance is garbage collected."""
        try:
            os.close(self._temp_fd)
            # The temp file will be automatically deleted
        except (AttributeError, OSError):
            pass

# Create a single instance to be used throughout the module
_storage = ThoughtStorage()

def think(thought: str) -> str:
    """
    Record a thought for complex reasoning or step-by-step analysis.
    
    Provides Claude with a dedicated space for structured thinking during 
    complex problem-solving tasks.
    
    Args:
        thought: A thought to think about. This can be structured reasoning, 
                step-by-step analysis, policy verification, or any other 
                mental process that helps with problem-solving.
    
    Returns:
        JSON string containing success status and a confirmation message
    """
    # Log the thought with a timestamp
    _storage.add_thought(thought)
    
    # Return a confirmation
    response = {
        "success": True,
        "message": f"Thought recorded: {thought[:50]}..." if len(thought) > 50 else f"Thought recorded: {thought}"
    }
    
    return json.dumps(response)

def get_thoughts() -> str:
    """
    Retrieve all thoughts recorded in the current session.
    
    This tool helps review the thinking process that has occurred so far.
    
    Returns:
        JSON string containing success status and all recorded thoughts
    """
    thoughts = _storage.get_thoughts()
    
    if not thoughts:
        response = {
            "success": True,
            "message": "No thoughts have been recorded yet.",
            "thoughts": []
        }
    else:
        formatted_thoughts = []
        for i, entry in enumerate(thoughts, 1):
            formatted_thoughts.append({
                "index": i,
                "timestamp": entry["timestamp"],
                "thought": entry["thought"]
            })
        
        response = {
            "success": True,
            "message": f"Retrieved {len(formatted_thoughts)} thoughts.",
            "thoughts": formatted_thoughts
        }
    
    return json.dumps(response)

def clear_thoughts() -> str:
    """
    Clear all recorded thoughts from the current session.
    
    Use this to start fresh if the thinking process needs to be reset.
    
    Returns:
        JSON string containing success status and confirmation message
    """
    count = _storage.clear_thoughts()
    
    response = {
        "success": True,
        "message": f"Cleared {count} recorded thoughts."
    }
    
    return json.dumps(response)

def get_thought_stats() -> str:
    """
    Get statistics about the thoughts recorded in the current session.
    
    Returns:
        JSON string containing success status and thought statistics
    """
    thoughts = _storage.get_thoughts()
    
    if not thoughts:
        response = {
            "success": True,
            "message": "No thoughts have been recorded yet.",
            "stats": {
                "total_thoughts": 0,
                "average_length": 0,
                "longest_thought_index": None,
                "longest_thought_length": None
            }
        }
    else:
        total_thoughts = len(thoughts)
        avg_length = sum(len(entry["thought"]) for entry in thoughts) / total_thoughts
        
        # Find the longest thought and its index
        longest_length = 0
        longest_index = 0
        
        for i, entry in enumerate(thoughts):
            length = len(entry["thought"])
            if length > longest_length:
                longest_length = length
                longest_index = i
        
        stats = {
            "total_thoughts": total_thoughts,
            "average_length": round(avg_length, 2),
            "longest_thought_index": longest_index + 1,  # 1-indexed for user-facing index
            "longest_thought_length": longest_length
        }
        
        response = {
            "success": True,
            "message": f"Retrieved statistics for {total_thoughts} thoughts.",
            "stats": stats
        }
    
    return json.dumps(response) 