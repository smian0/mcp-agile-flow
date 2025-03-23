"""
MCP Agile Flow - Server Implementation

This module implements the MCP server with tools for agile workflow.
It uses the standard MCP protocol over stdin/stdout for use with Cursor.
"""

import asyncio
import datetime
import json
import logging
import os
import re
import shutil
import sys
import traceback
from typing import Any, Dict, List, Optional, Tuple

import mcp.types as types
from mcp.server import NotificationOptions, Server, stdio
from mcp.server.models import InitializationOptions

# Import local modules
from .memory_graph import register_memory_tools
from .utils import get_project_settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize MCP server globally so it can be imported by IDE plugins
mcp = Server("agile-flow")  # Must match entry point name in pyproject.toml

# Initialize memory graph tools and manager
# These will be populated when run() is called
memory_tools = []
memory_manager = None

# Export the server instance for MCP plugins
__mcp__ = mcp


def create_text_response(text: str, is_error: bool = False) -> types.TextContent:
    """Create a text response with optional error flag."""
    if is_error:
        logger.error(text)
    response = types.TextContent(type="text", text=text, isError=is_error)
    # Set is_error for backwards compatibility
    response.is_error = is_error
    return response


def check_for_greeting(message: str) -> bool:
    """Check if a message contains a greeting."""
    greeting_patterns = [r"^hello\b", r"^hi\b", r"^hey\b", r"^greetings\b"]
    return any(re.search(pattern, message.lower()) for pattern in greeting_patterns)


def parse_greeting_command(message: str) -> Tuple[str, Dict[str, Any]]:
    """Parse a greeting message for potential command and arguments."""
    command_pattern = (
        r"(hello|hi|hey|greetings),?\s+please\s+([\w\-]+)(?:\s+with\s+(.+))?"
    )
    match = re.search(command_pattern, message.lower())

    if not match:
        return "", {}

    command = match.group(2)
    args_str = match.group(3) if match.group(3) else ""

    # Parse simple key=value arguments
    args = {}
    if args_str:
        for arg in args_str.split(","):
            parts = arg.strip().split("=", 1)
            if len(parts) == 2:
                args[parts[0].strip()] = parts[1].strip()

    return command, args


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
            name="migrate-mcp-config",
            description="Migrate MCP configuration between different IDEs with smart merging and conflict resolution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_ide": {
                        "type": "string",
                        "enum": [
                            "cursor",
                            "windsurf",
                            "windsurf-next",
                            "cline",
                            "roo",
                            "claude-desktop",
                        ],
                        "description": "Source IDE to migrate configuration from",
                    },
                    "to_ide": {
                        "type": "string",
                        "enum": [
                            "cursor",
                            "windsurf",
                            "windsurf-next",
                            "cline",
                            "roo",
                            "claude-desktop",
                        ],
                        "description": "Target IDE to migrate configuration to",
                    },
                    "backup": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to create backups before modifying files",
                    },
                    "conflict_resolutions": {
                        "type": "object",
                        "description": "Mapping of server names to resolution choices (true = use source, false = keep target)",
                        "additionalProperties": {"type": "boolean"},
                    },
                },
                "required": ["from_ide", "to_ide"],
            },
        ),
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
                        "default": "cursor",
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Custom project path to use (optional). If not provided, will use PROJECT_PATH environment variable or current directory.",
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="initialize-ide-rules",
            description="Initialize a project with rules for a specific IDE. The project path will default to the PROJECT_PATH environment variable if set, or the current directory if not set.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ide": {
                        "type": "string",
                        "description": "IDE to initialize (cursor, windsurf, cline, or copilot). Defaults to cursor if not specified.",
                        "enum": ["cursor", "windsurf", "cline", "copilot"],
                        "default": "cursor",
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Custom project path to use (optional). If not provided, will use PROJECT_PATH environment variable or current directory.",
                    },
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
                        "default": "standard",
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional specific areas to focus on (e.g., ['architecture', 'current_story', 'progress'])",
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Custom project path to use (optional). If not provided, will use PROJECT_PATH environment variable or current directory.",
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get-project-settings",
            description="Returns comprehensive project settings including project path, knowledge graph directory, AI docs directory, project type, metadata, and other configuration. Also validates the path to ensure it's safe and writable. If the root directory or a non-writable path is detected, it will automatically use a safe alternative path. Takes an optional 'proposed_path' parameter to check a specific path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "proposed_path": {
                        "type": "string",
                        "description": "Optional path to check. If not provided, standard environment variables or default paths will be used.",
                    }
                },
                "required": [],
            },
        ),
    ]

    # Add memory graph tools if available
    if "memory_tools" in globals() and memory_tools is not None:
        tools.extend(memory_tools)

    return tools


