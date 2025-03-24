# Installation Guide

This guide will help you install and configure MCP Agile Flow.

## Prerequisites

- Python 3.10 or higher
- pip or uv (Python package manager)

## Basic Installation

### Option 1: Install from PyPI

```bash
pip install mcp-agile-flow
```

### Option 2: Install from GitHub

```bash
# Using SSH (if you have SSH keys configured)
pip install git+ssh://git@github.com/yourusername/mcp-agile-flow.git

# Using HTTPS
pip install git+https://github.com/yourusername/mcp-agile-flow.git
```

## Development Installation

For development, you can install the package in editable mode:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-agile-flow.git
   cd mcp-agile-flow
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## IDE Configuration

To use MCP Agile Flow with your AI IDE, add the following configuration:

### Cursor

Add to `~/.cursor/config/settings.json`:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "/path/to/python",
      "args": ["-m", "mcp_agile_flow"],
      "disabled": false,
      "autoApprove": ["initialize-ide-rules", "get-project-settings"],
      "timeout": 30
    }
  }
}
```

### Windsurf 

Add to `~/.windsurf/settings.json`:

```json
{
  "mcpServers": {
    "agile-flow": {
      "command": "/path/to/python",
      "args": ["-m", "mcp_agile_flow"],
      "disabled": false,
      "autoApprove": ["initialize-ide-rules", "get-project-settings"],
      "timeout": 30
    }
  }
}
```

Replace `/path/to/python` with the actual path to your Python executable (e.g., the path to the Python in your virtual environment).

## Usage Verification

After installation, you can verify the installation by running:

```bash
python -m mcp_agile_flow --version
```

You should see the version number of MCP Agile Flow.

## Troubleshooting

### Common Issues

1. **Module Not Found**: If you see "ModuleNotFoundError", check your installation path and make sure you're using the correct Python environment.

2. **Path Issues**: Make sure to use the full path to Python in your IDE configuration.

3. **Version Compatibility**: Ensure you have Python 3.10 or higher installed.

## Getting Help

If you encounter any issues, please open an issue on GitHub with detailed information about the problem and steps to reproduce it. 