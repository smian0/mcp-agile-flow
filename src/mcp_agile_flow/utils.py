"""
Utility functions for MCP Agile Flow.
"""

import os
from typing import Dict, Any, Tuple


def get_project_settings() -> Dict[str, Any]:
    """
    Get project settings including project path, knowledge graph directory, and AI docs directory.
    
    This is a common utility function used by various components to ensure consistent
    project path handling throughout the application.
    
    Returns:
        Dict with the following keys:
            - project_path: The project path (defaults to user's home directory if not set)
            - current_directory: The current working directory
            - is_project_path_manually_set: Whether PROJECT_PATH was set manually
            - knowledge_graph_directory: Path to the knowledge graph directory
            - ai_docs_directory: Path to the AI docs directory
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
    
    # Check PROJECT_PATH
    if project_path_env is not None and project_path_env.strip() != '':
        is_manually_set = True
        project_path = project_path_env
        logger.info(f"Using PROJECT_PATH environment variable: {project_path}")
    # Default to home directory if not set
    else:
        project_path = home_directory
        logger.info(f"Using user's home directory as project_path: {project_path}")
    
    # Ensure project_path is an absolute path
    if not os.path.isabs(project_path):
        old_path = project_path
        project_path = os.path.abspath(project_path)
        logger.info(f"Converted relative path '{old_path}' to absolute path '{project_path}'")
    
    # Safety check - if project_path is '/' or very short, use home directory instead
    if project_path == '/' or len(project_path) < 3:
        logger.warning(f"Invalid project path '{project_path}'. Using home directory instead.")
        project_path = home_directory
        logger.info(f"Using home directory as project_path: {project_path}")
    
    # Check if the project path exists and is writable
    if not os.path.exists(project_path):
        logger.warning(f"Project path does not exist: {project_path}")
        project_path = home_directory
        logger.info(f"Using home directory as project_path: {project_path}")
    elif not os.access(project_path, os.W_OK):
        logger.warning(f"Project path is not writable: {project_path}")
        project_path = home_directory
        logger.info(f"Using home directory as project_path: {project_path}")
    
    # Get knowledge graph and AI docs directories
    knowledge_graph_dir, ai_docs_dir = get_special_directories(project_path)
    logger.info(f"Knowledge graph directory: {knowledge_graph_dir}")
    logger.info(f"AI docs directory: {ai_docs_dir}")
    
    result = {
        "project_path": project_path,
        "current_directory": current_directory,
        "is_project_path_manually_set": is_manually_set,
        "knowledge_graph_directory": knowledge_graph_dir,
        "ai_docs_directory": ai_docs_dir
    }
    logger.info(f"Returning project settings: {result}")
    return result


def get_special_directories(project_path: str) -> Tuple[str, str]:
    """
    Get the knowledge graph and AI docs directories for a given project path.
    If the directories don't exist, they will be created.
    
    Args:
        project_path: The project path to find special directories for
        
    Returns:
        Tuple of (knowledge_graph_directory, ai_docs_directory)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Define knowledge graph directory (primarily ai-kngr, with fallbacks)
    knowledge_graph_dir = os.path.join(project_path, "ai-kngr")
    if not os.path.exists(knowledge_graph_dir):
        # Check fallback directories
        found_fallback = False
        for fallback in [".kg", ".knowledge"]:
            fallback_dir = os.path.join(project_path, fallback)
            if os.path.exists(fallback_dir):
                knowledge_graph_dir = fallback_dir
                found_fallback = True
                logger.info(f"Using existing knowledge graph directory: {knowledge_graph_dir}")
                break
        
        # No fallback found - create the default directory
        if not found_fallback:
            knowledge_graph_dir = os.path.join(project_path, "ai-kngr")
            try:
                os.makedirs(knowledge_graph_dir, exist_ok=True)
                logger.info(f"Created knowledge graph directory: {knowledge_graph_dir}")
            except Exception as e:
                logger.warning(f"Failed to create knowledge graph directory: {e}")
    else:
        logger.info(f"Using existing knowledge graph directory: {knowledge_graph_dir}")
    
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
