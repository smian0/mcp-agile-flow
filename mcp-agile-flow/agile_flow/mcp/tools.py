"""
Tool registration and handling for the MCP Agile Flow server.
"""

from typing import Dict, List, Any, Callable, Optional
import json

from ..utils.logger import setup_logger
from .protocol import McpServer

logger = setup_logger("agile_flow.mcp.tools")


# JSON Schema for common parameter types
STRING_PARAM = {
    "type": "string"
}

OPTIONAL_STRING_PARAM = {
    "type": ["string", "null"]
}

INTEGER_PARAM = {
    "type": "integer"
}

BOOLEAN_PARAM = {
    "type": "boolean"
}

# Schema definitions for the various tool categories
PROJECT_SCHEMAS = {
    "create_project": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the project"
            },
            "description": {
                "type": ["string", "null"],
                "description": "Description of the project"
            }
        },
        "required": ["name"],
        "description": "Creates a new Agile project"
    },
    
    "list_projects": {
        "type": "object",
        "properties": {},
        "description": "Lists all available projects"
    },
    
    "set_active_project": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the project to activate"
            }
        },
        "required": ["name"],
        "description": "Sets the active project"
    }
}

EPIC_SCHEMAS = {
    "create_epic": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the epic"
            },
            "description": {
                "type": ["string", "null"],
                "description": "Description of the epic"
            },
            "priority": {
                "type": ["string", "null"],
                "description": "Priority of the epic",
                "enum": ["High", "Medium", "Low", None]
            }
        },
        "required": ["name"],
        "description": "Creates a new epic"
    },
    
    "list_epics": {
        "type": "object",
        "properties": {},
        "description": "Lists all epics in the current project"
    },
    
    "get_epic": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the epic"
            }
        },
        "required": ["name"],
        "description": "Gets details of a specific epic"
    },
    
    "update_epic": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the epic to update"
            },
            "field": {
                "type": "string",
                "description": "Field to update",
                "enum": ["description", "status", "priority", "acceptance_criteria", "notes"]
            },
            "value": {
                "type": ["string", "null"],
                "description": "New value for the field"
            }
        },
        "required": ["name", "field", "value"],
        "description": "Updates an existing epic"
    }
}

STORY_SCHEMAS = {
    "create_story": {
        "type": "object",
        "properties": {
            "epic": {
                "type": "string",
                "description": "Name of the epic this story belongs to"
            },
            "name": {
                "type": "string",
                "description": "Name of the story"
            },
            "description": {
                "type": ["string", "null"],
                "description": "Description of the story"
            },
            "points": {
                "type": ["integer", "string", "null"],
                "description": "Story points"
            }
        },
        "required": ["epic", "name"],
        "description": "Creates a new user story"
    },
    
    "list_stories": {
        "type": "object",
        "properties": {
            "epic": {
                "type": "string",
                "description": "Name of the epic to list stories for"
            }
        },
        "required": ["epic"],
        "description": "Lists all stories for an epic"
    },
    
    "get_story": {
        "type": "object",
        "properties": {
            "epic": {
                "type": "string",
                "description": "Name of the epic"
            },
            "name": {
                "type": "string",
                "description": "Name of the story"
            }
        },
        "required": ["epic", "name"],
        "description": "Gets details of a specific story"
    },
    
    "update_story": {
        "type": "object",
        "properties": {
            "epic": {
                "type": "string",
                "description": "Name of the epic"
            },
            "name": {
                "type": "string",
                "description": "Name of the story to update"
            },
            "field": {
                "type": "string",
                "description": "Field to update",
                "enum": ["description", "status", "points", "acceptance_criteria", "notes"]
            },
            "value": {
                "type": ["string", "integer", "null"],
                "description": "New value for the field"
            }
        },
        "required": ["epic", "name", "field", "value"],
        "description": "Updates an existing story"
    }
}

