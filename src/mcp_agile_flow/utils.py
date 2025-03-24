"""
Utility functions for MCP Agile Flow.
"""

import os
from typing import Any, Dict, Tuple, Optional
import re


def get_project_settings(proposed_path: str = None) -> Dict[str, Any]:
    """
    Get project settings including project path and AI docs directory.

    This is a common utility function used by various components to ensure consistent
    project path handling throughout the application.

    Args:
        proposed_path: Optional explicit path to use. If provided, this takes precedence
                       over environment variables. Useful when a specific path needs to be
                       validated and used.

    Returns:
        Dict with the following keys:
            - project_path: The project path (defaults to user's home directory if not set)
            - current_directory: The current working directory
            - is_project_path_manually_set: Whether PROJECT_PATH was set manually
            - ai_docs_directory: Path to the AI docs directory
            - source: Information about where the project path was derived from
            - is_root: Whether the path is the root directory (important for safety checks)
            - is_writable: Whether the path is writable
            - exists: Whether the path exists
    """
    import logging

    logger = logging.getLogger(__name__)

    # Always get the current directory first
    current_directory = os.getcwd()
    logger.info(f"Current working directory: {current_directory}")

    # Get the user's home directory as the default path
    home_directory = os.path.expanduser("~")
    logger.info(f"User's home directory: {home_directory}")

    # Get the environment variable for project path
    project_path_env = os.environ.get("PROJECT_PATH")

    logger.info(f"PROJECT_PATH environment variable: {project_path_env}")

    # Determine if the project path was manually set
    is_manually_set = False
    project_path = None
    source = "unknown"

    # First check if a proposed path was provided
    if proposed_path is not None and proposed_path.strip() != "":
        raw_path = proposed_path.strip()
        # If using relative path notation like "." or "./", convert to absolute
        if raw_path == "." or raw_path == "./":
            project_path = os.getcwd()
            source = "current directory (from relative path)"
        else:
            project_path = os.path.abspath(raw_path)
            source = "proposed path parameter"
        is_manually_set = True
    # Check PROJECT_PATH
    elif project_path_env is not None and project_path_env.strip() != "":
        project_path = project_path_env
        source = "PROJECT_PATH environment variable"
        is_manually_set = True
    # Default to current directory if not set
    else:
        project_path = current_directory
        source = "current working directory (default)"
        logger.info(f"Using current working directory as project_path: {project_path}")

    # Ensure project_path is an absolute path
    if not os.path.isabs(project_path):
        old_path = project_path
        project_path = os.path.abspath(project_path)
        logger.info(
            f"Converted relative path '{old_path}' to absolute path '{project_path}'"
        )

    # Check if the path is root directory
    is_root = project_path == "/" or project_path == "\\"

    # Safety check - if project_path is root, use current directory instead
    # (unless current directory is also root, then use home directory)
    if is_root:
        if current_directory == "/":
            logger.warning(
                "Root path specified and current directory is also root. Using home directory instead."
            )
            project_path = home_directory
            source = "home directory (safety fallback from root)"
            is_root = False
        else:
            logger.warning(
                f"Root path specified. Using current directory for safety: {current_directory}"
            )
            project_path = current_directory
            source = "current directory (safety fallback from root)"
            is_root = False

    # Check if the path exists
    exists = os.path.exists(project_path)

    # Check if the path is writable
    is_writable = exists and os.access(project_path, os.W_OK)

    # For non-existent paths, fall back to current directory (unless current dir is root)
    if not exists:
        if current_directory == "/":
            logger.warning(
                f"Path doesn't exist: {project_path} and current directory is root. Using home directory."
            )
            project_path = home_directory
            source = "home directory (fallback from non-existent path)"
        else:
            logger.warning(
                f"Path doesn't exist: {project_path}. Using current directory: {current_directory}"
            )
            project_path = current_directory
            source = "current directory (fallback from non-existent path)"
        exists = os.path.exists(project_path)
        is_writable = exists and os.access(project_path, os.W_OK)

    # For non-writable paths, fall back to current directory or home directory
    if not is_writable:
        if current_directory == "/":
            logger.warning(
                f"Path not writable: {project_path} and current directory is root. Using home directory."
            )
            project_path = home_directory
            source = "home directory (fallback from non-writable path)"
        else:
            logger.warning(
                f"Path not writable: {project_path}. Using current directory: {current_directory}"
            )
            project_path = current_directory
            source = "current directory (fallback from non-writable path)"
        exists = os.path.exists(project_path)
        is_writable = exists and os.access(project_path, os.W_OK)

    # Get AI docs directory
    _, ai_docs_dir = get_special_directories(project_path)
    logger.info(f"AI docs directory: {ai_docs_dir}")

    result = {
        "project_path": project_path,
        "current_directory": current_directory,
        "is_project_path_manually_set": is_manually_set,
        "ai_docs_directory": ai_docs_dir,
        "source": source,
        "is_root": is_root,
        "is_writable": is_writable,
        "exists": exists,
    }
    logger.info(f"Returning project settings: {result}")
    return result


