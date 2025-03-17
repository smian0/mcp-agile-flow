"""
MCP Agile Flow - Main entry point for the MCP server.
"""

import os
import sys
from typing import Dict, Any

from ..config import Config
from ..utils.logger import setup_logger
from ..mcp.protocol import McpServer
from ..mcp.tools import register_tools
from ..storage.file_manager import FileManager
from ..storage.templates import TemplateManager
from ..storage.document_generator import DocumentGenerator
from ..tools.project import ProjectManager
from ..tools.ide_rules import IDERulesManager

# Set up logger
logger = setup_logger("agile_flow.server")


def get_empty_handlers() -> Dict[str, Any]:
    """Return an empty handlers dictionary for tools that aren't implemented yet."""
    return {}


def main() -> None:
    """Run the MCP Agile Flow server."""
    # Load configuration
    config = Config()
    logger.info(f"Starting MCP Agile Flow server with project path: {config.get_project_path()}")
    
    # Initialize storage components
    file_manager = FileManager(config.get_agile_docs_path())
    template_manager = TemplateManager()
    document_generator = DocumentGenerator(file_manager, template_manager)
    
    # Initialize tool managers
    project_manager = ProjectManager(file_manager, document_generator)
    ide_rules_manager = IDERulesManager(config.get_project_path(), file_manager)
    
    # Create MCP server
    server = McpServer()
    
    # Get tool handlers
    project_handlers = project_manager.get_project_handlers()
    
    # TODO: Implement these tool handlers
    epic_handlers = get_empty_handlers()
    story_handlers = get_empty_handlers()
    task_handlers = get_empty_handlers()
    doc_handlers = get_empty_handlers()
    
    # IDE tool handlers
    ide_handlers = {
        "generate_cursor_rules": lambda args: {"rules": ide_rules_manager.generate_cursor_rules()},
        "generate_cline_rules": lambda args: {"rules": [ide_rules_manager.generate_cline_rules()]},
        "generate_all_rules": lambda args: {"rules": ide_rules_manager.generate_all_rules()}
    }
    
    # Config tool handlers
    config_handlers = {
        "get_config": lambda args: {
            "config": {
                "project_path": config.get_project_path(),
                "debug": config.is_debug_enabled()
            }
        }
    }
    
    # Register all tools
    register_tools(
        server,
        project_handlers,
        epic_handlers,
        story_handlers,
        task_handlers,
        doc_handlers,
        ide_handlers,
        config_handlers
    )
    
    # Run the server
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
        
    logger.info("Server stopped")


if __name__ == "__main__":
    main()
