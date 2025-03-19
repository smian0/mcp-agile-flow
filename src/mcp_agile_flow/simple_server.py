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
import datetime
from typing import Dict, List, Optional, Tuple, Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import stdio

# Configure logging
logger = logging.getLogger(__name__)

# Store notes as a simple key-value dict to demonstrate state management
notes: Dict[str, str] = {}

# Keep track of tool invocations for debugging
tool_invocations = []

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
    
    # Also log to stderr for immediate visibility during testing
    print(f"TOOL INVOCATION: {name} with args: {arguments}", file=sys.stderr)

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
            name="hello-world",
            description="Returns a simple hello world message",
            inputSchema={
                "type": "object",
                "properties": {
                    "random_string": {"type": "string"},
                },
                "required": [],
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
            name="Hey Sho",
            description="Process natural language commands using 'Hey Sho' syntax. This tool allows you to use natural language instead of specific tool syntax. You can ask for project paths, create notes, or get simple greetings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string", 
                        "description": "The natural language command starting with 'Hey Sho'. For example: 'Hey Sho, get project path', 'Hey Sho, add a note called meeting with content Remember the team meeting', or 'Hey Sho, hello world'.",
                        "examples": [
                            "Hey Sho, get project path",
                            "Hey Sho, add a note called reminder with content Don't forget the meeting",
                            "Hey Sho, hello world"
                        ]
                    },
                },
                "required": ["message"],
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

class ToolResponse:
    """Response from a tool call."""
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text

def check_for_greeting(message: str) -> bool:
    """Check if a message contains a greeting for Sho."""
    return message and "hey sho" in message.lower()

