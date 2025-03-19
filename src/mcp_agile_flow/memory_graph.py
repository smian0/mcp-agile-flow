#!/usr/bin/env python3
"""
Memory Knowledge Graph - A Python implementation of the repository memory system
that integrates with MCP Agile Flow.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from dataclasses import dataclass, field

# Import MCP server types
from mcp.server import Server
from mcp.types import Tool, TextContent


@dataclass
class Entity:
    """An entity in the knowledge graph."""
    name: str
    entity_type: str
    observations: List[str] = field(default_factory=list)


@dataclass
class Relation:
    """A relation between entities in the knowledge graph."""
    from_entity: str
    to_entity: str
    relation_type: str


@dataclass
class KnowledgeGraph:
    """The complete knowledge graph structure."""
    entities: List[Entity] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)


class KnowledgeGraphManager:
    """Manager for the knowledge graph operations.
    
    This class provides methods to create, read, update, and delete entities
    and relations in a knowledge graph. The graph is stored as a JSON file.
    
    By default, the graph is stored in 'memory.json' in the 'ai-kngr' directory
    at the project root. During test runs, it uses 'tests/test_outputs/memory.json'.
    A custom path can be provided during initialization to override these defaults.
    """

    def __init__(self, memory_file_path: Optional[str] = None):
        """Initialize the knowledge graph manager.
        
        Args:
            memory_file_path: Path to the memory storage file
        """
        if memory_file_path:
            self.memory_file_path = Path(memory_file_path)
        else:
            # Find the project root (going up from the current file)
            current_dir = Path(__file__).parent
            # Go up until we find the project root (where src directory is)
            project_root = current_dir
            while project_root.name != "src" and project_root.parent != project_root:
                project_root = project_root.parent
            
            if project_root.name == "src":
                project_root = project_root.parent
            
            # Detect if we're running in a test environment
            # Check if pytest is running or if we're in a test directory
            in_test_environment = 'pytest' in sys.modules or 'test' in __file__.lower()
            
            if in_test_environment:
                # Use tests/test_outputs folder for tests
                test_outputs_dir = project_root / "tests" / "test_outputs"
                test_outputs_dir.mkdir(exist_ok=True)
                self.memory_file_path = test_outputs_dir / "memory.json"
            else:
                # Use ai-kngr folder in project root for normal operation
                ai_kngr_dir = project_root / "ai-kngr"
                ai_kngr_dir.mkdir(exist_ok=True)
                self.memory_file_path = ai_kngr_dir / "memory.json"
    
    def _load_graph(self) -> KnowledgeGraph:
        """Load the knowledge graph from storage."""
        try:
            with open(self.memory_file_path, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
                graph = KnowledgeGraph()
                
                for line in lines:
                    item = json.loads(line)
                    if item.get("type") == "entity":
                        graph.entities.append(Entity(
                            name=item["name"],
                            entity_type=item["entityType"],
                            observations=item["observations"]
                        ))
                    elif item.get("type") == "relation":
                        graph.relations.append(Relation(
                            from_entity=item["from"],
                            to_entity=item["to"],
                            relation_type=item["relationType"]
                        ))
                return graph
        except FileNotFoundError:
            return KnowledgeGraph()
    
    def _save_graph(self, graph: KnowledgeGraph) -> None:
        """Save the knowledge graph to storage."""
        lines = []
        for entity in graph.entities:
            lines.append(json.dumps({
                "type": "entity",
                "name": entity.name,
                "entityType": entity.entity_type,
                "observations": entity.observations
            }))
        
        for relation in graph.relations:
            lines.append(json.dumps({
                "type": "relation",
                "from": relation.from_entity,
                "to": relation.to_entity,
                "relationType": relation.relation_type
            }))
        
        # Ensure directory exists
        self.memory_file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(self.memory_file_path, "w") as f:
            f.write("\n".join(lines))
    
    def create_entities(self, entities: List[Dict[str, Any]]) -> List[Entity]:
        """Create new entities in the knowledge graph."""
        graph = self._load_graph()
        
        # Convert dict input to Entity objects
        entity_objects = [
            Entity(
                name=e["name"],
                entity_type=e["entityType"],
                observations=e.get("observations", [])
            ) for e in entities
        ]
        
        # Filter out entities that already exist
        existing_names = {entity.name for entity in graph.entities}
        new_entities = [e for e in entity_objects if e.name not in existing_names]
        
        # Add to graph and save
        graph.entities.extend(new_entities)
        self._save_graph(graph)
        
        return new_entities
    
    def create_relations(self, relations: List[Dict[str, Any]]) -> List[Relation]:
        """Create new relations in the knowledge graph."""
        graph = self._load_graph()
        
        # Convert dict input to Relation objects
        relation_objects = [
            Relation(
                from_entity=r["from"],
                to_entity=r["to"],
                relation_type=r["relationType"]
            ) for r in relations
        ]
        
        # Filter out relations that already exist
        new_relations = []
        for r in relation_objects:
            if not any(
                existing.from_entity == r.from_entity and
                existing.to_entity == r.to_entity and
                existing.relation_type == r.relation_type
                for existing in graph.relations
            ):
                new_relations.append(r)
        
        # Add to graph and save
        graph.relations.extend(new_relations)
        self._save_graph(graph)
        
        return new_relations
    
    def add_observations(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add observations to existing entities."""
        graph = self._load_graph()
        results = []
        
        for obs in observations:
            entity_name = obs["entityName"]
            contents = obs["contents"]
            
            # Find the entity
            entity = next((e for e in graph.entities if e.name == entity_name), None)
            if not entity:
                raise ValueError(f"Entity with name '{entity_name}' not found")
            
            # Add new observations
            existing_obs = set(entity.observations)
            new_obs = [c for c in contents if c not in existing_obs]
            entity.observations.extend(new_obs)
            
            results.append({
                "entityName": entity_name,
                "addedObservations": new_obs
            })
        
        self._save_graph(graph)
        return results
    
    def delete_entities(self, entity_names: List[str]) -> None:
        """Delete entities and their relations."""
        graph = self._load_graph()
        
        # Create a set for faster lookups
        names_to_delete = set(entity_names)
        
        # Filter out deleted entities
        graph.entities = [e for e in graph.entities if e.name not in names_to_delete]
        
        # Filter out relations connected to deleted entities
        graph.relations = [
            r for r in graph.relations
            if r.from_entity not in names_to_delete and r.to_entity not in names_to_delete
        ]
        
        self._save_graph(graph)
    
    def delete_observations(self, deletions: List[Dict[str, Any]]) -> None:
        """Delete specific observations from entities."""
        graph = self._load_graph()
        
        for deletion in deletions:
            entity_name = deletion["entityName"]
            obs_to_delete = set(deletion["observations"])
            
            # Find the entity
            entity = next((e for e in graph.entities if e.name == entity_name), None)
            if entity:
                # Remove observations
                entity.observations = [obs for obs in entity.observations if obs not in obs_to_delete]
        
        self._save_graph(graph)
    
    def delete_relations(self, relations: List[Dict[str, Any]]) -> None:
        """Delete specific relations."""
        graph = self._load_graph()
        
        # Convert to set of tuples for comparison
        relations_to_delete = {
            (r["from"], r["to"], r["relationType"]) 
            for r in relations
        }
        
        # Filter out deleted relations
        graph.relations = [
            r for r in graph.relations
            if (r.from_entity, r.to_entity, r.relation_type) not in relations_to_delete
        ]
        
        self._save_graph(graph)
    
    def read_graph(self) -> KnowledgeGraph:
        """Read the entire knowledge graph."""
        return self._load_graph()
    
    def search_nodes(self, query: str) -> KnowledgeGraph:
        """Search for nodes matching a query."""
        graph = self._load_graph()
        query = query.lower()
        
        # Filter entities
        filtered_entities = [
            e for e in graph.entities
            if query in e.name.lower() or 
               query in e.entity_type.lower() or
               any(query in obs.lower() for obs in e.observations)
        ]
        
        # Get set of filtered entity names
        filtered_names = {e.name for e in filtered_entities}
        
        # Filter relations between filtered entities
        filtered_relations = [
            r for r in graph.relations
            if r.from_entity in filtered_names and r.to_entity in filtered_names
        ]
        
        return KnowledgeGraph(entities=filtered_entities, relations=filtered_relations)
    
    def open_nodes(self, names: List[str]) -> KnowledgeGraph:
        """Open specific nodes by name."""
        graph = self._load_graph()
        name_set = set(names)
        
        # Filter entities
        filtered_entities = [e for e in graph.entities if e.name in name_set]
        filtered_names = {e.name for e in filtered_entities}
        
        # Filter relations between filtered entities
        filtered_relations = [
            r for r in graph.relations
            if r.from_entity in filtered_names and r.to_entity in filtered_names
        ]
        
        return KnowledgeGraph(entities=filtered_entities, relations=filtered_relations)


