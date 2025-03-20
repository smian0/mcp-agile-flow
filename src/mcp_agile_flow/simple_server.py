"""
MCP Agile Flow - Simple Server Implementation

This module implements a simple MCP server with basic tools.
It uses the standard MCP protocol over stdin/stdout for use with Cursor.
"""
import os
import sys
import asyncio
import logging
import re
import json
import shutil
import datetime
import glob
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import traceback
import threading
import importlib.resources

from .utils import get_project_settings

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import stdio

# Import local modules
from .memory_graph import register_memory_tools, KnowledgeGraphManager

# Configure logging
logger = logging.getLogger(__name__)

# Initialize memory graph tools and manager after server starts
# This will be done in the run_server function
memory_tools = []
memory_manager = None

# Create an MCP server
mcp = Server("MCP Agile Flow - Simple")

def create_text_response(text: str, is_error: bool = False) -> types.TextContent:
    """Helper function to create properly formatted TextContent responses."""
    return types.TextContent(
        type="text",
        text=text,
        isError=is_error
    )

def check_for_greeting(message: str) -> bool:
    """Check if a message contains a greeting for Sho."""
    return message and "hey sho" in message.lower()

def parse_greeting_command(message: str) -> Tuple[str, Dict[str, Any]]:
    """Parse a greeting command into a tool name and arguments."""
    # Remove the greeting
    command = message.lower().replace("hey sho", "").strip()
    
    # Extract command name and arguments
    parts = command.split(" ", 1)
    cmd_name = parts[0]
    cmd_args = {}
    
    if len(parts) > 1:
        try:
            cmd_args = json.loads(parts[1])
        except json.JSONDecodeError:
            cmd_args = {"message": parts[1]}
    
    return cmd_name, cmd_args

def get_safe_project_path(arguments: Optional[dict] = None, environment_variable: str = None, default: str = None) -> Tuple[str, bool, str]:
    """
    Get a safe project path that is guaranteed to be writable.
    
    Args:
        arguments: Optional arguments dictionary that might contain 'project_path'
        environment_variable: Optional environment variable to use if 'project_path' is not provided
        default: Optional default path to use if 'project_path' is not provided and environment variable is not set
        
    Returns:
        Tuple[str, bool, str]: The safe project path, whether it's root, and the source of the path
    """
    print("get_safe_project_path called with arguments:", arguments)
    source = "unknown"
    path = ""
    is_root = False
    
    # First check if project_path is provided in arguments
    if arguments and "project_path" in arguments and arguments["project_path"].strip() != '':
        raw_path = arguments["project_path"].strip()
        # If using relative path notation like "." or "./", convert to absolute
        if raw_path == "." or raw_path == "./":
            path = os.getcwd()
            source = "current directory (from relative path)"
        else:
            path = os.path.abspath(raw_path)
            source = "arguments parameter"
    # Then check environment variable
    elif environment_variable and os.environ.get(environment_variable) is not None and os.environ.get(environment_variable).strip() != '':
        path = os.path.abspath(os.environ.get(environment_variable))
        source = f"{environment_variable} environment variable"
    # Default to current directory if not set
    else:
        current_dir = os.getcwd()
        # Check if current directory is root
        if current_dir == '/':
            # Current directory is root - need user input
            raise ValueError("Current directory is the root directory. Please provide a specific project path.")
        else:
            path = current_dir
            source = "current directory"
    
    # Safety check: Never write to root directory
    is_root = path == '/' or path == '\\'
    if is_root:
        # Root directory was specified either by argument or env var
        # Check if current directory is also root
        current_dir = os.getcwd()
        if current_dir == '/':
            # Both specified path and current dir are root - need user input
            raise ValueError("Specified path is root directory and current directory is also root. Please provide a non-root project path.")
        else:
            # Use current dir as fallback
            path = current_dir
            source = "current directory (safety fallback from root)"
            is_root = False
            logger.warning("Attempted to use root directory. Falling back to current working directory for safety.")
    
    # Check if path exists and is writable
    if not os.path.exists(path):
        # Path doesn't exist - check if current dir is root
        current_dir = os.getcwd()
        if current_dir == '/':
            # Current directory is root - need user input
            raise ValueError(f"Path {path} does not exist, and current directory is root. Please provide a valid project path.")
        else:
            # Use current dir as fallback
            logger.warning(f"Path {path} does not exist. Falling back to current directory: {current_dir}")
            path = current_dir
            source = "current directory (fallback from non-existent path)"
            is_root = current_dir == '/'
    
    if not os.access(path, os.W_OK):
        # Path is not writable - check if current dir is root
        current_dir = os.getcwd()
        if current_dir == '/':
            # Current directory is root - need user input
            raise ValueError(f"Path {path} is not writable, and current directory is root. Please provide a valid, writable project path.")
        else:
            # Use current dir as fallback
            logger.warning(f"Path {path} is not writable. Falling back to current directory: {current_dir}")
            path = current_dir
            source = "current directory (fallback from non-writable path)"
            is_root = current_dir == '/'
    
    return path, is_root, source

