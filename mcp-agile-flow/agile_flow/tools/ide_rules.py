"""
IDE rule generation tools for Agile Flow.
"""

import os
import re
from typing import Dict, List, Optional

from ..utils.logger import setup_logger
from ..storage.file_manager import FileManager

logger = setup_logger("agile_flow.tools.ide_rules")

class CursorRuleGenerator:
    """
    Generates rule files for Cursor IDE.
    """
    
    def __init__(self, project_path: str, file_manager: FileManager):
        """
        Initialize the CursorRuleGenerator.
        
        Args:
            project_path: Path to the project root.
            file_manager: FileManager instance for reading Agile docs.
        """
        if not os.path.isabs(project_path):
            project_path = os.path.abspath(project_path)
        
        if not os.path.isdir(project_path):
            raise ValueError(f"Invalid project path: {project_path}")

        self.project_path = project_path
        self.file_manager = file_manager
        self.cursor_rules_path = os.path.join(self.project_path, ".cursor", "rules")
        
        # Create the rules directory with proper error handling
        try:
            os.makedirs(self.cursor_rules_path, exist_ok=True)
            logger.info(f"Created/verified Cursor rules directory at: {self.cursor_rules_path}")
        except PermissionError as e:
            # Try user's home directory as fallback
            home_dir = os.path.expanduser("~")
            self.cursor_rules_path = os.path.join(home_dir, ".cursor", "rules")
            os.makedirs(self.cursor_rules_path, exist_ok=True)
            logger.warning(f"Using fallback rules directory in home: {self.cursor_rules_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to create Cursor rules directory: {str(e)}")
        
    def generate_rules(self) -> List[str]:
        """
        Generate Cursor IDE rules based on Agile documentation.
        
        Returns:
            List of paths to the generated rule files.
        """
        generated_files = []
        
        try:
            # Generate agile workflow rule
            workflow_path = self._generate_agile_workflow_rule()
            generated_files.append(workflow_path)
            
            # Generate project structure rule
            try:
                project_path = self._generate_project_structure_rule()
                generated_files.append(project_path)
            except FileNotFoundError:
                logger.warning("Project document not found, skipping project structure rule")
            
            # Generate epic rules
            try:
                epic_files = self.file_manager.list_files("epics")
                for epic_file in epic_files:
                    epic_path = self._generate_epic_rule(f"epics/{epic_file}")
                    generated_files.append(epic_path)
            except Exception as e:
                logger.warning(f"Failed to generate epic rules: {str(e)}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to generate Cursor rules: {str(e)}")
            
        return generated_files
        
    def _generate_agile_workflow_rule(self) -> str:
        """
        Generate the Cursor rule file for Agile workflow.
        
        Returns:
            Path to the generated rule file.
        """
        rule_content = """# Agile Workflow

## Context
This project follows an Agile development methodology with epics, stories, and tasks.
All Agile documentation is stored in the agile-docs directory.

## Requirements
- Follow the Agile workflow defined in the project documentation
- Understand the project structure with epics, stories, and tasks
- Reference the agile-docs directory for project documentation
- Follow the existing naming conventions for new features
- Ensure commits reference the relevant story or task
- Update documentation when implementing new features

## Relevant locations
- /agile-docs/project.md
- /agile-docs/progress.md
- /agile-docs/epics/
- /agile-docs/stories/
- /agile-docs/tasks/
"""
        file_path = os.path.join(self.cursor_rules_path, "000-agile-workflow.mdc")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rule_content)
            
        logger.info(f"Generated Cursor rule file: {file_path}")
        return file_path
        
    def _generate_project_structure_rule(self) -> str:
        """
        Generate the Cursor rule file for project structure.
        
        Returns:
            Path to the generated rule file.
            
        Raises:
            FileNotFoundError: If the project document doesn't exist.
        """
        # Read project document
        project_content = self.file_manager.read_markdown("project.md")
        
        # Extract project name
        project_name = "Unknown Project"
        name_match = re.search(r"# Project: (.+)", project_content)
        if name_match:
            project_name = name_match.group(1)
            
        # Extract project description
        description = "No description available."
        desc_match = re.search(r"## Overview\s*\n((.+\n)+?)##", project_content)
        if desc_match:
            description = desc_match.group(1).strip()
            
        # Generate rule content
        rule_content = f"""# Project Structure: {project_name}

## Context
{description}

This project is organized according to the documentation in the agile-docs directory.

## Requirements
- Review documentation in agile-docs before making significant changes
- Follow the project structure defined in the documentation
- Update agile-docs when implementing new features
- Maintain consistency with existing code patterns
- Reference the appropriate epic and story when making changes

## Relevant locations
- /agile-docs/project.md
- /agile-docs/progress.md
"""
        file_path = os.path.join(self.cursor_rules_path, "001-project-structure.mdc")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rule_content)
            
        logger.info(f"Generated Cursor rule file: {file_path}")
        return file_path
        
    def _generate_epic_rule(self, epic_path: str) -> str:
        """
        Generate a Cursor rule file for an epic.
        
        Args:
            epic_path: Path to the epic document (relative to agile-docs).
            
        Returns:
            Path to the generated rule file.
        """
        # Read epic document
        epic_content = self.file_manager.read_markdown(epic_path)
        
        # Extract epic name
        epic_name = "Unknown Epic"
        name_match = re.search(r"# Epic: (.+)", epic_content)
        if name_match:
            epic_name = name_match.group(1)
            
        # Extract epic description
        description = "No description available."
        desc_match = re.search(r"## Overview\s*\n((.+\n)+?)##", epic_content)
        if desc_match:
            description = desc_match.group(1).strip()
            
        # Extract status and priority
        status = "Unknown"
        priority = "Unknown"
        status_match = re.search(r"- Status: (.+)", epic_content)
        priority_match = re.search(r"- Priority: (.+)", epic_content)
        
        if status_match:
            status = status_match.group(1)
        if priority_match:
            priority = priority_match.group(1)
            
        # Extract acceptance criteria
        criteria = "No acceptance criteria available."
        criteria_match = re.search(r"## Acceptance Criteria\s*\n((.+\n)+?)##", epic_content)
        if criteria_match:
            criteria = criteria_match.group(1).strip()
            
        # Generate rule content
        rule_content = f"""# Epic: {epic_name}

## Context
{description}

Status: {status}
Priority: {priority}

## Requirements
- Follow the acceptance criteria for this epic:
{criteria}

- Reference this epic when implementing related features
- Update the epic documentation when making changes
- Maintain consistency with other features in this epic

## Relevant locations
- /agile-docs/{epic_path}
"""
        
        # Create a filename based on the epic name
        safe_name = re.sub(r'[^\w\s-]', '', epic_name.lower())
        safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-_')
        file_path = os.path.join(self.cursor_rules_path, f"100-epic-{safe_name}.mdc")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rule_content)
            
        logger.info(f"Generated Cursor rule file: {file_path}")
        return file_path

