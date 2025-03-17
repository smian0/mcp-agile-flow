#!/usr/bin/env python3
"""
MCP Agile Flow Server - Simplified implementation using MCP Python SDK.
This server provides Agile workflow tools through the Model Context Protocol.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import FastMCP, Context
from agile_flow.storage.file_manager import FileManager
from agile_flow.storage.templates import TemplateManager
from agile_flow.storage.document_generator import DocumentGenerator
from agile_flow.tools.ide_rules import IDERulesManager

# Create an MCP server
mcp = FastMCP("Agile Flow")

# Initialize storage components with safe project path detection
def find_valid_project_path():
    """Find a valid project path that isn't the root directory."""
    # Start with env var or current directory
    path = os.environ.get("PROJECT_PATH", os.getcwd())
    
    # Check if it's a problematic path
    if path == "/" or "${PROJECT_PATH}" in path or "#{PROJECT_PATH}" in path:
        # Try current directory
        path = os.getcwd()
        print(f"Using current directory as project path: {path}", file=sys.stderr)
    
    # If still problematic, use home directory
    if path == "/":
        home_dir = os.path.expanduser("~/mcp-agile-flow")
        os.makedirs(home_dir, exist_ok=True)
        path = home_dir
        print(f"Using home directory as project path: {path}", file=sys.stderr)
    
    return os.path.abspath(path)

# Get safe project path
import sys
project_path = find_valid_project_path()
print(f"Using project path: {project_path}", file=sys.stderr)

# Initialize components with validated path
agile_docs_path = os.path.join(project_path, "agile-docs")
file_manager = FileManager(agile_docs_path)
template_manager = TemplateManager()
document_generator = DocumentGenerator(file_manager, template_manager)

# Only create IDE rules manager after project path is confirmed valid
ide_rules_manager = IDERulesManager(project_path, file_manager)


# ===== Project Management Tools =====

@mcp.tool()
def create_project(name: str, description: str = "No description provided.") -> Dict[str, Any]:
    """
    Create a new Agile project.

    Args:
        name: Name of the project.
        description: Description of the project (optional).

    Returns:
        Information about the created project.
    """
    # Check if project.md already exists
    if file_manager.file_exists("project.md"):
        return {
            "error": {
                "message": "Project already exists",
                "code": "duplicate_resource"
            }
        }

    # Create agile-docs directory structure
    file_manager.ensure_directory_structure()

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
    project_path = document_generator.generate_project_doc(project_data)

    # Generate progress document
    progress_data = {
        "project_name": name,
        "progress_summary": "Project initialized.",
        "epic_status_table": "No epics created yet.",
        "recent_updates": "- Project created",
        "upcoming_work": "- Define initial epics",
        "blockers": "None"
    }
    progress_path = document_generator.generate_progress_doc(progress_data)

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


@mcp.tool()
def list_projects() -> Dict[str, Any]:
    """
    List available projects.

    Returns:
        List of available projects.
    """
    # Check if project.md exists
    if not file_manager.file_exists("project.md"):
        return {
            "projects": []
        }

    try:
        # Read project document
        project_content = file_manager.read_markdown("project.md")

        # Extract project name
        import re
        project_name = "Unknown Project"
        name_match = re.search(r"# Project: (.+)", project_content)
        if name_match:
            project_name = name_match.group(1)

        # Extract metadata
        metadata = file_manager.get_markdown_metadata(project_content)
        status = metadata.get("Status", "Unknown")

        # Check if progress.md exists
        progress_summary = None
        if file_manager.file_exists("progress.md"):
            progress_content = file_manager.read_markdown("progress.md")
            progress_match = re.search(r"## Summary\s*\n((.+\n)+?)##", progress_content)
            if progress_match:
                progress_summary = progress_match.group(1).strip()

        # Count epics
        epic_count = 0
        if os.path.exists(os.path.join(file_manager.agile_docs_path, "epics")):
            epic_files = file_manager.list_files("epics")
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
        return {
            "error": {
                "message": f"Error listing projects: {str(e)}",
                "code": "internal_error"
            }
        }


# ===== IDE Rule Generation Tools =====

@mcp.tool()
def generate_cursor_rules() -> Dict[str, Any]:
    """
    Generate Cursor IDE rules based on project documentation.

    Returns:
        List of generated rule file paths.
    """
    try:
        rule_files = ide_rules_manager.generate_cursor_rules()
        return {
            "rules": rule_files
        }
    except Exception as e:
        return {
            "error": {
                "message": f"Error generating Cursor IDE rules: {str(e)}",
                "code": "internal_error"
            }
        }


@mcp.tool()
def generate_cline_rules() -> Dict[str, Any]:
    """
    Generate Cline IDE rules based on project documentation.

    Returns:
        Path to the generated rules file.
    """
    try:
        rules_file = ide_rules_manager.generate_cline_rules()
        return {
            "rules": [rules_file]
        }
    except Exception as e:
        return {
            "error": {
                "message": f"Error generating Cline IDE rules: {str(e)}",
                "code": "internal_error"
            }
        }


@mcp.tool()
def generate_all_rules() -> Dict[str, Any]:
    """
    Generate rules for all supported IDEs.

    Returns:
        Dictionary mapping IDE names to lists of generated rule file paths.
    """
    try:
        rules = ide_rules_manager.generate_all_rules()
        return {
            "rules": rules
        }
    except Exception as e:
        return {
            "error": {
                "message": f"Error generating all IDE rules: {str(e)}",
                "code": "internal_error"
            }
        }


# ===== Configuration Resources =====

@mcp.resource("agile-flow://config")
def get_config() -> str:
    """
    Get the current Agile Flow configuration.

    Returns:
        Configuration information as text.
    """
    return f"""
Agile Flow Configuration:
------------------------
Project Path: {project_path}
Agile Docs Path: {agile_docs_path}
"""


@mcp.resource("agile-flow://project")
def get_project() -> str:
    """
    Get the current project information.

    Returns:
        Project information as text.
    """
    try:
        if file_manager.file_exists("project.md"):
            return file_manager.read_markdown("project.md")
        return "No project found. Use the 'create_project' tool to create a new project."
    except Exception as e:
        return f"Error reading project information: {str(e)}"


@mcp.resource("agile-flow://progress")
def get_progress() -> str:
    """
    Get the current project progress information.

    Returns:
        Progress information as text.
    """
    try:
        if file_manager.file_exists("progress.md"):
            return file_manager.read_markdown("progress.md")
        return "No progress information found."
    except Exception as e:
        return f"Error reading progress information: {str(e)}"


@mcp.resource("agile-flow://epic/{epic_name}")
def get_epic(epic_name: str) -> str:
    """
    Get information about a specific epic.

    Args:
        epic_name: Name of the epic.

    Returns:
        Epic information as text.
    """
    try:
        # Create a safe filename from the epic name
        import re
        safe_name = re.sub(r'[^\w\s-]', '', epic_name.lower())
        safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-_')

        epic_path = f"epics/{safe_name}.md"
        if file_manager.file_exists(epic_path):
            return file_manager.read_markdown(epic_path)
        return f"No epic found with name '{epic_name}'."
    except Exception as e:
        return f"Error reading epic information: {str(e)}"


# Run the server if executed directly
if __name__ == "__main__":
    mcp.run()