@mcp.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    
    Returns:
        A list of Tool objects defining the available tools and their arguments.
    """
    # Start with the standard tools
    tools = [
        types.Tool(
            name="initialize-ide",
            description="Initialize a project with rules for a specific IDE. The project path will default to the PROJECT_PATH environment variable if set, or the current directory if not set.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ide": {
                        "type": "string", 
                        "description": "IDE to initialize (cursor, windsurf, cline, or copilot). Defaults to cursor if not specified.",
                        "enum": ["cursor", "windsurf", "cline", "copilot"],
                        "default": "cursor"
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Custom project path to use (optional). If not provided, will use PROJECT_PATH environment variable or current directory."
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="prime-context",
            description="Analyzes project's AI documentation to build contextual understanding. This tool examines PRD, architecture docs, stories, and other AI-generated artifacts to provide a comprehensive project overview and current development state. Always prioritizes data from the ai-docs directory before falling back to README.md.",
            inputSchema={
                "type": "object",
                "properties": {
                    "depth": {
                        "type": "string",
                        "description": "Level of detail to include (minimal, standard, comprehensive)",
                        "enum": ["minimal", "standard", "comprehensive"],
                        "default": "standard"
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional specific areas to focus on (e.g., ['architecture', 'current_story', 'progress'])"
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Custom project path to use (optional). If not provided, will use PROJECT_PATH environment variable or current directory."
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get-project-settings",
            description="Returns comprehensive project settings including project path (defaults to user's home directory), knowledge graph directory, AI docs directory, and other agile flow configuration. Use this to understand your project's structure and agile workflow settings. The project path will default to the user's home directory if PROJECT_PATH environment variable is not set.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="get-safe-project-path",
            description="Get a safe, writable project path that can be used for file operations. If the root directory is detected, this will automatically use the current working directory instead.",
            inputSchema={
                "type": "object",
                "properties": {
                    "proposed_path": {
                        "type": "string",
                        "description": "Optional path to check. If not provided, standard environment variables or current directory will be used."
                    }
                },
                "required": [],
            },
        ),
    ]
    
    # Add memory graph tools if available
    if 'memory_tools' in globals() and memory_tools is not None:
        tools.extend(memory_tools)
    
    return tools

@mcp.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[dict]
) -> List[types.TextContent]:
    """
    Handle tool execution requests.
    
    This function processes tool calls based on the name and arguments provided.
    It handles errors by returning error messages with the isError flag set to True.
    
    Args:
        name: The name of the tool to call
        arguments: The arguments to pass to the tool, or None
        
    Returns:
        A list of responses from the tool
    """
    logger.info(f"Handling tool call: {name}")
    logger.debug(f"Tool arguments: {arguments or {}}")
    
    # Validate arguments if they exist
    if arguments is None and name not in ["get_project_info", "get_mermaid_diagram", "update_markdown_with_mermaid", "update_mermaid_diagram"]:
        return [create_text_response(f"Error: The tool '{name}' requires arguments, but none were provided.", is_error=True)]
    
    try:
        if name == "initialize-ide":
            # Get a safe project path using the utility function
            try:
                project_path, is_root, source = get_safe_project_path(arguments)
                logger.info(f"Using project_path from {source}: {project_path}")
            except ValueError as e:
                # Handle case where current directory is root
                current_dir = os.getcwd()
                response_data = {
                    "error": str(e),
                    "status": "error",
                    "needs_user_input": True,
                    "current_directory": current_dir,
                    "is_root": current_dir == "/",
                    "message": "Please provide a specific project path using the 'project_path' argument.",
                    "success": False
                }
                return [create_text_response(json.dumps(response_data, indent=2), is_error=True)]
            
            # Check if IDE is specified in arguments
            if not arguments or "ide" not in arguments:
                # If IDE is not specified, use the default "cursor"
                ide = "cursor"
                logger.info("IDE not specified, defaulting to 'cursor'")
            else:
                ide = arguments["ide"]
            
            # Always back up existing rule files (but not templates)
            backup_existing = True
            
            # Validate IDE
            if ide not in ["cursor", "windsurf", "cline", "copilot"]:
                raise ValueError("Invalid IDE. Must be one of: cursor, windsurf, cline, or copilot")
            
            # Log which source was used for project_path
            logger.info(f"Using project_path from {source}: {project_path}")
            print(f"initialize-ide using project_path from {source}: {project_path}")
            
            # At this point, we've already verified the path exists and is writable in get_safe_project_path
            
            if ide == "cursor":
                # Initialize Cursor rules
                cursor_dir = os.path.join(project_path, ".cursor")
                rules_dir = os.path.join(cursor_dir, "rules")
                # Place ai-templates at the project root
                templates_dir = os.path.join(project_path, ".ai-templates")
                
                os.makedirs(rules_dir, exist_ok=True)
                os.makedirs(templates_dir, exist_ok=True)
                
                # Get paths to our rule and template files
                server_dir = os.path.dirname(os.path.abspath(__file__))
                cursor_rules_dir = os.path.join(server_dir, "cursor_rules")
                ai_templates_dir = os.path.join(server_dir, "ai-templates")
                
                # Verify source directories exist
                if not os.path.exists(cursor_rules_dir):
                    raise FileNotFoundError(f"Source rules directory not found: {cursor_rules_dir}")
                if not os.path.exists(ai_templates_dir):
                    raise FileNotFoundError(f"Source templates directory not found: {ai_templates_dir}")
                
                # Track what files were initialized
                initialized_rules = []
                initialized_templates = []
                
                # First, handle any existing files that need backup
                existing_files = os.listdir(rules_dir) if os.path.exists(rules_dir) else []
                for existing_file in existing_files:
                    if backup_existing:
                        src = os.path.join(rules_dir, existing_file)
                        backup = src + ".back"
                        if os.path.exists(src):
                            shutil.copy2(src, backup)
                            initialized_rules.append({"file_name": existing_file, "status": "backed_up"})
                
                # Copy rules
                for rule_file in os.listdir(cursor_rules_dir):
                    if not rule_file.endswith('.md'):
                        continue
                    
                    src = os.path.join(cursor_rules_dir, rule_file)
                    # Convert .md to .mdc for the destination file
                    dst = os.path.join(rules_dir, rule_file.replace('.md', '.mdc'))
                    
                    # Copy the file
                    shutil.copy2(src, dst)
                    initialized_rules.append({"file_name": rule_file, "status": "copied"})
                
                # Handle existing template files
                existing_templates = os.listdir(templates_dir) if os.path.exists(templates_dir) else []
                
                # Copy templates - always overwrite without conditional logic
                for template_file in os.listdir(ai_templates_dir):
                    src = os.path.join(ai_templates_dir, template_file)
                    dst = os.path.join(templates_dir, template_file)
                    
                    # Copy the file, always overwriting existing files
                    shutil.copy2(src, dst)
                    initialized_templates.append({"file_name": template_file, "status": "copied"})
                
                # Create response
                response_data = {
                    "initialized_rules": initialized_rules,
                    "initialized_templates": initialized_templates,
                    "rules_directory": os.path.abspath(rules_dir),
                    "templates_directory": os.path.abspath(templates_dir),
                    "success": True
                }
                
                return [create_text_response(json.dumps(response_data, indent=2))]
            elif ide == "windsurf":
                # Initialize Windsurf rules
                windsurf_rule_file = os.path.join(project_path, ".windsurfrules")
                
                # Backup if needed
                if os.path.exists(windsurf_rule_file) and backup_existing:
                    backup = windsurf_rule_file + ".back"
                    os.rename(windsurf_rule_file, backup)
                    status = "backed up existing file"
                else:
                    status = "no existing file to backup"
                
                # Get the windsurf template path
                server_dir = os.path.dirname(os.path.abspath(__file__))
                ide_rules_dir = os.path.join(server_dir, "ide_rules")
                template_file = os.path.join(ide_rules_dir, "ide_rules.md")
                
                # Copy the template
                shutil.copy2(template_file, windsurf_rule_file)
                
                # Create and populate the ai-templates directory
                templates_dir = os.path.join(project_path, ".ai-templates")
                os.makedirs(templates_dir, exist_ok=True)
                
                # Get paths to our template files
                ai_templates_dir = os.path.join(server_dir, "ai-templates")
                
                # Verify source directories exist
                if not os.path.exists(ai_templates_dir):
                    raise FileNotFoundError(f"Source templates directory not found: {ai_templates_dir}")
                
                # Copy templates - always overwrite without conditional logic
                for template_file in os.listdir(ai_templates_dir):
                    src = os.path.join(ai_templates_dir, template_file)
                    dst = os.path.join(templates_dir, template_file)
                    
                    # Copy the file, always overwriting existing files
                    shutil.copy2(src, dst)
                
                # Create response
                response_data = {
                    "initialized_windsurf": True,
                    "file_path": os.path.abspath(windsurf_rule_file),
                    "templates_directory": os.path.abspath(templates_dir),
                    "status": status,
                    "success": True
                }
                
                return [create_text_response(json.dumps(response_data, indent=2))]
            elif ide == "cline":
                # Initialize Cline rules
                cline_rule_file = os.path.join(project_path, ".clinerules")
                
                # Backup if needed
                if os.path.exists(cline_rule_file) and backup_existing:
                    backup = cline_rule_file + ".back"
                    os.rename(cline_rule_file, backup)
                    status = "backed up existing file"
                else:
                    status = "no existing file to backup"
                
                # Get the cline template path (we'll use the same template)
                server_dir = os.path.dirname(os.path.abspath(__file__))
                ide_rules_dir = os.path.join(server_dir, "ide_rules")
                template_file = os.path.join(ide_rules_dir, "ide_rules.md")
                
                # Copy the template
                shutil.copy2(template_file, cline_rule_file)
                
                # Create and populate the ai-templates directory
                templates_dir = os.path.join(project_path, ".ai-templates")
                os.makedirs(templates_dir, exist_ok=True)
                
                # Get paths to our template files
                ai_templates_dir = os.path.join(server_dir, "ai-templates")
                
                # Verify source directories exist
                if not os.path.exists(ai_templates_dir):
                    raise FileNotFoundError(f"Source templates directory not found: {ai_templates_dir}")
                
                # Copy templates - always overwrite without conditional logic
                for template_file in os.listdir(ai_templates_dir):
                    src = os.path.join(ai_templates_dir, template_file)
                    dst = os.path.join(templates_dir, template_file)
                    
                    # Copy the file, always overwriting existing files
                    shutil.copy2(src, dst)
                
                # Create response
                response_data = {
                    "initialized_cline": True,
                    "file_path": os.path.abspath(cline_rule_file),
                    "templates_directory": os.path.abspath(templates_dir),
                    "status": status,
                    "success": True
                }
                
                return [create_text_response(json.dumps(response_data, indent=2))]
            elif ide == "copilot":
                # Initialize Copilot rules
                github_dir = os.path.join(project_path, ".github")
                os.makedirs(github_dir, exist_ok=True)
                copilot_rule_file = os.path.join(github_dir, "copilot-instructions.md")
                
                # Backup if needed
                if os.path.exists(copilot_rule_file) and backup_existing:
                    backup = copilot_rule_file + ".back"
                    os.rename(copilot_rule_file, backup)
                    status = "backed up existing file"
                else:
                    status = "no existing file to backup"
                
                # Get the copilot template path (we'll use the same template)
                server_dir = os.path.dirname(os.path.abspath(__file__))
                ide_rules_dir = os.path.join(server_dir, "ide_rules")
                template_file = os.path.join(ide_rules_dir, "ide_rules.md")
                
                # Copy the template
                shutil.copy2(template_file, copilot_rule_file)
                
                # Create and populate the ai-templates directory
                templates_dir = os.path.join(project_path, ".ai-templates")
                os.makedirs(templates_dir, exist_ok=True)
                
                # Get paths to our template files
                ai_templates_dir = os.path.join(server_dir, "ai-templates")
                
                # Verify source directories exist
                if not os.path.exists(ai_templates_dir):
                    raise FileNotFoundError(f"Source templates directory not found: {ai_templates_dir}")
                
                # Copy templates - always overwrite without conditional logic
                for template_file in os.listdir(ai_templates_dir):
                    src = os.path.join(ai_templates_dir, template_file)
                    dst = os.path.join(templates_dir, template_file)
                    
                    # Copy the file, always overwriting existing files
                    shutil.copy2(src, dst)
                
                # Create response
                response_data = {
                    "initialized_copilot": True,
                    "file_path": os.path.abspath(copilot_rule_file),
                    "templates_directory": os.path.abspath(templates_dir),
                    "status": status,
                    "success": True
                }
                
                return [create_text_response(json.dumps(response_data, indent=2))]
            else:
                raise ValueError(f"Unknown IDE: {ide}. Supported values are 'cursor', 'windsurf', 'cline', or 'copilot'")
        
        elif name == "prime-context":
            try:
                # Get safe project path
                project_path = None
                if 'project_path' in arguments:
                    project_path = arguments['project_path']
                    logging.info(f"Using project path from arguments: {project_path}")
                else:
                    # Only if not provided in arguments, try environment variables
                    try:
                        project_path, is_root, source = get_safe_project_path(
                            None,
                            environment_variable="AGILE_FLOW_PROJECT_PATH"
                        )
                        logging.info(f"Using project path from {source}: {project_path}")
                    except ValueError:
                        try:
                            project_path, is_root, source = get_safe_project_path(
                                None,
                                environment_variable="PROJECT_PATH",
                                default=os.getcwd()
                            )
                            logging.info(f"Using project path from {source}: {project_path}")
                        except ValueError as e:
                            return [create_text_response(f"Error: {str(e)}", is_error=True)]
                    
                if project_path == "/":
                    return [create_text_response("Error: Current directory is root. This is likely not the correct project path.", is_error=True)]
                
                logging.info(f"Prime context using project path: {project_path}")
                
                # Parse arguments
                depth = arguments.get("depth", "standard")
                focus_areas = arguments.get("focus_areas", [])
                
                # Check if ai-docs directory exists
                ai_docs_dir = os.path.join(project_path, "ai-docs")
                if not os.path.isdir(ai_docs_dir):
                    return [create_text_response("Error: AI docs directory not found. Run 'initialize-ide' to set up project structure.", is_error=True)]
                
                # Initialize context data structure
                context = {
                    "project": {
                        "name": os.path.basename(project_path),  # Will be overridden if PRD or README has a title
                        "overview": "", 
                        "status": "Unknown",
                        "readme": None
                    },
                    "architecture": {"overview": "", "status": "Unknown"},
                    "epics": [],
                    "current_epic": None,
                    "current_story": None,
                    "progress": {
                        "epics_total": 0,
                        "epics_completed": 0,
                        "stories_total": 0,
                        "stories_completed": 0,
                        "stories_in_progress": 0,
                        "tasks_total": 0,
                        "tasks_completed": 0,
                        "tasks_percentage": 0
                    }
                }
                
                # Look for Makefile in project root
                makefile_path = os.path.join(project_path, "Makefile")
                makefile_commands = extract_makefile_commands(makefile_path)
                
                if makefile_commands:
                    context["project"]["makefile_commands"] = makefile_commands
                    logging.info("Found Makefile with commands")

                # Read project's README.md as a primary source for context (not a fallback)
                readme_path = os.path.join(project_path, "README.md")
                readme_content = None
                
                if os.path.isfile(readme_path):
                    with open(readme_path, 'r') as file:
                        readme_content = file.read()
                        context["project"]["readme"] = readme_content
                        
                        # Extract title from README
                        readme_title = extract_markdown_title(readme_content)
                        if readme_title:
                            # Store README title for potential use
                            readme_title_for_use = readme_title
                        
                        # Extract status from README
                        readme_status = extract_status(readme_content)
                        if readme_status:
                            # Store README status for potential use
                            readme_status_for_use = readme_status
                            
                    logging.info(f"Found README.md at project root")
                
                # Look for additional documentation files in ai-docs
                documentation_files = {}
                for filename in os.listdir(ai_docs_dir):
                    if filename.endswith('.md') and filename not in ['README.md', 'prd.md', 'architecture.md']:
                        file_path = os.path.join(ai_docs_dir, filename)
                        if os.path.isfile(file_path):
                            with open(file_path, 'r') as file:
                                content = file.read()
                                name = filename[:-3]  # Remove .md extension
                                documentation_files[name] = {
                                    "title": extract_markdown_title(content),
                                    "content": summarize_content(content, depth),
                                    "status": extract_status(content)
                                }
                
                # Add additional documentation to context if any was found
                if documentation_files:
                    context["additional_docs"] = documentation_files
                    logging.info(f"Found {len(documentation_files)} additional documentation files in ai-docs")
                
                # Read PRD
                prd_path = os.path.join(ai_docs_dir, "prd.md")
                if os.path.isfile(prd_path):
                    with open(prd_path, 'r') as file:
                        prd_content = file.read()
                        
                        # Extract information from PRD
                        title = extract_markdown_title(prd_content)
                        if title:
                            # Use PRD title for project name, but keep README info for context
                            context["project"]["name"] = title
                            context["project"]["prd_title"] = title
                        elif 'readme_title_for_use' in locals():
                            # Use README title if PRD has no title
                            context["project"]["name"] = readme_title_for_use
                        
                        # Extract status from PRD
                        status = extract_status(prd_content)
                        if status:
                            # Use PRD status, but keep README status for context
                            context["project"]["status"] = status
                            context["project"]["prd_status"] = status
                        elif 'readme_status_for_use' in locals():
                            # Use README status if PRD has no status
                            context["project"]["status"] = readme_status_for_use
                        
                        # Store PRD overview alongside README content
                        prd_overview = summarize_content(prd_content)
                        context["project"]["prd_overview"] = prd_overview
                        context["project"]["overview"] = prd_overview
                else:
                    # Use README content as overview if no PRD
                    if readme_content:
                        context["project"]["overview"] = readme_content
                        # Also use README title and status if we have them and there's no PRD
                        if 'readme_title_for_use' in locals():
                            context["project"]["name"] = readme_title_for_use
                        if 'readme_status_for_use' in locals():
                            context["project"]["status"] = readme_status_for_use
                
                # Read and parse architecture document
                arch_path = os.path.join(ai_docs_dir, "architecture.md")
                if os.path.isfile(arch_path):
                    with open(arch_path, 'r') as file:
                        arch_content = file.read()
                        
                        # Extract status
                        arch_status = extract_status(arch_content)
                        if arch_status:
                            context["architecture"]["status"] = arch_status
                        
                        # Extract overview
                        context["architecture"]["overview"] = summarize_content(arch_content)
                else:
                    context["architecture"]["overview"] = "No architecture documentation available."
                
                # Process epics
                epics_dir = os.path.join(ai_docs_dir, "epics")
                current_epic = None
                current_story = None
                
                if os.path.exists(epics_dir):
                    epic_dirs = [d for d in os.listdir(epics_dir) 
                                 if os.path.isdir(os.path.join(epics_dir, d))]
                    
                    for epic_dir in epic_dirs:
                        epic_path = os.path.join(epics_dir, epic_dir)
                        epic_md_path = os.path.join(epic_path, "epic.md")
                        
                        if not os.path.exists(epic_md_path):
                            continue
                        
                        with open(epic_md_path, "r") as f:
                            epic_content = f.read()
                        
                        epic_data = {
                            "name": extract_markdown_title(epic_content),
                            "id": epic_dir,
                            "status": extract_status(epic_content),
                            "description": summarize_content(epic_content, depth),
                            "stories": [],
                            "progress": {
                                "total_stories": 0,
                                "complete": 0,
                                "in_progress": 0,
                                "draft": 0
                            }
                        }
                        
                        # Process stories within epic
                        stories_dir = os.path.join(epic_path, "stories")
                        if os.path.exists(stories_dir):
                            story_files = glob.glob(os.path.join(stories_dir, "*.md"))
                            
                            for story_file in story_files:
                                with open(story_file, "r") as f:
                                    story_content = f.read()
                                
                                story_status = extract_status(story_content)
                                story_name = extract_markdown_title(story_content)
                                
                                # Update epic story counts
                                epic_data["progress"]["total_stories"] += 1
                                
                                if story_status.lower() == "complete":
                                    epic_data["progress"]["complete"] += 1
                                elif story_status.lower() == "in progress":
                                    epic_data["progress"]["in_progress"] += 1
                                    
                                    # Track current story and epic
                                    if current_story is None:
                                        current_story = {
                                            "name": story_name,
                                            "file": os.path.basename(story_file),
                                            "status": story_status,
                                            "content": summarize_content(story_content, depth),
                                            "completion": extract_task_completion(story_content)
                                        }
                                        current_epic = epic_data
                                else:
                                    # Assume draft status
                                    epic_data["progress"]["draft"] += 1
                                
                                # Only include detailed story info for comprehensive depth
                                if depth == "comprehensive":
                                    story_data = {
                                        "name": story_name,
                                        "file": os.path.basename(story_file),
                                        "status": story_status,
                                        "content": summarize_content(story_content, "minimal" if depth != "comprehensive" else depth)
                                    }
                                    epic_data["stories"].append(story_data)
                        
                        # Determine epic status if not explicitly set
                        if epic_data["status"] == "Unknown":
                            if epic_data["progress"]["total_stories"] == 0:
                                epic_data["status"] = "Empty"
                            elif epic_data["progress"]["complete"] == epic_data["progress"]["total_stories"]:
                                epic_data["status"] = "Complete"
                            elif epic_data["progress"]["in_progress"] > 0:
                                epic_data["status"] = "In Progress"
                            else:
                                epic_data["status"] = "Draft"
                        
                        context["epics"].append(epic_data)
                
                # Set current epic and story
                if current_epic is not None:
                    context["current_epic"] = {
                        "name": current_epic["name"],
                        "id": current_epic["id"],
                        "status": current_epic["status"],
                        "progress": current_epic["progress"]
                    }
                
                if current_story is not None:
                    context["current_story"] = current_story
                    # Update global progress with current story task completion
                    if "completion" in current_story:
                        context["progress"]["tasks_total"] = current_story["completion"]["total"]
                        context["progress"]["tasks_completed"] = current_story["completion"]["completed"]
                        context["progress"]["tasks_percentage"] = current_story["completion"]["percentage"]
                
                # Generate human-readable summary based on aggregated data
                summary = f"# {context['project']['name']} Project Context\n\n"
                
                # Project overview combining PRD and README data
                summary += "## Project Overview\n"
                summary += f"Status: {context['project']['status']}\n\n"
                
                # Include overview from PRD or README
                if context["project"]["overview"]:
                    summary += context["project"]["overview"] + "\n\n"
                else:
                    summary += "No project overview available.\n\n"
                
                # README information (always include, even if used for overview)
                if context["project"]["readme"]:
                    summary += "## From Project README\n"
                    # Extract just the essential parts for the summary to keep it concise
                    readme_summary = summarize_content(context["project"]["readme"])
                    summary += readme_summary + "\n\n"
                
                # Makefile commands if available
                if "makefile_commands" in context["project"] and context["project"]["makefile_commands"]:
                    summary += "## Project Commands (from Makefile)\n"
                    for category, commands in context["project"]["makefile_commands"].items():
                        summary += f"### {category.title()} Commands\n"
                        for cmd in commands:
                            summary += f"- `make {cmd['target']}`: {cmd['command']}\n"
                        summary += "\n"
                
                # Additional documentation if present and depth is comprehensive
                if "additional_docs" in context and depth == "comprehensive":
                    summary += "## Additional Documentation\n"
                    for doc_name, doc_info in context["additional_docs"].items():
                        summary += f"### {doc_info['title']} ({doc_info['status']})\n"
                        summary += doc_info['content'] + "\n\n"
                
                # Architecture
                if depth != "minimal":
                    summary += "## Architecture\n"
                    if context["architecture"]["status"]:
                        summary += f"Status: {context['architecture']['status']}\n\n"
                    
                    if context["architecture"]["overview"]:
                        summary += context["architecture"]["overview"] + "\n\n"
                    else:
                        summary += "No architecture documentation available.\n\n"
                
                # Epics
                summary += "## Epics\n"
                if context["epics"]:
                    for epic in context["epics"]:
                        progress = epic["progress"]
                        progress_percentage = 0
                        if progress["total_stories"] > 0:
                            progress_percentage = round(progress["complete"] / progress["total_stories"] * 100)
                        
                        summary += f"### {epic['name']} ({epic['status']})\n"
                        summary += f"Progress: {progress_percentage}% - {progress['complete']}/{progress['total_stories']} stories complete\n"
                        summary += f"Stories: {progress['complete']} complete, {progress['in_progress']} in progress, {progress['draft']} draft\n\n"
                else:
                    summary += "No epics found.\n\n"
                
                # Current focus
                summary += "## Current Focus\n"
                if context["current_epic"] and context["current_story"]:
                    summary += f"Epic: {context['current_epic']['name']} ({context['current_epic']['status']})\n"
                    summary += f"Story: {context['current_story']['name']} ({context['current_story']['status']})\n"
                    summary += f"Progress: {context['progress']['tasks_percentage']}% - {context['progress']['tasks_completed']}/{context['progress']['tasks_total']} tasks complete\n\n"
                    summary += context['current_story']['content']
                else:
                    summary += "No current work items identified.\n"
                
                # Create final context object
                result = {
                    "context": context,
                    "summary": summary
                }
                
                # Filter by focus areas if specified
                if focus_areas:
                    filtered_context = {}
                    for area in focus_areas:
                        if area in context:
                            filtered_context[area] = context[area]
                    
                    if filtered_context:
                        result["context"] = filtered_context
                
                return [create_text_response(json.dumps(result, indent=2))]
            except Exception as e:
                logging.error(f"Error in prime-context: {str(e)}")
                traceback.print_exc()
                return [create_text_response(f"Error: {str(e)}", is_error=True)]
        
        elif name == "get-project-settings":
            logger.info("Getting project settings (defaults to user's home directory)")
            
            # Use the common utility function to get project settings
            response_data = get_project_settings()
            
            # Log the response for debugging
            logger.info(f"Project settings response: {response_data}")
            
            return [create_text_response(json.dumps(response_data, indent=2))]
        
        elif name == "get-safe-project-path":
            # Get a proposed path from arguments if provided
            proposed_path = arguments.get("proposed_path", "").strip() if arguments else ""
            
            try:
                # Use the get_safe_project_path function
                safe_path, is_root, source = get_safe_project_path({"project_path": proposed_path} if proposed_path else None)
                
                # Create response for successful case
                response_data = {
                    "safe_path": safe_path,
                    "source": source,
                    "is_root": is_root,
                    "is_writable": os.access(safe_path, os.W_OK),
                    "exists": os.path.exists(safe_path),
                    "current_directory": os.getcwd()
                }
                
                return [create_text_response(json.dumps(response_data, indent=2))]
            except ValueError as e:
                # Handle case where current directory is root
                current_dir = os.getcwd()
                response_data = {
                    "error": str(e),
                    "needs_user_input": True,
                    "current_directory": current_dir,
                    "safe_path": None,
                    "is_root": current_dir == "/",
                    "message": "Please provide a specific project path using the 'proposed_path' argument."
                }
                
                return [create_text_response(json.dumps(response_data, indent=2), is_error=True)]
        
        # Handle memory graph tools
        elif name in ["get_project_info", "get_mermaid_diagram", "update_mermaid_diagram", "update_markdown_with_mermaid", "create_entities", "create_relations", "add_observations", 
                    "delete_entities", "delete_observations", "delete_relations",
                    "read_graph", "search_nodes", "open_nodes"]:
            # Check if memory_manager is initialized
            if memory_manager is None:
                return [create_text_response("Memory graph manager is not initialized yet. Please try again in a moment.", is_error=True)]
            
            if name == "get_project_info":
                project_info = memory_manager.get_project_info()
                md_path = memory_manager.graph_path.replace(".json", ".md")
                md_exists = os.path.exists(md_path)
                
                response = {
                    "project_type": project_info["project_type"],
                    "project_metadata": project_info["project_metadata"],
                    "graph_path": memory_manager.graph_path,
                    "markdown_path": md_path,
                    "markdown_exists": md_exists,
                    "entity_count": len(memory_manager.graph.entities),
                    "relation_count": len(memory_manager.graph.relations)
                }
                
                return [create_text_response(json.dumps(response, indent=2))]
                
            elif name in ["get_mermaid_diagram", "update_mermaid_diagram", "update_markdown_with_mermaid"]:
                # Generate and save the Markdown file with embedded Mermaid diagram
                mermaid_content = memory_manager.update_markdown_with_mermaid()
                md_path = memory_manager.graph_path.replace(".json", ".md")
                
                # Create a descriptive status message
                if os.path.exists(md_path):
                    save_status = f"Markdown file with embedded Mermaid diagram saved to {md_path}"
                else:
                    save_status = f"Warning: Failed to save Markdown file with embedded Mermaid diagram to {md_path}"
                
                response = {
                    "markdown_content": mermaid_content,
                    "markdown_path": md_path,
                    "entity_count": len(memory_manager.graph.entities),
                    "relation_count": len(memory_manager.graph.relations),
                    "save_status": save_status
                }
                
                # Return both the Markdown content and the save status
                return [create_text_response(f"{mermaid_content}\n\n{save_status}")]
                
            elif name == "create_entities":
                try:
                    if "entities" not in arguments:
                        return [create_text_response("Error: Missing 'entities' field in arguments", is_error=True)]
                    
                    entities_arg = arguments["entities"]
                    if not isinstance(entities_arg, list):
                        return [create_text_response("Error: 'entities' must be a list", is_error=True)]
                    
                    # Validate each entity in the list
                    for i, entity in enumerate(entities_arg):
                        if not isinstance(entity, dict):
                            return [create_text_response(f"Error: Entity at index {i} is not a valid object", is_error=True)]
                        
                        if "name" not in entity:
                            return [create_text_response(f"Error: Entity at index {i} is missing required 'name' field", is_error=True)]
                        
                        if "entityType" not in entity:
                            return [create_text_response(f"Error: Entity at index {i} is missing required 'entityType' field", is_error=True)]
                        
                        if "observations" in entity and not isinstance(entity["observations"], list):
                            return [create_text_response(f"Error: 'observations' for entity '{entity['name']}' must be a list", is_error=True)]
                    
                    # If validation passes, create the entities
                    entities = memory_manager.create_entities(entities_arg)
                    return [create_text_response(f"{len(entities)} entities created successfully")]
                except Exception as e:
                    logger.error(f"Error creating entities: {str(e)}")
                    return [create_text_response(f"Error creating entities: {str(e)}", is_error=True)]
                
            elif name == "create_relations":
                try:
                    if "relations" not in arguments:
                        return [create_text_response("Error: Missing 'relations' field in arguments", is_error=True)]
                    
                    relations_arg = arguments["relations"]
                    if not isinstance(relations_arg, list):
                        return [create_text_response("Error: 'relations' must be a list", is_error=True)]
                    
                    # Validate each relation in the list
                    for i, relation in enumerate(relations_arg):
                        if not isinstance(relation, dict):
                            return [create_text_response(f"Error: Relation at index {i} is not a valid object", is_error=True)]
                        
                        if "from" not in relation:
                            return [create_text_response(f"Error: Relation at index {i} is missing required 'from' field", is_error=True)]
                        
                        if "to" not in relation:
                            return [create_text_response(f"Error: Relation at index {i} is missing required 'to' field", is_error=True)]
                        
                        if "relationType" not in relation:
                            return [create_text_response(f"Error: Relation at index {i} is missing required 'relationType' field", is_error=True)]
                    
                    # If validation passes, create the relations
                    relations = memory_manager.create_relations(relations_arg)
                    return [create_text_response(f"{len(relations)} relations created successfully")]
                except Exception as e:
                    logger.error(f"Error creating relations: {str(e)}")
                    return [create_text_response(f"Error creating relations: {str(e)}", is_error=True)]
                
            elif name == "add_observations":
                try:
                    if "observations" not in arguments:
                        return [create_text_response("Error: Missing 'observations' field in arguments", is_error=True)]
                    
                    observations_arg = arguments["observations"]
                    if not isinstance(observations_arg, list):
                        return [create_text_response("Error: 'observations' must be a list", is_error=True)]
                    
                    # Validate each observation in the list
                    for i, observation in enumerate(observations_arg):
                        if not isinstance(observation, dict):
                            return [create_text_response(f"Error: Observation at index {i} is not a valid object", is_error=True)]
                        
                        if "entityName" not in observation:
                            return [create_text_response(f"Error: Observation at index {i} is missing required 'entityName' field", is_error=True)]
                        
                        if "contents" not in observation:
                            return [create_text_response(f"Error: Observation at index {i} is missing required 'contents' field", is_error=True)]
                        
                        if not isinstance(observation["contents"], list):
                            return [create_text_response(f"Error: 'contents' for entity '{observation['entityName']}' must be a list", is_error=True)]
                    
                    # If validation passes, add the observations
                    results = memory_manager.add_observations(observations_arg)
                    total_observations = sum(len(r["addedObservations"]) for r in results)
                    return [create_text_response(f"{total_observations} observations added to {len(results)} entities")]
                except Exception as e:
                    logger.error(f"Error adding observations: {str(e)}")
                    return [create_text_response(f"Error adding observations: {str(e)}", is_error=True)]
                
            elif name == "delete_entities":
                graph = memory_manager.delete_entities(arguments["entityNames"])
                return [create_text_response(f"Entities deleted. Graph now has {len(graph.entities)} entities and {len(graph.relations)} relations")]
                
            elif name == "delete_observations":
                graph = memory_manager.delete_observations(arguments["deletions"])
                return [create_text_response(f"Observations deleted. Graph updated with {len(graph.entities)} entities")]
                
            elif name == "delete_relations":
                graph = memory_manager.delete_relations(arguments["relations"])
                return [create_text_response(f"Relations deleted. Graph now has {len(graph.relations)} relations")]
                
            elif name == "read_graph":
                graph = memory_manager.read_graph()
                return [create_text_response(f"Graph contains {len(graph.entities)} entities and {len(graph.relations)} relations")]
                
            elif name == "search_nodes":
                result_graph = memory_manager.search_nodes(arguments["query"])
                return [create_text_response(f"Found {len(result_graph.entities)} entities and {len(result_graph.relations)} relations matching query")]
                
            elif name == "open_nodes":
                result_graph = memory_manager.open_nodes(arguments["names"])
                return [create_text_response(f"Opened {len(result_graph.entities)} entities with {len(result_graph.relations)} relations")]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in tool call: {str(e)}")
        return [create_text_response(str(e), is_error=True)]

def extract_markdown_title(content):
    """Extract the title from markdown content.
    
    Args:
        content (str): Markdown content
        
    Returns:
        str: The title of the document, or "Untitled" if no title found
    """
    lines = content.split('\n')
    for line in lines:
        # Look for level 1 heading
        if line.strip().startswith('# '):
            return line.strip()[2:].strip()
    
    return "Untitled"

def extract_status(content):
    """Extract the status from markdown content.
    
    Args:
        content (str): Markdown content
        
    Returns:
        str: The status of the document, or "Unknown" if no status found
    """
    # Check for "## Status" section
    status_pattern = r"^\s*##\s+Status\s*$"
    status_section = None
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if re.search(status_pattern, line, re.IGNORECASE):
            status_section = i
            break
    
    if status_section is not None:
        # Look for status value in the lines after the section heading
        for i in range(status_section + 1, min(status_section + 10, len(lines))):
            line = lines[i].strip()
            if line and not line.startswith('#'):
                # Extract status value which could be in formats like:
                # - Status: Draft
                # - Draft
                # - **Status**: Draft
                
                # Remove markdown formatting and list markers
                line = re.sub(r'^\s*[-*]\s+', '', line)
                line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
                
                # Check if line contains a status indicator
                if ':' in line:
                    parts = line.split(':', 1)
                    if parts[1].strip():
                        return parts[1].strip()
                
                # If no colon, check for common status values
                statuses = ["Draft", "In Progress", "Complete", "Approved", "Current", "Future"]
                for status in statuses:
                    if status.lower() in line.lower():
                        return status
                
                # If we got to a non-empty line but didn't find a status, use the whole line
                return line
    
    return "Unknown"

def summarize_content(content, depth="standard"):
    """Summarize markdown content based on depth.
    
    Args:
        content (str): Markdown content
        depth (str): Summarization depth ('minimal', 'standard', or 'comprehensive')
        
    Returns:
        str: Summarized content
    """
    lines = content.split('\n')
    
    if depth == "minimal":
        # Just return the title and a few key sections
        result = []
        
        # Extract title
        title = extract_markdown_title(content)
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
                if not lines[i].startswith('#'):
                    result.append(lines[i])
                else:
                    break
        
        return '\n'.join(result)
    
    elif depth == "standard":
        # Return all headings and their first paragraph
        result = []
        current_heading = None
        paragraph_lines = []
        
        for line in lines:
            if line.startswith('#'):
                # If we were building a paragraph, add it to result
                if paragraph_lines:
                    result.append('\n'.join(paragraph_lines))
                    paragraph_lines = []
                
                # Add the heading
                result.append(line)
                current_heading = line
            elif line.strip() == '' and paragraph_lines:
                # End of paragraph
                result.append('\n'.join(paragraph_lines))
                paragraph_lines = []
            elif current_heading is not None and line.strip():
                # Add line to current paragraph
                paragraph_lines.append(line)
        
        # Add any remaining paragraph
        if paragraph_lines:
            result.append('\n'.join(paragraph_lines))
        
        return '\n'.join(result)
    
    else:  # comprehensive or any other value
        return content

def extract_task_completion(content):
    """Extract task completion information from markdown content.
    
    Args:
        content (str): Markdown content
        
    Returns:
        dict: Task completion information
    """
    lines = content.split('\n')
    total = 0
    completed = 0
    
    # Look for task items (- [ ] or - [x])
    for line in lines:
        line = line.strip()
        if re.match(r'^\s*-\s*\[\s*\]\s+', line):
            total += 1
        elif re.match(r'^\s*-\s*\[\s*x\s*\]\s+', line):
            total += 1
            completed += 1
    
    return {
        "total": total,
        "completed": completed,
        "percentage": round(completed / total * 100) if total > 0 else 0
    }

def extract_makefile_commands(makefile_path):
    """Extract key shell commands from a Makefile.
    
    Args:
        makefile_path (str): Path to the Makefile
        
    Returns:
        dict: Dictionary of command categories and their commands
    """
    if not os.path.exists(makefile_path):
        return None
    
    try:
        with open(makefile_path, 'r') as file:
            content = file.read()
        
        # Parse Makefile content to extract commands and targets
        commands = {}
        lines = content.split('\n')
        current_target = None
        
        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue
                
            # Look for target definitions (lines ending with a colon)
            if ':' in line and not line.strip().startswith('\t'):
                # Extract target name (everything before the colon and optional dependencies)
                target_parts = line.split(':')[0].strip().split()
                if target_parts:
                    current_target = target_parts[0]
                    
                    # Skip phony targets or other special targets
                    if current_target.startswith('.'):
                        current_target = None
                        continue
                        
                    # Look for the command in the next lines
                    for j in range(i + 1, len(lines)):
                        cmd_line = lines[j].strip()
                        # Commands in Makefiles typically start with a tab
                        if cmd_line and lines[j].startswith('\t'):
                            # Remove the tab
                            command = cmd_line
                            
                            # Categorize the command
                            if any(keyword in current_target.lower() for keyword in ['test', 'pytest', 'check']):
                                category = 'testing'
                            elif any(keyword in current_target.lower() for keyword in ['build', 'compile', 'install', 'setup']):
                                category = 'build'
                            elif any(keyword in current_target.lower() for keyword in ['run', 'start', 'serve', 'dev']):
                                category = 'run'
                            elif any(keyword in current_target.lower() for keyword in ['clean', 'clear', 'reset']):
                                category = 'clean'
                            elif any(keyword in current_target.lower() for keyword in ['deploy', 'publish', 'release', 'dist']):
                                category = 'deploy'
                            elif any(keyword in current_target.lower() for keyword in ['lint', 'format', 'style', 'check']):
                                category = 'lint'
                            else:
                                category = 'other'
                            
                            if category not in commands:
                                commands[category] = []
                            
                            commands[category].append({
                                'target': current_target,
                                'command': command
                            })
                            break
                    
                    current_target = None
        
        return commands
    except Exception as e:
        logger.error(f"Error parsing Makefile: {str(e)}")
        return None

def handle_brd_commands(command, args):
    """Handle BRD-related commands."""
    if re.match(r"create a new brd for", command, re.IGNORECASE):
        project_name = command.split("for", 1)[1].strip()
        return create_brd(project_name)
    elif re.match(r"initialize brd for", command, re.IGNORECASE):
        project_name = command.split("for", 1)[1].strip()
        return create_brd(project_name)
    elif re.match(r"generate business requirements document for", command, re.IGNORECASE):
        project_name = command.split("for", 1)[1].strip()
        return create_brd(project_name)
    # Handle BRD update commands
    elif re.match(r"add business objective (.*) to brd", command, re.IGNORECASE):
        objective = re.match(r"add business objective (.*) to brd", command, re.IGNORECASE).group(1)
        return add_to_brd_section("Business Objectives", objective)
    elif re.match(r"add market problem (.*) to brd", command, re.IGNORECASE):
        problem = re.match(r"add market problem (.*) to brd", command, re.IGNORECASE).group(1)
        return add_to_brd_section("Market Problem Analysis", problem)
    elif re.match(r"add success metric (.*) to brd", command, re.IGNORECASE):
        metric = re.match(r"add success metric (.*) to brd", command, re.IGNORECASE).group(1)
        return add_to_brd_section("Success Metrics", metric)
    elif re.match(r"update brd status to (.*)", command, re.IGNORECASE):
        status = re.match(r"update brd status to (.*)", command, re.IGNORECASE).group(1)
        return update_document_status("brd", status)
    return None

def create_brd(project_name):
    """Create a Business Requirements Document (BRD) for the given project.
    
    Args:
        project_name (str): The name of the project
        
    Returns:
        str: Confirmation message
    """
    # Check if ai-docs directory exists, create if not
    if not os.path.exists("ai-docs"):
        os.makedirs("ai-docs")
    
    # Read the BRD template
    template_path = ".ai-templates/template-brd.md"
    with open(template_path, "r") as f:
        template_content = f.read()
    
    # Replace placeholders
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    content = template_content.replace("{project-name}", project_name)
    content = content.replace("{date}", today)
    
    # Create the BRD file
    output_path = "ai-docs/brd.md"
    with open(output_path, "w") as f:
        f.write(content)
    
    return f"Created Business Requirements Document for {project_name} in `{output_path}`"

def add_to_brd_section(section_name, content_to_add):
    """Add content to a specific section in the BRD.
    
    Args:
        section_name (str): The name of the section to add content to
        content_to_add (str): The content to add
        
    Returns:
        str: Confirmation message
    """
    brd_path = "ai-docs/brd.md"
    if not os.path.exists(brd_path):
        return "Error: BRD not found. Create a BRD first using 'Create a new BRD for <project-name>'."
    
    with open(brd_path, "r") as f:
        content = f.read()
    
    # Find the section
    section_pattern = f"## {section_name}"
    if section_name not in content:
        return f"Error: Section '{section_name}' not found in the BRD."
    
    # Split the content by sections
    sections = re.split(r"^## ", content, flags=re.MULTILINE)
    updated_content = ""
    
    # Add the first part (before any section)
    if sections[0].strip():
        updated_content += sections[0]
    
    # Process each section
    for i, section in enumerate(sections[1:], 1):
        section_content = "## " + section
        if section.startswith(section_name):
            # Add the new content to this section
            lines = section_content.split("\n")
            # Find where to insert the new content
            insert_index = -1
            for j, line in enumerate(lines):
                if j > 0 and (line.startswith("##") or j == len(lines) - 1):
                    insert_index = j
                    break
            
            if insert_index == -1:
                # If we couldn't find a good spot, just append to the end of the section
                lines.append(f"- {content_to_add}")
            else:
                # Insert before the next section
                lines.insert(insert_index, f"- {content_to_add}")
            
            section_content = "\n".join(lines)
        
        updated_content += section_content
    
    # Write the updated content back to the file
    with open(brd_path, "w") as f:
        f.write(updated_content)
    
    return f"Added '{content_to_add}' to the '{section_name}' section of the BRD."

def update_document_status(doc_type, new_status):
    """Update the status of a document.
    
    Args:
        doc_type (str): The type of document ('brd', 'prd', 'architecture', 'story')
        new_status (str): The new status to set
        
    Returns:
        str: Confirmation message
    """
    # Map document type to file path
    doc_path_map = {
        "brd": "ai-docs/brd.md",
        "prd": "ai-docs/prd.md",
        "architecture": "ai-docs/arch.md",
        # Story paths would need to be handled differently
    }
    
    if doc_type.lower() not in doc_path_map:
        return f"Error: Unknown document type '{doc_type}'"
    
    doc_path = doc_path_map[doc_type.lower()]
    
    if not os.path.exists(doc_path):
        return f"Error: {doc_type.upper()} not found at {doc_path}"
    
    with open(doc_path, "r") as f:
        content = f.read()
    
    # Look for status section
    status_pattern = r"## Status:?\s*(.*)"
    status_match = re.search(status_pattern, content, re.IGNORECASE | re.MULTILINE)
    
    if not status_match:
        # For BRD, look for Document Control section
        if doc_type.lower() == "brd":
            control_pattern = r"## Document Control\s*\n(.*\n)*?[\-\*]\s*\*\*Status:\*\*\s*(.*)"
            control_match = re.search(control_pattern, content, re.IGNORECASE | re.MULTILINE)
            
            if control_match:
                updated_content = re.sub(
                    r"(## Document Control\s*\n(?:.*\n)*?[\-\*]\s*\*\*Status:\*\*\s*)(.*)(\s*)",
                    f"\\1{new_status}\\3",
                    content,
                    flags=re.IGNORECASE | re.MULTILINE
                )
                
                with open(doc_path, "w") as f:
                    f.write(updated_content)
                
                return f"Updated {doc_type.upper()} status to '{new_status}'"
        
        return f"Error: Could not find status section in {doc_type.upper()}"
    
    # Update the status
    updated_content = re.sub(
        r"(## Status:?\s*)(.*)",
        f"\\1{new_status}",
        content,
        flags=re.IGNORECASE | re.MULTILINE
    )
    
    with open(doc_path, "w") as f:
        f.write(updated_content)
    
    return f"Updated {doc_type.upper()} status to '{new_status}'"

async def run_server():
    """
    Run the server using stdin/stdout streams.
    
    This sets up the MCP server to communicate over stdin/stdout,
    which allows it to be used with the MCP protocol directly.
    """
    global memory_tools, memory_manager
    
    logger.info("Starting Simple server (stdin/stdout mode)")
    print("Starting MCP Agile Flow Simple server...", file=sys.stderr)
    
    # Initialize memory graph tools and manager
    try:
        # Register memory tools with the MCP server
        memory_tools, memory_manager = register_memory_tools(mcp)
        logger.info(f"Initialized memory graph manager with path: {memory_manager.graph_path}")
        print(f"Initialized memory graph manager with path: {memory_manager.graph_path}", file=sys.stderr)
    except Exception as e:
        logger.error(f"Error initializing memory graph manager: {e}")
        print(f"Error initializing memory graph manager: {e}", file=sys.stderr)
        # Continue without memory graph functionality
    
    async with stdio.stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            initialization_options=InitializationOptions(
                server_name="MCP Agile Flow - Simple",
                server_version="0.1.0",
                capabilities=mcp.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

def run():
    """Entry point for running the server."""
    asyncio.run(run_server())

if __name__ == "__main__":
    run() 