class ClineRuleGenerator:
    """
    Generates rule files for Cline.
    """
    
    def __init__(self, project_path: str, file_manager: FileManager):
        """
        Initialize the ClineRuleGenerator.
        
        Args:
            project_path: Path to the project root.
            file_manager: FileManager instance for reading Agile docs.
        """
        if not os.path.isabs(project_path):
            project_path = os.path.abspath(project_path)

        self.project_path = project_path
        self.file_manager = file_manager
        self.cline_rules_path = os.path.join(self.project_path, ".clinerules")
        
    def generate_rules(self) -> str:
        """
        Generate Cline rules based on Agile documentation.
        
        Returns:
            Path to the generated rules file.
        """
        # Generate rule content
        rule_content = self._generate_cline_rule_content()
        
        try:
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(self.cline_rules_path), exist_ok=True)
            
            # Write to file
            with open(self.cline_rules_path, "w", encoding="utf-8") as f:
                f.write(rule_content)
                
            logger.info(f"Generated Cline rules file: {self.cline_rules_path}")
            
        except PermissionError:
            # Try user's home directory as fallback
            home_path = os.path.join(os.path.expanduser("~"), ".clinerules")
            with open(home_path, "w", encoding="utf-8") as f:
                f.write(rule_content)
            logger.warning(f"Using fallback location for Cline rules: {home_path}")
            return home_path
            
        return self.cline_rules_path
        
    def _generate_cline_rule_content(self) -> str:
        """
        Generate the content for the Cline rules file.
        
        Returns:
            Content of the rules file.
        """
        # Start with header
        content = "# Agile Project Guidelines\n\n"
        
        # Add project information
        try:
            project_content = self.file_manager.read_markdown("project.md")
            
            # Extract project name
            project_name = "Unknown Project"
            name_match = re.search(r"# Project: (.+)", project_content)
            if name_match:
                project_name = name_match.group(1)
                
            # Extract project description
            description = "No description available."
            desc_match = re.search(r"## Overview\s*\n((.+\n)+?)##", project_content)
            if desc_match:
                description = desc_match.group(1).strip()
                
            content += f"## Project: {project_name}\n\n"
            content += f"{description}\n\n"
            
        except FileNotFoundError:
            content += "## Project\n\nNo project information available.\n\n"
            
        # Add Agile workflow information
        content += """## Agile Workflow

This project follows an Agile development methodology with epics, stories, and tasks.
All Agile documentation is stored in the agile-docs directory.

### Guidelines

- Follow the Agile workflow defined in the project documentation
- Understand the project structure with epics, stories, and tasks
- Reference the agile-docs directory for project documentation
- Follow the existing naming conventions for new features
- Ensure commits reference the relevant story or task
- Update documentation when implementing new features

"""
        
        # Add epics information
        content += "## Epics\n\n"
        
        try:
            epic_files = self.file_manager.list_files("epics")
            if epic_files:
                for epic_file in epic_files:
                    try:
                        epic_content = self.file_manager.read_markdown(f"epics/{epic_file}")
                        
                        # Extract epic name
                        epic_name = "Unknown Epic"
                        name_match = re.search(r"# Epic: (.+)", epic_content)
                        if name_match:
                            epic_name = name_match.group(1)
                            
                        # Extract status
                        status = "Unknown"
                        status_match = re.search(r"- Status: (.+)", epic_content)
                        if status_match:
                            status = status_match.group(1)
                            
                        # Add epic to content
                        content += f"### {epic_name}\n\n"
                        content += f"Status: {status}\n\n"
                    except Exception as e:
                        logger.warning(f"Failed to process epic file {epic_file}: {str(e)}")
            else:
                content += "No epics defined yet.\n\n"
        except Exception as e:
            content += f"Failed to list epics: {str(e)}\n\n"
            
        # Add documentation locations
        content += """## Documentation Locations

- Project overview: /agile-docs/project.md
- Progress tracking: /agile-docs/progress.md
- Epics: /agile-docs/epics/
- Stories: /agile-docs/stories/
- Tasks: /agile-docs/tasks/
"""
        
        return content

