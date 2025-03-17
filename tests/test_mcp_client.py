#!/usr/bin/env python3
"""
MCP Agile Flow Test Client

This script tests the MCP Agile Flow server by connecting to it using the
MCP client library and running various tests to verify functionality.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    # Import the MCP SDK
    # The specific imports might vary based on the MCP SDK version
    try:
        # Try newer MCP SDK structure
        from mcp.client import ClientSession
        from mcp.transport.stdio import StdioTransport
        print("Using MCP SDK with client/transport.stdio structure")
    except ImportError as e1:
        # Try older/alternative MCP SDK structure
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            print("Using MCP SDK with client.stdio structure")
        except ImportError as e2:
            print(f"Error: MCP SDK not found or incompatible version.")
            print(f"First import error: {e1}")
            print(f"Second import error: {e2}")
            print("Please install MCP SDK with: uv pip install 'mcp[cli]'")
            sys.exit(1)
except Exception as e:
    print(f"Unexpected error importing MCP SDK: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp_test_client.log"),
    ],
)
logger = logging.getLogger("mcp_test_client")


class McpTestClient:
    """
    MCP Test Client for testing the Agile Flow server.
    """

    def __init__(self, server_script_path: str, project_path: Optional[str] = None):
        """
        Initialize the MCP Test Client.
        
        Args:
            server_script_path: Path to the server script or wrapper.
            project_path: Path to use for PROJECT_PATH environment variable.
        """
        self.server_script_path = server_script_path
        self.project_path = project_path or os.getcwd()
        self.test_results = {}
        
    async def run_tests(self) -> Dict[str, Any]:
        """
        Run all tests against the MCP server.
        
        Returns:
            Dictionary of test results.
        """
        logger.info(f"Starting tests against server at: {self.server_script_path}")
        logger.info(f"Using project path: {self.project_path}")
        
        # Create transport
        transport = StdioTransport(
            command=self.server_script_path,
            args=[],
            env={"PROJECT_PATH": self.project_path}
        )
        
        try:
            # Connect to server using transport
            logger.info("Connecting to MCP server...")
            
            async with await transport.connect() as (reader, writer):
                async with ClientSession(reader, writer) as session:
                    logger.info("Connected to MCP server")
                    
                    # Initialize the session
                    await session.initialize()
                    logger.info("MCP session initialized")
                    
                    # Run test scenarios
                    await self._test_list_tools(session)
                    await self._test_project_tools(session)
                    await self._test_ide_tools(session)
                    await self._test_resources(session)
                    
                    # Summarize results
                    success_count = sum(1 for result in self.test_results.values() if result["success"])
                    total_count = len(self.test_results)
                    logger.info(f"Test summary: {success_count}/{total_count} tests passed")
                    
                    return {
                        "summary": {
                            "success_count": success_count,
                            "total_count": total_count,
                            "success_percentage": (success_count / total_count) * 100 if total_count > 0 else 0
                        },
                        "results": self.test_results
                    }
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {str(e)}")
            return {
                "summary": {
                    "success_count": 0,
                    "total_count": 0,
                    "success_percentage": 0
                },
                "error": str(e)
            }
    
    async def _test_list_tools(self, session: ClientSession) -> None:
        """Test listing tools from the server."""
        try:
            logger.info("Testing list_tools...")
            tools = await session.list_tools()
            
            # Verify we got some tools
            tool_count = len(tools)
            logger.info(f"Found {tool_count} tools")
            
            # Log tool names
            tool_names = [tool.name for tool in tools]
            logger.info(f"Tools: {', '.join(tool_names)}")
            
            success = tool_count > 0
            self.test_results["list_tools"] = {
                "success": success,
                "message": f"Found {tool_count} tools" if success else "No tools found",
                "tools": tool_names
            }
        except Exception as e:
            logger.error(f"Error testing list_tools: {str(e)}")
            self.test_results["list_tools"] = {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    async def _test_project_tools(self, session: ClientSession) -> None:
        """Test project management tools."""
        try:
            logger.info("Testing project tools...")
            
            # Test list_projects
            try:
                logger.info("Testing list_projects...")
                result = await session.call_tool("list_projects", {})
                self.test_results["list_projects"] = {
                    "success": True,
                    "message": "Successfully listed projects",
                    "result": result
                }
                logger.info(f"list_projects result: {json.dumps(result, indent=2)}")
            except Exception as e:
                logger.error(f"Error testing list_projects: {str(e)}")
                self.test_results["list_projects"] = {
                    "success": False,
                    "message": f"Error: {str(e)}"
                }
            
            # Test create_project with a test project name
            try:
                logger.info("Testing create_project...")
                test_project_name = f"Test Project {asyncio.get_event_loop().time()}"
                result = await session.call_tool("create_project", {
                    "name": test_project_name,
                    "description": "Test project created by MCP test client"
                })
                self.test_results["create_project"] = {
                    "success": "project" in result,
                    "message": "Successfully created project" if "project" in result else "Failed to create project",
                    "result": result
                }
                logger.info(f"create_project result: {json.dumps(result, indent=2)}")
            except Exception as e:
                logger.error(f"Error testing create_project: {str(e)}")
                self.test_results["create_project"] = {
                    "success": False,
                    "message": f"Error: {str(e)}"
                }
        except Exception as e:
            logger.error(f"Error testing project tools: {str(e)}")
            self.test_results["project_tools"] = {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    async def _test_ide_tools(self, session: ClientSession) -> None:
        """Test IDE rule generation tools."""
        try:
            logger.info("Testing IDE rule generation tools...")
            
            # Test generate_cursor_rules
            try:
                logger.info("Testing generate_cursor_rules...")
                result = await session.call_tool("generate_cursor_rules", {})
                self.test_results["generate_cursor_rules"] = {
                    "success": "rules" in result,
                    "message": "Successfully generated Cursor rules" if "rules" in result else "Failed to generate Cursor rules",
                    "result": result
                }
                logger.info(f"generate_cursor_rules result: {json.dumps(result, indent=2)}")
            except Exception as e:
                logger.error(f"Error testing generate_cursor_rules: {str(e)}")
                self.test_results["generate_cursor_rules"] = {
                    "success": False,
                    "message": f"Error: {str(e)}"
                }
            
            # Test generate_cline_rules
            try:
                logger.info("Testing generate_cline_rules...")
                result = await session.call_tool("generate_cline_rules", {})
                self.test_results["generate_cline_rules"] = {
                    "success": "rules" in result,
                    "message": "Successfully generated Cline rules" if "rules" in result else "Failed to generate Cline rules",
                    "result": result
                }
                logger.info(f"generate_cline_rules result: {json.dumps(result, indent=2)}")
            except Exception as e:
                logger.error(f"Error testing generate_cline_rules: {str(e)}")
                self.test_results["generate_cline_rules"] = {
                    "success": False,
                    "message": f"Error: {str(e)}"
                }
        except Exception as e:
            logger.error(f"Error testing IDE tools: {str(e)}")
            self.test_results["ide_tools"] = {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    async def _test_resources(self, session: ClientSession) -> None:
        """Test resource access."""
        try:
            logger.info("Testing resources...")
            
            # List available resources
            try:
                logger.info("Listing resources...")
                resources = await session.list_resources()
                
                # Log resource URIs
                resource_uris = [resource.uri for resource in resources]
                logger.info(f"Found {len(resources)} resources: {', '.join(resource_uris)}")
                
                self.test_results["list_resources"] = {
                    "success": True,
                    "message": f"Found {len(resources)} resources",
                    "resources": resource_uris
                }
                
                # Test reading each resource
                for resource in resources:
                    try:
                        logger.info(f"Reading resource: {resource.uri}")
                        content, mime_type = await session.read_resource(resource.uri)
                        
                        self.test_results[f"read_resource_{resource.uri}"] = {
                            "success": True,
                            "message": f"Successfully read resource {resource.uri}",
                            "mime_type": mime_type,
                            "content_preview": content[:100] + "..." if len(content) > 100 else content
                        }
                    except Exception as e:
                        logger.error(f"Error reading resource {resource.uri}: {str(e)}")
                        self.test_results[f"read_resource_{resource.uri}"] = {
                            "success": False,
                            "message": f"Error: {str(e)}"
                        }
            except Exception as e:
                logger.error(f"Error listing resources: {str(e)}")
                self.test_results["list_resources"] = {
                    "success": False,
                    "message": f"Error: {str(e)}"
                }
        except Exception as e:
            logger.error(f"Error testing resources: {str(e)}")
            self.test_results["resources"] = {
                "success": False,
                "message": f"Error: {str(e)}"
            }


async def main():
    """Main entry point."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='MCP Agile Flow Test Client')
    parser.add_argument('--server', '-s', default='/Users/smian/mcp-agile-flow/run_server.sh',
                        help='Path to server script or wrapper')
    parser.add_argument('--project-path', '-p', default='/Users/smian/mcp-agile-flow/mcp-agile-flow',
                        help='Path to use for PROJECT_PATH environment variable')
    args = parser.parse_args()
    
    # Run tests
    test_client = McpTestClient(args.server, args.project_path)
    results = await test_client.run_tests()
    
    # Print results
    print("\n=== MCP Test Results ===")
    print(f"Success rate: {results['summary']['success_percentage']:.2f}% ({results['summary']['success_count']}/{results['summary']['total_count']})")
    print("\nDetailed results:")
    for test_name, result in results.get('results', {}).items():
        if result.get('success', False):
            print(f"✅ {test_name}: {result.get('message', '')}")
        else:
            print(f"❌ {test_name}: {result.get('message', '')}")
    
    # Return success code based on test results
    return 0 if results.get('summary', {}).get('success_count', 0) == results.get('summary', {}).get('total_count', 1) else 1


if __name__ == "__main__":
    asyncio.run(main())
