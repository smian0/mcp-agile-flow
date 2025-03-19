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

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import stdio

# Import local modules
from .rules_migration import migrate_cursor_to_windsurf

# Configure logging
logger = logging.getLogger(__name__)

# Store notes as a simple key-value dict to demonstrate state management
notes: Dict[str, str] = {}

# Keep track of tool invocations for debugging
tool_invocations = []

def create_text_response(text: str, is_error: bool = False) -> types.TextContent:
    """Helper function to create properly formatted TextContent responses."""
    return types.TextContent(
        type="text",
        text=text,
        isError=is_error
    )

def log_tool_invocation(name: str, arguments: Optional[dict], response: Any) -> None:
    """
    Log a tool invocation to help with debugging.
    
    Args:
        name: The name of the tool that was invoked
        arguments: The arguments passed to the tool
        response: The response returned by the tool
    """
    # Create a log entry
    invocation = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tool": name,
        "arguments": arguments or {},
        "response_summary": str(response)[:100] + ("..." if len(str(response)) > 100 else "")
    }
    
    # Add to the in-memory log
    tool_invocations.append(invocation)
    
    # Write to debug log
    logger.debug(f"Tool invocation: {json.dumps(invocation)}")

# Create an MCP server
mcp = Server("MCP Agile Flow - Simple")

@mcp.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    
    Returns:
        A list of Tool objects defining the available tools and their arguments.
    """
    return [
        types.Tool(
            name="initialize-ide-rules",
            description="Initialize a project with rules for a specific IDE",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory"
                    },
                    "ide": {
                        "type": "string", 
                        "description": "IDE to initialize (cursor, windsurf, cline, or copilot)",
                        "enum": ["cursor", "windsurf", "cline", "copilot"]
                    },
                    "backup_existing": {
                        "type": "boolean",
                        "description": "Whether to back up existing rules",
                        "default": True
                    }
                },
                "required": ["project_path", "ide"],
            },
        ),
        types.Tool(
            name="initialize-rules",
            description="Initialize a project with cursor rules and templates",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory"
                    },
                    "backup_existing": {
                        "type": "boolean",
                        "description": "Whether to back up existing rules",
                        "default": True
                    }
                },
                "required": ["project_path"],
            },
        ),
        types.Tool(
            name="migrate-rules-to-windsurf",
            description="Migrate rules from Cursor to Windsurf",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory. If not provided, uses current working directory."
                    },
                    "specific_file": {
                        "type": "string",
                        "description": "Specific file to migrate (without .mdc extension). If not provided, migrates all files."
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Whether to show detailed information during migration.",
                        "default": False
                    },
                    "no_truncate": {
                        "type": "boolean",
                        "description": "Skip truncation even for IDEs with character limits.",
                        "default": False
                    }
                },
            },
        ),
        types.Tool(
            name="add-note",
            description="Add a new note",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["name", "content"],
            },
        ),
        types.Tool(
            name="get-project-path",
            description="Returns the current project directory path",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="debug-tools",
            description="Get debug information about recent tool invocations",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of recent invocations to show (default: 5)",
                        "default": 5
                    },
                },
                "required": [],
            },
        )
    ]

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
    
    try:
        if name == "initialize-ide-rules":
            if not arguments or "project_path" not in arguments or "ide" not in arguments:
                raise ValueError("Missing required arguments: project_path and ide")
            
            project_path = arguments["project_path"]
            ide = arguments["ide"]
            backup_existing = arguments.get("backup_existing", True)
            
            # Validate IDE
            if ide not in ["cursor", "windsurf", "cline", "copilot"]:
                raise ValueError("Invalid IDE. Must be one of: cursor, windsurf, cline, or copilot")
            
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
                    "file_path": windsurf_rule_file,
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
                    "file_path": cline_rule_file,
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
                    "file_path": copilot_rule_file,
                    "status": status,
                    "success": True
                }
                
                return [create_text_response(json.dumps(response_data, indent=2))]
            else:
                raise ValueError(f"Unknown IDE: {ide}. Supported values are 'cursor', 'windsurf', 'cline', or 'copilot'")
        
        elif name == "initialize-rules":
            if not arguments or "project_path" not in arguments:
                raise ValueError("Missing project_path argument")
            
            project_path = arguments["project_path"]
            backup_existing = arguments.get("backup_existing", True)
            
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
                "success": True
            }
            
            return [create_text_response(json.dumps(response_data, indent=2))]
            
        elif name == "migrate-rules-to-windsurf":
            project_path = arguments.get("project_path", os.getcwd())
            specific_file = arguments.get("specific_file")
            verbose = arguments.get("verbose", False)
            no_truncate = arguments.get("no_truncate", False)
            
            result = migrate_cursor_to_windsurf(
                project_path=project_path,
                specific_file=specific_file,
                verbose=verbose,
                no_truncate=no_truncate
            )
            
            if result["success"]:
                response_text = f"Rules migration completed successfully.\n"
                response_text += f"Files processed: {result['files_processed']}\n"
                response_text += f"Character count: {result['character_count']}\n"
                
                if result.get("truncated"):
                    response_text += "NOTE: Content was truncated to fit within the 6000 character limit.\n"
                
                response_text += f"Output file: {result.get('message', '')}"
            else:
                response_text = f"Rules migration failed: {result.get('error', 'Unknown error')}"
            
            return [create_text_response(response_text)]
            
        elif name == "add-note":
            if not arguments or "name" not in arguments or "content" not in arguments:
                raise ValueError("Missing required arguments: name and content")
            
            note_name = arguments["name"]
            note_content = arguments["content"]
            
            # Store the note
            notes[note_name] = note_content
            
            return [create_text_response(f"Note '{note_name}' added successfully")]
            
        elif name == "get-project-path":
            logger.info("Getting project paths")
            
            # Get the current working directory
            current_dir = os.getcwd()
            
            # Get the directory of the current file
            file_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Create response
            response_data = {
                "current_directory": current_dir,
                "file_directory": file_dir
            }
            
            return [create_text_response(json.dumps(response_data, indent=2))]
            
        elif name == "debug-tools":
            count = arguments.get("count", 5)
            
            # Get the most recent invocations
            recent = tool_invocations[-count:] if tool_invocations else []
            
            # Format the response
            response_text = f"Last {len(recent)} tool invocations:\n\n"
            for invocation in recent:
                response_text += json.dumps(invocation, indent=2) + "\n\n"
            
            return [create_text_response(response_text)]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in tool call: {str(e)}")
        return [create_text_response(str(e), is_error=True)]
    finally:
        # Log the tool invocation for debugging
        log_tool_invocation(name, arguments, None)

async def run_server():
    """
    Run the server using stdin/stdout streams.
    
    This sets up the MCP server to communicate over stdin/stdout,
    which allows it to be used with the MCP protocol directly.
    """
    logger.info("Starting Simple server (stdin/stdout mode)")
    print("Starting MCP Agile Flow Simple server...", file=sys.stderr)
    
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