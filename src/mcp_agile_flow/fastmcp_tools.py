"""
Tools for the MCP Agile Flow server.
FastMCP tool implementations.
"""
import os
import json
import time
import warnings
import logging
import typing
from typing import Optional, Dict, Any, List, Tuple, Union, Annotated
from pathlib import Path
import shutil

# Import from mcp directly
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Import IDE paths from migration tool
from .migration_tool import IDE_PATHS

# Constants for IDE types and validation
VALID_IDES = IDE_PATHS

# Import models and utilities
from .models import ProjectSettingsResponse, InitializeIDEResponse
from .utils import (
    get_project_settings as get_settings_util,
    get_special_directories,
    detect_mcp_command,
)
from .migration_tool import (
    detect_conflicts,
    get_conflict_details,
    get_ide_path,
    migrate_config,
    merge_configurations,
)
from .think_tool import think as think_impl
from .think_tool import get_thoughts as get_thoughts_impl
from .think_tool import clear_thoughts as clear_thoughts_impl
from .think_tool import get_thought_stats as get_thought_stats_impl
from .think_tool import detect_thinking_directive as detect_thinking_directive_impl
from .think_tool import think_more as think_more_impl
from .think_tool import should_think as should_think_impl
from .initialize_ide_rules import initialize_ide_rules as initialize_ide_rules_impl

# Create FastMCP instance
mcp = FastMCP("mcp_agile_flow")

# Tool implementations
@mcp.tool()
def get_project_settings(
    proposed_path: Optional[str] = Field(
        description="Optional path to the project directory. If omitted, invalid, or not a string, the current working directory will be used", 
        default=None
    ),
) -> str:
    """
    Get the project settings for the current working directory or a proposed path.
    
    Returns configuration settings including project path, type, and metadata.
    If proposed_path is not provided or invalid, uses the current directory.
    """
    try:
        # Extract actual value if it's a Field object
        if hasattr(proposed_path, "default"):
            proposed_path = proposed_path.default
        
        # Handle potentially invalid paths (incorrect types, etc.)
        if proposed_path is not None and not isinstance(proposed_path, str):
            proposed_path = None  # This will trigger using the current directory
            
        # Handle potentially unsafe paths
        if proposed_path == "/":
            return json.dumps({
                "success": False,
                "error": "Root path is not allowed for safety reasons",
                "message": "Please provide a valid project path. You can look up project path and try again.",
                "project_path": None,
                "source": "fallback from rejected root path",
                "is_root": True
            }, indent=2)
            
        # Get project path and settings
        project_settings = get_settings_util(proposed_path)
        
        # Return with success flag
        return json.dumps({
            "success": True,
            "project_path": project_settings["project_path"],
            "current_directory": project_settings["current_directory"],
            "is_project_path_manually_set": project_settings["is_project_path_manually_set"],
            "ai_docs_directory": project_settings["ai_docs_directory"],
            "source": project_settings["source"],
            "is_root": project_settings["is_root"],
            "is_writable": project_settings["is_writable"],
            "exists": project_settings["exists"],
            "project_type": project_settings["project_type"],
            "rules": project_settings["rules"],
            "project_metadata": {},  # Add empty project_metadata as expected by tests
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Please provide a valid project path. You can look up project path and try again.",
            "project_path": None,
            "source": "error fallback"
        }, indent=2)

@mcp.tool()
def think(
    thought: str = Field(description="The content of the thought to record"),
    category: str = Field(description="Category for organizing thoughts", default="default"),
    depth: int = Field(description="Depth level of the thought (0 for normal, higher for deeper analysis)", default=0),
    timestamp: Optional[int] = Field(description="Optional timestamp for the thought", default=None),
    references: Optional[List[str]] = Field(description="Optional list of references for the thought", default=None),
    metadata: Optional[Dict[str, Any]] = Field(description="Optional metadata for the thought", default=None),
) -> str:
    """
    Record a thought for later reference and analysis.
    
    This tool allows you to record thoughts during development or analysis processes.
    Thoughts can be organized by category and depth to create a hierarchical structure
    of analysis.
    """
    # Extract actual values if they're Field objects
    if hasattr(thought, "default"):
        thought = thought.default
    if hasattr(category, "default"):
        category = category.default
    if hasattr(depth, "default"):
        depth = depth.default
    if hasattr(timestamp, "default"):
        timestamp = timestamp.default
    if hasattr(references, "default"):
        references = references.default
    if hasattr(metadata, "default"):
        metadata = metadata.default
        
    result = think_impl(thought, category, depth, None)
    # Convert dict to formatted JSON string
    return json.dumps(result, indent=2)

