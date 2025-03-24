"""
Think Tool for MCP Agile Flow

This module implements a thinking tool that allows LLMs to work through complex problems
in a structured way, storing thoughts and allowing reflection on previous thinking.
"""

import json
import datetime
from typing import Optional, Dict, List, Any

class ThoughtStorage:
    """Singleton class to store thoughts."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThoughtStorage, cls).__new__(cls)
            cls._instance._thoughts = []
        return cls._instance
    
    def add_thought(self, thought: str) -> None:
        """Add a thought to storage with current timestamp."""
        self._thoughts.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "thought": thought
        })
    
    def get_thoughts(self) -> List[Dict[str, Any]]:
        """Get all thoughts."""
        return self._thoughts
    
    def clear_thoughts(self) -> int:
        """Clear all thoughts and return count of cleared thoughts."""
        count = len(self._thoughts)
        self._thoughts = []
        return count
    
    def get_thought_count(self) -> int:
        """Get the number of thoughts."""
        return len(self._thoughts)

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