# Helper functions for MCP tool responses
def create_text_response(text: str, is_error: bool = False) -> TextContent:
    """Create a properly formatted MCP text content response."""
    return TextContent(
        type="text",
        text=text,
        isError=is_error
    )


def register_memory_tools(mcp_server):
    """Register memory graph tools with the MCP server.
    
    Args:
        mcp_server: The MCP server instance to register tools with
    """
    # Create a singleton KnowledgeGraphManager to handle all operations
    manager = KnowledgeGraphManager()
    
    # Get the existing list_tools handler
    original_list_tools = None
    for handler in getattr(mcp_server, "_request_handlers", {}).values():
        if handler.__name__ == "handle_list_tools":
            original_list_tools = handler
            break
    
    # Get the existing call_tool handler
    original_call_tool = None
    for handler in getattr(mcp_server, "_request_handlers", {}).values():
        if handler.__name__ == "handle_call_tool":
            original_call_tool = handler
            break
    
    if original_list_tools:
        # Create a new list_tools handler that adds our tools
        async def enhanced_list_tools():
            original_tools = await original_list_tools()
            
            # Add memory graph tools
            memory_tools = [
                Tool(
                    name="create_entities",
                    description="Create multiple new entities in the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "The name of the entity"},
                                        "entityType": {"type": "string", "description": "The type of the entity"},
                                        "observations": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "An array of observation contents associated with the entity"
                                        }
                                    },
                                    "required": ["name", "entityType"]
                                }
                            }
                        },
                        "required": ["entities"]
                    }
                ),
                Tool(
                    name="create_relations",
                    description="Create multiple new relations between entities in the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "relations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "from": {"type": "string", "description": "The name of the entity where the relation starts"},
                                        "to": {"type": "string", "description": "The name of the entity where the relation ends"},
                                        "relationType": {"type": "string", "description": "The type of the relation"}
                                    },
                                    "required": ["from", "to", "relationType"]
                                }
                            }
                        },
                        "required": ["relations"]
                    }
                ),
                Tool(
                    name="add_observations",
                    description="Add new observations to existing entities in the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "observations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "entityName": {"type": "string", "description": "The name of the entity to add the observations to"},
                                        "contents": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "An array of observation contents to add"
                                        }
                                    },
                                    "required": ["entityName", "contents"]
                                }
                            }
                        },
                        "required": ["observations"]
                    }
                ),
                Tool(
                    name="delete_entities",
                    description="Delete multiple entities and their associated relations from the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entityNames": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "An array of entity names to delete"
                            }
                        },
                        "required": ["entityNames"]
                    }
                ),
                Tool(
                    name="delete_observations",
                    description="Delete specific observations from entities in the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deletions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "entityName": {"type": "string", "description": "The name of the entity containing the observations"},
                                        "observations": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "An array of observations to delete"
                                        }
                                    },
                                    "required": ["entityName", "observations"]
                                }
                            }
                        },
                        "required": ["deletions"]
                    }
                ),
                Tool(
                    name="delete_relations",
                    description="Delete multiple relations from the knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "relations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "from": {"type": "string", "description": "The name of the entity where the relation starts"},
                                        "to": {"type": "string", "description": "The name of the entity where the relation ends"},
                                        "relationType": {"type": "string", "description": "The type of the relation"}
                                    },
                                    "required": ["from", "to", "relationType"]
                                },
                                "description": "An array of relations to delete"
                            }
                        },
                        "required": ["relations"]
                    }
                ),
                Tool(
                    name="read_graph",
                    description="Read the entire knowledge graph",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="search_nodes",
                    description="Search for nodes in the knowledge graph based on a query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query to match against entity names, types, and observation content"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="open_nodes",
                    description="Open specific nodes in the knowledge graph by their names",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "names": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "An array of entity names to retrieve"
                            }
                        },
                        "required": ["names"]
                    }
                )
            ]
            
            return original_tools + memory_tools
        
        # Replace the handler
        for key, handler in getattr(mcp_server, "_request_handlers", {}).items():
            if handler.__name__ == "handle_list_tools":
                mcp_server._request_handlers[key] = enhanced_list_tools
                break
    
    if original_call_tool:
        # Create a new call_tool handler that adds our tool implementations
        async def enhanced_call_tool(name: str, arguments: Optional[dict]) -> List[TextContent]:
            # Handle memory graph tool calls
            try:
                if name == "create_entities":
                    if not arguments or "entities" not in arguments:
                        raise ValueError("Missing required argument: entities")
                    
                    result = manager.create_entities(arguments["entities"])
                    response = json.dumps([{
                        "name": e.name,
                        "entityType": e.entity_type,
                        "observations": e.observations
                    } for e in result], indent=2)
                    return [create_text_response(response)]
                
                elif name == "create_relations":
                    if not arguments or "relations" not in arguments:
                        raise ValueError("Missing required argument: relations")
                    
                    result = manager.create_relations(arguments["relations"])
                    response = json.dumps([{
                        "from": r.from_entity,
                        "to": r.to_entity,
                        "relationType": r.relation_type
                    } for r in result], indent=2)
                    return [create_text_response(response)]
                
                elif name == "add_observations":
                    if not arguments or "observations" not in arguments:
                        raise ValueError("Missing required argument: observations")
                    
                    result = manager.add_observations(arguments["observations"])
                    return [create_text_response(json.dumps(result, indent=2))]
                
                elif name == "delete_entities":
                    if not arguments or "entityNames" not in arguments:
                        raise ValueError("Missing required argument: entityNames")
                    
                    manager.delete_entities(arguments["entityNames"])
                    return [create_text_response("Entities deleted successfully")]
                
                elif name == "delete_observations":
                    if not arguments or "deletions" not in arguments:
                        raise ValueError("Missing required argument: deletions")
                    
                    manager.delete_observations(arguments["deletions"])
                    return [create_text_response("Observations deleted successfully")]
                
                elif name == "delete_relations":
                    if not arguments or "relations" not in arguments:
                        raise ValueError("Missing required argument: relations")
                    
                    manager.delete_relations(arguments["relations"])
                    return [create_text_response("Relations deleted successfully")]
                
                elif name == "read_graph":
                    graph = manager.read_graph()
                    response = json.dumps({
                        "entities": [{
                            "name": e.name,
                            "entityType": e.entity_type,
                            "observations": e.observations
                        } for e in graph.entities],
                        "relations": [{
                            "from": r.from_entity,
                            "to": r.to_entity,
                            "relationType": r.relation_type
                        } for r in graph.relations]
                    }, indent=2)
                    return [create_text_response(response)]
                
                elif name == "search_nodes":
                    if not arguments or "query" not in arguments:
                        raise ValueError("Missing required argument: query")
                    
                    graph = manager.search_nodes(arguments["query"])
                    response = json.dumps({
                        "entities": [{
                            "name": e.name,
                            "entityType": e.entity_type,
                            "observations": e.observations
                        } for e in graph.entities],
                        "relations": [{
                            "from": r.from_entity,
                            "to": r.to_entity,
                            "relationType": r.relation_type
                        } for r in graph.relations]
                    }, indent=2)
                    return [create_text_response(response)]
                
                elif name == "open_nodes":
                    if not arguments or "names" not in arguments:
                        raise ValueError("Missing required argument: names")
                    
                    graph = manager.open_nodes(arguments["names"])
                    response = json.dumps({
                        "entities": [{
                            "name": e.name,
                            "entityType": e.entity_type,
                            "observations": e.observations
                        } for e in graph.entities],
                        "relations": [{
                            "from": r.from_entity,
                            "to": r.to_entity,
                            "relationType": r.relation_type
                        } for r in graph.relations]
                    }, indent=2)
                    return [create_text_response(response)]
                
                # If not one of our tools, delegate to the original handler
                else:
                    return await original_call_tool(name, arguments)
                    
            except Exception as e:
                # For our tools, handle errors ourselves
                if name in [
                    "create_entities", "create_relations", "add_observations",
                    "delete_entities", "delete_observations", "delete_relations",
                    "read_graph", "search_nodes", "open_nodes"
                ]:
                    return [create_text_response(str(e), is_error=True)]
                # For other tools, let the original handler deal with errors
                else:
                    return await original_call_tool(name, arguments)
        
        # Replace the handler
        for key, handler in getattr(mcp_server, "_request_handlers", {}).items():
            if handler.__name__ == "handle_call_tool":
                mcp_server._request_handlers[key] = enhanced_call_tool
                break


# If run directly, this will provide a test API - not used when imported
if __name__ == "__main__":
    # Simple test to demonstrate the functionality
    manager = KnowledgeGraphManager()
    test_entities = [
        {"name": "TestEntity1", "entityType": "test", "observations": ["Test observation 1"]},
        {"name": "TestEntity2", "entityType": "test", "observations": ["Test observation 2"]}
    ]
    manager.create_entities(test_entities)
    print("Test entities created. Graph contents:")
    print(json.dumps(manager.read_graph(), default=lambda o: o.__dict__, indent=2)) 