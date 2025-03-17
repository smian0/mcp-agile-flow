#!/bin/bash
# Script to inspect the MCP Agile Flow server using the MCP CLI tools

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "mcp-agile-flow/.venv" ]; then
    source mcp-agile-flow/.venv/bin/activate
    echo "Activated virtual environment at mcp-agile-flow/.venv"
fi

# Check for MCP CLI
if ! command -v mcp &> /dev/null; then
    echo "MCP CLI not found. Checking if it's in the Python environment..."
    if ! python -c "import mcp; print('MCP package found')" &> /dev/null; then
        echo "MCP SDK not found in Python environment. Installing..."
        uv pip install "mcp[cli]" || {
            echo "ERROR: Failed to install MCP SDK. Please install it manually with:"
            echo "  uv pip install \"mcp[cli]\""
            exit 1
        }
    else
        # MCP package is installed, but mcp command isn't in PATH
        # Let's create an alias for Python module execution
        echo "MCP SDK found in Python environment, but command not in PATH."
        echo "Creating function for mcp command..."
        mcp() {
            python -m mcp "$@"
        }
        export -f mcp
    fi
fi

# Ensure PYTHONPATH includes the project root
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Check if the server file exists
SERVER_FILE="mcp-agile-flow/agile_flow_sdk.py"
if [ ! -f "$SERVER_FILE" ]; then
    echo "Error: Server file not found at $SERVER_FILE"
    exit 1
fi

# Function to run an MCP dev session in the background and capture logs
function run_mcp_dev {
    echo "Starting MCP dev session..."
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Run MCP dev in the background
    LOGFILE="logs/mcp_dev_$(date +%Y%m%d_%H%M%S).log"
    mcp dev "$SERVER_FILE" > "$LOGFILE" 2>&1 &
    MCP_PID=$!
    
    # Give it time to start
    sleep 2
    
    # Check if it's still running
    if kill -0 $MCP_PID 2>/dev/null; then
        echo "MCP dev running with PID $MCP_PID"
        echo "Logs available at $LOGFILE"
        
        # Use tail to show log output in real-time
        echo "=== Server Logs ==="
        tail -n 10 "$LOGFILE"
        echo "================="
    else
        echo "Error: MCP dev failed to start. Check logs at $LOGFILE"
        cat "$LOGFILE"
        exit 1
    fi
    
    # Return the PID so we can kill it later
    echo $MCP_PID
}

# Function to install the server in MCP
function install_server {
    echo "Installing server in MCP..."
    mcp install "$SERVER_FILE"
    
    # Check installation status
    if [ $? -eq 0 ]; then
        echo "Server installed successfully"
        mcp list
    else
        echo "Error: Failed to install server"
        exit 1
    fi
}

# Function to display MCP version
function show_version {
    echo "Getting MCP version..."
    mcp version
}

# Function to run the server directly
function run_server {
    echo "Running MCP server..."
    mcp run "$SERVER_FILE" "$@"
}

# Process command line options
case "$1" in
    dev)
        PID=$(run_mcp_dev)
        echo "Press Ctrl+C to stop the MCP dev session"
        wait $PID
        ;;
    install)
        install_server
        ;;
    run)
        shift
        run_server "$@"
        ;;
    version)
        show_version
        ;;
    *)
        echo "Usage: $0 {dev|install|run|version}"
        echo "  dev     - Run the server in development mode with the MCP Inspector"
        echo "  install - Install the server in MCP"
        echo "  run     - Run the MCP server directly"
        echo "  version - Show MCP version"
        exit 1
        ;;
esac

exit 0
