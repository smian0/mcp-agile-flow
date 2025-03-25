"""
Tests for natural language command detection functionality.
"""

import pytest
from src.mcp_agile_flow.utils import detect_mcp_command
from src.mcp_agile_flow import process_natural_language


def test_detect_migration_commands():
    """Test migration command patterns."""
    # Basic migration command
    tool_name, args = detect_mcp_command("migrate mcp config to claude")
    assert tool_name == "migrate_mcp_config"
    assert args == {"from_ide": "cursor", "to_ide": "claude-desktop"}
    
    # With explicit source
    tool_name, args = detect_mcp_command("migrate config from windsurf to claude")
    assert tool_name == "migrate_mcp_config"
    assert args == {"from_ide": "windsurf", "to_ide": "claude-desktop"}
    
    # Alternative wordings
    tool_name, args = detect_mcp_command("copy mcp settings to cline")
    assert tool_name == "migrate_mcp_config"
    assert args == {"from_ide": "cursor", "to_ide": "cline"}
    
    tool_name, args = detect_mcp_command("transfer config from cline to copilot")
    assert tool_name == "migrate_mcp_config"
    assert args == {"from_ide": "cline", "to_ide": "cursor"}
    
    # Test with hyphenated IDE name
    tool_name, args = detect_mcp_command("migrate config to claude-desktop")
    assert tool_name == "migrate_mcp_config"
    assert args == {"from_ide": "cursor", "to_ide": "claude-desktop"}


def test_detect_initialize_commands():
    """Test initialization command patterns."""
    # Basic initialization
    tool_name, args = detect_mcp_command("initialize ide for claude")
    assert tool_name == "initialize_ide"
    assert args == {"ide": "claude-desktop"}
    
    # Alternative wordings
    tool_name, args = detect_mcp_command("setup rules for windsurf")
    assert tool_name == "initialize_ide"
    assert args == {"ide": "windsurf"}
    
    tool_name, args = detect_mcp_command("create ide for cline")
    assert tool_name == "initialize_ide"
    assert args == {"ide": "cline"}


def test_detect_settings_commands():
    """Test settings command patterns."""
    # Basic settings command
    tool_name, args = detect_mcp_command("get project settings")
    assert tool_name == "get_project_settings"
    assert args == {}
    
    # Alternative wordings
    tool_name, args = detect_mcp_command("show settings")
    assert tool_name == "get_project_settings"
    assert args == {}
    
    tool_name, args = detect_mcp_command("project settings")
    assert tool_name == "get_project_settings"
    assert args == {}


def test_detect_context_commands():
    """Test context analysis command patterns."""
    # Basic context command
    tool_name, args = detect_mcp_command("prime context")
    assert tool_name == "prime_context"
    assert args == {}
    
    # Alternative wordings
    tool_name, args = detect_mcp_command("analyze project context")
    assert tool_name == "prime_context"
    assert args == {}
    
    tool_name, args = detect_mcp_command("build context")
    assert tool_name == "prime_context"
    assert args == {}


def test_detect_think_commands():
    """Test think command patterns."""
    # Basic think command
    tool_name, args = detect_mcp_command("think about improving code quality")
    assert tool_name == "think"
    assert args == {"thought": "improving code quality"}


def test_no_command_detection():
    """Test cases where no command should be detected."""
    # Random text
    tool_name, args = detect_mcp_command("hello world")
    assert tool_name is None
    assert args is None
    
    # Empty string
    tool_name, args = detect_mcp_command("")
    assert tool_name is None
    assert args is None
    
    # Similar but not matching pattern
    tool_name, args = detect_mcp_command("migrate to a new place")
    assert tool_name is None
    assert args is None


def test_process_natural_language_integration():
    """Test integration with process_natural_language function."""
    # Valid command
    result = process_natural_language("get project settings")
    assert "project_path" in result
    assert "ai_docs_directory" in result
    
    # Invalid command
    result = process_natural_language("hello world")
    assert "success" in result
    assert result["success"] is False
    assert "error" in result 