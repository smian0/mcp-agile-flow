"""
Document generator for Agile Flow documentation.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from ..utils.logger import setup_logger
from .file_manager import FileManager
from .templates import TemplateManager

logger = setup_logger("agile_flow.storage.document_generator")


class DocumentGenerator:
    """
    Generates Agile documentation using templates and file storage.
    """
    
    def __init__(self, file_manager: FileManager, template_manager: TemplateManager):
        """
        Initialize the DocumentGenerator.
        
        Args:
            file_manager: FileManager instance for file operations.
            template_manager: TemplateManager instance for template rendering.
        """
        self.file_manager = file_manager
        self.template_manager = template_manager
        
    def generate_project_doc(self, project_data: Dict) -> str:
        """
        Generate project document.
        
        Args:
            project_data: Dictionary containing project data.
            
        Returns:
            Path to the generated document (relative to agile-docs).
        """
        # Ensure required fields
        if "project_name" not in project_data:
            raise ValueError("Project name is required")
            
        # Set default values for optional fields
        defaults = {
            "project_description": "No description provided.",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "Active",
            "priority": "Medium",
            "project_goals": "- Add project goals here",
            "key_metrics": "- Add key metrics here",
            "team_members": "- Add team members here"
        }
        
        # Merge defaults with provided data
        context = {**defaults, **project_data}
        
        # Render template
        content = self.template_manager.render_template("project", context)
        
        # Write to file
        path = "project.md"
        self.file_manager.write_markdown(path, content)
        
        logger.info(f"Generated project document: {path}")
        return path
        
    def generate_epic_doc(self, epic_data: Dict) -> str:
        """
        Generate epic document.
        
        Args:
            epic_data: Dictionary containing epic data.
            
        Returns:
            Path to the generated document (relative to agile-docs).
        """
        # Ensure required fields
        if "epic_name" not in epic_data:
            raise ValueError("Epic name is required")
            
        # Set default values for optional fields
        now = datetime.now().strftime("%Y-%m-%d")
        defaults = {
            "epic_description": "No description provided.",
            "status": "Planned",
            "priority": "Medium",
            "created_date": now,
            "updated_date": now,
            "acceptance_criteria": "- Add acceptance criteria here",
            "story_references": "No stories yet.",
            "notes": "No notes yet."
        }
        
        # Merge defaults with provided data
        context = {**defaults, **epic_data}
        
        # Create filename from epic name
        filename = self._safe_filename(epic_data["epic_name"])
        
        # Render template
        content = self.template_manager.render_template("epic", context)
        
        # Write to file
        path = f"epics/{filename}.md"
        self.file_manager.write_markdown(path, content)
        
        logger.info(f"Generated epic document: {path}")
        return path
        
    def generate_story_doc(self, story_data: Dict) -> str:
        """
        Generate story document.
        
        Args:
            story_data: Dictionary containing story data.
            
        Returns:
            Path to the generated document (relative to agile-docs).
        """
        # Ensure required fields
        if "story_name" not in story_data:
            raise ValueError("Story name is required")
        if "epic_name" not in story_data:
            raise ValueError("Epic name is required")
            
        # Set default values for optional fields
        now = datetime.now().strftime("%Y-%m-%d")
        defaults = {
            "story_description": "No description provided.",
            "status": "Planned",
            "story_points": "1",
            "created_date": now,
            "updated_date": now,
            "acceptance_criteria": "- Add acceptance criteria here",
            "tasks": "No tasks yet.",
            "notes": "No notes yet."
        }
        
        # Merge defaults with provided data
        context = {**defaults, **story_data}
        
        # Create filenames
        epic_filename = self._safe_filename(story_data["epic_name"])
        story_filename = self._safe_filename(story_data["story_name"])
        
        # Add epic filename to context
        context["epic_filename"] = f"{epic_filename}.md"
        
        # Render template
        content = self.template_manager.render_template("story", context)
        
        # Write to file
        path = f"stories/{epic_filename}/{story_filename}.md"
        self.file_manager.write_markdown(path, content)
        
        logger.info(f"Generated story document: {path}")
        return path
        
    def generate_task_doc(self, task_data: Dict) -> str:
        """
        Generate task document.
        
        Args:
            task_data: Dictionary containing task data.
            
        Returns:
            Path to the generated document (relative to agile-docs).
        """
        # Ensure required fields
        if "task_name" not in task_data:
            raise ValueError("Task name is required")
        if "story_name" not in task_data:
            raise ValueError("Story name is required")
        if "epic_name" not in task_data:
            raise ValueError("Epic name is required")
            
        # Set default values for optional fields
        now = datetime.now().strftime("%Y-%m-%d")
        defaults = {
            "task_description": "No description provided.",
            "status": "Planned",
            "assigned_to": "Unassigned",
            "created_date": now,
            "updated_date": now,
            "checklist": "- [ ] Add checklist items here",
            "notes": "No notes yet."
        }
        
        # Merge defaults with provided data
        context = {**defaults, **task_data}
        
        # Create filenames
        epic_filename = self._safe_filename(task_data["epic_name"])
        story_filename = self._safe_filename(task_data["story_name"])
        task_filename = self._safe_filename(task_data["task_name"])
        
        # Add related filenames to context
        context["epic_filename"] = f"{epic_filename}.md"
        context["story_filename"] = f"{story_filename}.md"
        context["epic_path"] = epic_filename
        
        # Render template
        content = self.template_manager.render_template("task", context)
        
        # Write to file
        path = f"tasks/{epic_filename}/{story_filename}/{task_filename}.md"
        self.file_manager.write_markdown(path, content)
        
        logger.info(f"Generated task document: {path}")
        return path
        
    def generate_progress_doc(self, progress_data: Dict) -> str:
        """
        Generate progress document.
        
        Args:
            progress_data: Dictionary containing progress data.
            
        Returns:
            Path to the generated document (relative to agile-docs).
        """
        # Ensure required fields
        if "project_name" not in progress_data:
            raise ValueError("Project name is required")
            
        # Set default values for optional fields
        defaults = {
            "progress_summary": "Project in progress.",
            "epic_status_table": "No epics yet.",
            "recent_updates": "- No recent updates",
            "upcoming_work": "- No upcoming work defined",
            "blockers": "None"
        }
        
        # Merge defaults with provided data
        context = {**defaults, **progress_data}
        
        # Render template
        content = self.template_manager.render_template("progress", context)
        
        # Write to file
        path = "progress.md"
        self.file_manager.write_markdown(path, content)
        
        logger.info(f"Generated progress document: {path}")
        return path
        
    def update_epic_story_references(self, epic_name: str, story_names: List[str]) -> None:
        """
        Update the story references section in an epic document.
        
        Args:
            epic_name: Name of the epic.
            story_names: List of story names to include in the references.
        """
        epic_filename = self._safe_filename(epic_name)
        path = f"epics/{epic_filename}.md"
        
        try:
            # Read current content
            content = self.file_manager.read_markdown(path)
            
            # Generate story references
            story_references = ""
            for story_name in story_names:
                story_filename = self._safe_filename(story_name)
                story_references += f"- [{story_name}](../stories/{epic_filename}/{story_filename}.md)\n"
                
            if not story_references:
                story_references = "No stories yet."
                
            # Replace story references section
            import re
            pattern = r"(## Stories\n)(.+?)(\n## Notes)"
            replacement = f"\\1{story_references}\\3"
            updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # Write updated content
            self.file_manager.write_markdown(path, updated_content)
            
            logger.info(f"Updated story references in epic document: {path}")
            
        except FileNotFoundError:
            logger.warning(f"Epic document not found: {path}")
        
    def _safe_filename(self, name: str) -> str:
        """
        Convert a name to a safe filename by replacing spaces with hyphens
        and removing special characters.
        
        Args:
            name: Name to convert.
            
        Returns:
            Safe filename.
        """
        # Replace spaces with hyphens and remove special characters
        import re
        safe_name = re.sub(r'[^\w\s-]', '', name.lower())
        safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-_')
        return safe_name
