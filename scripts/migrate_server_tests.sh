#!/bin/bash
# Utility script to run tests against both server implementations
# and compare results to ensure they're equivalent.

set -e # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_FILE=""
VERBOSE=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -f|--file)
            TEST_FILE="$2"
            shift
            shift
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -f, --file FILE    Run tests from specific file"
            echo "  -v, --verbose      Run tests in verbose mode"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

PYTEST_ARGS=""
if [ $VERBOSE -eq 1 ]; then
    PYTEST_ARGS="-v"
fi

# Function to run tests with a specific server implementation
run_tests() {
    implementation=$1
    test_file=$2
    
    echo -e "${BLUE}Running tests with $implementation implementation...${NC}"
    
    if [ "$implementation" == "FastMCP" ]; then
        export MCP_USE_FASTMCP=true
    else
        export MCP_USE_FASTMCP=false
    fi
    
    if [ -n "$test_file" ]; then
        python -m pytest $test_file $PYTEST_ARGS
    else
        # Run all adapter-based tests
        python -m pytest tests/test_*_adapter.py $PYTEST_ARGS
    fi
    
    result=$?
    
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}Tests passed with $implementation implementation${NC}"
    else
        echo -e "${RED}Tests failed with $implementation implementation${NC}"
        exit 1
    fi
    
    return $result
}

# Run tests with both implementations
echo -e "${YELLOW}=============== TESTING BOTH SERVER IMPLEMENTATIONS ===============${NC}"
echo -e "${YELLOW}First testing with legacy server implementation...${NC}"
run_tests "Legacy" "$TEST_FILE"

echo -e "\n${YELLOW}Now testing with FastMCP implementation...${NC}"
run_tests "FastMCP" "$TEST_FILE"

echo -e "\n${GREEN}ALL TESTS PASSED WITH BOTH IMPLEMENTATIONS! The implementations are equivalent.${NC}"

# Check if any other adapter-based tests need to be created
echo -e "\n${YELLOW}Checking for tests that need to be migrated to use the adapter...${NC}"

# Get all test files
all_test_files=$(find tests -name "test_*.py" | grep -v "_adapter.py" | sort)
adapter_test_files=$(find tests -name "test_*_adapter.py" | sort)

# Extract base names for adapter tests
adapter_base_names=()
for file in $adapter_test_files; do
    base_name=$(basename "$file" | sed 's/_adapter.py$//')
    adapter_base_names+=("$base_name")
done

# Check which test files don't have adapter versions
for file in $all_test_files; do
    base_name=$(basename "$file" | sed 's/.py$//')
    
    # Skip files that start with test_ but aren't actual test files
    if [[ ! -f "$file" || ! "$file" =~ test_ ]]; then
        continue
    fi
    
    # Check if this test has an adapter version
    has_adapter=0
    for adapter_base in "${adapter_base_names[@]}"; do
        if [[ "$base_name" == "$adapter_base" ]]; then
            has_adapter=1
            break
        fi
    done
    
    if [[ $has_adapter -eq 0 ]]; then
        # Check if this file uses handle_call_tool from server.py
        if grep -q "handle_call_tool" "$file"; then
            echo -e "${YELLOW}Test file '$file' uses handle_call_tool but doesn't have an adapter version.${NC}"
        fi
    fi
done

echo -e "\n${GREEN}Migration test completed.${NC}" 