@mcp.tool()
def get_thoughts(
    category: Optional[str] = Field(description="Filter to get thoughts from a specific category", default=None),
    organize_by_depth: bool = Field(description="Whether to organize thoughts by depth relationships", default=False),
) -> str:
    """
    Retrieve recorded thoughts.
    
    This tool retrieves all previously recorded thoughts, optionally filtered by category.
    You can also choose to organize them hierarchically by depth.
    """
    # Extract actual values if they're Field objects
    if hasattr(category, "default"):
        category = category.default
    if hasattr(organize_by_depth, "default"):
        organize_by_depth = organize_by_depth.default
        
    result = get_thoughts_impl(category, organize_by_depth)
    return json.dumps(result, indent=2)

@mcp.tool()
def clear_thoughts(
    category: Optional[str] = Field(description="Filter to clear thoughts from a specific category only", default=None),
) -> str:
    """
    Clear recorded thoughts.
    
    This tool removes previously recorded thoughts, optionally filtered by category.
    If no category is specified, all thoughts will be cleared.
    """
    # Extract actual value if it's a Field object
    if hasattr(category, "default"):
        category = category.default
        
    result = clear_thoughts_impl(category)
    return json.dumps(result, indent=2)

@mcp.tool()
def get_thought_stats(
    category: Optional[str] = Field(description="Filter to get stats for a specific category", default=None),
) -> str:
    """
    Get statistics about recorded thoughts.
    
    This tool provides statistics about recorded thoughts, such as count and 
    depth distribution. Results can be filtered by category.
    """
    # Extract actual value if it's a Field object
    if hasattr(category, "default"):
        category = category.default
        
    result = get_thought_stats_impl(category)
    return json.dumps(result, indent=2)

@mcp.tool()
def detect_thinking_directive(
    text: str = Field(description="The text to analyze for thinking directives")
) -> str:
    """
    Detect thinking directives.
    
    This tool analyzes text to detect directives suggesting deeper thinking,
    such as "think harder", "think deeper", "think again", etc.
    """
    # Extract actual value if it's a Field object
    if hasattr(text, "default"):
        text = text.default
        
    result = detect_thinking_directive_impl(text)
    return json.dumps(result, indent=2)

@mcp.tool()
def should_think(
    query: str = Field(description="The query to assess for deep thinking requirements")
) -> str:
    """
    Assess whether deeper thinking is needed for a query.
    
    This tool analyzes a query to determine if it requires deeper thinking,
    based on complexity indicators and context.
    """
    # Extract actual value if it's a Field object
    if hasattr(query, "default"):
        query = query.default
        
    result = should_think_impl(query)
    return json.dumps(result, indent=2)

@mcp.tool()
def think_more(
    query: str = Field(description="The query to think more deeply about")
) -> str:
    """
    Get guidance for thinking more deeply.
    
    This tool provides suggestions and guidance for thinking more deeply
    about a specific query or thought.
    """
    # Extract actual value if it's a Field object
    if hasattr(query, "default"):
        query = query.default
        
    result = think_more_impl(query, None)
    return json.dumps(result, indent=2)

