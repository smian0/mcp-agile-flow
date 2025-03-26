"""
Data models for MCP tools.
"""
from typing import Optional, Dict, List
from dataclasses import dataclass

@dataclass
class ProjectSettingsResponse:
    """Response model for project settings."""
    success: bool
    project_path: str
    current_directory: str
    is_project_path_manually_set: bool
    ai_docs_directory: str
    source: str
    is_root: bool
    is_writable: bool 
    exists: bool
    project_type: Optional[str] = None
    project_metadata: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None

@dataclass
class InitializeIDEResponse:
    """Response model for IDE initialization."""
    success: bool
    project_path: str
    templates_directory: str
    rules_directory: Optional[str] = None
    rules_file: Optional[str] = None
    initialized_rules: Optional[List[str]] = None
    initialized_templates: Optional[List[str]] = None
    initialized_windsurf: bool = False
    error: Optional[str] = None
    message: Optional[str] = None