@mcp.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[dict]
) -> List[types.TextContent]:
    """
    Handle a tool call from the MCP client.

    Args:
        name: The name of the tool to call
        arguments: Optional arguments to pass to the tool

    Returns:
        A list of TextContent objects with the tool's response.
    """
    try:
        logger.info(f"Tool call received: {name} with arguments: {arguments}")
        print(f"DEBUG: Tool call received: {name} with arguments: {arguments}")

        # Normalize tool name (handle different formats that IDEs might send)
        # Some IDEs might convert dashes to underscores or camelCase
        normalized_name = name.replace("_", "-").lower()

        # If we get a normalized version that's different from original, log it
        if normalized_name != name:
            logger.info(f"Normalized tool name from '{name}' to '{normalized_name}'")
            print(f"DEBUG: Normalized tool name from '{name}' to '{normalized_name}'")
            name = normalized_name

        # Handle memory graph tools
        if memory_manager is not None and name in memory_tools:
            # These tools are registered by the memory graph manager
            return await memory_manager.handle_tool_call(name, arguments)

        # Handle migration tool
        elif name == "migrate-mcp-config":
            from .migration_tool import (
                detect_conflicts,
                get_conflict_details,
                get_ide_path,
                migrate_config,
            )

            if not arguments:
                return [
                    create_text_response(
                        json.dumps(
                            {
                                "success": False,
                                "error": "No arguments provided for migrate-mcp-config",
                            }
                        ),
                        is_error=True,
                    )
                ]

            required_args = ["from_ide", "to_ide"]
            missing_args = [arg for arg in required_args if arg not in arguments]
            if missing_args:
                return [
                    create_text_response(
                        json.dumps(
                            {
                                "success": False,
                                "error": f"Missing required arguments: {', '.join(missing_args)}",
                            }
                        ),
                        is_error=True,
                    )
                ]

            from_ide = arguments["from_ide"]
            to_ide = arguments["to_ide"]
            backup = arguments.get("backup", True)
            conflict_resolutions = arguments.get("conflict_resolutions", {})

            # If conflict resolutions are provided, perform the migration with them
            if conflict_resolutions:
                try:
                    from .migration_tool import merge_configurations

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
                        return [
                            create_text_response(json.dumps(response), is_error=True)
                        ]

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
                        return [
                            create_text_response(json.dumps(response), is_error=True)
                        ]

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
                        return [
                            create_text_response(json.dumps(response), is_error=True)
                        ]

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
                    return [create_text_response(json.dumps(response))]
                except Exception as e:
                    response = {
                        "success": False,
                        "error": f"Error during migration with conflict resolutions: {str(e)}",
                    }
                    return [create_text_response(json.dumps(response), is_error=True)]
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
                    return [create_text_response(json.dumps(response), is_error=True)]

                if conflicts:
                    # Check if conflict_resolutions was provided as an empty dict
                    # This is different from not providing conflict_resolutions at all
                    if (
                        "conflict_resolutions" in arguments
                        and isinstance(conflict_resolutions, dict)
                        and len(conflict_resolutions) == 0
                    ):
                        response = {
                            "success": False,
                            "error": "Missing conflict resolutions",
                            "needs_resolution": True,
                            "conflicts": conflicts,
                            "conflict_details": conflict_details,
                            "source_path": get_ide_path(from_ide),
                            "target_path": get_ide_path(to_ide),
                        }
                        return [
                            create_text_response(json.dumps(response), is_error=True)
                        ]

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
                    return [create_text_response(json.dumps(response))]
                else:
                    # No conflicts, migration was successful
                    response = {
                        "success": True,
                        "needs_resolution": False,
                        "source_path": get_ide_path(from_ide),
                        "target_path": get_ide_path(to_ide),
                    }
                    return [create_text_response(json.dumps(response))]
        elif name == "initialize-ide":
            # Initialize-ide logic (previously existing implementation)
            if not arguments:
                arguments = {}

            ide = arguments.get("ide", "cursor")
            if ide not in ["cursor", "windsurf", "cline", "copilot"]:
                return [
                    create_text_response(f"Error: Unknown IDE: {ide}", is_error=True)
                ]

            try:
                # Determine project path with improved handling of current directory
                if arguments.get("project_path"):
                    # Explicit path provided - use get_project_settings to validate it
                    project_settings = get_project_settings(
                        proposed_path=arguments.get("project_path")
                    )
                    project_path = project_settings["project_path"]
                    source = project_settings["source"]
                elif os.environ.get("PROJECT_PATH"):
                    # Environment variable set - use get_project_settings to validate it
                    project_settings = get_project_settings()
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
                        return [
                            create_text_response(
                                json.dumps(response_data, indent=2), is_error=True
                            )
                        ]

                # Log the determined path
                logger.info(f"initialize-ide using project_path from {source}: {project_path}")
                print(f"initialize-ide using project_path from {source}: {project_path}")

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
                else:
                    # For other IDEs, create a rules directory
                    os.makedirs(
                        os.path.join(project_path, f".{ide}-rules"), exist_ok=True
                    )

                # Copy default templates to .ai-templates directory
                # Source path is within the package's resources
                # Get the templates from the installed package

                # Create templates directory if it doesn't exist
                templates_dir = os.path.join(project_path, ".ai-templates")
                os.makedirs(templates_dir, exist_ok=True)

                # Get the source templates directory path
                templates_source_dir = os.path.join(
                    os.path.dirname(__file__), "ai-templates"
                )

                # Check if the source directory exists
                if os.path.exists(templates_source_dir) and os.path.isdir(
                    templates_source_dir
                ):
                    # Copy all template files from the source directory
                    for template_file in os.listdir(templates_source_dir):
                        try:
                            template_source_path = os.path.join(
                                templates_source_dir, template_file
                            )
                            template_target_path = os.path.join(
                                templates_dir, template_file
                            )

                            # Only copy files, not directories
                            if os.path.isfile(template_source_path):
                                shutil.copy2(template_source_path, template_target_path)
                                print(f"Copied template: {template_file}")

                        except Exception as e:
                            print(f"Error copying template {template_file}: {str(e)}")
                else:
                    print(
                        f"Warning: Template directory not found at {templates_source_dir}"
                    )

                # Initialize IDE-specific rules
                # Call initialize-ide-rules with the IDE parameter for more specific setup
                if ide == "cursor":
                    rule_result = await handle_call_tool(
                        "initialize-ide-rules",
                        {"project_path": project_path, "ide": "cursor"},
                    )
                    if (
                        rule_result
                        and len(rule_result) > 0
                        and rule_result[0].type == "text"
                    ):
                        return rule_result
                else:
                    # Copy IDE-specific rules
                    rules_source_dir = os.path.join(
                        os.path.dirname(__file__), "ide_rules", ide
                    )
                    rules_target_dir = os.path.join(project_path, f".{ide}-rules")

                    if os.path.exists(rules_source_dir):
                        for rule_file in os.listdir(rules_source_dir):
                            source_file = os.path.join(rules_source_dir, rule_file)
                            target_file = os.path.join(rules_target_dir, rule_file)
                            if os.path.isfile(source_file):
                                shutil.copy2(source_file, target_file)
                    else:
                        print(
                            f"Warning: IDE rules directory not found at {rules_source_dir}"
                        )

                # Create a JSON response
                response_data = {
                    "success": True,
                    "message": f"Initialized {ide} project in {project_path}",
                    "project_path": project_path,
                    "templates_directory": os.path.join(project_path, ".ai-templates"),
                }

                # Add IDE-specific paths to the response
                if ide == "windsurf":
                    response_data["rules_file"] = os.path.join(
                        project_path, ".windsurfrules"
                    )
                    response_data["rules_directory"] = (
                        None  # No rules directory for windsurf
                    )
                    response_data["initialized_windsurf"] = (
                        True  # Only include this for windsurf
                    )
                elif ide == "cline":
                    response_data["rules_file"] = os.path.join(
                        project_path, ".clinerules"
                    )
                    response_data["rules_directory"] = (
                        None  # No rules directory for cline
                    )
                else:
                    response_data["rules_directory"] = os.path.join(
                        project_path, f".{ide}-rules"
                    )

                return [create_text_response(json.dumps(response_data, indent=2))]
            except ValueError as e:
                return [create_text_response(f"Error: {str(e)}", is_error=True)]
            except Exception as e:
                print(f"Error in initialize-ide: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error initializing project: {str(e)}", is_error=True
                    )
                ]
        elif name == "initialize-ide-rules":
            # Get a safe project path using the utility function with improved handling
            try:
                # Determine project path with improved handling of current directory
                if arguments and arguments.get("project_path"):
                    # Explicit path provided - use get_project_settings to validate it
                    project_settings = get_project_settings(
                        proposed_path=arguments.get("project_path")
                    )
                    project_path = project_settings["project_path"]
                    source = project_settings["source"]
                elif os.environ.get("PROJECT_PATH"):
                    # Environment variable set - use get_project_settings to validate it
                    project_settings = get_project_settings()
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
                        return [
                            create_text_response(
                                json.dumps(response_data, indent=2), is_error=True
                            )
                        ]

                # Log the determined path
                logger.info(f"Using project_path from {source}: {project_path}")
                print(f"{name} using project_path from {source}: {project_path}")
            except Exception as e:
                # Handle case where the path is problematic
                current_dir = os.getcwd()
                response_data = {
                    "error": str(e),
                    "status": "error",
                    "needs_user_input": True,
                    "current_directory": current_dir,
                    "is_root": current_dir == "/",
                    "message": "Please provide a specific project path using the 'project_path' argument.",
                    "success": False,
                }
                return [
                    create_text_response(
                        json.dumps(response_data, indent=2), is_error=True
                    )
                ]

            # Default to cursor for both tools
            ide = "cursor"

            # For initialize-ide-rules, check if IDE is specified
            if name == "initialize-ide-rules" and arguments and "ide" in arguments:
                ide = arguments["ide"]

            # Always back up existing rule files (but not templates)
            backup_existing = True

            # Validate IDE
            if ide not in ["cursor", "windsurf", "cline", "copilot"]:
                raise ValueError(
                    "Invalid IDE. Must be one of: cursor, windsurf, cline, or copilot"
                )

            # Log which source was used for project_path
            logger.info(f"Using project_path from {source}: {project_path}")
            print(f"{name} using project_path from {source}: {project_path}")

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
                server_dir = os.path.dirname(os.path.abspath(__file__))
                cursor_rules_dir = os.path.join(server_dir, "cursor_rules")
                ai_templates_dir = os.path.join(server_dir, "ai-templates")

                # Verify source directories exist
                if not os.path.exists(cursor_rules_dir):
                    raise FileNotFoundError(
                        f"Source rules directory not found: {cursor_rules_dir}"
                    )
                if not os.path.exists(ai_templates_dir):
                    raise FileNotFoundError(
                        f"Source templates directory not found: {ai_templates_dir}"
                    )

                # Track what files were initialized
                initialized_rules = []
                initialized_templates = []

                # First, handle any existing files that need backup
                (os.listdir(rules_dir) if os.path.exists(rules_dir) else [])

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

                    logger.info(
                        f"Copying rule file from {source_file} to {target_file}"
                    )

                    # If target exists and backup is enabled, create a backup
                    if os.path.exists(target_file) and backup_existing:
                        backup_file = f"{target_file}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        shutil.copy2(target_file, backup_file)

                    # Copy the rule file
                    shutil.copy2(source_file, target_file)
                    initialized_rules.append(target_filename)

                # Verify rules were copied
                rule_files = os.listdir(rules_dir)
                logger.info(
                    f"After copying, rules directory contains {len(rule_files)} files: {rule_files}"
                )

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

                return [create_text_response(json.dumps(response_data, indent=2))]

            elif ide == "windsurf":
                # Initialize Windsurf rules and templates
                # Place ai-templates at the project root
                templates_dir = os.path.join(project_path, ".ai-templates")
                os.makedirs(templates_dir, exist_ok=True)

                # Get paths to our template files
                server_dir = os.path.dirname(os.path.abspath(__file__))
                ai_templates_dir = os.path.join(server_dir, "ai-templates")
                cursor_rules_dir = os.path.join(server_dir, "cursor_rules")

                # Verify source directories exist
                if not os.path.exists(ai_templates_dir):
                    raise FileNotFoundError(
                        f"Source templates directory not found: {ai_templates_dir}"
                    )
                if not os.path.exists(cursor_rules_dir):
                    raise FileNotFoundError(
                        f"Source rules directory not found: {cursor_rules_dir}"
                    )

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
                        if os.path.isfile(source_file) and (
                            rule_file.endswith(".md") or rule_file.endswith(".mdc")
                        ):
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

                return [create_text_response(json.dumps(response_data, indent=2))]

            elif ide in ["cline", "copilot"]:
                # Initialize VS Code extension rules
                # Place ai-templates at the project root
                templates_dir = os.path.join(project_path, ".ai-templates")
                os.makedirs(templates_dir, exist_ok=True)

                # Get paths to our template files
                server_dir = os.path.dirname(os.path.abspath(__file__))
                ai_templates_dir = os.path.join(server_dir, "ai-templates")
                cursor_rules_dir = os.path.join(server_dir, "cursor_rules")

                # Verify source directories exist
                if not os.path.exists(ai_templates_dir):
                    raise FileNotFoundError(
                        f"Source templates directory not found: {ai_templates_dir}"
                    )
                if not os.path.exists(cursor_rules_dir):
                    raise FileNotFoundError(
                        f"Source rules directory not found: {cursor_rules_dir}"
                    )

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
                    template_file = os.path.join(
                        server_dir, "ide_rules", "ide_rules.md"
                    )

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
                    vs_code_rules_file = os.path.join(
                        project_path, f".{ide.lower()}rules"
                    )

                    # If target exists and backup is enabled, create a backup
                    if os.path.exists(vs_code_rules_file) and backup_existing:
                        backup_file = f"{vs_code_rules_file}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        shutil.copy2(vs_code_rules_file, backup_file)

                    # Get the template path
                    template_file = os.path.join(
                        server_dir, "ide_rules", "ide_rules.md"
                    )

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

                return [create_text_response(json.dumps(response_data, indent=2))]

        elif name == "prime-context":
            logger.info("Analyzing project context")
            if not arguments:
                return [
                    create_text_response(
                        "Error: Missing arguments for prime-context", is_error=True
                    )
                ]

            project_path = arguments.get("project_path", None)
            if not project_path:
                # Check for PROJECT_PATH environment variable
                project_path = os.environ.get("PROJECT_PATH")

                if not project_path:
                    # Use the current working directory
                    project_path = os.getcwd()
                    logger.info(
                        f"Using current directory for project_path: {project_path}"
                    )
                else:
                    logger.info(
                        f"Using PROJECT_PATH environment variable: {project_path}"
                    )
            else:
                logger.info(f"Using provided project_path: {project_path}")

            depth = arguments.get("depth", "standard")
            focus_areas = arguments.get("focus_areas", None)

            # Call the prime context function
            response_data = handle_prime_context(project_path, depth, focus_areas)

            return [create_text_response(json.dumps(response_data, indent=2))]
        elif name == "get-project-settings":
            logger.info("Getting project settings")

            # Get proposed path from arguments if provided
            proposed_path = arguments.get("proposed_path", "") if arguments else ""

            # Use the common utility function to get project settings
            response_data = get_project_settings(
                proposed_path=proposed_path if proposed_path else None
            )

            # Also include project type and metadata from the memory graph if available
            if memory_manager is not None:
                try:
                    # Get project info from the memory graph
                    project_info = memory_manager.get_project_info()

                    # Add project type and metadata to the response
                    response_data["project_type"] = project_info.get(
                        "project_type", "generic"
                    )
                    response_data["project_metadata"] = project_info.get(
                        "project_metadata", {}
                    )
                    logger.info(
                        "Added project type and metadata from memory graph to project settings"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to get project info from memory graph: {str(e)}"
                    )
                    # Add default values if memory manager fails
                    response_data["project_type"] = "generic"
                    response_data["project_metadata"] = {}
            else:
                # Memory manager not available, add default values
                logger.info(
                    "Memory manager not available, using default project type and metadata"
                )
                response_data["project_type"] = "generic"
                response_data["project_metadata"] = {}

            # Log the response for debugging
            logger.info(f"Project settings response: {response_data}")

            return [create_text_response(json.dumps(response_data, indent=2))]
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error handling tool call '{name}': {str(e)}")
        logger.error(traceback.format_exc())
        return [
            create_text_response(
                f"Error processing tool '{name}': {str(e)}\n\nPlease check server logs for details.",
                is_error=True,
            )
        ]