@mcp.tool()
def initialize_ide(
    project_path: Optional[str] = Field(
        description="Path to the project. If not provided, invalid, or directory doesn't exist, the current working directory will be used automatically", 
        default=None
    ),
    ide_type: str = Field(
        description=f"The type of IDE to initialize ({', '.join(VALID_IDES.keys())})",
        default="cursor"
    )
) -> str:
    """
    Initialize IDE project structure with appropriate directories and config files.
    
    This tool sets up the necessary directories and configuration files for IDE 
    integration, including .ai-templates directory and IDE-specific rules.
    
    Note: If project_path is omitted, not a string, invalid, or the directory doesn't exist,
    the current working directory will be used automatically.
    """
    # Extract actual values if they're Field objects
    if hasattr(project_path, "default"):
        project_path = project_path.default
    if hasattr(ide_type, "default"):
        ide_type = ide_type.default
        
    # Get project settings first to ensure we have a valid path
    settings_json = get_project_settings(proposed_path=project_path)
    settings = json.loads(settings_json)
    
    if not settings["success"]:
        return json.dumps({
            "success": False,
            "project_path": None,
            "templates_directory": "",
            "error": settings["error"] if "error" in settings else "Invalid project path",
            "message": "Please provide a valid project path. You can look up project path and try again."
        }, indent=2)
    
    # Use the validated project path from settings
    project_path = settings["project_path"]
    
    # Override project type with explicitly provided IDE type if given
    project_type = ide_type.lower() if ide_type else settings["project_type"]
    
    if project_type not in VALID_IDES:
        return json.dumps({
            "success": False,
            "project_path": project_path,
            "templates_directory": "",
            "error": f"Unknown IDE type: {project_type}",
            "message": f"Supported IDE types are: {', '.join(VALID_IDES.keys())}"
        }, indent=2)
    
    try:
        # Create .ai-templates directory
        templates_dir = os.path.join(project_path, ".ai-templates")
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create IDE-specific rules file/directory
        if project_type == "cursor":
            rules_dir = os.path.join(project_path, ".cursor", "rules")
            os.makedirs(rules_dir, exist_ok=True)
            
            # Create default markdown files
            default_files = {
                "001-project-basics.md": "# Project Structure\n\n- Follow the existing project structure\n- Document new components\n- Keep related files together",
                "002-code-guidelines.md": "# Coding Standards\n\n- Follow PEP 8 for Python code\n- Write tests for all new features\n- Document public functions and classes",
                "003-best-practices.md": "# Best Practices\n\n- Review code before submitting\n- Handle errors gracefully\n- Use meaningful variable and function names"
            }
            
            for filename, content in default_files.items():
                file_path = os.path.join(rules_dir, filename)
                if not os.path.exists(file_path):
                    with open(file_path, "w") as f:
                        f.write(content)
            
            rules_location = rules_dir
        else:
            # Handle other IDE types
            rules_file = os.path.join(
                project_path,
                ".windsurfrules" if project_type.startswith("windsurf") else
                ".clinerules" if project_type in ["cline", "roo"] else
                os.path.join(".github", "copilot-instructions.md") if project_type == "copilot" else
                ".claude-desktop-rules"
            )
            
            # Create parent directory if needed (e.g., for .github)
            if project_type == "copilot":
                os.makedirs(os.path.dirname(rules_file), exist_ok=True)
                
            with open(rules_file, "w") as f:
                f.write(f"# {project_type.title()} Rules\n")
            rules_location = rules_file
        
        return json.dumps({
            "success": True,
            "project_path": project_path,
            "templates_directory": os.path.join(project_path, ".ai-templates"),
            "rules_directory": rules_location if project_type == "cursor" else None,
            "rules_file": rules_location if project_type != "cursor" else None,
            "message": f"Initialized {project_type} project in {project_path}",
            "initialized_rules": True
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "project_path": project_path,
            "templates_directory": "",
            "error": str(e),
            "message": "Please provide a valid project path. You can look up project path and try again."
        }, indent=2)

@mcp.tool()
def initialize_ide_rules(
    ide: str = Field(
        description="The IDE to initialize rules for (cursor, windsurf, cline, copilot)",
        default="cursor"
    ),
    project_path: Optional[str] = Field(
        description="Path to the project. If not provided or invalid, the current working directory will be used automatically",
        default=None
    ),
) -> str:
    """
    Initialize IDE rules for a project.
    
    This tool sets up IDE-specific rules for a project, creating the necessary 
    files and directories for AI assistants to understand project conventions.
    
    Note: If project_path is omitted, not a string, or invalid, the current working
    directory will be used automatically.
    """
    # Extract the actual value from the project_path if it's a Field
    if hasattr(project_path, "default"):
        project_path = project_path.default
    
    # Handle potentially invalid paths (empty strings, incorrect types, etc.)
    if project_path is not None and not isinstance(project_path, str):
        project_path = None  # This will trigger using the current directory
        
    # Extract the actual value from ide if it's a Field  
    if hasattr(ide, "default"):
        ide = ide.default
    
    # Get project settings and parse the JSON response
    settings_json = get_project_settings(proposed_path=project_path)
    settings = json.loads(settings_json)
    
    if not settings["success"]:
        return json.dumps({
            "success": False,
            "error": settings.get("error", "Failed to get project settings"),
            "message": "Please provide a valid project path. You can look up project path and try again.",
            "project_path": None
        }, indent=2)
    
    actual_project_path = settings["project_path"]
    
    try:
        # Call the specialized implementation and format the result
        result = initialize_ide_rules_impl(ide=ide, project_path=actual_project_path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Please provide a valid project path. You can look up project path and try again.",
            "project_path": None
        }, indent=2)