TASK_SCHEMAS = {
    "create_task": {
        "type": "object",
        "properties": {
            "epic": {
                "type": "string",
                "description": "Name of the epic"
            },
            "story": {
                "type": "string",
                "description": "Name of the story this task belongs to"
            },
            "name": {
                "type": "string",
                "description": "Name of the task"
            },
            "description": {
                "type": ["string", "null"],
                "description": "Description of the task"
            }
        },
        "required": ["epic", "story", "name"],
        "description": "Creates a new task"
    },
    
    "list_tasks": {
        "type": "object",
        "properties": {
            "epic": {
                "type": "string",
                "description": "Name of the epic"
            },
            "story": {
                "type": "string",
                "description": "Name of the story to list tasks for"
            }
        },
        "required": ["epic", "story"],
        "description": "Lists all tasks for a story"
    },
    
    "get_task": {
        "type": "object",
        "properties": {
            "epic": {
                "type": "string",
                "description": "Name of the epic"
            },
            "story": {
                "type": "string",
                "description": "Name of the story"
            },
            "name": {
                "type": "string",
                "description": "Name of the task"
            }
        },
        "required": ["epic", "story", "name"],
        "description": "Gets details of a specific task"
    },
    
    "update_task": {
        "type": "object",
        "properties": {
            "epic": {
                "type": "string",
                "description": "Name of the epic"
            },
            "story": {
                "type": "string",
                "description": "Name of the story"
            },
            "name": {
                "type": "string",
                "description": "Name of the task to update"
            },
            "field": {
                "type": "string",
                "description": "Field to update",
                "enum": ["description", "status", "assigned_to", "checklist", "notes"]
            },
            "value": {
                "type": ["string", "null"],
                "description": "New value for the field"
            }
        },
        "required": ["epic", "story", "name", "field", "value"],
        "description": "Updates an existing task"
    }
}

DOC_SCHEMAS = {
    "generate_prd": {
        "type": "object",
        "properties": {},
        "description": "Generates a PRD (Product Requirements Document)"
    },
    
    "generate_architecture": {
        "type": "object",
        "properties": {},
        "description": "Generates architecture documentation"
    },
    
    "generate_progress": {
        "type": "object",
        "properties": {},
        "description": "Generates progress report"
    },
    
    "get_document": {
        "type": "object",
        "properties": {
            "doc_type": {
                "type": "string",
                "description": "Type of document to retrieve",
                "enum": ["project", "progress", "epic", "story", "task"]
            },
            "epic": {
                "type": ["string", "null"],
                "description": "Name of the epic (for epic, story, or task documents)"
            },
            "story": {
                "type": ["string", "null"],
                "description": "Name of the story (for story or task documents)"
            },
            "name": {
                "type": ["string", "null"],
                "description": "Name of the item (for epic, story, or task documents)"
            }
        },
        "required": ["doc_type"],
        "description": "Gets content of a document"
    },
    
    "update_document": {
        "type": "object",
        "properties": {
            "doc_type": {
                "type": "string",
                "description": "Type of document to update",
                "enum": ["project", "progress", "epic", "story", "task"]
            },
            "epic": {
                "type": ["string", "null"],
                "description": "Name of the epic (for epic, story, or task documents)"
            },
            "story": {
                "type": ["string", "null"],
                "description": "Name of the story (for story or task documents)"
            },
            "name": {
                "type": ["string", "null"],
                "description": "Name of the item (for epic, story, or task documents)"
            },
            "content": {
                "type": "string",
                "description": "New content for the document"
            }
        },
        "required": ["doc_type", "content"],
        "description": "Updates a document"
    }
}

IDE_SCHEMAS = {
    "generate_cursor_rules": {
        "type": "object",
        "properties": {},
        "description": "Generates Cursor IDE rules"
    },
    
    "generate_windsurfer_rules": {
        "type": "object",
        "properties": {},
        "description": "Generates WindSurfer IDE rules"
    },
    
    "generate_copilot_rules": {
        "type": "object",
        "properties": {},
        "description": "Generates GitHub Copilot rules"
    },
    
    "generate_vscode_rules": {
        "type": "object",
        "properties": {},
        "description": "Generates VS Code rules"
    },
    
    "generate_cline_rules": {
        "type": "object",
        "properties": {},
        "description": "Generates Cline IDE rules"
    },
    
    "generate_all_rules": {
        "type": "object",
        "properties": {},
        "description": "Generates rules for all supported IDEs"
    }
}