def extract_markdown_title(content):
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


def summarize_content(content, depth="standard"):
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


def extract_task_completion(content):
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
        with open(makefile_path, "r") as file:
            content = file.read()

        # Parse Makefile content to extract commands and targets
        commands = {}
        lines = content.split("\n")
        current_target = None

        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith("#") or not line.strip():
                continue

            # Look for target definitions (lines ending with a colon)
            if ":" in line and not line.strip().startswith("\t"):
                # Extract target name (everything before the colon and optional dependencies)
                target_parts = line.split(":")[0].strip().split()
                if target_parts:
                    current_target = target_parts[0]

                    # Skip phony targets or other special targets
                    if current_target.startswith("."):
                        current_target = None
                        continue

                    # Look for the command in the next lines
                    for j in range(i + 1, len(lines)):
                        cmd_line = lines[j].strip()
                        # Commands in Makefiles typically start with a tab
                        if cmd_line and lines[j].startswith("\t"):
                            # Remove the tab
                            command = cmd_line

                            # Categorize the command
                            if any(
                                keyword in current_target.lower()
                                for keyword in ["test", "pytest", "check"]
                            ):
                                category = "testing"
                            elif any(
                                keyword in current_target.lower()
                                for keyword in ["build", "compile", "install", "setup"]
                            ):
                                category = "build"
                            elif any(
                                keyword in current_target.lower()
                                for keyword in ["run", "start", "serve", "dev"]
                            ):
                                category = "run"
                            elif any(
                                keyword in current_target.lower()
                                for keyword in ["clean", "clear", "reset"]
                            ):
                                category = "clean"
                            elif any(
                                keyword in current_target.lower()
                                for keyword in ["deploy", "publish", "release", "dist"]
                            ):
                                category = "deploy"
                            elif any(
                                keyword in current_target.lower()
                                for keyword in ["lint", "format", "style", "check"]
                            ):
                                category = "lint"
                            else:
                                category = "other"

                            if category not in commands:
                                commands[category] = []

                            commands[category].append(
                                {"target": current_target, "command": command}
                            )
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
    elif re.match(
        r"generate business requirements document for", command, re.IGNORECASE
    ):
        project_name = command.split("for", 1)[1].strip()
        return create_brd(project_name)
    # Handle BRD update commands
    elif re.match(r"add business objective (.*) to brd", command, re.IGNORECASE):
        objective = re.match(
            r"add business objective (.*) to brd", command, re.IGNORECASE
        ).group(1)
        return add_to_brd_section("Business Objectives", objective)
    elif re.match(r"add market problem (.*) to brd", command, re.IGNORECASE):
        problem = re.match(
            r"add market problem (.*) to brd", command, re.IGNORECASE
        ).group(1)
        return add_to_brd_section("Market Problem Analysis", problem)
    elif re.match(r"add success metric (.*) to brd", command, re.IGNORECASE):
        metric = re.match(
            r"add success metric (.*) to brd", command, re.IGNORECASE
        ).group(1)
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

    return (
        f"Created Business Requirements Document for {project_name} in `{output_path}`"
    )


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
    if section_name not in content:
        return f"Error: Section '{section_name}' not found in the BRD."

    # Split the content by sections
    sections = re.split(r"^## ", content, flags=re.MULTILINE)
    updated_content = ""

    # Add the first part (before any section)
    if sections[0].strip():
        updated_content += sections[0]

    # Process each section
    for _i, section in enumerate(sections[1:], 1):
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
            control_pattern = (
                r"## Document Control\s*\n(.*\n)*?[\-\*]\s*\*\*Status:\*\*\s*(.*)"
            )
            control_match = re.search(
                control_pattern, content, re.IGNORECASE | re.MULTILINE
            )

            if control_match:
                updated_content = re.sub(
                    r"(## Document Control\s*\n(?:.*\n)*?[\-\*]\s*\*\*Status:\*\*\s*)(.*)(\s*)",
                    f"\\1{new_status}\\3",
                    content,
                    flags=re.IGNORECASE | re.MULTILINE,
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
        flags=re.IGNORECASE | re.MULTILINE,
    )

    with open(doc_path, "w") as f:
        f.write(updated_content)

    return f"Updated {doc_type.upper()} status to '{new_status}'"


