#!/bin/bash
# Helper script to run MCP Agile Flow tests

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "mcp-agile-flow/.venv" ]; then
    source mcp-agile-flow/.venv/bin/activate
    echo "Activated virtual environment at mcp-agile-flow/.venv"
fi

# Check if MCP SDK is installed
if ! python -c "import mcp" 2>/dev/null; then
    echo "MCP SDK not installed. Installing..."
    uv pip install "mcp[cli]" || {
        echo "ERROR: Failed to install MCP SDK. Please install it manually with:"
        echo "  uv pip install \"mcp[cli]\""
        exit 1
    }
    # Verify installation was successful
    if ! python -c "import mcp" 2>/dev/null; then
        echo "ERROR: MCP SDK installation failed verification."
        exit 1
    fi
    echo "MCP SDK installed successfully."
fi

# Ensure PYTHONPATH includes the project root
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Set up logging directory
mkdir -p logs

# Run the test client
echo "Running MCP test client..."
python tests/test_mcp_client.py "$@" 2>&1 | tee logs/mcp_test_$(date +%Y%m%d_%H%M%S).log

# Return the exit code from the tests
exit ${PIPESTATUS[0]}
