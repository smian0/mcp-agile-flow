"""
Integration tests for FastMCP Tools.

These tests verify that the FastMCP tools can be called through the MCP protocol.
"""

import asyncio
import json
import os
import pytest
from unittest.mock import patch, MagicMock

from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

from mcp_agile_flow.server import mcp
from mcp_agile_flow.fastmcp_tools import fastmcp, get_project_settings


class MockStream:
    """Mock stream for testing MCP server communication."""
    
    def __init__(self):
        self.sent_messages = []
        self.receive_queue = asyncio.Queue()
    
    async def send(self, message):
        self.sent_messages.append(message)
    
    async def receive(self):
        return await self.receive_queue.get()
    
    async def put_message(self, message):
        await self.receive_queue.put(message)


@pytest.mark.asyncio
async def test_get_project_settings_integration():
    """Test that the get-project-settings tool works through the MCP protocol."""
    # Set up mock streams for testing MCP server
    read_stream = MockStream()
    write_stream = MockStream()
    
    # Patch the register_fastmcp method instead of calling it directly
    with patch.object(mcp, 'register_fastmcp', MagicMock()) as mock_register:
        # Create a Task to run the MCP server in the background
        server_task = asyncio.create_task(
            mcp.run(
                read_stream,
                write_stream,
                initialization_options=InitializationOptions(
                    server_name="agile-flow-test",
                    server_version="0.1.0",
                    capabilities=mcp.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
        )
        
        try:
            # Wait for the server to start up
            await asyncio.sleep(0.1)
            
            # Simulate list_tools request
            await read_stream.put_message({
                "id": "1",
                "method": "listTools",
                "params": {}
            })
            
            # Wait for the response and check that our FastMCP tool is listed
            response = None
            for _ in range(10):  # Try a few times with a delay
                if write_stream.sent_messages:
                    response = write_stream.sent_messages[-1]
                    break
                await asyncio.sleep(0.1)
            
            assert response is not None
            assert response["id"] == "1"
            assert "result" in response
            
            # Find the get-project-settings tool in the result
            found_tool = False
            for tool in response["result"]:
                if tool["name"] == "get-project-settings":
                    found_tool = True
                    # Verify the tool parameters
                    assert "proposed_path" in tool["inputSchema"]["properties"]
                    break
            
            assert found_tool, "get-project-settings tool not found in listTools response"
            
            # Now, simulate calling the tool
            await read_stream.put_message({
                "id": "2",
                "method": "callTool",
                "params": {
                    "name": "get-project-settings",
                    "arguments": {}
                }
            })
            
            # Wait for the response
            response = None
            for _ in range(10):  # Try a few times with a delay
                for msg in write_stream.sent_messages:
                    if msg.get("id") == "2":
                        response = msg
                        break
                if response:
                    break
                await asyncio.sleep(0.1)
            
            assert response is not None
            assert response["id"] == "2"
            assert "result" in response
            
            # Verify the result
            settings_text = response["result"][0]["text"]
            settings = json.loads(settings_text)
            
            # Check that the result has the expected keys
            assert "project_path" in settings
            assert "current_directory" in settings
            assert "knowledge_graph_directory" in settings
            assert "ai_docs_directory" in settings
            assert "project_type" in settings
            assert "project_metadata" in settings
            
            # Check specific values
            assert settings["project_type"] == "generic"
            assert isinstance(settings["project_metadata"], dict)
            
        finally:
            # Clean up the server task
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass 