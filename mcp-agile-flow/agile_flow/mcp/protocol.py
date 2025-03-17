"""
MCP protocol handling for the Agile Flow server.
"""

import json
import sys
import logging
from typing import Dict, List, Any, Callable, Optional, TypedDict

from ..utils.logger import setup_logger

logger = setup_logger("agile_flow.mcp.protocol")


class JsonRpcRequest(TypedDict):
    """JSON-RPC request structure."""
    jsonrpc: str
    id: str
    method: str
    params: Dict[str, Any]


class JsonRpcResponse(TypedDict):
    """JSON-RPC response structure."""
    jsonrpc: str
    id: str
    result: Dict[str, Any]


class JsonRpcError(TypedDict):
    """JSON-RPC error response structure."""
    jsonrpc: str
    id: str
    error: Dict[str, Any]


class McpServer:
    """
    MCP Server that handles the Model Context Protocol over standard I/O.
    """
    
    def __init__(self):
        """Initialize the MCP server."""
        self.tools = {}
        self.running = False
        
    def register_tool(self, name: str, handler: Callable, schema: Dict[str, Any]) -> None:
        """
        Register a tool with the MCP server.
        
        Args:
            name: Name of the tool.
            handler: Function that handles the tool request.
            schema: JSON Schema for the tool parameters.
        """
        self.tools[name] = {
            "handler": handler,
            "schema": schema
        }
        logger.debug(f"Registered tool: {name}")
        
    def get_tool_handler(self, name: str) -> Optional[Callable]:
        """
        Get the handler function for a tool.
        
        Args:
            name: Name of the tool.
            
        Returns:
            Handler function if the tool exists, None otherwise.
        """
        tool = self.tools.get(name)
        if tool:
            return tool["handler"]
        return None
        
    def get_tools_list(self) -> List[Dict[str, Any]]:
        """
        Get a list of all registered tools with their schemas.
        
        Returns:
            List of tool definitions.
        """
        tools_list = []
        for name, tool in self.tools.items():
            tools_list.append({
                "name": name,
                "description": tool.get("schema", {}).get("description", ""),
                "inputSchema": tool.get("schema", {})
            })
        
        logger.debug(f"Returning {len(tools_list)} tools: {[t['name'] for t in tools_list]}")
        return tools_list
        
    def handle_request(self, request: JsonRpcRequest) -> Dict[str, Any]:
        """
        Handle an MCP request.
        
        Args:
            request: The JSON-RPC request object.
            
        Returns:
            JSON-RPC response object.
        """
        request_id = request.get("id", "")
        method = request.get("method", "")
        params = request.get("params", {})
        
        logger.debug(f"Handling request: {method}")
        
        # Handle special methods
        if method == "list_tools":
            return self._create_response(request_id, {"tools": self.get_tools_list()})
            
        # Handle tool calls
        if method == "call_tool":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            
            handler = self.get_tool_handler(tool_name)
            if not handler:
                return self._create_error(request_id, -32601, f"Tool not found: {tool_name}")
                
            try:
                result = handler(tool_args)
                return self._create_response(request_id, result)
            except Exception as e:
                logger.error(f"Error handling tool {tool_name}: {str(e)}")
                return self._create_error(request_id, -32603, str(e))
                
        # Method not supported
        return self._create_error(request_id, -32601, f"Method not supported: {method}")
        
    def _create_response(self, request_id: str, result: Dict[str, Any]) -> JsonRpcResponse:
        """
        Create a JSON-RPC response object.
        
        Args:
            request_id: ID of the request.
            result: Result of the request.
            
        Returns:
            JSON-RPC response object.
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
    def _create_error(self, request_id: str, code: int, message: str) -> JsonRpcError:
        """
        Create a JSON-RPC error response object.
        
        Args:
            request_id: ID of the request.
            code: Error code.
            message: Error message.
            
        Returns:
            JSON-RPC error response object.
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        
    def run(self) -> None:
        """
        Run the MCP server, listening for requests on stdin and
        sending responses on stdout.
        """
        self.running = True
        
        try:
            logger.info("Starting MCP server")
            
            while self.running:
                # Read a line from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                    
                try:
                    # Parse the request
                    request = json.loads(line)
                    
                    # Handle the request
                    response = self.handle_request(request)
                    
                    # Send the response
                    json.dump(response, sys.stdout)
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON: {line}")
                    error = self._create_error("unknown", -32700, "Parse error")
                    json.dump(error, sys.stdout)
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            logger.info("MCP server interrupted")
            
        except Exception as e:
            logger.error(f"Error in MCP server: {str(e)}")
            
        finally:
            self.running = False
            logger.info("MCP server stopped")
