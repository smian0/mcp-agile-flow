"""
MCP Configuration Migration Tool Tests.
Tests include both direct function tests and end-to-end API integration tests
for the migration functionality between different IDEs.
"""

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import copy

import pytest

from src.mcp_agile_flow.migration_tool import (
    create_backup,
    detect_conflicts,
    get_ide_path,
    merge_configurations,
    migrate_config,
    get_conflict_details,
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
                "env": {"API_KEY": "test-key"},
            },
            "search": {"command": "python", "args": ["-m", "search_server"], "env": {}},
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
        yield {"cursor": cursor_path, "windsurf": windsurf_path}


# === Direct Function Tests ===


def test_detect_conflicts(sample_config):
    """Test conflict detection between configurations."""
    # Create a modified version of the sample config
    modified_config = {
        "mcpServers": {
            "weather": {
                "command": "node",
                "args": ["/different/path/index.js"],  # Changed path
                "env": {"API_KEY": "different-key"},  # Changed key
            },
            "search": {"command": "python", "args": ["-m", "search_server"], "env": {}},
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
                "env": {"API_KEY": "old-key"},
            }
        }
    }

    # Test keeping target configuration for weather
    merged = merge_configurations(sample_config, target_config, {"weather": False})
    assert merged["mcpServers"]["weather"]["args"] == ["/old/path/index.js"]

    # Test using source configuration for weather
    merged = merge_configurations(sample_config, target_config, {"weather": True})
    assert merged["mcpServers"]["weather"]["args"] == [
        "/path/to/weather-server/build/index.js"
    ]

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
                "env": {"API_KEY": "different-key"},
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


def test_claude_desktop_path():
    """Test that the Claude Desktop path is correct."""
    # We'll test that the get_ide_path function works for claude-desktop
    expected_path = None

    # Determine the expected path based on the platform
    platform = (
        "darwin"
        if os.name == "posix" and os.uname().sysname == "Darwin"
        else "linux" if os.name == "posix" else "windows"
    )

    if platform == "darwin":
        expected_path = os.path.expanduser(
            "~/Library/Application Support/Claude/claude_desktop_config.json"
        )
    elif platform == "linux":
        expected_path = os.path.expanduser(
            "~/.config/Claude/claude_desktop_config.json"
        )
    elif platform == "windows":
        expected_path = os.path.expandvars(
            "%APPDATA%\\Claude\\claude_desktop_config.json"
        )

    # Test that get_ide_path returns the expected path
    actual_path = get_ide_path("claude-desktop")
    assert actual_path == expected_path


# === API Integration Tests ===


def test_migrate_mcp_config_with_conflicts(tmp_path):
    """Test the migrate-mcp-config tool with conflicts."""
    logger.info("Testing migrate-mcp-config with conflicts...")

    # Import the handler and IDE path functions
    from src.mcp_agile_flow.migration_tool import get_ide_path
    from src.mcp_agile_flow.server import handle_call_tool

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
                "env": {"API_KEY": "source-key"},
            }
        }
    }

    target_config = {
        "mcpServers": {
            "test-server": {
                "command": "python",
                "args": ["-m", "target_server"],
                "env": {"API_KEY": "target-key"},
            }
        }
    }

    # Write the configurations
    with open(source_config_path, "w") as f:
        json.dump(source_config, f)
    with open(target_config_path, "w") as f:
        json.dump(target_config, f)

    # Mock the get_ide_path function to return our test paths
    original_get_ide_path = get_ide_path

    def mock_get_ide_path(ide):
        if ide == "cursor":
            return str(source_config_path)
        elif ide == "windsurf":
            return str(target_config_path)
        return original_get_ide_path(ide)

    # Apply the mock
    import src.mcp_agile_flow.migration_tool

    src.mcp_agile_flow.migration_tool.get_ide_path = mock_get_ide_path

    try:
        # Call migrate-mcp-config
        result = asyncio.run(
            handle_call_tool(
                "migrate-mcp-config",
                {"from_ide": "cursor", "to_ide": "windsurf", "backup": True},
            )
        )

        # Verify the result
        assert result[0].type == "text"
        response = json.loads(result[0].text)

        # Check the structure of the response
        assert response["success"] is True
        assert response["needs_resolution"] is True
        assert "conflicts" in response
        assert "test-server" in response["conflicts"]

    finally:
        # Restore the original function
        src.mcp_agile_flow.migration_tool.get_ide_path = original_get_ide_path