CONFIG_SCHEMAS = {
    "get_config": {
        "type": "object",
        "properties": {},
        "description": "Gets current configuration"
    },
    
    "set_config": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Configuration key to set"
            },
            "value": {
                "type": ["string", "boolean", "integer", "null"],
                "description": "Value to set for the key"
            }
        },
        "required": ["key", "value"],
        "description": "Updates configuration"
    }
}


def register_tools(
    server: McpServer, 
    project_handlers: Dict[str, Callable],
    epic_handlers: Dict[str, Callable],
    story_handlers: Dict[str, Callable],
    task_handlers: Dict[str, Callable],
    doc_handlers: Dict[str, Callable],
    ide_handlers: Dict[str, Callable],
    config_handlers: Dict[str, Callable]
) -> None:
    """
    Register all tools with the MCP server.
    
    Args:
        server: McpServer instance.
        project_handlers: Dictionary mapping project tool names to handler functions.
        epic_handlers: Dictionary mapping epic tool names to handler functions.
        story_handlers: Dictionary mapping story tool names to handler functions.
        task_handlers: Dictionary mapping task tool names to handler functions.
        doc_handlers: Dictionary mapping doc tool names to handler functions.
        ide_handlers: Dictionary mapping ide tool names to handler functions.
        config_handlers: Dictionary mapping config tool names to handler functions.
    """
    # Log the handlers we received
    logger.debug(f"Project handlers: {list(project_handlers.keys())}")
    logger.debug(f"Epic handlers: {list(epic_handlers.keys())}")
    logger.debug(f"Story handlers: {list(story_handlers.keys())}")
    logger.debug(f"Task handlers: {list(task_handlers.keys())}")
    logger.debug(f"Doc handlers: {list(doc_handlers.keys())}")
    logger.debug(f"IDE handlers: {list(ide_handlers.keys())}")
    logger.debug(f"Config handlers: {list(config_handlers.keys())}")
    
    # Register project tools
    for name, handler in project_handlers.items():
        if name in PROJECT_SCHEMAS:
            server.register_tool(name, handler, PROJECT_SCHEMAS[name])
            logger.debug(f"Registered project tool: {name}")
        else:
            logger.warning(f"No schema defined for project tool: {name}")
    
    # Register epic tools
    for name, handler in epic_handlers.items():
        if name in EPIC_SCHEMAS:
            server.register_tool(name, handler, EPIC_SCHEMAS[name])
            logger.debug(f"Registered epic tool: {name}")
        else:
            logger.warning(f"No schema defined for epic tool: {name}")
    
    # Register story tools
    for name, handler in story_handlers.items():
        if name in STORY_SCHEMAS:
            server.register_tool(name, handler, STORY_SCHEMAS[name])
            logger.debug(f"Registered story tool: {name}")
        else:
            logger.warning(f"No schema defined for story tool: {name}")
    
    # Register task tools
    for name, handler in task_handlers.items():
        if name in TASK_SCHEMAS:
            server.register_tool(name, handler, TASK_SCHEMAS[name])
            logger.debug(f"Registered task tool: {name}")
        else:
            logger.warning(f"No schema defined for task tool: {name}")
    
    # Register doc tools
    for name, handler in doc_handlers.items():
        if name in DOC_SCHEMAS:
            server.register_tool(name, handler, DOC_SCHEMAS[name])
            logger.debug(f"Registered doc tool: {name}")
        else:
            logger.warning(f"No schema defined for doc tool: {name}")
    
    # Register IDE tools
    for name, handler in ide_handlers.items():
        if name in IDE_SCHEMAS:
            server.register_tool(name, handler, IDE_SCHEMAS[name])
            logger.debug(f"Registered IDE tool: {name}")
        else:
            logger.warning(f"No schema defined for IDE tool: {name}")
    
    # Register config tools
    for name, handler in config_handlers.items():
        if name in CONFIG_SCHEMAS:
            server.register_tool(name, handler, CONFIG_SCHEMAS[name])
            logger.debug(f"Registered config tool: {name}")
        else:
            logger.warning(f"No schema defined for config tool: {name}")
            
    logger.info(f"Registered {len(server.tools)} tools: {list(server.tools.keys())}")