def handle_prime_context(project_path, depth="standard", focus_areas=None):
    """
    Prime the context with project information from various documentation sources.

    Args:
        project_path (str): Project path
        depth (str): Level of detail to include (minimal, standard, comprehensive)
        focus_areas (list): Optional specific areas to focus on

    Returns:
        dict: Structured project context information
    """
    logger.info(f"Priming context from project at: {project_path}")

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
        logger.info(f"AI docs directory not found at: {ai_docs_dir}")
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
        logger.info(f"Found PRD at: {prd_path}")
        with open(prd_path, "r") as f:
            prd_content = f.read()
            context["project"]["name"] = extract_markdown_title(prd_content)
            context["project"]["status"] = extract_status(prd_content)
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
        logger.info(f"Found README at: {readme_path}")
        with open(readme_path, "r") as f:
            readme_content = f.read()
            context["project"]["readme"] = summarize_content(readme_content, depth)

            # If PRD wasn't found, use README for project name
            if "prd_title" not in context["project"]:
                context["project"]["name"] = extract_markdown_title(readme_content)
                context["project"]["status"] = extract_status(readme_content)

    # Extract architecture information
    arch_path = os.path.join(ai_docs_dir, "architecture.md")
    if os.path.exists(arch_path) and ("architecture" in context):
        logger.info(f"Found architecture document at: {arch_path}")
        with open(arch_path, "r") as f:
            arch_content = f.read()
            context["architecture"]["overview"] = summarize_content(arch_content, depth)

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
        logger.info(f"Found epics directory at: {epics_dir}")

        epic_folders = [
            f
            for f in os.listdir(epics_dir)
            if os.path.isdir(os.path.join(epics_dir, f))
        ]
        for epic_folder in epic_folders:
            epic_path = os.path.join(epics_dir, epic_folder, "epic.md")
            if os.path.exists(epic_path):
                logger.info(f"Found epic at: {epic_path}")
                with open(epic_path, "r") as f:
                    epic_content = f.read()
                    epic_info = {
                        "name": extract_markdown_title(epic_content),
                        "status": extract_status(epic_content),
                        "description": summarize_content(epic_content, depth),
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
                                story_name = extract_markdown_title(story_content)
                                story_status = extract_status(story_content)

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
        logger.info(f"Found Makefile at: {makefile_path}")
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


async def run_server():
    """
    Run the server using stdin/stdout streams.

    This sets up the MCP server to communicate over stdin/stdout,
    which allows it to be used with the MCP protocol directly.
    """
    global memory_tools, memory_manager

    logger.info("Starting MCP Agile Flow server (stdin/stdout mode)")
    print("Starting MCP Agile Flow server...", file=sys.stderr)

    # Initialize memory graph tools and manager
    try:
        # Register memory tools with the MCP server
        memory_tools, memory_manager = register_memory_tools(mcp)
        logger.info(
            f"Initialized memory graph manager with path: {memory_manager.graph_path}"
        )
        print(
            f"Initialized memory graph manager with path: {memory_manager.graph_path}",
            file=sys.stderr,
        )
    except Exception as e:
        logger.error(f"Error initializing memory graph manager: {e}")
        print(f"Error initializing memory graph manager: {e}", file=sys.stderr)
        # Continue without memory graph functionality

    async with stdio.stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            initialization_options=InitializationOptions(
                server_name="agile-flow",
                server_version="0.1.0",
                capabilities=mcp.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run():
    """Entry point for running the server."""
    asyncio.run(run_server())


# All project ideation functions have been removed since they are handled by copying IDE rules files

if __name__ == "__main__":
    run()
