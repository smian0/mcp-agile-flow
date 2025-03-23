"""
FastMCP Tools for MCP Agile Flow

This module implements MCP Agile Flow tools using FastMCP for a more Pythonic interface.
These implementations coexist with the traditional MCP tools while we migrate.
"""

import json
import logging
import os
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP
from .utils import get_project_settings as get_settings_util
from .memory_graph import KnowledgeGraphManager

# Set up logging
logger = logging.getLogger(__name__)

# Create a FastMCP instance
fastmcp = FastMCP("agile-flow-fast")


@fastmcp.tool()
def get_project_settings(proposed_path: Optional[str] = None) -> str:
    """
    Returns comprehensive project settings including project path, knowledge graph directory, 
    AI docs directory, project type, metadata, and other configuration.
    
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
    # In a real implementation, we would get these from memory_manager if available
    response_data["project_type"] = "generic"
    response_data["project_metadata"] = {}
    
    # Log the response for debugging
    logger.info(f"FastMCP: Project settings response: {response_data}")
    
    # Return as a JSON string to match the expected return type
    return json.dumps(response_data, indent=2)


@fastmcp.tool()
def get_mermaid_diagram() -> str:
    """
    Get a Mermaid diagram representation of the knowledge graph.
    
    Returns:
        JSON string containing a Mermaid diagram representation
    """
    logger.info("FastMCP: Getting Mermaid diagram representation of knowledge graph")
    
    try:
        # This is a placeholder implementation
        # In a real implementation, you would:
        # 1. Import the necessary function to generate the diagram
        # 2. Call that function to get the diagram data
        # 3. Format and return it as JSON
        
        # Placeholder response
        response_data = {
            "success": True,
            "diagram_type": "mermaid",
            "content": "graph TD;\nA[Knowledge Graph] --> B[No nodes available];"
        }
        
        # Return as a JSON string to match the expected return type
        return json.dumps(response_data, indent=2)
    except Exception as e:
        logger.error(f"FastMCP: Error getting Mermaid diagram: {str(e)}")
        
        # Return error as JSON
        response_data = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(response_data, indent=2)


@fastmcp.tool()
def read_graph() -> str:
    """
    Read the entire knowledge graph.
    
    Returns:
        JSON string containing the entire knowledge graph
    """
    logger.info("FastMCP: Reading the entire knowledge graph")
    
    try:
        # Create a KnowledgeGraphManager instance
        manager = KnowledgeGraphManager()
        
        # Get the graph data
        graph = manager.graph
        
        # Convert to a serializable format
        graph_data = {
            "success": True,
            "project_type": graph.project_type,
            "project_metadata": graph.project_metadata,
            "entities": [
                {
                    "name": entity.name,
                    "entity_type": entity.entity_type,
                    "observations": entity.observations
                }
                for entity in graph.entities
            ],
            "relations": [
                {
                    "from_entity": relation.from_entity,
                    "to_entity": relation.to_entity,
                    "relation_type": relation.relation_type
                }
                for relation in graph.relations
            ]
        }
        
        # Return as a JSON string
        return json.dumps(graph_data, indent=2)
    except Exception as e:
        logger.error(f"FastMCP: Error reading knowledge graph: {str(e)}")
        
        # Return error as JSON
        response_data = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(response_data, indent=2)


@fastmcp.tool()
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