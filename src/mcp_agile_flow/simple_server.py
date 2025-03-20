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
from typing import Dict, List, Optional, Tuple, Any

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

def get_safe_project_path(arguments: Optional[dict] = None) -> Tuple[str, str]:
    """
    Get a safe project path that is guaranteed to be writable.
    
    Args:
        arguments: Optional arguments dictionary that might contain 'project_path'
        
    Returns:
        Tuple containing (safe_path, source_description)
    """
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
    # Then check AGILE_FLOW_PROJECT_PATH (preferred)
    else:
        agile_flow_project_path = os.environ.get("AGILE_FLOW_PROJECT_PATH")
        # Then check PROJECT_PATH for backward compatibility
        project_path_env = os.environ.get("PROJECT_PATH")
        
        # First check AGILE_FLOW_PROJECT_PATH
        if agile_flow_project_path is not None and agile_flow_project_path.strip() != '':
            # Check if the environment variable points to root
            if agile_flow_project_path.strip() == '/' or agile_flow_project_path.strip() == '\\':
                # If env var points to root, check if current dir is root
                current_dir = os.getcwd()
                if current_dir == '/':
                    # Both env var and current dir are root - need user input
                    raise ValueError("Environment variable points to root directory and current directory is also root. Please provide a specific project path.")
                else:
                    # Use current dir as fallback
                    path = current_dir
                    source = "current directory (env var was root path)"
            else:
                path = os.path.abspath(agile_flow_project_path)
                source = "AGILE_FLOW_PROJECT_PATH environment variable"
        # Then check PROJECT_PATH for backward compatibility
        elif project_path_env is not None and project_path_env.strip() != '':
            # Check if the environment variable points to root
            if project_path_env.strip() == '/' or project_path_env.strip() == '\\':
                # If env var points to root, check if current dir is root
                current_dir = os.getcwd()
                if current_dir == '/':
                    # Both env var and current dir are root - need user input
                    raise ValueError("Environment variable points to root directory and current directory is also root. Please provide a specific project path.")
                else:
                    # Use current dir as fallback
                    path = current_dir
                    source = "current directory (env var was root path)"
            else:
                path = os.path.abspath(project_path_env)
                source = "PROJECT_PATH environment variable (legacy)"
        # Default to current directory if neither is set
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
    if path == '/' or path == '\\':
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
            return current_dir, "current directory (fallback from non-existent path)"
    
    if not os.access(path, os.W_OK):
        # Path is not writable - check if current dir is root
        current_dir = os.getcwd()
        if current_dir == '/':
            # Current directory is root - need user input
            raise ValueError(f"Path {path} is not writable, and current directory is root. Please provide a valid, writable project path.")
        else:
            # Use current dir as fallback
            logger.warning(f"Path {path} is not writable. Falling back to current directory: {current_dir}")
            return current_dir, "current directory (fallback from non-writable path)"
    
    return path, source

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
            name="initialize-ide-rules",
            description="Initialize a project with rules for a specific IDE. The project path will default to the AGILE_FLOW_PROJECT_PATH environment variable if set, falling back to PROJECT_PATH, or the current directory if neither is set.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ide": {
                        "type": "string", 
                        "description": "IDE to initialize (cursor, windsurf, cline, or copilot)",
                        "enum": ["cursor", "windsurf", "cline", "copilot"]
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Custom project path to use (optional). If not provided, will use environment variables or current directory."
                    }
                },
                "required": ["ide"],
            },
        ),
        types.Tool(
            name="initialize-rules",
            description="Initialize Cursor rules for the project (for backward compatibility, use initialize-ide-rules for other IDEs). The project path will default to the AGILE_FLOW_PROJECT_PATH environment variable if set, falling back to PROJECT_PATH, or the current directory if neither is set.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Custom project path to use (optional). If not provided, will use environment variables or current directory."
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get-project-settings",
            description="Returns comprehensive project settings including project path (defaults to user's home directory), knowledge graph directory, AI docs directory, and other agile flow configuration. Use this to understand your project's structure and agile workflow settings. The project path will default to the user's home directory if AGILE_FLOW_PROJECT_PATH or PROJECT_PATH environment variable is not set. AGILE_FLOW_PROJECT_PATH takes precedence over PROJECT_PATH if both are set.",
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
        if name == "initialize-ide-rules":
            # Get a safe project path using the utility function
            try:
                project_path, source = get_safe_project_path(arguments)
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
                # If IDE is not specified, return a message asking the user to specify it
                return [create_text_response(json.dumps({
                    "status": "error",
                    "message": "Please specify which IDE you are using. Supported options are: cursor, windsurf, cline, or copilot",
                    "supported_ides": ["cursor", "windsurf", "cline", "copilot"]
                }, indent=2))]
            
            ide = arguments["ide"]
            # Always back up existing files
            backup_existing = True
            
            # Validate IDE
            if ide not in ["cursor", "windsurf", "cline", "copilot"]:
                raise ValueError("Invalid IDE. Must be one of: cursor, windsurf, cline, or copilot")
            
            # Log which source was used for project_path
            logger.info(f"Using project_path from {source}: {project_path}")
            print(f"initialize-ide-rules using project_path from {source}: {project_path}")
            
            # At this point, we've already verified the path exists and is writable in get_safe_project_path
            
            if ide == "cursor":
                # Initialize Cursor rules
                cursor_dir = os.path.join(project_path, ".cursor")
                rules_dir = os.path.join(cursor_dir, "rules")
                templates_dir = os.path.join(cursor_dir, "templates")
                
                os.makedirs(rules_dir, exist_ok=True)
                os.makedirs(templates_dir, exist_ok=True)
                
                # Get paths to our rule and template files
                server_dir = os.path.dirname(os.path.abspath(__file__))
                cursor_rules_dir = os.path.join(server_dir, "cursor_rules")
                cursor_templates_dir = os.path.join(server_dir, "cursor_templates")
                
                # Verify source directories exist
                if not os.path.exists(cursor_rules_dir):
                    raise FileNotFoundError(f"Source rules directory not found: {cursor_rules_dir}")
                if not os.path.exists(cursor_templates_dir):
                    raise FileNotFoundError(f"Source templates directory not found: {cursor_templates_dir}")
                
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
                for existing_file in existing_templates:
                    if backup_existing:
                        src = os.path.join(templates_dir, existing_file)
                        backup = src + ".back"
                        if os.path.exists(src):
                            shutil.copy2(src, backup)
                            initialized_templates.append({"file_name": existing_file, "status": "backed_up"})
                
                # Copy templates
                for template_file in os.listdir(cursor_templates_dir):
                    src = os.path.join(cursor_templates_dir, template_file)
                    dst = os.path.join(templates_dir, template_file)
                    
                    # Copy the file
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
                windsurf_template_dir = os.path.join(server_dir, "windsurf_templates")
                template_file = os.path.join(windsurf_template_dir, "windsurf_rules_template.md")
                
                # Copy the template
                shutil.copy2(template_file, windsurf_rule_file)
                
                # Create response
                response_data = {
                    "initialized_windsurf": True,
                    "file_path": os.path.abspath(windsurf_rule_file),
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
                
                # Get the windsurf template path (we'll use the same template)
                server_dir = os.path.dirname(os.path.abspath(__file__))
                windsurf_template_dir = os.path.join(server_dir, "windsurf_templates")
                template_file = os.path.join(windsurf_template_dir, "windsurf_rules_template.md")
                
                # Copy the template
                shutil.copy2(template_file, cline_rule_file)
                
                # Create response
                response_data = {
                    "initialized_cline": True,
                    "file_path": os.path.abspath(cline_rule_file),
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
                
                # Get the windsurf template path (we'll use the same template)
                server_dir = os.path.dirname(os.path.abspath(__file__))
                windsurf_template_dir = os.path.join(server_dir, "windsurf_templates")
                template_file = os.path.join(windsurf_template_dir, "windsurf_rules_template.md")
                
                # Copy the template
                shutil.copy2(template_file, copilot_rule_file)
                
                # Create response
                response_data = {
                    "initialized_copilot": True,
                    "file_path": os.path.abspath(copilot_rule_file),
                    "status": status,
                    "success": True
                }
                
                return [create_text_response(json.dumps(response_data, indent=2))]
            else:
                raise ValueError(f"Unknown IDE: {ide}. Supported values are 'cursor', 'windsurf', 'cline', or 'copilot'")
        
        elif name == "initialize-rules":
            # Get a safe project path using the utility function
            try:
                project_path, source = get_safe_project_path(arguments)
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
            
            # Always back up existing files
            backup_existing = True
            
            # Log which source was used for project_path
            logger.info(f"Using project_path from {source}: {project_path}")
            print(f"initialize-rules using project_path from {source}: {project_path}")
            
            # At this point, we've already verified the path exists and is writable in get_safe_project_path
            
            # Create .cursor directory structure
            cursor_dir = os.path.join(project_path, ".cursor")
            rules_dir = os.path.join(cursor_dir, "rules")
            templates_dir = os.path.join(cursor_dir, "templates")
            
            os.makedirs(rules_dir, exist_ok=True)
            os.makedirs(templates_dir, exist_ok=True)
            
            # Get paths to our rule and template files
            server_dir = os.path.dirname(os.path.abspath(__file__))
            cursor_rules_dir = os.path.join(server_dir, "cursor_rules")
            cursor_templates_dir = os.path.join(server_dir, "cursor_templates")
            
            # Verify source directories exist
            if not os.path.exists(cursor_rules_dir):
                raise FileNotFoundError(f"Source rules directory not found: {cursor_rules_dir}")
            if not os.path.exists(cursor_templates_dir):
                raise FileNotFoundError(f"Source templates directory not found: {cursor_templates_dir}")
            
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
            for existing_file in existing_templates:
                if backup_existing:
                    src = os.path.join(templates_dir, existing_file)
                    backup = src + ".back"
                    if os.path.exists(src):
                        shutil.copy2(src, backup)
                        initialized_templates.append({"file_name": existing_file, "status": "backed_up"})
            
            # Copy templates
            for template_file in os.listdir(cursor_templates_dir):
                src = os.path.join(cursor_templates_dir, template_file)
                dst = os.path.join(templates_dir, template_file)
                
                # Copy the file
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
                safe_path, source = get_safe_project_path({"project_path": proposed_path} if proposed_path else None)
                
                # Create response for successful case
                response_data = {
                    "safe_path": safe_path,
                    "source": source,
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