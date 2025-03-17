"""
Project management tools for Agile Flow.
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..utils.logger import setup_logger
from ..storage.file_manager import FileManager
from ..storage.document_generator import DocumentGenerator
from ..storage.templates import TemplateManager

logger = setup_logger("agile_flow.tools.project")


class ProjectManager:
    """
    Manages Agile project operations.
    """
    
    def __init__(self, file_manager: FileManager, document_generator: DocumentGenerator):
        """
        Initialize the ProjectManager.
        
        Args:
            file_manager: FileManager instance for file operations.
            document_generator: DocumentGenerator instance for document generation.
        """
        self.file_manager = file_manager
        self.document_generator = document_generator
        
    def create_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Agile project.
        
        Args:
            args: Dictionary containing project arguments.
              - name: Name of the project (required).
              - description: Description of the project (optional).
              
        Returns:
            Dictionary containing the result of the operation.
        """
        # Extract arguments
        name = args.get("name")
        description = args.get("description", "No description provided.")
        
        # Validate arguments
        if not name:
            return {
                "error": {
                    "message": "Project name is required",
                    "code": "missing_parameter"
                }
            }
            
        # Check if project.md already exists
        if self.file_manager.file_exists("project.md"):
            return {
                "error": {
                    "message": "Project already exists",
                    "code": "duplicate_resource"
                }
            }
            
        # Create agile-docs directory structure
        self.file_manager.ensure_directory_structure()
        
        # Generate project document
        project_data = {
            "project_name": name,
            "project_description": description,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "Active",
            "priority": "Medium",
            "project_goals": "- Add project goals here",
            "key_metrics": "- Add key metrics here",
            "team_members": "- Add team members here"
        }
        project_path = self.document_generator.generate_project_doc(project_data)
        
        # Generate progress document
        progress_data = {
            "project_name": name,
            "progress_summary": "Project initialized.",
            "epic_status_table": "No epics created yet.",
            "recent_updates": "- Project created",
            "upcoming_work": "- Define initial epics",
            "blockers": "None"
        }
        progress_path = self.document_generator.generate_progress_doc(progress_data)
        
        logger.info(f"Created project: {name}")
        
        # Return result
        return {
            "project": {
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "documents": [
                    {"type": "project", "path": project_path},
                    {"type": "progress", "path": progress_path}
                ]
            }
        }
        
    def list_projects(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        List available projects.
        
        Args:
            args: Dictionary containing arguments (unused).
            
        Returns:
            Dictionary containing the result of the operation.
        """
        # Check if project.md exists
        if not self.file_manager.file_exists("project.md"):
            return {
                "projects": []
            }
            
        try:
            # Read project document
            project_content = self.file_manager.read_markdown("project.md")
            
            # Extract project name
            import re
            project_name = "Unknown Project"
            name_match = re.search(r"# Project: (.+)", project_content)
            if name_match:
                project_name = name_match.group(1)
                
            # Extract metadata
            metadata = self.file_manager.get_markdown_metadata(project_content)
            status = metadata.get("Status", "Unknown")
            
            # Check if progress.md exists
            progress_summary = None
            if self.file_manager.file_exists("progress.md"):
                progress_content = self.file_manager.read_markdown("progress.md")
                progress_match = re.search(r"## Summary\s*\n((.+\n)+?)##", progress_content)
                if progress_match:
                    progress_summary = progress_match.group(1).strip()
                    
            # Count epics
            epic_count = 0
            if os.path.exists(os.path.join(self.file_manager.agile_docs_path, "epics")):
                epic_files = self.file_manager.list_files("epics")
                epic_count = len(epic_files)
                
            # Return result
            return {
                "projects": [
                    {
                        "name": project_name,
                        "status": status,
                        "epic_count": epic_count,
                        "progress_summary": progress_summary,
                        "documents": [
                            {"type": "project", "path": "project.md"},
                            {"type": "progress", "path": "progress.md"}
                        ]
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            return {
                "error": {
                    "message": f"Error listing projects: {str(e)}",
                    "code": "internal_error"
                }
            }
            
    def set_active_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set the active project.
        
        Note: Since we only support a single project in the current
        implementation, this is a placeholder for future multi-project support.
        
        Args:
            args: Dictionary containing arguments.
              - name: Name of the project to activate (required).
              
        Returns:
            Dictionary containing the result of the operation.
        """
        # Extract arguments
        name = args.get("name")
        
        # Validate arguments
        if not name:
            return {
                "error": {
                    "message": "Project name is required",
                    "code": "missing_parameter"
                }
            }
            
        # Check if project.md exists
        if not self.file_manager.file_exists("project.md"):
            return {
                "error": {
                    "message": f"Project '{name}' not found",
                    "code": "not_found"
                }
            }
            
        # Read project document to verify name
        try:
            project_content = self.file_manager.read_markdown("project.md")
            
            # Extract project name
            import re
            project_name = "Unknown Project"
            name_match = re.search(r"# Project: (.+)", project_content)
            if name_match:
                project_name = name_match.group(1)
                
            # Check if the name matches
            if project_name.lower() != name.lower():
                return {
                    "error": {
                        "message": f"Project '{name}' not found",
                        "code": "not_found"
                    }
                }
                
            # Return success result
            return {
                "project": {
                    "name": project_name,
                    "active": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error setting active project: {str(e)}")
            return {
                "error": {
                    "message": f"Error setting active project: {str(e)}",
                    "code": "internal_error"
                }
            }
            
    def get_project_handlers(self) -> Dict[str, Any]:
        """
        Get all project tool handlers.
        
        Returns:
            Dictionary mapping tool names to handler functions.
        """
        return {
            "create_project": self.create_project,
            "list_projects": self.list_projects,
            "set_active_project": self.set_active_project
        }