def parse_greeting_command(message: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parse a greeting message to extract the command and arguments.
    
    Args:
        message: The greeting message (e.g., "Hey Sho, get project path")
        
    Returns:
        A tuple of (command, arguments)
    """
    # Remove the greeting part but preserve the original case for content extraction
    original_command_text = re.sub(r'hey\s+sho[,\s]*', '', message, flags=re.IGNORECASE)
    # Lowercase version for pattern matching 
    command_text = original_command_text.lower()
    
    # Default command and arguments
    command = "hello-world"
    arguments = {}
    
    # Command mapping
    command_mappings = {
        r'(get|show|display).*project.*path': {
            'command': 'get-project-path',
            'args': {}
        },
        r'(add|create|make|save).*note': {
            'command': 'add-note',
            'args': lambda text: extract_note_args(original_command_text)
        },
        r'hello.*world': {
            'command': 'hello-world',
            'args': {}
        }
    }
    
    # Try to match a command
    for pattern, action in command_mappings.items():
        if re.search(pattern, command_text, re.IGNORECASE):
            command = action['command']
            
            # Handle arguments
            if callable(action['args']):
                arguments = action['args'](original_command_text)
            else:
                arguments = action['args']
            
            break
    
    logger.debug(f"Parsed command: {command} with arguments: {arguments}")
    return command, arguments

def extract_note_args(command_text: str) -> Dict[str, str]:
    """Extract note name and content from command text."""
    # Try to find a name for the note
    name_match = re.search(r'(?:called|named|with name|title)\s+["\']?([^"\']+?)["\']?(?:\s+with\s+content|\s+saying|\s+that\s+says|\s+contents?|$)', command_text, re.IGNORECASE)
    note_name = name_match.group(1).strip() if name_match else "new-note"
    
    # Try to find content for the note - retain original case
    content_match = re.search(r'(?:with\s+content|saying|that\s+says|contents?)\s+["\']?([^"\']+)["\']?$', command_text, re.IGNORECASE)
    note_content = content_match.group(1).strip() if content_match else "New note content"
    
    return {
        "name": note_name,
        "content": note_content
    }

@mcp.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[dict]
) -> List[ToolResponse]:
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
    
    # Visible indicator that this function was called
    print(f"🛠️ TOOL CALL RECEIVED: {name}", file=sys.stderr)
    
    response = None
    try:
        if name == "Hey Sho":
            if not arguments or "message" not in arguments:
                raise ValueError("Missing message argument for Hey Sho command")
                
            message = arguments["message"]
            logger.info(f"Processing Hey Sho command: {message}")
            print(f"✨ HEY SHO COMMAND: {message}", file=sys.stderr)
            
            if not check_for_greeting(message):
                response = [ToolResponse(
                    type="error", 
                    text="Message must start with 'Hey Sho'"
                )]
                log_tool_invocation(name, arguments, response)
                return response
            
            # Parse the command and arguments
            command, cmd_args = parse_greeting_command(message)
            logger.info(f"Parsed command: {command} with arguments: {cmd_args}")
            print(f"🔄 PARSED COMMAND: {command} with args: {cmd_args}", file=sys.stderr)
            
            # Call the appropriate tool with the parsed arguments
            response = await handle_call_tool(command, cmd_args)
            log_tool_invocation(name, arguments, response)
            return response
        
        elif name == "debug-tools":
            # Get the count parameter, default to 5
            count = 5
            if arguments and "count" in arguments:
                count = int(arguments["count"])
            
            # Get the most recent invocations
            recent = tool_invocations[-count:] if tool_invocations else []
            
            if not recent:
                text = "No tool invocations recorded yet."
            else:
                text = f"Recent tool invocations (last {len(recent)}):\n\n"
                for idx, inv in enumerate(recent, 1):
                    time = inv["timestamp"].split("T")[1].split(".")[0]  # Just the time portion
                    text += f"{idx}. [{time}] Tool: {inv['tool']}\n"
                    text += f"   Arguments: {json.dumps(inv['arguments'])}\n"
                    text += f"   Response: {inv['response_summary']}\n\n"
            
            response = [ToolResponse(
                type="text",
                text=text
            )]
            log_tool_invocation(name, arguments, response)
            return response
        
        elif name == "add-note":
            if not arguments:
                raise ValueError("Missing arguments")

            note_name = arguments.get("name")
            content = arguments.get("content")

            if not note_name or not content:
                raise ValueError("Missing name or content")

            # Update server state
            notes[note_name] = content
            
            logger.info(f"Added note: {note_name}")
            logger.debug(f"Note content: {content}")

            response = [ToolResponse(
                type="text",
                text=f"Added note '{note_name}' with content: {content}"
            )]
            log_tool_invocation(name, arguments, response)
            return response
            
        elif name == "hello-world":
            response = [ToolResponse(
                type="text",
                text="Hello, World!"
            )]
            log_tool_invocation(name, arguments, response)
            return response
            
        elif name == "get-project-path":
            logger.info("Getting project paths")
            
            # Get the current working directory
            current_dir = os.getcwd()
            
            # Get the directory of the current file
            file_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Get the project root (2 levels up)
            project_root = os.path.abspath(os.path.join(file_dir, "..", ".."))
            
            logger.debug(f"Current working directory: {current_dir}")
            logger.debug(f"Server file directory: {file_dir}")
            logger.debug(f"Project root directory: {project_root}")
            
            response = [ToolResponse(
                type="text",
                text=f"Current working directory: {current_dir}\n"
                     f"Server file directory: {file_dir}\n"
                     f"Project root directory: {project_root}"
            )]
            log_tool_invocation(name, arguments, response)
            return response
            
        else:
            # Unknown tool
            response = [ToolResponse(
                type="error",
                text=f"Unknown tool: {name}"
            )]
            log_tool_invocation(name, arguments, response)
            return response
            
    except Exception as e:
        logger.error(f"Error in tool call: {e}")
        response = [ToolResponse(
            type="error",
            text=str(e)
        )]
        log_tool_invocation(name, {"error": str(e)}, response)
        return response

async def run_server():
    """
    Run the server using stdin/stdout streams.
    
    This sets up the MCP server to communicate over stdin/stdout,
    which allows it to be used with the MCP protocol directly.
    """
    logger.info("Starting Simple server (stdin/stdout mode)")
    
    async with stdio.stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="MCP Agile Flow - Simple",
                server_version="0.1.0",
                capabilities=mcp.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def run():
    """
    Run the MCP server.
    
    This is the main entry point for running the server from a command line or as a module.
    It initializes asyncio and runs the server until terminated.
    """
    print("Starting MCP Agile Flow Simple server...", file=sys.stderr)
    asyncio.run(run_server()) 