@mcp.tool()
def prime_context(
    project_path: Optional[str] = Field(
        description="Path to the project. If not provided or invalid, the current working directory will be used automatically", 
        default=None
    ),
    depth: str = Field(
        description="Depth of analysis (minimal, standard, deep)",
        default="standard"
    )
) -> str:
    """
    Prime project context by analyzing documentation and structure.
    
    This tool analyzes the project structure and documentation to provide
    context information for AI assistants working with the project.
    
    Note: If project_path is omitted, not a string, or invalid, the current working
    directory will be used automatically.
    """
    # Extract the actual values if they're Field objects
    if hasattr(project_path, "default"):
        project_path = project_path.default
    if hasattr(depth, "default"):
        depth = depth.default
        
    # Handle potentially invalid paths (incorrect types, etc.)
    if project_path is not None and not isinstance(project_path, str):
        project_path = None  # This will trigger using the current directory
        
    settings = get_project_settings(proposed_path=project_path)
    actual_project_path = settings["project_path"]
    
    # Create a context structure that matches test expectations
    context = {
        "project": {
            "name": os.path.basename(actual_project_path),
            "path": actual_project_path,
            "type": settings["project_type"],
            "location": {
                "path": actual_project_path
            },
        },
        "depth": depth,
        "focus_areas": []
    }
    
    # Scan for documents in the ai-docs directory
    ai_docs_dir = settings.get("ai_docs_directory")
    if ai_docs_dir and os.path.exists(ai_docs_dir):
        focus_areas = []
        for doc_file in Path(ai_docs_dir).glob("*.md"):
            try:
                with open(doc_file, "r") as f:
                    content = f.read()
                focus_areas.append({
                    "type": doc_file.stem,
                    "path": str(doc_file),
                    "name": doc_file.stem.title(),
                })
            except Exception as e:
                logger.warning(f"Error reading document {doc_file}: {str(e)}")
        
        context["focus_areas"] = focus_areas
    
    return json.dumps({
        "success": True,
        "message": "Context primed for project analysis",
        "context": context
    }, indent=2)

@mcp.tool()
def migrate_mcp_config(
    from_ide: str = Field(
        description=f"Source IDE to migrate from. Valid options: {', '.join(IDE_PATHS.keys())}",
        default="cursor"
    ),
    to_ide: Optional[str] = Field(
        description=f"Target IDE to migrate to. Valid options: {', '.join(IDE_PATHS.keys())}",
        default=None
    )
) -> str:
    """
    Migrate MCP configuration between different IDEs.
    
    This tool helps migrate configuration and rules between different IDEs,
    ensuring consistent AI assistance across different environments.
    """
    # Extract actual values if they're Field objects
    if hasattr(from_ide, "default"):
        from_ide = from_ide.default
    if hasattr(to_ide, "default"):
        to_ide = to_ide.default
    
    # Validate IDE types
    from_ide = from_ide.lower() if from_ide else "cursor"
    to_ide = to_ide.lower() if to_ide else None
    
    if from_ide not in IDE_PATHS:
        return json.dumps({
            "success": False,
            "error": f"Unknown source IDE: {from_ide}",
            "message": f"Supported IDE types are: {', '.join(IDE_PATHS.keys())}",
            "source_path": None,
            "target_path": None
        }, indent=2)
        
    if not to_ide:
        return json.dumps({
            "success": False,
            "message": "Please specify the target IDE to migrate to",
            "source_path": get_ide_path(from_ide),
            "target_path": None
        }, indent=2)
        
    if to_ide not in IDE_PATHS:
        return json.dumps({
            "success": False,
            "error": f"Unknown target IDE: {to_ide}",
            "message": f"Supported IDE types are: {', '.join(IDE_PATHS.keys())}",
            "source_path": get_ide_path(from_ide),
            "target_path": None
        }, indent=2)
        
    if from_ide == to_ide:
        return json.dumps({
            "success": False,
            "error": "Source and target IDEs are the same",
            "message": "Cannot migrate configuration to the same IDE",
            "source_path": get_ide_path(from_ide),
            "target_path": get_ide_path(to_ide)
        }, indent=2)
    
    # Get the actual paths for both IDEs
    source_path = get_ide_path(from_ide)
    target_path = get_ide_path(to_ide)
    
    # Perform the migration
    success, error_message, conflicts, conflict_details = migrate_config(
        from_ide=from_ide,
        to_ide=to_ide,
        backup=True
    )
    
    if not success:
        return json.dumps({
            "success": False,
            "error": error_message,
            "message": f"Failed to migrate configuration from {from_ide} to {to_ide}",
            "source_path": source_path,
            "target_path": target_path
        }, indent=2)
    
    return json.dumps({
        "success": True,
        "from_ide": from_ide,
        "to_ide": to_ide,
        "source_path": source_path,
        "target_path": target_path,
        "migrated_rules": True,
        "conflicts": conflicts if conflicts else [],
        "conflict_details": conflict_details if conflict_details else {},
        "message": f"Migrated configuration from {from_ide} ({source_path}) to {to_ide} ({target_path})"
    }, indent=2)

