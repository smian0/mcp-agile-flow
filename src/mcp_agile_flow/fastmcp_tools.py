"""
FastMCP Tools for MCP Agile Flow

This module implements MCP Agile Flow tools using FastMCP for a more Pythonic interface.
These implementations coexist with the traditional MCP tools while we migrate.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List
import re
import shutil

from .utils import get_project_settings as get_settings_util
from .migration_tool import (
    detect_conflicts,
    get_conflict_details,
    get_ide_path,
    migrate_config,
    merge_configurations,
)
from .think_tool import think, get_thoughts, clear_thoughts, get_thought_stats

# Set up logging
logger = logging.getLogger(__name__)

def get_project_settings(proposed_path: Optional[str] = None) -> str:
    """
    Returns comprehensive project settings including project path, AI docs directory, 
    project type, metadata, and other configuration.
    
    Also validates the path to ensure it's safe and writable. If the root directory or a 
    non-writable path is detected, it will automatically use a safe alternative path.
    
    Args:
        proposed_path: Optional path to check. If not provided, standard environment 
                      variables or default paths will be used.
    
    Returns:
        JSON string containing the project settings
    """
    logger.info("FastMCP: Getting project settings")
    
    # Use the utility function to get project settings
    response_data = get_settings_util(
        proposed_path=proposed_path if proposed_path else None
    )
    
    # Add default project type and metadata
    response_data["project_type"] = "generic"
    response_data["project_metadata"] = {}
    
    # Log the response for debugging
    logger.info(f"FastMCP: Project settings response: {response_data}")
    
    # Return as a JSON string to match the expected return type
    return json.dumps(response_data, indent=2)


def initialize_ide(ide: str = "cursor", project_path: Optional[str] = None) -> str:
    """
    Initialize a project with rules for a specific IDE.
    
    This function sets up the necessary directory structure and configuration files
    for the specified IDE in the given project path. It creates IDE-specific rule files
    or directories, copies template files, and ensures all necessary directories exist.
    
    Args:
        ide: IDE to initialize (cursor, windsurf, cline, or copilot)
        project_path: Custom project path to use (optional)
    
    Returns:
        JSON string containing the result of the initialization
    """
    import datetime
    import os
    import shutil
    
    logger.info(f"FastMCP: Initializing project for IDE: {ide}")
    
    if ide not in ["cursor", "windsurf", "cline", "copilot"]:
        error_response = {
            "success": False,
            "error": f"Error: Unknown IDE: {ide}",
            "message": "Supported IDEs are: cursor, windsurf, cline, copilot"
        }
        return json.dumps(error_response, indent=2)
    
    try:
        # Determine project path with improved handling of current directory
        if project_path:
            # Explicit path provided - use get_project_settings to validate it
            project_settings = get_settings_util(proposed_path=project_path)
            project_path = project_settings["project_path"]
            source = project_settings["source"]
        elif os.environ.get("PROJECT_PATH"):
            # Environment variable set - use get_project_settings to validate it
            project_settings = get_settings_util()
            project_path = project_settings["project_path"]
            source = project_settings["source"]
        else:
            # No path specified - use current working directory directly
            project_path = os.getcwd()
            source = "current working directory (direct)"
            
            # Check if it's root and handle that case
            if project_path == "/" or project_path == "\\":
                # Handle case where the path is problematic
                response_data = {
                    "error": "Current directory is the root directory. Please provide a specific project path.",
                    "status": "error",
                    "needs_user_input": True,
                    "current_directory": "/",
                    "is_root": True,
                    "message": "Please provide a specific project path using the 'project_path' argument.",
                    "success": False,
                }
                return json.dumps(response_data, indent=2)
        
        # Log the determined path
        logger.info(f"FastMCP: initialize_ide using project_path from {source}: {project_path}")
        
        # Create directory structure if it doesn't exist
        os.makedirs(os.path.join(project_path, "ai-docs"), exist_ok=True)
        os.makedirs(os.path.join(project_path, ".ai-templates"), exist_ok=True)
        
        # Create IDE-specific rules directory/file based on IDE
        if ide == "windsurf":
            # For windsurf, create an empty .windsurfrules file
            windsurf_rules_path = os.path.join(project_path, ".windsurfrules")
            with open(windsurf_rules_path, "w") as f:
                f.write("# Windsurf Rules\n")
        elif ide == "cline":
            # For cline, create a .clinerules file
            cline_rules_path = os.path.join(project_path, ".clinerules")
            with open(cline_rules_path, "w") as f:
                f.write("# Cline Rules\n")
        elif ide == "copilot":
            # For GitHub Copilot, create .github directory and copilot-instructions.md
            github_dir = os.path.join(project_path, ".github")
            os.makedirs(github_dir, exist_ok=True)
            copilot_file = os.path.join(github_dir, "copilot-instructions.md")
            with open(copilot_file, "w") as f:
                f.write("# GitHub Copilot Instructions\n")
        else:
            # For other IDEs (cursor), create a rules directory
            os.makedirs(os.path.join(project_path, f".{ide}", "rules"), exist_ok=True)
        
        # Copy default templates to .ai-templates directory
        # Source path is within the package's resources
        # Get the templates from the installed package
        
        # Create templates directory if it doesn't exist
        templates_dir = os.path.join(project_path, ".ai-templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # Get the source templates directory path
        templates_source_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_agile_flow", "ai-templates")
        
        # Check if the source directory exists
        if os.path.exists(templates_source_dir) and os.path.isdir(templates_source_dir):
            # Copy all template files from the source directory
            for template_file in os.listdir(templates_source_dir):
                try:
                    template_source_path = os.path.join(templates_source_dir, template_file)
                    template_target_path = os.path.join(templates_dir, template_file)
                    
                    # Only copy files, not directories
                    if os.path.isfile(template_source_path):
                        shutil.copy2(template_source_path, template_target_path)
                        logger.info(f"FastMCP: Copied template: {template_file}")
                
                except Exception as e:
                    logger.error(f"FastMCP: Error copying template {template_file}: {str(e)}")
        else:
            logger.warning(f"FastMCP: Template directory not found at {templates_source_dir}")
        
        # For cursor, further initialize with IDE rules
        if ide == "cursor":
            # Instead of calling back to the server which causes asyncio issues,
            # Let's implement the cursor rules initialization directly here
            cursor_dir = os.path.join(project_path, ".cursor")
            rules_dir = os.path.join(cursor_dir, "rules")
            os.makedirs(rules_dir, exist_ok=True)
            
            # Get paths to our rule files
            cursor_rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "mcp_agile_flow", "cursor_rules")
            
            # Verify source directory exists
            if not os.path.exists(cursor_rules_dir):
                logger.warning(f"FastMCP: Source rules directory not found: {cursor_rules_dir}")
            else:
                # Copy rules - Ensure they have .mdc extension for Cursor
                for rule_file in os.listdir(cursor_rules_dir):
                    source_file = os.path.join(cursor_rules_dir, rule_file)
                    
                    # For Cursor, we need to ensure the file has .mdc extension
                    target_filename = rule_file
                    if rule_file.endswith(".md") and not rule_file.endswith(".mdc"):
                        # Change the extension from .md to .mdc
                        target_filename = f"{rule_file[:-3]}.mdc"
                    elif not rule_file.endswith(".mdc"):
                        # Add .mdc extension if it's not already there and doesn't have .md
                        target_filename = f"{rule_file}.mdc"
                    
                    target_file = os.path.join(rules_dir, target_filename)
                    
                    logger.info(f"FastMCP: Copying rule file from {source_file} to {target_file}")
                    
                    # Copy the rule file
                    shutil.copy2(source_file, target_file)
                    
                # Log success
                logger.info(f"FastMCP: Successfully initialized cursor rules in {rules_dir}")
            
        # For other IDEs, copy IDE-specific rules if needed
        if ide != "cursor":
            # Copy IDE-specific rules
            rules_source_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_agile_flow", "ide_rules", ide)
            
            if ide == "windsurf":
                # For windsurf, there's no rules directory, just the .windsurfrules file
                pass
            elif ide == "cline":
                # For cline, there's no rules directory, just the .clinerules file
                pass
            elif ide == "copilot":
                # For copilot, rules go in .github/copilot-instructions.md
                pass
            else:
                # For other IDEs, copy to the rules directory
                rules_target_dir = os.path.join(project_path, f".{ide}-rules")
                os.makedirs(rules_target_dir, exist_ok=True)
                
                if os.path.exists(rules_source_dir):
                    for rule_file in os.listdir(rules_source_dir):
                        source_file = os.path.join(rules_source_dir, rule_file)
                        target_file = os.path.join(rules_target_dir, rule_file)
                        if os.path.isfile(source_file):
                            shutil.copy2(source_file, target_file)
                else:
                    logger.warning(f"FastMCP: IDE rules directory not found at {rules_source_dir}")
        
        # Create a JSON response
        response_data = {
            "success": True,
            "message": f"Initialized {ide} project in {project_path}",
            "project_path": project_path,
            "templates_directory": os.path.join(project_path, ".ai-templates"),
        }
        
        # Add IDE-specific paths to the response
        if ide == "windsurf":
            response_data["rules_file"] = os.path.join(project_path, ".windsurfrules")
            response_data["rules_directory"] = None  # No rules directory for windsurf
            response_data["initialized_windsurf"] = True  # Only include this for windsurf
        elif ide == "cline":
            response_data["rules_file"] = os.path.join(project_path, ".clinerules")
            response_data["rules_directory"] = None  # No rules directory for cline
        elif ide == "copilot":
            response_data["rules_file"] = os.path.join(project_path, ".github", "copilot-instructions.md")
            response_data["rules_directory"] = None  # No rules directory for copilot
        else:
            # For cursor, add rule-specific fields
            response_data["rules_directory"] = os.path.join(project_path, f".{ide}", "rules")
            
            # Add initialized_rules and initialized_templates for compatibility with tests
            cursor_rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                         "mcp_agile_flow", "cursor_rules")
            
            if os.path.exists(cursor_rules_dir):
                # List all rules that were initialized
                initialized_rules = []
                for rule_file in os.listdir(cursor_rules_dir):
                    source_file = os.path.join(cursor_rules_dir, rule_file)
                    if os.path.isfile(source_file):
                        if rule_file.endswith(".md") and not rule_file.endswith(".mdc"):
                            # Include with the .mdc extension as copied
                            initialized_rules.append(f"{rule_file[:-3]}.mdc")
                        elif not rule_file.endswith(".mdc"):
                            # Add .mdc extension if it's not already there
                            initialized_rules.append(f"{rule_file}.mdc")
                        else:
                            initialized_rules.append(rule_file)
                
                response_data["initialized_rules"] = initialized_rules
            
            # List all templates that were initialized
            templates_source_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                             "mcp_agile_flow", "ai-templates")
            
            if os.path.exists(templates_source_dir):
                # List all templates that were initialized
                initialized_templates = []
                for template_file in os.listdir(templates_source_dir):
                    source_file = os.path.join(templates_source_dir, template_file)
                    if os.path.isfile(source_file):
                        initialized_templates.append(template_file)
                
                response_data["initialized_templates"] = initialized_templates
        
        return json.dumps(response_data, indent=2)
    
    except Exception as e:
        logger.error(f"FastMCP: Error initializing IDE: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error as JSON
        response_data = {
            "success": False,
            "error": f"Error initializing project: {str(e)}",
            "message": "An error occurred during initialization"
        }
        return json.dumps(response_data, indent=2)


def initialize_ide_rules(ide: str = "cursor", project_path: Optional[str] = None) -> str:
    """
    Initialize a project with rules for a specific IDE.
    
    This function is similar to initialize_ide but focuses specifically on the rules files
    rather than the full project structure. It's provided for compatibility with existing tools.
    
    Args:
        ide: IDE to initialize (cursor, windsurf, cline, or copilot)
        project_path: Custom project path to use (optional)
    
    Returns:
        JSON string containing the result of the initialization
    """
    import datetime
    import os
    import shutil
    
    logger.info(f"FastMCP: Initializing IDE rules for: {ide}")
    
    if ide not in ["cursor", "windsurf", "cline", "copilot"]:
        error_response = {
            "success": False,
            "error": f"Error: Unknown IDE: {ide}",
            "message": "Supported IDEs are: cursor, windsurf, cline, copilot"
        }
        return json.dumps(error_response, indent=2)
    
    try:
        # Determine project path with improved handling of current directory
        if project_path:
            # Explicit path provided - use get_project_settings to validate it
            project_settings = get_settings_util(proposed_path=project_path)
            project_path = project_settings["project_path"]
            source = project_settings["source"]
        elif os.environ.get("PROJECT_PATH"):
            # Environment variable set - use get_project_settings to validate it
            project_settings = get_settings_util()
            project_path = project_settings["project_path"]
            source = project_settings["source"]
        else:
            # No path specified - use current working directory directly
            project_path = os.getcwd()
            source = "current working directory (direct)"
            
            # Check if it's root and handle that case
            if project_path == "/" or project_path == "\\":
                # Handle case where the path is problematic
                response_data = {
                    "error": "Current directory is the root directory. Please provide a specific project path.",
                    "status": "error",
                    "needs_user_input": True,
                    "current_directory": "/",
                    "is_root": True,
                    "message": "Please provide a specific project path using the 'project_path' argument.",
                    "success": False,
                }
                return json.dumps(response_data, indent=2)
        
        # Log the determined path
        logger.info(f"FastMCP: initialize_ide_rules using project_path from {source}: {project_path}")
        
        # Always back up existing rule files
        backup_existing = True
        
        # Handle different IDEs
        if ide == "cursor":
            # Initialize Cursor rules
            cursor_dir = os.path.join(project_path, ".cursor")
            rules_dir = os.path.join(cursor_dir, "rules")
            # Place ai-templates at the project root
            templates_dir = os.path.join(project_path, ".ai-templates")
            
            os.makedirs(rules_dir, exist_ok=True)
            os.makedirs(templates_dir, exist_ok=True)
            
            # Get paths to our rule and template files
            cursor_rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "mcp_agile_flow", "cursor_rules")
            ai_templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "mcp_agile_flow", "ai-templates")
            
            # Verify source directories exist
            if not os.path.exists(cursor_rules_dir):
                raise FileNotFoundError(f"Source rules directory not found: {cursor_rules_dir}")
            if not os.path.exists(ai_templates_dir):
                raise FileNotFoundError(f"Source templates directory not found: {ai_templates_dir}")
            
            # Track what files were initialized
            initialized_rules = []
            initialized_templates = []
            
            # Copy rules - Ensure they have .mdc extension for Cursor
            for rule_file in os.listdir(cursor_rules_dir):
                source_file = os.path.join(cursor_rules_dir, rule_file)
                
                # For Cursor, we need to ensure the file has .mdc extension
                target_filename = rule_file
                if rule_file.endswith(".md") and not rule_file.endswith(".mdc"):
                    # Change the extension from .md to .mdc
                    target_filename = f"{rule_file[:-3]}.mdc"
                elif not rule_file.endswith(".mdc"):
                    # Add .mdc extension if it's not already there and doesn't have .md
                    target_filename = f"{rule_file}.mdc"
                
                target_file = os.path.join(rules_dir, target_filename)
                
                logger.info(f"FastMCP: Copying rule file from {source_file} to {target_file}")
                
                # If target exists and backup is enabled, create a backup
                if os.path.exists(target_file) and backup_existing:
                    backup_file = f"{target_file}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.copy2(target_file, backup_file)
                
                # Copy the rule file
                shutil.copy2(source_file, target_file)
                initialized_rules.append(target_filename)
            
            # Verify rules were copied
            rule_files = os.listdir(rules_dir)
            logger.info(f"FastMCP: After copying, rules directory contains {len(rule_files)} files: {rule_files}")
            
            # Copy templates
            for template_file in os.listdir(ai_templates_dir):
                source_file = os.path.join(ai_templates_dir, template_file)
                target_file = os.path.join(templates_dir, template_file)
                
                # No backup for templates, we'll just overwrite them
                shutil.copy2(source_file, target_file)
                initialized_templates.append(template_file)
            
            # Return successful response
            response_data = {
                "success": True,
                "message": f"Initialized {ide} rules and templates.",
                "project_path": project_path,
                "rules_directory": rules_dir,
                "templates_directory": templates_dir,
                "initialized_rules": initialized_rules,
                "initialized_templates": initialized_templates,
            }
            
        elif ide == "windsurf":
            # Initialize Windsurf rules and templates
            # Place ai-templates at the project root
            templates_dir = os.path.join(project_path, ".ai-templates")
            os.makedirs(templates_dir, exist_ok=True)
            
            # Get paths to our template files
            ai_templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "mcp_agile_flow", "ai-templates")
            cursor_rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "mcp_agile_flow", "cursor_rules")
            
            # Verify source directories exist
            if not os.path.exists(ai_templates_dir):
                raise FileNotFoundError(f"Source templates directory not found: {ai_templates_dir}")
            if not os.path.exists(cursor_rules_dir):
                raise FileNotFoundError(f"Source rules directory not found: {cursor_rules_dir}")
            
            # Track what files were initialized
            initialized_templates = []
            
            # Copy templates
            for template_file in os.listdir(ai_templates_dir):
                source_file = os.path.join(ai_templates_dir, template_file)
                target_file = os.path.join(templates_dir, template_file)
                
                # No backup for templates, we'll just overwrite them
                shutil.copy2(source_file, target_file)
                initialized_templates.append(template_file)
            
            # For Windsurf, we combine all cursor rules into one .windsurfrules file
            windsurf_rules_file = os.path.join(project_path, ".windsurfrules")
            
            # If target exists and backup is enabled, create a backup
            if os.path.exists(windsurf_rules_file) and backup_existing:
                backup_file = f"{windsurf_rules_file}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.copy2(windsurf_rules_file, backup_file)
            
            # Build combined rules file
            with open(windsurf_rules_file, "w") as wf:
                for rule_file in sorted(os.listdir(cursor_rules_dir)):
                    source_file = os.path.join(cursor_rules_dir, rule_file)
                    if os.path.isfile(source_file) and (rule_file.endswith(".md") or rule_file.endswith(".mdc")):
                        with open(source_file, "r") as rf:
                            content = rf.read()
                            wf.write(f"### {rule_file} ###\n\n")
                            wf.write(content)
                            wf.write("\n\n")
            
            # Return successful response
            response_data = {
                "success": True,
                "message": f"Initialized {ide} rules and templates.",
                "project_path": project_path,
                "rules_file": windsurf_rules_file,
                "templates_directory": templates_dir,
                "initialized_windsurf": True,
                "initialized_templates": initialized_templates,
            }
            
        elif ide in ["cline", "copilot"]:
            # Initialize VS Code extension rules
            # Place ai-templates at the project root
            templates_dir = os.path.join(project_path, ".ai-templates")
            os.makedirs(templates_dir, exist_ok=True)
            
            # Get paths to our template files
            ai_templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "mcp_agile_flow", "ai-templates")
            cursor_rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "mcp_agile_flow", "cursor_rules")
            
            # Verify source directories exist
            if not os.path.exists(ai_templates_dir):
                raise FileNotFoundError(f"Source templates directory not found: {ai_templates_dir}")
            if not os.path.exists(cursor_rules_dir):
                raise FileNotFoundError(f"Source rules directory not found: {cursor_rules_dir}")
            
            # Track what files were initialized
            initialized_templates = []
            
            # Copy templates
            for template_file in os.listdir(ai_templates_dir):
                source_file = os.path.join(ai_templates_dir, template_file)
                target_file = os.path.join(templates_dir, template_file)
                
                # No backup for templates, we'll just overwrite them
                shutil.copy2(source_file, target_file)
                initialized_templates.append(template_file)
            
            # For VS Code extensions, create appropriate rule files
            if ide == "copilot":
                # For Copilot, we create a .github directory with copilot-instructions.md
                github_dir = os.path.join(project_path, ".github")
                os.makedirs(github_dir, exist_ok=True)
                rule_file = os.path.join(github_dir, "copilot-instructions.md")
                
                # Get the template path
                template_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "mcp_agile_flow", "ide_rules", "ide_rules.md")
                
                # Create backup if needed
                if os.path.exists(rule_file) and backup_existing:
                    backup_file = f"{rule_file}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.copy2(rule_file, backup_file)
                
                # Copy the template to the copilot instructions file
                shutil.copy2(template_file, rule_file)
                
                # Return successful response
                response_data = {
                    "success": True,
                    "message": f"Initialized {ide} rules and templates.",
                    "project_path": project_path,
                    "rules_file": rule_file,
                    "templates_directory": templates_dir,
                    "initialized_templates": initialized_templates,
                }
            else:
                # For cline, create a .clinerules file
                vs_code_rules_file = os.path.join(project_path, f".{ide.lower()}rules")
                
                # If target exists and backup is enabled, create a backup
                if os.path.exists(vs_code_rules_file) and backup_existing:
                    backup_file = f"{vs_code_rules_file}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.copy2(vs_code_rules_file, backup_file)
                
                # Get the template path
                template_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "mcp_agile_flow", "ide_rules", "ide_rules.md")
                
                # Copy the template
                shutil.copy2(template_file, vs_code_rules_file)
                
                # Return successful response
                response_data = {
                    "success": True,
                    "message": f"Initialized {ide} rules and templates.",
                    "project_path": project_path,
                    "rules_file": vs_code_rules_file,
                    "templates_directory": templates_dir,
                    "initialized_templates": initialized_templates,
                }
        
        return json.dumps(response_data, indent=2)
    
    except Exception as e:
        logger.error(f"FastMCP: Error initializing IDE rules: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error as JSON
        response_data = {
            "success": False,
            "error": f"Error initializing IDE rules: {str(e)}",
            "message": "An error occurred during initialization"
        }
        return json.dumps(response_data, indent=2)


def prime_context(depth: str = "standard", focus_areas: Optional[List[str]] = None, project_path: Optional[str] = None) -> str:
    """
    Analyzes project's AI documentation to build contextual understanding.
    
    This tool examines PRD, architecture docs, stories, and other AI-generated artifacts
    to provide a comprehensive project overview and current development state. Always
    prioritizes data from the ai-docs directory before falling back to README.md.
    
    Args:
        depth: Level of detail to include (minimal, standard, comprehensive)
        focus_areas: Optional specific areas to focus on
        project_path: Custom project path to use (optional)
    
    Returns:
        JSON string containing the project context information
    """
    logger.info(f"FastMCP: Priming context with depth: {depth}")
    
    try:
        # Determine project path with improved handling of current directory
        if project_path:
            # Explicit path provided - use get_project_settings to validate it
            project_settings = get_settings_util(proposed_path=project_path)
            project_path = project_settings["project_path"]
            source = project_settings["source"]
        elif os.environ.get("PROJECT_PATH"):
            # Environment variable set - use get_project_settings to validate it
            project_settings = get_settings_util()
            project_path = project_settings["project_path"]
            source = project_settings["source"]
        else:
            # No path specified - use current working directory directly
            project_path = os.getcwd()
            source = "current working directory (direct)"
            
            # Check if it's root and handle that case
            if project_path == "/" or project_path == "\\":
                # Handle case where the path is problematic
                response_data = {
                    "error": "Current directory is the root directory. Please provide a specific project path.",
                    "status": "error",
                    "needs_user_input": True,
                    "current_directory": "/",
                    "is_root": True,
                    "message": "Please provide a specific project path using the 'project_path' argument.",
                    "success": False,
                }
                return json.dumps(response_data, indent=2)
        
        # Log the determined path
        logger.info(f"FastMCP: prime_context using project_path from {source}: {project_path}")
        
        # Call internal implementation 
        response_data = _handle_prime_context(project_path, depth, focus_areas)
        return json.dumps(response_data, indent=2)
    
    except Exception as e:
        logger.error(f"FastMCP: Error priming context: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error as JSON
        response_data = {
            "success": False,
            "error": f"Error priming context: {str(e)}",
            "message": "An error occurred while analyzing project documentation"
        }
        return json.dumps(response_data, indent=2)


def _extract_markdown_title(content):
    """Extract the title from markdown content.

    Args:
        content (str): Markdown content

    Returns:
        str: The title of the document, or "Untitled" if no title found
    """
    lines = content.split("\n")
    for line in lines:
        # Look for level 1 heading
        if line.strip().startswith("# "):
            return line.strip()[2:].strip()

    return "Untitled"


def _extract_status(content):
    """Extract the status from markdown content.

    Args:
        content (str): Markdown content

    Returns:
        str: The status of the document, or "Unknown" if no status found
    """
    # Check for "## Status" section
    status_pattern = r"^\s*##\s+Status\s*$"
    status_section = None
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if re.search(status_pattern, line, re.IGNORECASE):
            status_section = i
            break

    if status_section is not None:
        # Look for status value in the lines after the section heading
        for i in range(status_section + 1, min(status_section + 10, len(lines))):
            line = lines[i].strip()
            if line and not line.startswith("#"):
                # Extract status value which could be in formats like:
                # - Status: Draft
                # - Draft
                # - **Status**: Draft

                # Remove markdown formatting and list markers
                line = re.sub(r"^\s*[-*]\s+", "", line)
                line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)

                # Check if line contains a status indicator
                if ":" in line:
                    parts = line.split(":", 1)
                    if parts[1].strip():
                        return parts[1].strip()

                # If no colon, check for common status values
                statuses = [
                    "Draft",
                    "In Progress",
                    "Complete",
                    "Approved",
                    "Current",
                    "Future",
                ]
                for status in statuses:
                    if status.lower() in line.lower():
                        return status

                # If we got to a non-empty line but didn't find a status, use the whole line
                return line

    return "Unknown"


def _summarize_content(content, depth="standard"):
    """Summarize markdown content based on depth.

    Args:
        content (str): Markdown content
        depth (str): Summarization depth ('minimal', 'standard', or 'comprehensive')

    Returns:
        str: Summarized content
    """
    lines = content.split("\n")

    if depth == "minimal":
        # Just return the title and a few key sections
        result = []

        # Extract title
        title = _extract_markdown_title(content)
        if title:
            result.append(f"# {title}")

        # Look for Status section
        status_section = None
        for i, line in enumerate(lines):
            if re.match(r"^\s*##\s+Status\s*$", line, re.IGNORECASE):
                status_section = i
                break

        if status_section is not None:
            result.append(lines[status_section])
            # Add a few lines after the Status heading
            for i in range(status_section + 1, min(status_section + 5, len(lines))):
                if not lines[i].startswith("#"):
                    result.append(lines[i])
                else:
                    break

        return "\n".join(result)

    elif depth == "standard":
        # Return all headings and their first paragraph
        result = []
        current_heading = None
        paragraph_lines = []

        for line in lines:
            if line.startswith("#"):
                # If we were building a paragraph, add it to result
                if paragraph_lines:
                    result.append("\n".join(paragraph_lines))
                    paragraph_lines = []

                # Add the heading
                result.append(line)
                current_heading = line
            elif line.strip() == "" and paragraph_lines:
                # End of paragraph
                result.append("\n".join(paragraph_lines))
                paragraph_lines = []
            elif current_heading is not None and line.strip():
                # Add line to current paragraph
                paragraph_lines.append(line)

        # Add any remaining paragraph
        if paragraph_lines:
            result.append("\n".join(paragraph_lines))

        return "\n".join(result)

    else:  # comprehensive or any other value
        return content


def _extract_task_completion(content):
    """Extract task completion information from markdown content.

    Args:
        content (str): Markdown content

    Returns:
        dict: Task completion information
    """
    lines = content.split("\n")
    total = 0
    completed = 0

    # Look for task items (- [ ] or - [x])
    for line in lines:
        line = line.strip()
        if re.match(r"^\s*-\s*\[\s*\]\s+", line):
            total += 1
        elif re.match(r"^\s*-\s*\[\s*x\s*\]\s+", line):
            total += 1
            completed += 1

    return {
        "total": total,
        "completed": completed,
        "percentage": round(completed / total * 100) if total > 0 else 0,
    }


def _handle_prime_context(project_path, depth="standard", focus_areas=None):
    """
    Prime the context with project information from various documentation sources.

    Args:
        project_path (str): Project path
        depth (str): Level of detail to include (minimal, standard, comprehensive)
        focus_areas (list): Optional specific areas to focus on

    Returns:
        dict: Structured project context information
    """
    logger.info(f"FastMCP: Priming context from project at: {project_path}")

    # Initialize the response structure with base project info
    context = {
        "project": {"name": "Untitled Project", "status": "Unknown", "overview": ""}
    }

    # Initialize other sections only if they're needed or if no focus areas specified
    if not focus_areas or "architecture" in focus_areas:
        context["architecture"] = {"overview": "", "components": []}

    if not focus_areas or "epics" in focus_areas:
        context["epics"] = []

    if not focus_areas or "progress" in focus_areas:
        context["progress"] = {
            "summary": "No progress information available",
            "stories_complete": 0,
            "stories_in_progress": 0,
            "stories_not_started": 0,
        }

    # Get paths to key directories
    ai_docs_dir = os.path.join(project_path, "ai-docs")

    # Check if the AI docs directory exists
    if not os.path.exists(ai_docs_dir):
        logger.info(f"FastMCP: AI docs directory not found at: {ai_docs_dir}")
        # Create a minimal context structure with defaults
        summary = "Project documentation not found. Limited context available."
        return {"context": context, "summary": summary}

    # Filter context based on focus areas if specified
    if focus_areas:
        filtered_context = {}
        for area in focus_areas:
            if area in context:
                filtered_context[area] = context[area]
        context = filtered_context if filtered_context else context

    # Extract project information from PRD or README
    prd_path = os.path.join(ai_docs_dir, "prd.md")
    if os.path.exists(prd_path) and ("project" in context):
        logger.info(f"FastMCP: Found PRD at: {prd_path}")
        with open(prd_path, "r") as f:
            prd_content = f.read()
            context["project"]["name"] = _extract_markdown_title(prd_content)
            context["project"]["status"] = _extract_status(prd_content)
            context["project"]["prd_title"] = context["project"]["name"]

            # Extract overview section from PRD
            overview_match = re.search(
                r"## Overview\s+([^\n#]*(?:\n(?!#)[^\n]*)*)", prd_content, re.MULTILINE
            )
            if overview_match:
                context["project"]["overview"] = overview_match.group(1).strip()

    # Check if README exists for additional project info
    readme_path = os.path.join(project_path, "README.md")
    if os.path.exists(readme_path) and ("project" in context):
        logger.info(f"FastMCP: Found README at: {readme_path}")
        with open(readme_path, "r") as f:
            readme_content = f.read()
            context["project"]["readme"] = _summarize_content(readme_content, depth)

            # If PRD wasn't found, use README for project name
            if "prd_title" not in context["project"]:
                context["project"]["name"] = _extract_markdown_title(readme_content)
                context["project"]["status"] = _extract_status(readme_content)

    # Extract architecture information
    arch_path = os.path.join(ai_docs_dir, "architecture.md")
    if os.path.exists(arch_path) and ("architecture" in context):
        logger.info(f"FastMCP: Found architecture document at: {arch_path}")
        with open(arch_path, "r") as f:
            arch_content = f.read()
            context["architecture"]["overview"] = _summarize_content(arch_content, depth)

            # Extract components section
            components_match = re.search(
                r"## Component Design\s+([^\n#]*(?:\n(?!#)[^\n]*)*)",
                arch_content,
                re.MULTILINE,
            )
            if components_match:
                component_text = components_match.group(1).strip()
                component_items = re.findall(r"- (.+)", component_text)
                context["architecture"]["components"] = component_items

    # Extract epic information
    epics_dir = os.path.join(ai_docs_dir, "epics")
    if os.path.exists(epics_dir) and ("epics" in context) and ("progress" in context):
        logger.info(f"FastMCP: Found epics directory at: {epics_dir}")

        epic_folders = [
            f
            for f in os.listdir(epics_dir)
            if os.path.isdir(os.path.join(epics_dir, f))
        ]
        for epic_folder in epic_folders:
            epic_path = os.path.join(epics_dir, epic_folder, "epic.md")
            if os.path.exists(epic_path):
                logger.info(f"FastMCP: Found epic at: {epic_path}")
                with open(epic_path, "r") as f:
                    epic_content = f.read()
                    epic_info = {
                        "name": _extract_markdown_title(epic_content),
                        "status": _extract_status(epic_content),
                        "description": _summarize_content(epic_content, depth),
                        "stories": [],
                    }

                    # Extract stories from the epic
                    stories_dir = os.path.join(epics_dir, epic_folder, "stories")
                    if os.path.exists(stories_dir):
                        story_files = [
                            f for f in os.listdir(stories_dir) if f.endswith(".md")
                        ]
                        for story_file in story_files:
                            story_path = os.path.join(stories_dir, story_file)
                            with open(story_path, "r") as sf:
                                story_content = sf.read()
                                story_name = _extract_markdown_title(story_content)
                                story_status = _extract_status(story_content)

                                # Track story completion for progress metrics
                                if "progress" in context:
                                    if story_status.lower() == "complete":
                                        context["progress"]["stories_complete"] += 1
                                    elif story_status.lower() in [
                                        "in progress",
                                        "started",
                                    ]:
                                        context["progress"]["stories_in_progress"] += 1
                                    else:
                                        context["progress"]["stories_not_started"] += 1

                                # Add story to epic
                                epic_info["stories"].append(
                                    {"name": story_name, "status": story_status}
                                )

                    context["epics"].append(epic_info)

    # Extract Makefile commands if Makefile exists
    makefile_path = os.path.join(project_path, "Makefile")
    if os.path.exists(makefile_path):
        logger.info(f"FastMCP: Found Makefile at: {makefile_path}")
        with open(makefile_path, "r") as f:
            makefile_content = f.read()

            # Extract targets from Makefile
            targets = re.findall(
                r"^([a-zA-Z0-9_-]+):\s*.*$", makefile_content, re.MULTILINE
            )

            # Group targets by category
            categories = {
                "testing": ["test", "tests", "unittest", "pytest", "check"],
                "build": ["build", "compile", "install", "setup"],
                "run": ["run", "start", "serve", "dev", "develop"],
                "clean": ["clean", "reset", "clear"],
                "lint": ["lint", "format", "style", "check"],
                "deploy": ["deploy", "publish", "release"],
            }

            categorized_targets = {}
            for category, keywords in categories.items():
                categorized_targets[category] = []
                for target in targets:
                    if any(keyword in target.lower() for keyword in keywords):
                        # Find the corresponding command
                        target_pattern = rf"^{re.escape(target)}:.*\n((\t.+\n)+)"
                        target_match = re.search(
                            target_pattern, makefile_content, re.MULTILINE
                        )
                        command = ""
                        if target_match:
                            command = target_match.group(1).strip()

                        categorized_targets[category].append(
                            {"target": target, "command": command}
                        )

                        # Remove this target from further consideration
                        targets = [t for t in targets if t != target]

            # Add "other" category for any remaining targets
            categorized_targets["other"] = []
            for target in targets:
                # Find the corresponding command
                target_pattern = rf"^{re.escape(target)}:.*\n((\t.+\n)+)"
                target_match = re.search(target_pattern, makefile_content, re.MULTILINE)
                command = ""
                if target_match:
                    command = target_match.group(1).strip()

                categorized_targets["other"].append(
                    {"target": target, "command": command}
                )

            # Add to project context
            context["project"]["makefile_commands"] = categorized_targets

    # Generate a project summary based on the depth
    summary_parts = []

    # Add project name and status
    summary_parts.append(f"Project: {context['project']['name']}")
    summary_parts.append(f"Status: {context['project']['status']}")

    # Add project overview if available
    if context["project"].get("overview"):
        summary_parts.append(f"\nOverview: {context['project']['overview']}")

    # Add architecture summary if available and requested
    if (
        "architecture" in context
        and context["architecture"].get("overview")
        and (not focus_areas or "architecture" in focus_areas)
    ):
        if depth == "minimal":
            summary_parts.append("\nArchitecture: Available")
        else:
            summary_parts.append(
                f"\nArchitecture: {context['architecture']['overview'][:150]}..."
            )

    # Add epic summary if available and requested
    if (
        "epics" in context
        and context["epics"]
        and (not focus_areas or "epics" in focus_areas)
    ):
        if depth == "minimal":
            summary_parts.append(f"\nEpics: {len(context['epics'])} found")
        else:
            epic_names = [epic["name"] for epic in context["epics"]]
            summary_parts.append(
                f"\nEpics ({len(epic_names)}): {', '.join(epic_names)}"
            )

    # Add progress summary if available and requested
    if "progress" in context and (not focus_areas or "progress" in focus_areas):
        total_stories = (
            context["progress"]["stories_complete"]
            + context["progress"]["stories_in_progress"]
            + context["progress"]["stories_not_started"]
        )

        if total_stories > 0:
            progress_pct = (
                context["progress"]["stories_complete"] / total_stories
            ) * 100
            summary_parts.append(
                f"\nProgress: {progress_pct:.1f}% complete ({context['progress']['stories_complete']}/{total_stories} stories)"
            )

    # Adjust summary length based on depth
    summary = "\n".join(summary_parts)
    if depth == "minimal":
        summary = "\n".join(summary_parts[:3])  # Just project info
    elif depth == "comprehensive":
        # Add more details for comprehensive depth
        if "epics" in context and context["epics"]:
            for epic in context["epics"]:
                summary += f"\n\nEpic: {epic['name']} ({epic['status']})"
                if epic["stories"]:
                    for story in epic["stories"]:
                        summary += f"\n  - {story['name']} ({story['status']})"

    # Create the final response
    response = {"context": context, "summary": summary}

    return response 


def migrate_mcp_config(from_ide: str, to_ide: str, backup: bool = True, conflict_resolutions: Optional[Dict[str, bool]] = None) -> str:
    """
    Migrate MCP configuration between different IDEs with smart merging and conflict resolution.
    
    Args:
        from_ide: Source IDE to migrate configuration from
        to_ide: Target IDE to migrate configuration to
        backup: Whether to create backups before modifying files
        conflict_resolutions: Mapping of server names to resolution choices (true = use source, false = keep target)
    
    Returns:
        JSON string containing the migration results
    """
    logger.info(f"FastMCP: Migrating MCP config from {from_ide} to {to_ide}")
    
    try:
        # If conflict resolutions are provided, perform the migration with them
        if conflict_resolutions:
            try:
                # Get paths
                source_path = get_ide_path(from_ide)
                target_path = get_ide_path(to_ide)

                # Read source configuration
                with open(source_path, "r") as f:
                    source_config = json.load(f)

                # Read target configuration
                target_config = {}
                if os.path.exists(target_path):
                    with open(target_path, "r") as f:
                        target_config = json.load(f)

                # Detect conflicts
                actual_conflicts = detect_conflicts(source_config, target_config)

                # Validate conflict resolutions
                if not actual_conflicts and conflict_resolutions:
                    # No actual conflicts but resolutions provided
                    response = {
                        "success": False,
                        "error": "Invalid conflict resolutions: no conflicts were detected",
                        "actual_conflicts": actual_conflicts,
                    }
                    return json.dumps(response, indent=2)

                # Check if all provided resolutions correspond to actual conflicts
                invalid_resolutions = [
                    server
                    for server in conflict_resolutions
                    if server not in actual_conflicts
                ]
                if invalid_resolutions:
                    response = {
                        "success": False,
                        "error": f"Invalid conflict resolutions: {', '.join(invalid_resolutions)} not in conflicts",
                        "actual_conflicts": actual_conflicts,
                    }
                    return json.dumps(response, indent=2)

                # Check if all conflicts have resolutions provided
                missing_resolutions = [
                    server
                    for server in actual_conflicts
                    if server not in conflict_resolutions
                ]
                if missing_resolutions:
                    response = {
                        "success": False,
                        "error": f"Missing conflict resolutions for: {', '.join(missing_resolutions)}",
                        "actual_conflicts": actual_conflicts,
                        "needs_resolution": True,
                        "conflicts": actual_conflicts,
                        "conflict_details": get_conflict_details(
                            source_config, target_config, actual_conflicts
                        ),
                    }
                    return json.dumps(response, indent=2)

                # Create backup if requested
                if backup and os.path.exists(target_path):
                    backup_path = f"{target_path}.bak"
                    shutil.copy2(target_path, backup_path)

                # Merge configurations with conflict resolutions
                merged_config = merge_configurations(
                    source_config, target_config, conflict_resolutions
                )

                # Create target directory if it doesn't exist
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # Write merged configuration
                with open(target_path, "w") as f:
                    json.dump(merged_config, f, indent=2)

                response = {
                    "success": True,
                    "resolved_conflicts": list(conflict_resolutions.keys()),
                    "source_path": source_path,
                    "target_path": target_path,
                }
                return json.dumps(response, indent=2)
            except Exception as e:
                response = {
                    "success": False,
                    "error": f"Error during migration with conflict resolutions: {str(e)}",
                }
                return json.dumps(response, indent=2)
        else:
            # Perform migration check first to detect conflicts
            success, error_message, conflicts, conflict_details = migrate_config(
                from_ide, to_ide, backup
            )

            if not success:
                response = {
                    "success": False,
                    "error": f"Error during migration check: {error_message}",
                }
                return json.dumps(response, indent=2)

            if conflicts:
                # Check if conflict_resolutions was provided as an empty dict
                # This is different from not providing conflict_resolutions at all
                if conflict_resolutions is not None and len(conflict_resolutions) == 0:
                    response = {
                        "success": False,
                        "error": "Missing conflict resolutions",
                        "needs_resolution": True,
                        "conflicts": conflicts,
                        "conflict_details": conflict_details,
                        "source_path": get_ide_path(from_ide),
                        "target_path": get_ide_path(to_ide),
                    }
                    return json.dumps(response, indent=2)

                # Initial check for conflicts, with no conflict_resolutions provided
                # Return success=True to match migrate_config behavior
                response = {
                    "success": True,
                    "needs_resolution": True,
                    "conflicts": conflicts,
                    "conflict_details": conflict_details,
                    "source_path": get_ide_path(from_ide),
                    "target_path": get_ide_path(to_ide),
                }
                return json.dumps(response, indent=2)
            else:
                # No conflicts, migration was successful
                response = {
                    "success": True,
                    "needs_resolution": False,
                    "source_path": get_ide_path(from_ide),
                    "target_path": get_ide_path(to_ide),
                }
                return json.dumps(response, indent=2)
    
    except Exception as e:
        logger.error(f"FastMCP: Error migrating MCP config: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error as JSON
        response_data = {
            "success": False,
            "error": f"Error migrating MCP config: {str(e)}",
            "message": "An unexpected error occurred during migration"
        }
        return json.dumps(response_data, indent=2) 