def get_special_directories(project_path: str) -> Tuple[str, str]:
    """
    Get the AI docs directory for a given project path.
    If the directory doesn't exist, it will be created.

    Args:
        project_path: The project path to find special directories for

    Returns:
        Tuple of (knowledge_graph_directory, ai_docs_directory) - first item is kept for backward compatibility
    """
    import logging

    logger = logging.getLogger(__name__)

    # For backward compatibility, we'll return a dummy value as the first item
    # But we won't actually create the knowledge graph directory
    knowledge_graph_dir = ""

    # Define AI docs directory (primarily ai-docs, with fallbacks)
    ai_docs_dir = os.path.join(project_path, "ai-docs")
    if not os.path.exists(ai_docs_dir):
        # Check fallback directories
        found_fallback = False
        for fallback in [".ai", ".docs", "docs"]:
            fallback_dir = os.path.join(project_path, fallback)
            if os.path.exists(fallback_dir):
                ai_docs_dir = fallback_dir
                found_fallback = True
                logger.info(f"Using existing AI docs directory: {ai_docs_dir}")
                break

        # No fallback found - create the default directory
        if not found_fallback:
            ai_docs_dir = os.path.join(project_path, "ai-docs")
            try:
                os.makedirs(ai_docs_dir, exist_ok=True)
                logger.info(f"Created AI docs directory: {ai_docs_dir}")
            except Exception as e:
                logger.warning(f"Failed to create AI docs directory: {e}")
    else:
        logger.info(f"Using existing AI docs directory: {ai_docs_dir}")

    return knowledge_graph_dir, ai_docs_dir


def detect_mcp_command(text: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Detects MCP commands from natural language text.
    
    Maps various ways users might phrase commands to the appropriate MCP tool.
    
    Args:
        text: The natural language text to analyze
        
    Returns:
        Tuple of (tool_name, arguments) or (None, None) if no command is detected
    """
    # Normalize text for consistent matching
    normalized_text = text.lower().strip()
    
    # Define valid IDE names and aliases
    valid_ides = {
        "cursor", "windsurf-next", "windsurf", "cline", "roo", "claude-desktop"
    }
    
    # Define IDE aliases
    ide_aliases = {
        "claude": "claude-desktop",  # Map "claude" to "claude-desktop"
        "copilot": "cursor",  # For backward compatibility
    }
    
    def validate_ide(ide):
        """Validate IDE name and map to correct name if needed."""
        if ide in valid_ides:
            return ide
        if ide in ide_aliases:
            return ide_aliases[ide]
        return ide  # Return as is, will be caught by migration tool
    
    # Migration command patterns
    migration_patterns = [
        r'migrate\s+(?:mcp\s+)?config(?:\s+from\s+(\w+(?:-\w+)?))?\s+to\s+(\w+(?:-\w+)?)',
        r'(?:copy|transfer|move)\s+(?:mcp\s+)?config(?:\s+from\s+(\w+(?:-\w+)?))?\s+to\s+(\w+(?:-\w+)?)',
        r'migrate\s+(?:mcp\s+)?settings(?:\s+from\s+(\w+(?:-\w+)?))?\s+to\s+(\w+(?:-\w+)?)',
        r'(?:copy|transfer|move)\s+(?:mcp\s+)?settings(?:\s+from\s+(\w+(?:-\w+)?))?\s+to\s+(\w+(?:-\w+)?)',
    ]
    
    for pattern in migration_patterns:
        match = re.search(pattern, normalized_text)
        if match:
            from_ide = match.group(1) if match.group(1) else 'cursor'
            to_ide = match.group(2)
            
            # Validate and correct IDE names
            from_ide = validate_ide(from_ide)
            to_ide = validate_ide(to_ide)
            
            return "migrate-mcp-config", {"from_ide": from_ide, "to_ide": to_ide}
    
    # Initialize IDE patterns
    init_patterns = [
        r'initialize\s+(?:ide|rules)\s+(?:for\s+)?(\w+(?:-\w+)?)',
        r'setup\s+(?:ide|rules)\s+(?:for\s+)?(\w+(?:-\w+)?)',
        r'create\s+(?:ide|rules)\s+(?:for\s+)?(\w+(?:-\w+)?)',
    ]
    
    for pattern in init_patterns:
        match = re.search(pattern, normalized_text)
        if match:
            ide = match.group(1)
            # Validate and correct IDE name
            ide = validate_ide(ide)
            return "initialize-ide", {"ide": ide}
    
    # Project settings patterns
    settings_patterns = [
        r'get\s+(?:project\s+)?settings',
        r'show\s+(?:project\s+)?settings',
        r'project\s+settings',
    ]
    
    for pattern in settings_patterns:
        if re.search(pattern, normalized_text):
            return "get-project-settings", {}
    
    # Prime context patterns
    context_patterns = [
        r'prime\s+(?:project\s+)?context',
        r'analyze\s+(?:project\s+)?context',
        r'build\s+(?:project\s+)?context',
    ]
    
    for pattern in context_patterns:
        if re.search(pattern, normalized_text):
            return "prime-context", {}
    
    # Think patterns
    if re.search(r'think\s+about', normalized_text):
        thought = re.sub(r'^think\s+about\s+', '', normalized_text)
        return "think", {"thought": thought}
        
    # No command detected
    return None, None
