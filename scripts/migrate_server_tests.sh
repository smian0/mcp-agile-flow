#!/bin/bash
# Utility script to run tests against the FastMCP implementation.

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

# Function to run tests with FastMCP
run_tests() {
    test_file=$1
    
    echo -e "${BLUE}Running tests with FastMCP implementation...${NC}"
    
    if [ -n "$test_file" ]; then
        python -m pytest $test_file $PYTEST_ARGS
    else
        # Run all adapter-based tests
        python -m pytest tests/test_*.py $PYTEST_ARGS
    fi
    
    result=$?
    
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}Tests passed with FastMCP implementation${NC}"
    else
        echo -e "${RED}Tests failed with FastMCP implementation${NC}"
        exit 1
    fi
    
    return $result
}

# Run tests
echo -e "${YELLOW}=============== RUNNING TESTS ===============${NC}"
run_tests "$TEST_FILE"

echo -e "\n${GREEN}ALL TESTS PASSED! The implementation is working correctly.${NC}" 