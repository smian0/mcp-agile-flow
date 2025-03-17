#!/bin/bash
# Helper script to run MCP Agile Flow sample project test

# Navigate to project directory
cd "$(dirname "$0")"

# Set up colors for terminal output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== MCP Agile Flow Sample Project Test =====${NC}"
echo -e "${BLUE}This test will create a sample project and exercise all MCP tools${NC}"
echo -e "${BLUE}The results can be manually inspected to verify functionality${NC}"
echo

# Activate virtual environment if it exists
if [ -d "mcp-agile-flow/.venv" ]; then
    source mcp-agile-flow/.venv/bin/activate
    echo -e "${GREEN}Activated virtual environment at mcp-agile-flow/.venv${NC}"
fi

# Verify MCP SDK is installed (but don't try to install it)
if ! python -c "import mcp" 2>/dev/null; then
    echo -e "${RED}ERROR: MCP SDK not installed.${NC}"
    echo -e "${YELLOW}This test requires MCP SDK to be pre-installed.${NC}"
    echo -e "${YELLOW}Please install it manually with one of:${NC}"
    echo -e "${YELLOW}  - pip install \"mcp[cli]\"${NC}"
    echo -e "${YELLOW}  - uv pip install \"mcp[cli]\"${NC}"
    echo -e "${YELLOW}Note: MCP SDK requires Python 3.10 or higher.${NC}"
    echo
    echo -e "${YELLOW}Continuing anyway for demonstration purposes...${NC}"
fi

# Note about colorama (used for colored output)
echo -e "${YELLOW}Note: For colored output, you can install colorama manually with: uv pip install colorama${NC}"
# We don't try to install it automatically as it's optional and might fail

# Ensure PYTHONPATH includes the project root
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Set up logging directory
mkdir -p logs

# Run the test client
echo -e "${BLUE}Running MCP sample project test...${NC}"
python tests/test_sample_project.py "$@" 2>&1 | tee logs/sample_project_test_$(date +%Y%m%d_%H%M%S).log

# Return the exit code from the tests
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Sample project test completed successfully!${NC}"
else
    echo -e "${RED}Sample project test completed with errors. Exit code: $EXIT_CODE${NC}"
fi

echo -e "${YELLOW}Check the log file for details and sample project created for manual inspection.${NC}"

# Make the script executable
chmod +x tests/test_sample_project.py

exit $EXIT_CODE
