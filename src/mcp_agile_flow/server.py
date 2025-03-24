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
from typing import Any, Dict, List, Optional, Tuple, Union

import mcp.types as types
from mcp.server import NotificationOptions, Server, stdio
from mcp.server.models import InitializationOptions

# Import local modules
from .utils import get_project_settings as get_settings_util  # Rename to avoid conflict
from .fastmcp_tools import (
    get_project_settings as get_project_settings_fastmcp,
    initialize_ide as initialize_ide_fastmcp,
    prime_context as prime_context_fastmcp,
    migrate_mcp_config as migrate_mcp_config_fastmcp,
    initialize_ide_rules as initialize_ide_rules_fastmcp,
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize MCP server globally so it can be imported by IDE plugins
mcp = Server("agile-flow")  # Must match entry point name in pyproject.toml

# Export the server instance for MCP plugins
__mcp__ = mcp
# Export the FastMCP instance
__fastmcp__ = [
    get_project_settings_fastmcp,
    initialize_ide_fastmcp,
    prime_context_fastmcp,
    migrate_mcp_config_fastmcp,
    initialize_ide_rules_fastmcp,
]

# Define stub functions for removed functionalities
def search_nodes(*args, **kwargs):
    """Stub for search_nodes - functionality moved to memory graph server."""
    logger.info("search_nodes called - returning stub response")
    return json.dumps({
        "success": False,
        "message": "Memory graph functionality has been moved to the memory graph MCP server."
    })

def open_nodes(*args, **kwargs):
    """Stub for open_nodes - functionality moved to memory graph server."""
    logger.info("open_nodes called - returning stub response")
    return json.dumps({
        "success": False,
        "message": "Memory graph functionality has been moved to the memory graph MCP server."
    })

def get_project_settings(*args, **kwargs):
    """Delegate to FastMCP implementation."""
    logger.info("get_project_settings called - delegating to FastMCP implementation")
    return get_project_settings_fastmcp(*args, **kwargs)



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
    Handler for the list_tools method.

    Returns:
        A list of available tools.
    """
    logger.info("List tools request received")

    # Basic tools
    tools = [
        types.Tool(
            name="get-project-settings",
            description="Get information about the current project settings such as IDE and project path.",
            parameters={
                "type": "object",
                "properties": {
                    "proposed_path": {
                        "type": "string",
                        "description": "Proposed project path to use, if not using the current workspace.",
                    }
                },
            },
        ),
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
            name="list-projects",
            description="List all projects in the memory bank",
            parameters={
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    }
                },
                "required": ["random_string"],
            },
        ),
    ]

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

        # First check if this is a FastMCP-implemented tool
        # Currently we only have get-project-settings implemented with FastMCP
        if name == "get-project-settings":
            # Call the FastMCP implementation
            logger.info("Delegating to FastMCP implementation for get-project-settings")
            try:
                # Execute the FastMCP tool
                proposed_path = arguments.get("proposed_path") if arguments else None
                result = get_project_settings_fastmcp(proposed_path=proposed_path)
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error calling FastMCP get_project_settings: {str(e)}")
                return [create_text_response(f"Error: {str(e)}", is_error=True)]
        
        elif name == "migrate-mcp-config":
            logger.info("Migrating MCP configuration")
            
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for migrate-mcp-config")
            try:
                # Extract parameters for FastMCP implementation
                if not arguments:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": "No arguments provided for migrate-mcp-config",
                            }),
                            is_error=True
                        )
                    ]
                
                # Check for required arguments
                required_args = ["from_ide", "to_ide"]
                missing_args = [arg for arg in required_args if arg not in arguments]
                if missing_args:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": f"Missing required arguments: {', '.join(missing_args)}",
                            }),
                            is_error=True
                        )
                    ]
                
                # Extract parameters for FastMCP implementation
                from_ide = arguments["from_ide"]
                to_ide = arguments["to_ide"]
                backup = arguments.get("backup", True)
                conflict_resolutions = arguments.get("conflict_resolutions", None)
                
                # Execute the FastMCP tool
                result = migrate_mcp_config_fastmcp(
                    from_ide=from_ide, 
                    to_ide=to_ide, 
                    backup=backup, 
                    conflict_resolutions=conflict_resolutions
                )
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in migrate-mcp-config FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error migrating MCP configuration: {str(e)}", is_error=True
                    )
                ]
        elif name == "initialize-ide":
            # Initialize-ide logic (previously existing implementation)
            # Now using FastMCP implementation
            logger.info(f"Calling initialize-ide using FastMCP implementation")
            try:
                # Extract parameters for FastMCP implementation
                ide = arguments.get("ide", "cursor") if arguments else "cursor"
                project_path = arguments.get("project_path") if arguments else None
                
                # Execute the FastMCP tool
                result = initialize_ide_fastmcp(ide=ide, project_path=project_path)
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in initialize-ide FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error initializing project: {str(e)}", is_error=True
                    )
                ]
        elif name == "initialize-ide-rules":
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for initialize-ide-rules")
            try:
                # Extract parameters for FastMCP implementation
                ide = arguments.get("ide", "cursor") if arguments else "cursor"
                project_path = arguments.get("project_path") if arguments else None
                
                # Execute the FastMCP tool
                result = initialize_ide_rules_fastmcp(ide=ide, project_path=project_path)
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in initialize-ide-rules FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error initializing IDE rules: {str(e)}", is_error=True
                    )
                ]
        elif name == "prime-context":
            logger.info("Analyzing project context")
            
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for prime-context")
            try:
                # Extract parameters for FastMCP implementation
                depth = arguments.get("depth", "standard") if arguments else "standard"
                focus_areas = arguments.get("focus_areas") if arguments else None
                project_path = arguments.get("project_path") if arguments else None
                
                # Execute the FastMCP tool
                result = prime_context_fastmcp(depth=depth, focus_areas=focus_areas, project_path=project_path)
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in prime-context FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error analyzing project context: {str(e)}", is_error=True
                    )
                ]
        elif name == "create-entities":
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for create-entities")
            try:
                # Extract parameters for FastMCP implementation
                if not arguments or "entities" not in arguments:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": "Missing required argument: entities",
                            }),
                            is_error=True
                        )
                    ]
                
                # Execute the FastMCP tool
                result = create_entities_fastmcp(entities=arguments["entities"])
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in create-entities FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error creating entities: {str(e)}", is_error=True
                    )
                ]

        elif name == "create-relations":
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for create-relations")
            try:
                # Extract parameters for FastMCP implementation
                if not arguments or "relations" not in arguments:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": "Missing required argument: relations",
                            }),
                            is_error=True
                        )
                    ]
                
                # Execute the FastMCP tool
                result = create_relations_fastmcp(relations=arguments["relations"])
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in create-relations FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error creating relations: {str(e)}", is_error=True
                    )
                ]

        elif name == "add-observations":
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for add-observations")
            try:
                # Extract parameters for FastMCP implementation
                if not arguments or "observations" not in arguments:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": "Missing required argument: observations",
                            }),
                            is_error=True
                        )
                    ]
                
                # Execute the FastMCP tool
                result = add_observations_fastmcp(observations=arguments["observations"])
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in add-observations FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error adding observations: {str(e)}", is_error=True
                    )
                ]

        elif name == "delete-entities":
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for delete-entities")
            try:
                # Extract parameters for FastMCP implementation
                if not arguments or "entityNames" not in arguments:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": "Missing required argument: entityNames",
                            }),
                            is_error=True
                        )
                    ]
                
                # Execute the FastMCP tool
                result = delete_entities_fastmcp(entityNames=arguments["entityNames"])
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in delete-entities FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error deleting entities: {str(e)}", is_error=True
                    )
                ]

        elif name == "delete-observations":
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for delete-observations")
            try:
                # Extract parameters for FastMCP implementation
                if not arguments or "deletions" not in arguments:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": "Missing required argument: deletions",
                            }),
                            is_error=True
                        )
                    ]
                
                # Execute the FastMCP tool
                result = delete_observations_fastmcp(deletions=arguments["deletions"])
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in delete-observations FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error deleting observations: {str(e)}", is_error=True
                    )
                ]

        elif name == "delete-relations":
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for delete-relations")
            try:
                # Extract parameters for FastMCP implementation
                if not arguments or "relations" not in arguments:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": "Missing required argument: relations",
                            }),
                            is_error=True
                        )
                    ]
                
                # Execute the FastMCP tool
                result = delete_relations_fastmcp(relations=arguments["relations"])
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in delete-relations FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error deleting relations: {str(e)}", is_error=True
                    )
                ]

        elif name == "search-nodes":
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for search-nodes")
            try:
                # Extract parameters for FastMCP implementation
                if not arguments or "query" not in arguments:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": "Missing required argument: query",
                            }),
                            is_error=True
                        )
                    ]
                
                # Execute the FastMCP tool
                result = search_nodes_fastmcp(query=arguments["query"])
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in search-nodes FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error searching nodes: {str(e)}", is_error=True
                    )
                ]

        elif name == "open-nodes":
            # Delegate to FastMCP implementation
            logger.info("Delegating to FastMCP implementation for open-nodes")
            try:
                # Extract parameters for FastMCP implementation
                if not arguments or "names" not in arguments:
                    return [
                        create_text_response(
                            json.dumps({
                                "success": False,
                                "error": "Missing required argument: names",
                            }),
                            is_error=True
                        )
                    ]
                
                # Execute the FastMCP tool
                result = open_nodes_fastmcp(names=arguments["names"])
                # Result is already a JSON string from the FastMCP implementation
                return [create_text_response(result)]
            except Exception as e:
                logger.error(f"Error in open-nodes FastMCP implementation: {str(e)}")
                traceback.print_exc()
                return [
                    create_text_response(
                        f"Error opening nodes: {str(e)}", is_error=True
                    )
                ]
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
    logger.info("Starting MCP Agile Flow server (stdin/stdout mode)")
    print("Starting MCP Agile Flow server...", file=sys.stderr)

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