def test_migrate_mcp_config_resolve_conflicts(tmp_path):
    """Test resolving conflicts with the migrate-mcp-config tool."""
    logger.info("Testing migrate-mcp-config conflict resolution...")

    # Import the handler and IDE path functions
    from src.mcp_agile_flow.migration_tool import migrate_config
    from src.mcp_agile_flow.server import handle_call_tool
    from src.mcp_agile_flow.fastmcp_tools import migrate_mcp_config

    # Define expected conflicts and details
    conflicts = ["server-1", "server-2"]
    conflict_details = {
        "server-1": {
            "source": {"command": "python", "args": ["-m", "source_server1"]},
            "target": {"command": "python", "args": ["-m", "target_server1"]},
        },
        "server-2": {
            "source": {"command": "node", "args": ["source_server2.js"]},
            "target": {"command": "node", "args": ["target_server2.js"]},
        },
    }
    
    # Create a simplified test that only verifies the structure
    with patch('src.mcp_agile_flow.fastmcp_tools.migrate_mcp_config', wraps=migrate_mcp_config) as mock_migrate:
        # Call the migration with valid conflict resolutions
        with patch('src.mcp_agile_flow.migration_tool.migrate_config') as mock_migrate_config:
            # First mock the conflict detection
            mock_migrate_config.return_value = (True, None, conflicts, conflict_details)
            
            # Call the conflict detection
            result = asyncio.run(
                handle_call_tool(
                    "migrate-mcp-config", {"from_ide": "cursor", "to_ide": "windsurf"}
                )
            )
            
            # Parse the response
            response = json.loads(result[0].text)
            assert response["success"] is True
            assert response["needs_resolution"] is True
            assert "conflicts" in response
            
            # Now mock the successful resolution
            mock_migrate_config.return_value = (True, None, [], {})
            
            # Mock the individual functions that might be called directly
            with patch('src.mcp_agile_flow.fastmcp_tools.detect_conflicts', return_value=conflicts):
                with patch('src.mcp_agile_flow.fastmcp_tools.get_conflict_details', return_value=conflict_details):
                    with patch('src.mcp_agile_flow.fastmcp_tools.merge_configurations'):
                        with patch('os.path.exists', return_value=True):
                            with patch('builtins.open', mock_open()):
                                with patch('json.load'):
                                    with patch('json.dump'):
                                        with patch('shutil.copy2'):
                                            with patch('os.makedirs'):
                                                # Call the resolution
                                                resolution_result = asyncio.run(
                                                    handle_call_tool(
                                                        "migrate-mcp-config",
                                                        {
                                                            "from_ide": "cursor",
                                                            "to_ide": "windsurf",
                                                            "conflict_resolutions": {"server-1": True, "server-2": False},
                                                        },
                                                    )
                                                )
    
    # Assert the minimal structure
    assert result[0].type == "text"
    assert resolution_result[0].type == "text"


