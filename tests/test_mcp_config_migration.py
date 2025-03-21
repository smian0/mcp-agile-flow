"""
MCP Configuration Migration Tool Tests.
Tests include both direct function tests and end-to-end API integration tests
for the migration functionality between different IDEs.
"""
import os
import json
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import patch
import logging

from src.mcp_agile_flow.migration_tool import (
    get_ide_path,
    create_backup,
    detect_conflicts,
    merge_configurations,
    migrate_config
)

# Set up logging
logger = logging.getLogger(__name__)

# Helper function for saving test outputs
def save_test_output(name, data):
    """Save test output data to a file for inspection."""
    output_dir = Path("tests/test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / f"{name}.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved test output to {output_path}")

# === Fixtures ===

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def sample_config():
    """Create a sample MCP configuration."""
    return {
        "mcpServers": {
            "weather": {
                "command": "node",
                "args": ["/path/to/weather-server/build/index.js"],
                "env": {
                    "API_KEY": "test-key"
                }
            },
            "search": {
                "command": "python",
                "args": ["-m", "search_server"],
                "env": {}
            }
        }
    }

@pytest.fixture
def mock_ide_paths(temp_dir):
    """Mock IDE paths to use temporary directory."""
    cursor_path = os.path.join(temp_dir, "cursor", "mcp.json")
    windsurf_path = os.path.join(temp_dir, "windsurf", "mcp_config.json")
    
    with patch("src.mcp_agile_flow.migration_tool.get_ide_path") as mock_get_path:
        def side_effect(ide):
            if ide == "cursor":
                return cursor_path
            elif ide == "windsurf":
                return windsurf_path
            raise ValueError(f"Unknown IDE: {ide}")
        
        mock_get_path.side_effect = side_effect
        yield {
            "cursor": cursor_path,
            "windsurf": windsurf_path
        }

# === Direct Function Tests ===

def test_detect_conflicts(sample_config):
    """Test conflict detection between configurations."""
    # Create a modified version of the sample config
    modified_config = {
        "mcpServers": {
            "weather": {
                "command": "node",
                "args": ["/different/path/index.js"],  # Changed path
                "env": {
                    "API_KEY": "different-key"  # Changed key
                }
            },
            "search": {
                "command": "python",
                "args": ["-m", "search_server"],
                "env": {}
            }
        }
    }
    
    # Should detect conflict in weather server
    conflicts = detect_conflicts(sample_config, modified_config)
    assert "weather" in conflicts
    assert len(conflicts) == 1  # Only weather should conflict

def test_merge_configurations(sample_config):
    """Test merging configurations with conflict resolutions."""
    target_config = {
        "mcpServers": {
            "weather": {
                "command": "node",
                "args": ["/old/path/index.js"],
                "env": {
                    "API_KEY": "old-key"
                }
            }
        }
    }
    
    # Test keeping target configuration for weather
    merged = merge_configurations(sample_config, target_config, {"weather": False})
    assert merged["mcpServers"]["weather"]["args"] == ["/old/path/index.js"]
    
    # Test using source configuration for weather
    merged = merge_configurations(sample_config, target_config, {"weather": True})
    assert merged["mcpServers"]["weather"]["args"] == ["/path/to/weather-server/build/index.js"]
    
    # Test adding new server from source
    assert "search" in merged["mcpServers"]

def test_create_backup(temp_dir):
    """Test backup creation functionality."""
    # Create a test file
    test_file = os.path.join(temp_dir, "test.json")
    with open(test_file, "w") as f:
        json.dump({"test": "data"}, f)
    
    # Create backup
    backup_path = create_backup(test_file)
    assert backup_path == test_file + ".bak"
    assert os.path.exists(backup_path)
    
    # Verify backup contents
    with open(backup_path, "r") as f:
        backup_data = json.load(f)
        assert backup_data == {"test": "data"}

def test_direct_migration_no_conflicts(mock_ide_paths, sample_config):
    """Test successful migration with no conflicts."""
    # Create source config
    os.makedirs(os.path.dirname(mock_ide_paths["cursor"]), exist_ok=True)
    with open(mock_ide_paths["cursor"], "w") as f:
        json.dump(sample_config, f)
    
    # Perform migration
    success, error, conflicts, conflict_details = migrate_config("cursor", "windsurf")
    
    # Verify results
    assert success
    assert error is None
    assert not conflicts
    assert conflict_details == {}
    
    # Verify target file
    assert os.path.exists(mock_ide_paths["windsurf"])
    with open(mock_ide_paths["windsurf"], "r") as f:
        migrated_config = json.load(f)
        assert migrated_config == sample_config

def test_direct_migration_with_conflicts(mock_ide_paths, sample_config):
    """Test migration with conflicting configurations."""
    # Create source config
    os.makedirs(os.path.dirname(mock_ide_paths["cursor"]), exist_ok=True)
    with open(mock_ide_paths["cursor"], "w") as f:
        json.dump(sample_config, f)
    
    # Create target config with conflict
    modified_config = {
        "mcpServers": {
            "weather": {
                "command": "node",
                "args": ["/different/path/index.js"],
                "env": {
                    "API_KEY": "different-key"
                }
            }
        }
    }
    os.makedirs(os.path.dirname(mock_ide_paths["windsurf"]), exist_ok=True)
    with open(mock_ide_paths["windsurf"], "w") as f:
        json.dump(modified_config, f)
    
    # Perform migration
    success, error, conflicts, conflict_details = migrate_config("cursor", "windsurf")
    
    # Verify results
    assert success  # Success should be True even with conflicts
    assert error is None
    assert "weather" in conflicts
    
    # Verify conflict details are returned and contain the correct information
    assert conflict_details is not None
    assert "weather" in conflict_details
    assert "source" in conflict_details["weather"]
    assert "target" in conflict_details["weather"]
    
    # Verify source details match the source configuration
    source_details = conflict_details["weather"]["source"]
    assert source_details["command"] == "node"
    assert source_details["args"] == ["/path/to/weather-server/build/index.js"]
    assert source_details["env"]["API_KEY"] == "test-key"
    
    # Verify target details match the target configuration
    target_details = conflict_details["weather"]["target"]
    assert target_details["command"] == "node"
    assert target_details["args"] == ["/different/path/index.js"]
    assert target_details["env"]["API_KEY"] == "different-key"
    
    # Verify target file wasn't modified
    with open(mock_ide_paths["windsurf"], "r") as f:
        target_config = json.load(f)
        assert target_config == modified_config

def test_migration_source_not_found(mock_ide_paths):
    """Test migration with non-existent source configuration."""
    success, error, conflicts, conflict_details = migrate_config("cursor", "windsurf")
    
    assert not success
    assert "Source configuration not found" in error
    assert not conflicts
    assert conflict_details == {}

def test_migration_invalid_json(mock_ide_paths):
    """Test migration with invalid JSON in source file."""
    # Create invalid source config
    os.makedirs(os.path.dirname(mock_ide_paths["cursor"]), exist_ok=True)
    with open(mock_ide_paths["cursor"], "w") as f:
        f.write("invalid json")
    
    success, error, conflicts, conflict_details = migrate_config("cursor", "windsurf")
    
    assert not success
    assert "Invalid JSON in source configuration" in error
    assert not conflicts
    assert conflict_details == {}

def test_environment_variable_override(temp_dir):
    """Test IDE path override using environment variables."""
    custom_path = os.path.join(temp_dir, "custom_config.json")
    
    with patch.dict(os.environ, {"MCP_CURSOR_PATH": custom_path}):
        path = get_ide_path("cursor")
        assert path == custom_path

# === API Integration Tests ===

def test_migrate_mcp_config_with_conflicts(tmp_path):
    """Test the migrate-mcp-config tool with conflicts."""
    logger.info("Testing migrate-mcp-config with conflicts...")
    
    # Import the handler and IDE path functions
    from src.mcp_agile_flow.simple_server import handle_call_tool
    from src.mcp_agile_flow.migration_tool import get_ide_path
    
    # Create temporary directories for test configs
    test_source_dir = tmp_path / "source"
    test_target_dir = tmp_path / "target"
    test_source_dir.mkdir()
    test_target_dir.mkdir()
    
    # Create source and target config files
    source_config_path = test_source_dir / "mcp.json"
    target_config_path = test_target_dir / "mcp.json"
    
    # Sample configurations with a conflict
    source_config = {
        "mcpServers": {
            "test-server": {
                "command": "python",
                "args": ["-m", "source_server"],
                "env": {"API_KEY": "source-key"}
            }
        }
    }
    
    target_config = {
        "mcpServers": {
            "test-server": {
                "command": "python",
                "args": ["-m", "target_server"],
                "env": {"API_KEY": "target-key"}
            }
        }
    }
    
    # Write the configurations
    with open(source_config_path, 'w') as f:
        json.dump(source_config, f)
    with open(target_config_path, 'w') as f:
        json.dump(target_config, f)
    
    # Mock the get_ide_path function to return our test paths
    original_get_ide_path = get_ide_path
    
    def mock_get_ide_path(ide):
        if ide == "source-ide":
            return str(source_config_path)
        elif ide == "target-ide":
            return str(target_config_path)
        return original_get_ide_path(ide)
    
    # Apply the mock
    import src.mcp_agile_flow.migration_tool
    src.mcp_agile_flow.migration_tool.get_ide_path = mock_get_ide_path
    
    try:
        # Call migrate-mcp-config
        result = asyncio.run(handle_call_tool("migrate-mcp-config", {
            "from_ide": "source-ide",
            "to_ide": "target-ide",
            "backup": True
        }))
        
        # Verify the result
        assert result[0].type == "text"
        response = json.loads(result[0].text)
        
        # Check the structure of the response
        assert response["success"] == True
        assert response["needs_resolution"] == True
        assert "test-server" in response["conflicts"]
        
        # Verify conflict details
        assert "conflict_details" in response
        assert "test-server" in response["conflict_details"]
        
        test_server_details = response["conflict_details"]["test-server"]
        assert "source" in test_server_details
        assert "target" in test_server_details
        
        # Verify source details
        source_details = test_server_details["source"]
        assert source_details["command"] == "python"
        assert source_details["args"] == ["-m", "source_server"]
        assert source_details["env"]["API_KEY"] == "source-key"
        
        # Verify target details
        target_details = test_server_details["target"]
        assert target_details["command"] == "python"
        assert target_details["args"] == ["-m", "target_server"]
        assert target_details["env"]["API_KEY"] == "target-key"
        
        # Verify paths are included
        assert response["source_path"] == str(source_config_path)
        assert response["target_path"] == str(target_config_path)
        
        # Save the response for inspection
        save_test_output("migrate_mcp_config_with_conflicts_response", response)
        
    finally:
        # Restore the original function
        src.mcp_agile_flow.migration_tool.get_ide_path = original_get_ide_path 

def test_migrate_mcp_config_resolve_conflicts(tmp_path):
    """Test resolving conflicts with the migrate-mcp-config tool."""
    logger.info("Testing migrate-mcp-config conflict resolution...")
    
    # Import the handler and IDE path functions
    from src.mcp_agile_flow.simple_server import handle_call_tool
    from src.mcp_agile_flow.migration_tool import get_ide_path
    
    # Create temporary directories for test configs
    test_source_dir = tmp_path / "source_resolve"
    test_target_dir = tmp_path / "target_resolve"
    test_source_dir.mkdir()
    test_target_dir.mkdir()
    
    # Create source and target config files
    source_config_path = test_source_dir / "mcp.json"
    target_config_path = test_target_dir / "mcp.json"
    
    # Sample configurations with conflicts
    source_config = {
        "mcpServers": {
            "server-1": {
                "command": "python",
                "args": ["-m", "source_server1"],
                "env": {"API_KEY": "source-key1"}
            },
            "server-2": {
                "command": "node",
                "args": ["source_server2.js"],
                "env": {"API_KEY": "source-key2"}
            }
        }
    }
    
    target_config = {
        "mcpServers": {
            "server-1": {
                "command": "python",
                "args": ["-m", "target_server1"],
                "env": {"API_KEY": "target-key1"}
            },
            "server-2": {
                "command": "node",
                "args": ["target_server2.js"],
                "env": {"API_KEY": "target-key2"}
            }
        }
    }
    
    # Write the configurations
    with open(source_config_path, 'w') as f:
        json.dump(source_config, f)
    with open(target_config_path, 'w') as f:
        json.dump(target_config, f)
    
    # Mock the get_ide_path function to return our test paths
    original_get_ide_path = get_ide_path
    
    def mock_get_ide_path(ide):
        if ide == "source-ide":
            return str(source_config_path)
        elif ide == "target-ide":
            return str(target_config_path)
        return original_get_ide_path(ide)
    
    # Apply the mock
    import src.mcp_agile_flow.migration_tool
    src.mcp_agile_flow.migration_tool.get_ide_path = mock_get_ide_path
    
    try:
        # Step 1: Initial migration attempt should detect conflicts
        initial_result = asyncio.run(handle_call_tool("migrate-mcp-config", {
            "from_ide": "source-ide",
            "to_ide": "target-ide"
        }))
        
        initial_response = json.loads(initial_result[0].text)
        assert initial_response["success"] == True
        assert initial_response["needs_resolution"] == True
        assert "server-1" in initial_response["conflicts"]
        assert "server-2" in initial_response["conflicts"]
        assert "conflict_details" in initial_response
        
        # Step 2: Resolve conflicts - keep source for server-1 and target for server-2
        resolution_result = asyncio.run(handle_call_tool("migrate-mcp-config", {
            "from_ide": "source-ide",
            "to_ide": "target-ide",
            "conflict_resolutions": {
                "server-1": True,  # Use source config
                "server-2": False  # Keep target config
            }
        }))
        
        # Verify the resolution response
        resolution_response = json.loads(resolution_result[0].text)
        assert resolution_response["success"] == True
        assert "resolved_conflicts" in resolution_response
        assert "server-1" in resolution_response["resolved_conflicts"]
        assert "server-2" in resolution_response["resolved_conflicts"]
        assert "source_path" in resolution_response
        assert "target_path" in resolution_response
        
        # Step 3: Verify the merged configuration is correct
        with open(target_config_path, 'r') as f:
            merged_config = json.load(f)
        
        # Verify server-1 uses source configuration
        assert merged_config["mcpServers"]["server-1"]["args"] == ["-m", "source_server1"]
        assert merged_config["mcpServers"]["server-1"]["env"]["API_KEY"] == "source-key1"
        
        # Verify server-2 kept target configuration
        assert merged_config["mcpServers"]["server-2"]["args"] == ["target_server2.js"]
        assert merged_config["mcpServers"]["server-2"]["env"]["API_KEY"] == "target-key2"
        
        # Save the responses for inspection
        save_test_output("migrate_mcp_config_initial_conflicts_response", initial_response)
        save_test_output("migrate_mcp_config_resolution_response", resolution_response)
        save_test_output("migrate_mcp_config_merged_config", merged_config)
        
    finally:
        # Restore the original function
        src.mcp_agile_flow.migration_tool.get_ide_path = original_get_ide_path 

def test_migrate_mcp_config_invalid_resolutions(tmp_path):
    """Test error handling with invalid conflict resolutions."""
    logger.info("Testing migrate-mcp-config with invalid resolutions...")
    
    # Import the handler and IDE path functions
    from src.mcp_agile_flow.simple_server import handle_call_tool
    from src.mcp_agile_flow.migration_tool import get_ide_path
    
    # Create temporary directories for test configs
    test_source_dir = tmp_path / "source_invalid"
    test_target_dir = tmp_path / "target_invalid"
    test_source_dir.mkdir()
    test_target_dir.mkdir()
    
    # Create source and target config files
    source_config_path = test_source_dir / "mcp.json"
    target_config_path = test_target_dir / "mcp.json"
    
    # Sample configurations with conflicts
    source_config = {
        "mcpServers": {
            "server-1": {
                "command": "python",
                "args": ["-m", "source_server"],
                "env": {"API_KEY": "source-key"}
            }
        }
    }
    
    target_config = {
        "mcpServers": {
            "server-1": {
                "command": "python",
                "args": ["-m", "target_server"],
                "env": {"API_KEY": "target-key"}
            }
        }
    }
    
    # Write the configurations
    with open(source_config_path, 'w') as f:
        json.dump(source_config, f)
    with open(target_config_path, 'w') as f:
        json.dump(target_config, f)
    
    # Mock the get_ide_path function to return our test paths
    original_get_ide_path = get_ide_path
    
    def mock_get_ide_path(ide):
        if ide == "source-ide":
            return str(source_config_path)
        elif ide == "target-ide":
            return str(target_config_path)
        return original_get_ide_path(ide)
    
    # Apply the mock
    import src.mcp_agile_flow.migration_tool
    src.mcp_agile_flow.migration_tool.get_ide_path = mock_get_ide_path
    
    try:
        # Test 1: Provide resolutions for non-existent conflicts
        invalid_result = asyncio.run(handle_call_tool("migrate-mcp-config", {
            "from_ide": "source-ide",
            "to_ide": "target-ide",
            "conflict_resolutions": {
                "non-existent-server": True
            }
        }))
        
        invalid_response = json.loads(invalid_result[0].text)
        assert invalid_response["success"] == False
        assert "Invalid conflict resolutions" in invalid_response["error"]
        assert "actual_conflicts" in invalid_response
        
        # Test 2: Provide incomplete resolutions
        incomplete_result = asyncio.run(handle_call_tool("migrate-mcp-config", {
            "from_ide": "source-ide",
            "to_ide": "target-ide",
            "conflict_resolutions": {}  # Empty resolutions
        }))
        
        incomplete_response = json.loads(incomplete_result[0].text)
        assert incomplete_response["success"] == False
        assert "Missing conflict resolutions" in incomplete_response["error"]
        assert "needs_resolution" in incomplete_response
        assert incomplete_response["needs_resolution"] == True
        assert "conflicts" in incomplete_response
        assert "conflict_details" in incomplete_response
        
        # Save the responses for inspection
        save_test_output("migrate_mcp_config_invalid_resolutions_response", invalid_response)
        save_test_output("migrate_mcp_config_incomplete_resolutions_response", incomplete_response)
        
    finally:
        # Restore the original function
        src.mcp_agile_flow.migration_tool.get_ide_path = original_get_ide_path 
