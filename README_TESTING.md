# MCP Agile Flow Server Testing Guide

This guide explains how to test the MCP Agile Flow server using various approaches to ensure it's working correctly and integrates properly with MCP clients.

## Testing Tools

We've provided several tools to help test and debug the MCP Agile Flow server:

1. **MCP Test Client** - A programmatic test client that verifies server functionality
2. **MCP Inspector** - An interactive web-based UI for testing tools and resources
3. **Server Installation Script** - Helps install the server into client applications
4. **Run Script Wrapper** - A reliable way to run the server with proper environment setup

## Automated Testing with MCP Test Client

The MCP test client runs a series of tests against the server to verify its functionality:

```bash
# Run tests with default configuration
./run_mcp_tests.sh

# Specify custom server script and project path
./run_mcp_tests.sh --server /path/to/server/script --project-path /path/to/project
```

The test client verifies:
- Basic connection to the server
- Listing available tools
- Creating and listing projects
- Generating IDE rules
- Accessing resources

Test results are logged both to the console and to a log file in the `logs` directory.

## Interactive Testing with MCP Inspector

The MCP Inspector provides a web-based UI for interactively testing the server:

```bash
# Start the inspector
./inspect_server.sh dev
```

This will:
1. Launch the server
2. Open a web interface for testing
3. Show real-time logs in the console

The MCP Inspector allows you to:
- Browse available tools and resources
- Execute tools with custom parameters
- See detailed results and error messages
- Explore tool documentation

## Server Installation and Status

You can also use the inspection script to install the server into client applications and check status:

```bash
# Install the server in Claude Desktop
./inspect_server.sh install

# Check server status
./inspect_server.sh status

# List available servers
./inspect_server.sh list
```

## Using the Server with Client Applications

### Claude Desktop

To use the server with Claude Desktop:

1. Install the server:
   ```bash
   ./inspect_server.sh install
   ```

2. Or manually add this configuration to Claude Desktop's configuration file:
   ```json
   {
     "mcpServers": {
       "agile-flow": {
         "command": "/Users/smian/mcp-agile-flow/run_server.sh",
         "args": [],
         "env": {
           "PROJECT_PATH": "${PROJECT_PATH}"
         },
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```

3. Restart Claude Desktop

### Other MCP Clients

For other MCP clients, use the configuration from the `docs/mcp_config.json` file.

## Troubleshooting

If you encounter issues:

1. **Connection Errors**:
   - Verify the server script path is correct
   - Check that the run_server.sh script has execute permissions
   - Make sure the PROJECT_PATH environment variable is set correctly

2. **No Tools Found**:
   - Run the MCP test client to see if it can connect and list tools
   - Check server logs for initialization errors
   - Verify the server is properly registering tools during startup

3. **Tool Execution Errors**:
   - Use the MCP Inspector to test the specific tool with different parameters
   - Look for detailed error messages in the logs

4. **Client Integration Issues**:
   - Use `./inspect_server.sh status` to check client configuration
   - Verify the client is using the correct path to the server

## Log Locations

- MCP test client logs: `logs/mcp_test_*.log`
- MCP Inspector logs: `logs/mcp_dev_*.log`
- Server logs may also be available in client application logs
