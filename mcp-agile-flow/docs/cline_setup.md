# Setting Up MCP Agile Flow with Cline

This guide will help you configure the MCP Agile Flow server with Cline, the Claude desktop app.

## Installation

### Prerequisites

- Python 3.10 or higher
- uv (Python package installer)
- Cline (Claude desktop app) installed

### Step 1: Install the MCP Agile Flow server

Clone the repository or use the local directory you already have:

```bash
# Option 1: Install from local directory
cd /path/to/mcp-agile-flow
uv pip install -e .

# Verify installation
mcp-agile-flow --version
```

### Step 2: Configure Cline

Configure Cline to use the MCP Agile Flow server by editing the Cline configuration file:

1. Open the Cline configuration file at:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP Agile Flow server configuration under the `mcpServers` section:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "mcp-agile-flow-start",
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

**Alternative Configuration (if PATH issues):**
```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "uvx",
      "args": ["run", "mcp-agile-flow-start"],
      "env": {
        "PROJECT_PATH": "${PROJECT_PATH}"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Note**: If the file doesn't exist or doesn't have an `mcpServers` section, you'll need to create it.

### Step 3: Restart Cline

After saving the configuration file, restart Cline to apply the changes.

## Testing with Cline

To test that the MCP Agile Flow server is working correctly with Cline:

1. Open Cline
2. Create a new chat
3. Ask Cline to perform an action using the MCP Agile Flow server:

```
I'd like to create a new Agile project with MCP Agile Flow. Please create a project called "My First Project" with a brief description.
```

Cline should respond by indicating it's using the MCP Agile Flow server to create a project.

### Example Prompts

Here are some example prompts you can use to test the MCP Agile Flow server with Cline:

- "Can you list all available Agile projects using MCP Agile Flow?"
- "Please create a new Agile project called 'Website Redesign' with a description."
- "Generate Cursor IDE rules for the current project using MCP Agile Flow."
- "Generate Cline rules for this project using the MCP Agile Flow server."

## Troubleshooting

If Cline isn't connecting to the MCP Agile Flow server:

1. Verify the server is installed correctly:
   ```bash
   uv pip list | grep mcp-agile-flow
   ```

2. Check the Cline logs for any error messages:
   - macOS: `~/Library/Logs/Claude/main.log`
   - Windows: `%USERPROFILE%\AppData\Roaming\Claude\logs\main.log`
   - Linux: `~/.config/Claude/logs/main.log`

3. Verify the configuration file syntax is correct (valid JSON)

4. Make sure the `PROJECT_PATH` environment variable is set correctly or remove it to use the current working directory

5. Ensure you have restarted Cline after making configuration changes