@mcp.tool()
def process_natural_language(
    query: str = Field(description="The natural language query to process into a tool call")
) -> str:
    """
    Process natural language command and route to appropriate tool.
    
    This tool takes a natural language query and determines which tool to call
    with what parameters, providing a way to interact with the MCP Agile Flow
    tools using natural language.
    """
    # Extract the actual value from query if it's a Field
    if hasattr(query, "default"):
        query = query.default
        
    # Detect command from natural language
    tool_name, arguments = detect_mcp_command(query)
    
    if not tool_name:
        response = {
            "success": False,
            "error": "Could not determine action",
            "message": "Your command wasn't recognized. Try a more specific request."
        }
        return json.dumps(response, indent=2)
    
    # List of supported tools
    supported_tools = [
        "get_project_settings",
        "initialize_ide",
        "initialize_ide_rules",
        "prime_context",
        "migrate_mcp_config",
        "think",
        "get_thoughts",
        "clear_thoughts",
        "get_thought_stats"
    ]
        
    # Check if tool is supported
    if tool_name not in supported_tools:
        response = {
            "success": False,
            "error": f"Unsupported tool: {tool_name}",
            "message": f"The action '{tool_name}' isn't supported."
        }
        return json.dumps(response, indent=2)
    
    # Call the appropriate tool
    try:
        if tool_name == "get_project_settings":
            result = get_project_settings(**(arguments or {}))
        elif tool_name == "initialize_ide":
            result = initialize_ide(**(arguments or {}))
        elif tool_name == "initialize_ide_rules":
            result = initialize_ide_rules(**(arguments or {}))
        elif tool_name == "prime_context":
            result = prime_context(**(arguments or {}))
        elif tool_name == "migrate_mcp_config":
            result = migrate_mcp_config(**(arguments or {}))
        elif tool_name == "think":
            result = think(**(arguments or {}))
        elif tool_name == "get_thoughts":
            result = get_thoughts()
        elif tool_name == "clear_thoughts":
            result = clear_thoughts()
        elif tool_name == "get_thought_stats":
            result = get_thought_stats()
        else:
            response = {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "message": "The detected command could not be routed to a known tool"
            }
            return json.dumps(response, indent=2)
        
        # Check if the result is already a JSON string
        try:
            # Try to parse as JSON to see if it's already a JSON string
            parsed_result = json.loads(result)
            # If it's already JSON, just return it
            return result
        except (json.JSONDecodeError, TypeError):
            # If it's not a JSON string, return it directly
            return result
            
    except Exception as e:
        # Handle any errors during processing
        response = {
            "success": False,
            "error": f"Error processing command: {str(e)}",
            "message": "An error occurred while processing your command"
        }
        return json.dumps(response, indent=2)

# Export all tools
__all__ = [
    'get_project_settings',
    'think',
    'get_thoughts',
    'clear_thoughts',
    'get_thought_stats',
    'detect_thinking_directive',
    'think_more',
    'initialize_ide',
    'initialize_ide_rules',
    'prime_context',
    'migrate_mcp_config',
    'process_natural_language'
]