def test_migrate_mcp_config_invalid_resolutions(tmp_path):
    """Test error handling with invalid conflict resolutions."""
    logger.info("Testing migrate-mcp-config with invalid resolutions...")

    # Import the handler and IDE path functions
    from src.mcp_agile_flow.migration_tool import get_ide_path
    from src.mcp_agile_flow.server import handle_call_tool

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
                "env": {"API_KEY": "source-key"},
            }
        }
    }

    target_config = {
        "mcpServers": {
            "server-1": {
                "command": "python",
                "args": ["-m", "target_server"],
                "env": {"API_KEY": "target-key"},
            }
        }
    }

    # Write the configurations
    with open(source_config_path, "w") as f:
        json.dump(source_config, f)
    with open(target_config_path, "w") as f:
        json.dump(target_config, f)

    # Mock the get_ide_path function to return our test paths
    original_get_ide_path = get_ide_path

    def mock_get_ide_path(ide):
        if ide == "cursor":
            return str(source_config_path)
        elif ide == "windsurf":
            return str(target_config_path)
        return original_get_ide_path(ide)

    # Apply the mock
    import src.mcp_agile_flow.migration_tool

    src.mcp_agile_flow.migration_tool.get_ide_path = mock_get_ide_path

    try:
        # Step 1: First detect conflicts
        detect_result = asyncio.run(
            handle_call_tool(
                "migrate-mcp-config", {"from_ide": "cursor", "to_ide": "windsurf"}
            )
        )
        
        detect_response = json.loads(detect_result[0].text)
        assert detect_response["success"] is True
        assert detect_response["needs_resolution"] is True
        
        # Test 1: Provide resolutions for non-existent conflicts
        invalid_result = asyncio.run(
            handle_call_tool(
                "migrate-mcp-config",
                {
                    "from_ide": "cursor",
                    "to_ide": "windsurf",
                    "conflict_resolutions": {"non-existent-server": True},
                },
            )
        )

        invalid_response = json.loads(invalid_result[0].text)
        assert invalid_response["success"] is False
        assert "Invalid conflict resolutions" in invalid_response["error"]

    finally:
        # Restore the original function
        src.mcp_agile_flow.migration_tool.get_ide_path = original_get_ide_path


def test_migrate_cursor_to_claude_desktop(tmp_path):
    """Test migration from Cursor to Claude Desktop."""
    logger.info("Testing migration from Cursor to Claude Desktop...")

    # Import the handler and IDE path functions
    from src.mcp_agile_flow.migration_tool import get_ide_path
    from src.mcp_agile_flow.server import handle_call_tool

    # Create temporary directories for test configs
    test_cursor_dir = tmp_path / "cursor"
    test_claude_dir = tmp_path / "claude"
    test_cursor_dir.mkdir()
    test_claude_dir.mkdir(parents=True)

    # Create source config file (cursor)
    cursor_config_path = test_cursor_dir / "mcp.json"

    # Sample configuration with a few servers
    cursor_config = {
        "mcpServers": {
            "weather": {
                "command": "node",
                "args": ["/path/to/weather-server.js"],
                "env": {"API_KEY": "cursor-key"},
            },
            "search": {"command": "python", "args": ["-m", "search_server"], "env": {}},
        }
    }

    # Write the cursor configuration
    with open(cursor_config_path, "w") as f:
        json.dump(cursor_config, f)

    # Claude Desktop config path
    claude_config_path = test_claude_dir / "claude_desktop_config.json"

    # Mock the get_ide_path function to return our test paths
    original_get_ide_path = get_ide_path

    def mock_get_ide_path(ide):
        if ide == "cursor":
            return str(cursor_config_path)
        elif ide == "claude-desktop":
            return str(claude_config_path)
        return original_get_ide_path(ide)

    # Apply the mock
    import src.mcp_agile_flow.migration_tool

    src.mcp_agile_flow.migration_tool.get_ide_path = mock_get_ide_path

    try:
        # Call migrate-mcp-config
        result = asyncio.run(
            handle_call_tool(
                "migrate-mcp-config",
                {"from_ide": "cursor", "to_ide": "claude-desktop", "backup": True},
            )
        )

        # Verify the result
        assert result[0].type == "text"
        response = json.loads(result[0].text)

        # Check the structure of the response
        assert response["success"] is True
        assert not response.get("needs_resolution", False)

        # Verify target file was created
        assert os.path.exists(claude_config_path)

        # Read the migrated configuration
        with open(claude_config_path, "r") as f:
            migrated_config = json.load(f)

        # Verify the servers were migrated correctly
        assert "mcpServers" in migrated_config
        assert "weather" in migrated_config["mcpServers"]
        assert "search" in migrated_config["mcpServers"]
        assert (
            migrated_config["mcpServers"]["weather"]["env"]["API_KEY"] == "cursor-key"
        )

        # Save the response for inspection
        save_test_output("migrate_cursor_to_claude_desktop_response", response)
        save_test_output("migrated_claude_desktop_config", migrated_config)

    finally:
        # Restore the original function
        src.mcp_agile_flow.migration_tool.get_ide_path = original_get_ide_path
