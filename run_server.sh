#!/bin/bash
# Wrapper script to run the MCP Agile Flow server

# Enable debug logging
set -x

# Get script directory (where this script is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script directory: $SCRIPT_DIR" >&2

# Find Python interpreter
if command -v python3 &> /dev/null; then
  PYTHON="python3"
elif command -v python &> /dev/null; then
  PYTHON="python"
else
  echo "Error: Python interpreter not found" >&2
  exit 1
fi
echo "Using Python: $PYTHON" >&2

# Check Python version
$PYTHON --version >&2

# Set up PYTHONPATH to find modules
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
echo "PYTHONPATH: $PYTHONPATH" >&2

# Check if the .venv exists and activate it if it does
if [ -d "$SCRIPT_DIR/mcp-agile-flow/.venv" ]; then
  echo "Found virtual environment at $SCRIPT_DIR/mcp-agile-flow/.venv" >&2
  source "$SCRIPT_DIR/mcp-agile-flow/.venv/bin/activate"
  echo "Activated virtual environment" >&2
  # Check if activation worked
  if [ -n "$VIRTUAL_ENV" ]; then
    echo "Virtual environment active: $VIRTUAL_ENV" >&2
  else
    echo "Warning: Virtual environment activation may have failed" >&2
  fi
fi

# Define SDK path
SDK_PATH="$SCRIPT_DIR/mcp-agile-flow/agile_flow_sdk.py"
echo "SDK path: $SDK_PATH" >&2

# Check if the SDK file exists
if [ ! -f "$SDK_PATH" ]; then
  echo "Error: MCP Agile Flow SDK not found at $SDK_PATH" >&2

  # Try alternative path
  ALT_PATH="$SCRIPT_DIR/agile_flow_sdk.py"
  if [ -f "$ALT_PATH" ]; then
    echo "Found alternative SDK path: $ALT_PATH" >&2
    SDK_PATH="$ALT_PATH"
  else
    echo "Alternative path not found either. Exiting." >&2
    exit 1
  fi
fi

# Check that the user has permission to execute the file
if [ ! -r "$SDK_PATH" ]; then
  echo "Error: Cannot read SDK file at $SDK_PATH" >&2
  exit 1
fi

# Check for MCP dependencies
$PYTHON -c "import mcp" 2>/dev/null || {
  echo "MCP SDK not found in Python environment. Trying to install..." >&2
  $PYTHON -m pip install "mcp[cli]" >&2 || {
    echo "Failed to install MCP SDK with pip. Trying with uv..." >&2
    if command -v uv &> /dev/null; then
      uv pip install "mcp[cli]" >&2 || {
        echo "ERROR: Failed to install MCP SDK. Please install it manually." >&2
        exit 1
      }
    else
      echo "ERROR: uv not found. Please install MCP SDK manually." >&2
      exit 1
    fi
  }
}

# Create a log directory
mkdir -p "$SCRIPT_DIR/logs" 2>/dev/null

# Run the server script with logging
LOG_FILE="$SCRIPT_DIR/logs/server_$(date +%Y%m%d_%H%M%S).log"
echo "Logging to $LOG_FILE" >&2
echo "Starting MCP server with SDK path: $SDK_PATH" >&2

# Make SDK file executable
chmod +x "$SDK_PATH" 2>/dev/null

# Run the server
$PYTHON "$SDK_PATH" 2>"$LOG_FILE"

# Capture exit code
EXIT_CODE=$?

# Log exit code
echo "Server exited with code: $EXIT_CODE" >&2

# Exit with the same status code as the Python script
exit $EXIT_CODE