class IDERulesManager:
    """
    Manages generation of IDE-specific rules.
    """
    
    def __init__(self, project_path: str, file_manager: FileManager):
        """
        Initialize the IDERulesManager.
        
        Args:
            project_path: Path to the project root.
            file_manager: FileManager instance for reading Agile docs.
        """
        if not os.path.isabs(project_path):
            project_path = os.path.abspath(project_path)
            
        if not os.path.isdir(project_path):
            raise ValueError(f"Invalid project directory: {project_path}")
            
        self.project_path = project_path
        self.file_manager = file_manager
        
        logger.info(f"Initializing IDE rules manager with project path: {self.project_path}")
        
        # Initialize rule generators
        self.cursor_generator = CursorRuleGenerator(project_path, file_manager)
        self.cline_generator = ClineRuleGenerator(project_path, file_manager)
        
    def generate_cursor_rules(self) -> List[str]:
        """
        Generate Cursor IDE rules.
        
        Returns:
            List of paths to the generated rule files.
        """
        return self.cursor_generator.generate_rules()
        
    def generate_cline_rules(self) -> str:
        """
        Generate Cline rules.
        
        Returns:
            Path to the generated rules file.
        """
        return self.cline_generator.generate_rules()
        
    def generate_all_rules(self) -> Dict[str, List[str]]:
        """
        Generate rules for all supported IDEs.
        
        Returns:
            Dictionary mapping IDE names to lists of generated rule file paths.
        """
        try:
            result = {
                "cursor": self.generate_cursor_rules(),
                "cline": [self.generate_cline_rules()]
            }
            return result
        except Exception as e:
            raise RuntimeError(f"Error generating all IDE rules: {str(e)}")
