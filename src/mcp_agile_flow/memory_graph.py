#!/usr/bin/env python3
"""
Memory Knowledge Graph - A Python implementation of the repository memory system
that integrates with MCP Agile Flow.
"""

import json
import os
import sys
import datetime
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from dataclasses import dataclass, field

from .utils import get_project_settings

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
    """The complete knowledge graph structure.
    
    Attributes:
        entities: List of Entity objects in the graph
        relations: List of Relation objects in the graph
        project_type: Type of project (software, data_science, generic)
        project_metadata: Additional metadata about the project
    """
    entities: List[Entity] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    project_type: str = "generic"  # Can be "software", "data_science", or "generic"
    project_metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeGraphManager:
    """Manager for the knowledge graph operations.
    
    This class provides methods to create, read, update, and delete entities
    and relations in a knowledge graph. The graph is stored as a JSON file.
    
    By default, the graph is stored in 'memory.json' in the 'ai-kngr' directory
    at the project root. During test runs, it uses 'tests/test_outputs/memory.json'.
    A custom path can be provided during initialization to override these defaults.
    """
    
    def __init__(self, graph_path: Optional[str] = None):
        """Initialize the KnowledgeGraphManager.
        
        Args:
            graph_path: Optional path to the knowledge graph JSON file.
                        If not provided, a default path will be used.
        """
        import logging
        self.logger = logging.getLogger(__name__)
        
        # Store original input path
        self.provided_path = graph_path
        
        # Set up the path to the knowledge graph file
        if graph_path:
            self.graph_path = graph_path
            self.logger.info(f"Using provided graph path: {self.graph_path}")
        else:
            # Try different paths in order of preference
            self.graph_path = self._determine_graph_path()
        
        # Ensure the parent directory exists
        self._ensure_directory_exists()
        
        # Load the graph if it exists, or create a new one
        self.graph = self._load_graph()
    
    def _determine_graph_path(self) -> str:
        """Determine the best path for the knowledge graph file.
        
        This method tries several locations in order of preference:
        1. Tests directory for pytest runs
        2. Knowledge graph directory from project settings
        3. ai-kngr subdirectory of the project root
        4. ai-kngr subdirectory of the current working directory
        5. ai-kngr subdirectory of a temporary directory as last resort
        
        Returns:
            str: The determined path for the knowledge graph file
        """
        # For test runs, use tests/test_outputs/memory.json
        if "pytest" in sys.modules:
            path = os.path.join("tests", "test_outputs", "ai-kngr", "memory.json")
            self.logger.info(f"Using test environment path: {path}")
            return path
        
        try:
            # Get project settings using the common utility function
            settings = get_project_settings()
            
            # Get the knowledge graph directory from settings
            if "knowledge_graph_directory" in settings and settings["knowledge_graph_directory"]:
                kngr_dir = settings["knowledge_graph_directory"]
                path = os.path.join(kngr_dir, "memory.json")
                self.logger.info(f"Using path from project settings: {path}")
                return path
            
            # If no knowledge graph directory in settings, use project_path + ai-kngr
            if "project_path" in settings and settings["project_path"]:
                project_path = settings["project_path"]
                kngr_dir = os.path.join(project_path, "ai-kngr")
                path = os.path.join(kngr_dir, "memory.json")
                self.logger.info(f"Using path based on project path: {path}")
                return path
                
        except Exception as e:
            self.logger.warning(f"Error getting path from project settings: {e}")
            
        # Fallback to the current working directory
        try:
            current_dir = os.getcwd()
            kngr_dir = os.path.join(current_dir, "ai-kngr")
            path = os.path.join(kngr_dir, "memory.json")
            self.logger.info(f"Using fallback path in current directory: {path}")
            return path
        except Exception as e:
            self.logger.warning(f"Error using current directory fallback: {e}")
        
        # Ultimate fallback - use a temporary directory
        import tempfile
        temp_dir = tempfile.gettempdir()
        kngr_dir = os.path.join(temp_dir, "ai-kngr")
        path = os.path.join(kngr_dir, "memory.json")
        self.logger.warning(f"Using temporary directory as last resort: {path}")
        return path
    
    def _ensure_directory_exists(self) -> None:
        """Ensure the directory for the graph file exists.
        
        Creates any missing directories in the path to the graph file.
        Handles errors gracefully and logs appropriate messages.
        """
        directory = os.path.dirname(self.graph_path)
        
        if not directory:
            self.logger.warning("No directory specified in graph path")
            return
            
        if os.path.exists(directory):
            # Check if directory is writable
            if not os.access(directory, os.W_OK):
                self.logger.warning(f"Directory exists but is not writable: {directory}")
                # We'll still try to use it, but log the warning
            else:
                self.logger.info(f"Using existing directory: {directory}")
            return
            
        # Try to create the directory
        try:
            os.makedirs(directory, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")
        except OSError as e:
            self.logger.error(f"Failed to create directory {directory}: {e}")
            # Continue anyway - we'll handle file operation errors when they occur
    
    def _detect_project_type(self, project_path: str) -> Tuple[str, Dict[str, Any]]:
        """Detect the type of project based on files and directories.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            A tuple of (project_type, project_metadata) where project_type is one of
            "software", "data_science", or "generic", and project_metadata is a
            dictionary of additional information about the project.
        """
        # Initialize metadata
        metadata = {}
        
        # Check for software project indicators
        software_indicators = {
            "python": ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile"],
            "javascript": ["package.json", "node_modules"],
            "java": ["pom.xml", "build.gradle", "settings.gradle"],
            "c_cpp": ["CMakeLists.txt", "Makefile"],
            "go": ["go.mod", "go.sum"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "dotnet": [".csproj", ".sln"],
        }
        
        # Check for data science project indicators
        data_science_indicators = {
            "jupyter": [".ipynb"],
            "r": ["DESCRIPTION", ".Rproj"],
            "data_files": [".csv", ".parquet", ".h5", ".pkl"],
            "ml_frameworks": ["tensorflow", "pytorch", "scikit-learn", "keras"],
        }
        
        # Count indicators for each type
        software_count = 0
        data_science_count = 0
        
        try:
            # Check for software project indicators
            for lang, files in software_indicators.items():
                for file in files:
                    if os.path.exists(os.path.join(project_path, file)) or any(f.endswith(file) for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f))):
                        software_count += 1
                        metadata[f"has_{lang}"] = True
                        break
            
            # Check for data science project indicators
            for category, files in data_science_indicators.items():
                for file in files:
                    # For file extensions, check if any file has that extension
                    if file.startswith("."):
                        if any(f.endswith(file) for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f))):
                            data_science_count += 1
                            metadata[f"has_{category}"] = True
                            break
                    # For directories or specific files
                    elif os.path.exists(os.path.join(project_path, file)):
                        data_science_count += 1
                        metadata[f"has_{category}"] = True
                        break
                    # For ML frameworks, check requirements.txt or pyproject.toml
                    elif category == "ml_frameworks":
                        req_file = os.path.join(project_path, "requirements.txt")
                        if os.path.exists(req_file):
                            with open(req_file, "r") as f:
                                content = f.read().lower()
                                if file in content:
                                    data_science_count += 1
                                    metadata[f"uses_{file}"] = True
                                    break
                        
                        pyproject_file = os.path.join(project_path, "pyproject.toml")
                        if os.path.exists(pyproject_file):
                            with open(pyproject_file, "r") as f:
                                content = f.read().lower()
                                if file in content:
                                    data_science_count += 1
                                    metadata[f"uses_{file}"] = True
                                    break
        except Exception as e:
            # If there's an error during detection, log it but continue
            print(f"Error during project type detection: {e}")
        
        # Determine project type based on indicators
        if data_science_count > software_count:
            project_type = "data_science"
        elif software_count > 0:
            project_type = "software"
        else:
            project_type = "generic"
        
        # Add additional metadata
        metadata["software_indicators_count"] = software_count
        metadata["data_science_indicators_count"] = data_science_count
        
        return project_type, metadata

    def _create_new_graph(self) -> KnowledgeGraph:
        """Create a new knowledge graph with project type detection.
        
        Returns:
            A new KnowledgeGraph object with detected project type.
        """
        # Get the project path from the graph path
        project_path = os.path.dirname(os.path.dirname(self.graph_path))
        if project_path.endswith("ai-kngr") or project_path.endswith(".kg") or project_path.endswith(".knowledge"):
            project_path = os.path.dirname(project_path)
        
        # Detect project type
        project_type, project_metadata = self._detect_project_type(project_path)
        
        return KnowledgeGraph(
            project_type=project_type,
            project_metadata=project_metadata
        )

    def _load_graph(self) -> KnowledgeGraph:
        """Load the knowledge graph from the JSON file.
        
        Returns:
            The loaded KnowledgeGraph object.
        """
        if os.path.exists(self.graph_path):
            try:
                self.logger.info(f"Loading knowledge graph from {self.graph_path}")
                with open(self.graph_path, "r") as f:
                    data = json.load(f)
                
                # Convert the JSON data to a KnowledgeGraph object
                entities = []
                for entity_data in data.get("entities", []):
                    entity = Entity(
                        name=entity_data["name"],
                        entity_type=entity_data["entity_type"],
                        observations=entity_data.get("observations", [])
                    )
                    entities.append(entity)
                
                relations = []
                for relation_data in data.get("relations", []):
                    relation = Relation(
                        from_entity=relation_data["from_entity"],
                        to_entity=relation_data["to_entity"],
                        relation_type=relation_data["relation_type"]
                    )
                    relations.append(relation)
                
                # Load project type and metadata if available
                project_type = data.get("project_type", "generic")
                project_metadata = data.get("project_metadata", {})
                
                graph = KnowledgeGraph(
                    entities=entities, 
                    relations=relations,
                    project_type=project_type,
                    project_metadata=project_metadata
                )
                self.logger.info(f"Successfully loaded graph with {len(entities)} entities and {len(relations)} relations")
                return graph
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decode error loading graph from {self.graph_path}: {e}")
                self._backup_corrupted_file("json_error")
            except KeyError as e:
                self.logger.error(f"Key error loading graph (missing required field): {e}")
                self._backup_corrupted_file("schema_error") 
            except (TypeError, ValueError) as e:
                self.logger.error(f"Type or value error loading graph: {e}")
                self._backup_corrupted_file("type_error")
            except (OSError, IOError) as e:
                self.logger.error(f"I/O error loading graph from {self.graph_path}: {e}")
                # No backup needed for I/O errors, the file is likely just inaccessible
        else:
            self.logger.info(f"Knowledge graph file does not exist at {self.graph_path}, creating new graph")
                
        return self._create_new_graph()
    
    def _backup_corrupted_file(self, error_type: str) -> None:
        """Create a backup of a corrupted knowledge graph file.
        
        Args:
            error_type: A string describing the type of error that occurred
        """
        try:
            if os.path.exists(self.graph_path):
                timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_path = f"{self.graph_path}.{error_type}.backup.{timestamp}"
                shutil.copy2(self.graph_path, backup_path)
                self.logger.info(f"Created backup of corrupted knowledge graph at {backup_path}")
                
                # Optionally, read the file content and log it for debugging
                try:
                    with open(self.graph_path, "r") as f:
                        content = f.read()
                    # Log only the first few hundred characters to avoid overwhelming logs
                    preview = content[:500] + ("..." if len(content) > 500 else "")
                    self.logger.debug(f"Content preview of corrupted file: {preview}")
                except Exception as read_error:
                    self.logger.warning(f"Could not read content of corrupted file: {read_error}")
        except Exception as e:
            self.logger.error(f"Failed to create backup of corrupted file: {e}")
    
    def _generate_mermaid_diagram(self) -> str:
        """Generate a Markdown document with an embedded Mermaid diagram of the knowledge graph.
        
        This method creates a complete Markdown document that includes:
        1. A Mermaid diagram representing the knowledge graph entities and relations
        2. Metadata about the knowledge graph
        3. Project-specific information
        
        Returns:
            A string containing the complete Markdown document with embedded Mermaid diagram.
        """
        # Start with the diagram header based on project type
        if self.graph.project_type == "software":
            diagram_type = "classDiagram"
        elif self.graph.project_type == "data_science":
            diagram_type = "flowchart TD"
        else:
            diagram_type = "graph TD"
            
        lines = [f"```mermaid", f"{diagram_type}", ""]
        
        # Add entity definitions with appropriate styling based on entity_type
        entity_definitions = {}
        for entity in self.graph.entities:
            # Create a safe ID for the entity (replace spaces and special chars)
            safe_id = f"entity_{len(entity_definitions)}"
            entity_definitions[entity.name] = safe_id
            
            # Format entity display based on project type
            if self.graph.project_type == "software":
                # For software projects, use class diagram notation
                class_def = f"class {safe_id} {{"
                lines.append(class_def)
                lines.append(f"  +{entity.entity_type}")
                # Add observations as methods/attributes
                for obs in entity.observations[:5]:  # Limit to 5 observations to keep diagram clean
                    # Truncate long observations
                    if len(obs) > 50:
                        obs = obs[:47] + "..."
                    lines.append(f"  +{obs}")
                lines.append("}")
                lines.append(f"{safe_id} : {entity.name}")
            else:
                # For other project types, use node notation
                node_def = f"{safe_id}[\"{entity.name}<br><i>{entity.entity_type}</i>\"]"
                lines.append(node_def)
                
                # Add styling based on entity type
                if entity.entity_type == "person":
                    lines.append(f"style {safe_id} fill:#f9f,stroke:#333,stroke-width:2px")
                elif entity.entity_type == "concept":
                    lines.append(f"style {safe_id} fill:#bbf,stroke:#333,stroke-width:1px")
                elif entity.entity_type == "file":
                    lines.append(f"style {safe_id} fill:#bfb,stroke:#333,stroke-width:1px")
                elif entity.entity_type == "task":
                    lines.append(f"style {safe_id} fill:#fbf,stroke:#333,stroke-width:1px")
        
        # Add relations
        for relation in self.graph.relations:
            from_id = entity_definitions.get(relation.from_entity)
            to_id = entity_definitions.get(relation.to_entity)
            
            if from_id and to_id:
                if self.graph.project_type == "software":
                    # For software projects, use class diagram relation notation
                    lines.append(f"{from_id} --> {to_id} : {relation.relation_type}")
                else:
                    # For other project types, use arrow notation
                    lines.append(f"{from_id} -->|{relation.relation_type}| {to_id}")
        
        lines.append("```")
        
        # Add metadata section
        lines.append("\n## Knowledge Graph Metadata")
        lines.append(f"- **Project Type**: {self.graph.project_type}")
        lines.append(f"- **Entity Count**: {len(self.graph.entities)}")
        lines.append(f"- **Relation Count**: {len(self.graph.relations)}")
        lines.append(f"- **Last Updated**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Add project-specific metadata
        if self.graph.project_metadata:
            lines.append("\n### Project Metadata")
            for key, value in self.graph.project_metadata.items():
                if isinstance(value, bool):
                    value = "Yes" if value else "No"
                lines.append(f"- **{key}**: {value}")
        
        return "\n".join(lines)
    
    def _save_graph(self) -> None:
        """Save the knowledge graph to the JSON file and generate a markdown visualization."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Convert the KnowledgeGraph object to a JSON-serializable dict
        data = {
            "entities": [
                {
                    "name": entity.name,
                    "entity_type": entity.entity_type,
                    "observations": entity.observations
                }
                for entity in self.graph.entities
            ],
            "relations": [
                {
                    "from_entity": relation.from_entity,
                    "to_entity": relation.to_entity,
                    "relation_type": relation.relation_type
                }
                for relation in self.graph.relations
            ],
            "project_type": self.graph.project_type,
            "project_metadata": self.graph.project_metadata
        }
        
        # Ensure the directory exists
        directory = os.path.dirname(self.graph_path)
        if not os.path.exists(directory):
            try:
                logger.info(f"Creating directory for knowledge graph: {directory}")
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                print(f"Warning: Could not create directory {directory}: {e}")
        
        # Save the data to the JSON file
        try:
            with open(self.graph_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved knowledge graph to {self.graph_path}")
                
            # Generate and save the Mermaid diagram markdown file
            md_path = self.graph_path.replace(".json", ".md")
            mermaid_content = self._generate_mermaid_diagram()
            with open(md_path, "w") as f:
                f.write(mermaid_content)
            logger.info(f"Saved Mermaid diagram to {md_path}")
        except (OSError, IOError) as e:
            logger.error(f"Could not save knowledge graph to {self.graph_path}: {e}")
            print(f"Warning: Could not save knowledge graph to {self.graph_path}: {e}")
    
    def create_entities(self, entities: List[Dict[str, Any]]) -> List[Entity]:
        """Create multiple new entities in the knowledge graph.
        
        Args:
            entities: A list of entity data dictionaries, each containing:
                     - name: The name of the entity
                     - entityType: The type of the entity
                     - observations: Optional list of observation contents
                     
        Returns:
            A list of the created Entity objects
        """
        created_entities = []
        for entity_data in entities:
            name = entity_data["name"]
            entity_type = entity_data["entityType"]
            observations = entity_data.get("observations", [])
            
            # Check if the entity already exists
            existing_entity = next((e for e in self.graph.entities if e.name == name), None)
            if existing_entity:
                # For duplicate entities, don't add them to the result
                # but still update their properties
                existing_entity.entity_type = entity_type
                for obs in observations:
                    if obs not in existing_entity.observations:
                        existing_entity.observations.append(obs)
            else:
                # Create a new entity
                entity = Entity(name=name, entity_type=entity_type, observations=observations)
                self.graph.entities.append(entity)
                created_entities.append(entity)
        
        # Save the updated graph
        self._save_graph()
        
        return created_entities
    
    def create_relations(self, relations: List[Dict[str, str]]) -> List[Relation]:
        """Create multiple new relations between entities in the knowledge graph.
        
        Args:
            relations: A list of relation data dictionaries, each containing:
                      - from: The name of the entity where the relation starts
                      - to: The name of the entity where the relation ends
                      - relationType: The type of the relation
                      
        Returns:
            A list of the created Relation objects
        """
        created_relations = []
        for relation_data in relations:
            from_entity = relation_data["from"]
            to_entity = relation_data["to"]
            relation_type = relation_data["relationType"]
            
            # Check if both entities exist
            from_exists = any(e.name == from_entity for e in self.graph.entities)
            to_exists = any(e.name == to_entity for e in self.graph.entities)
            
            if not from_exists or not to_exists:
                # Create missing entities as "unknown" type
                if not from_exists:
                    self.graph.entities.append(Entity(name=from_entity, entity_type="unknown"))
                if not to_exists:
                    self.graph.entities.append(Entity(name=to_entity, entity_type="unknown"))
            
            # Check if the relation already exists
            existing_relation = next((
                r for r in self.graph.relations
                if r.from_entity == from_entity and 
                   r.to_entity == to_entity and 
                   r.relation_type == relation_type
            ), None)
            
            if existing_relation:
                # For duplicate relations, don't add them to the result
                pass
            else:
                # Create the new relation
                relation = Relation(
                    from_entity=from_entity,
                    to_entity=to_entity,
                    relation_type=relation_type
                )
                self.graph.relations.append(relation)
                created_relations.append(relation)
        
        # Save the updated graph
        self._save_graph()
        
        return created_relations
    
    def add_observations(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add new observations to existing entities in the knowledge graph.
        
        Args:
            observations: A list of observation data dictionaries, each containing:
                         - entityName: The name of the entity to add the observations to
                         - contents: A list of observation contents to add
                         
        Returns:
            A list of dictionaries with entity name and added observations
        """
        result = []
        for observation_data in observations:
            entity_name = observation_data["entityName"]
            contents = observation_data["contents"]
            added_observations = []
            
            # Find the entity
            entity = next((e for e in self.graph.entities if e.name == entity_name), None)
            if entity:
                # Add the observations if they don't already exist
                for content in contents:
                    if content not in entity.observations:
                        entity.observations.append(content)
                        added_observations.append(content)
            else:
                # Create a new entity with the observations
                entity = Entity(name=entity_name, entity_type="unknown", observations=contents.copy())
                self.graph.entities.append(entity)
                added_observations = contents.copy()
            
            # Add the result in the expected format
            result.append({
                "entityName": entity_name,
                "addedObservations": added_observations
            })
        
        # Save the updated graph
        self._save_graph()
        
        return result
    
    def delete_entities(self, entity_names: List[str]) -> KnowledgeGraph:
        """Delete multiple entities and their associated relations from the knowledge graph.
        
        Args:
            entity_names: A list of entity names to delete
            
        Returns:
            The updated KnowledgeGraph
        """
        # Remove the entities
        self.graph.entities = [e for e in self.graph.entities if e.name not in entity_names]
        
        # Remove any relations involving the deleted entities
        self.graph.relations = [
            r for r in self.graph.relations
            if r.from_entity not in entity_names and r.to_entity not in entity_names
        ]
        
        # Save the updated graph
        self._save_graph()
        
        return self.graph
    
    def delete_observations(self, deletions: List[Dict[str, Any]]) -> KnowledgeGraph:
        """Delete specific observations from entities in the knowledge graph.
        
        Args:
            deletions: A list of deletion data dictionaries, each containing:
                      - entityName: The name of the entity containing the observations
                      - observations: A list of observations to delete
                      
        Returns:
            The updated KnowledgeGraph
        """
        for deletion_data in deletions:
            entity_name = deletion_data["entityName"]
            observations_to_delete = deletion_data["observations"]
            
            # Find the entity
            entity = next((e for e in self.graph.entities if e.name == entity_name), None)
            if entity:
                # Remove the observations
                entity.observations = [
                    obs for obs in entity.observations
                    if obs not in observations_to_delete
                ]
        
        # Save the updated graph
        self._save_graph()
        
        return self.graph
    
    def delete_relations(self, relations: List[Dict[str, str]]) -> KnowledgeGraph:
        """Delete multiple relations from the knowledge graph.
        
        Args:
            relations: A list of relation data dictionaries, each containing:
                      - from: The name of the entity where the relation starts
                      - to: The name of the entity where the relation ends
                      - relationType: The type of the relation
                      
        Returns:
            The updated KnowledgeGraph
        """
        for relation_data in relations:
            from_entity = relation_data["from"]
            to_entity = relation_data["to"]
            relation_type = relation_data["relationType"]
            
            # Remove the relations that match the criteria
            self.graph.relations = [
                r for r in self.graph.relations
                if not (
                    r.from_entity == from_entity and
                    r.to_entity == to_entity and
                    r.relation_type == relation_type
                )
            ]
        
        # Save the updated graph
        self._save_graph()
        
        return self.graph
    
    def read_graph(self) -> KnowledgeGraph:
        """Read the entire knowledge graph.
        
        Returns:
            The current KnowledgeGraph object.
        """
        return self.graph
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get information about the project type and metadata.
        
        Returns:
            A dictionary containing project_type and project_metadata.
        """
        return {
            "project_type": self.graph.project_type,
            "project_metadata": self.graph.project_metadata
        }
        
    def get_mermaid_diagram(self) -> str:
        """Get the Mermaid diagram representation of the knowledge graph.
        
        This method always generates a fresh diagram based on the current state
        of the knowledge graph.
        
        Note: This method is deprecated. Use update_markdown_with_mermaid instead.
        
        Returns:
            A string containing the Markdown with embedded Mermaid diagram.
        """
        # Always generate a fresh diagram
        return self.update_markdown_with_mermaid()
        
    def update_markdown_with_mermaid(self) -> str:
        """Update the Markdown file with an embedded Mermaid diagram of the knowledge graph.
        
        This method:
        1. Generates a fresh Mermaid diagram based on the current state of the knowledge graph
        2. Embeds the diagram in a Markdown file with the same base name as the knowledge graph JSON file
        3. Saves the Markdown file to disk
        
        Returns:
            A string containing the Markdown with embedded Mermaid diagram.
        """
        # Generate a fresh diagram
        mermaid_content = self._generate_mermaid_diagram()
        
        # Save the Markdown file with embedded Mermaid diagram to disk
        md_path = self.graph_path.replace(".json", ".md")
        try:
            with open(md_path, "w") as f:
                f.write(mermaid_content)
            print(f"Markdown file with Mermaid diagram saved to {md_path}")
        except (OSError, IOError) as e:
            print(f"Warning: Could not save Markdown file with Mermaid diagram to {md_path}: {e}")
            
        return mermaid_content
        
    def update_mermaid_diagram(self) -> str:
        """Update the Markdown file with an embedded Mermaid diagram of the knowledge graph.
        
        Note: This method is deprecated. Use update_markdown_with_mermaid instead.
        
        Returns:
            A string containing the Markdown with embedded Mermaid diagram.
        """
        return self.update_markdown_with_mermaid()
        
    def search_nodes(self, query: str) -> KnowledgeGraph:
        """Search for nodes in the knowledge graph based on a query.
        
        Args:
            query: The search query to match against entity names, types, and observation content
        
        Returns:
            A KnowledgeGraph object containing the matching entities and their relations.
        """
        query = query.lower()
        
        # Find entities that match the query
        matching_entities = []
        for entity in self.graph.entities:
            if (
                query in entity.name.lower() or
                query in entity.entity_type.lower() or
                any(query in obs.lower() for obs in entity.observations)
            ):
                matching_entities.append(entity.name)
        
        # Create a new knowledge graph with the matching entities and relations
        result_graph = KnowledgeGraph(
            project_type=self.graph.project_type,
            project_metadata=self.graph.project_metadata
        )
        
        # Add matching entities
        for name in matching_entities:
            entity = next(e for e in self.graph.entities if e.name == name)
            result_graph.entities.append(Entity(
                name=entity.name,
                entity_type=entity.entity_type,
                observations=entity.observations.copy()
            ))
        
        # Add relations involving the matching entities
        for relation in self.graph.relations:
            if relation.from_entity in matching_entities or relation.to_entity in matching_entities:
                result_graph.relations.append(Relation(
                    from_entity=relation.from_entity,
                    to_entity=relation.to_entity,
                    relation_type=relation.relation_type
                ))
        
        return result_graph
    
    def open_nodes(self, names: List[str]) -> KnowledgeGraph:
        """Open specific nodes in the knowledge graph by their names.
        
        Args:
            names: A list of entity names to retrieve
        
        Returns:
            A KnowledgeGraph object containing the specified entities and their relations.
        """
        # Create a new knowledge graph with the specified entities and relations
        result_graph = KnowledgeGraph(
            project_type=self.graph.project_type,
            project_metadata=self.graph.project_metadata
        )
        
        # Add the specified entities
        for name in names:
            entity = next((e for e in self.graph.entities if e.name == name), None)
            if entity:
                result_graph.entities.append(Entity(
                    name=entity.name,
                    entity_type=entity.entity_type,
                    observations=entity.observations.copy()
                ))
        
        # Add only relations between the specified entities
        for relation in self.graph.relations:
            if relation.from_entity in names and relation.to_entity in names:
                result_graph.relations.append(Relation(
                    from_entity=relation.from_entity,
                    to_entity=relation.to_entity,
                    relation_type=relation.relation_type
                ))
        
        return result_graph


def register_memory_tools(mcp_server):
    """Register memory graph tools with the MCP server.
    
    Args:
        mcp_server: The MCP server instance to register tools with
        
    Returns:
        A tuple of (memory_tools, manager) where memory_tools is a list of Tool objects
        and manager is the KnowledgeGraphManager instance.
    """
    # Create a singleton KnowledgeGraphManager to handle all operations
    manager = KnowledgeGraphManager()
    
    # Define memory graph tools to be added to the handle_list_tools function
    memory_tools = [
        Tool(
            name="get_project_info",
            description="Get information about the project type and metadata from the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_mermaid_diagram",
            description="Get a Mermaid diagram representation of the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
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
    
    # Register the tools with the MCP server if provided
    if mcp_server:
        # If the server is provided, register the tools
        pass
    
    # Export the memory tools and manager for use in simple_server.py
    return memory_tools, manager
