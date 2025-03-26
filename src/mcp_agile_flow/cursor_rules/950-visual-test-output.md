---
description: Use visual output formatting when writing or running tests to improve readability and debugging
globs: "**/*test*.py"
alwaysApply: false
---

# Visual Test Output Guidelines

## Context
- When writing or running test code
- When debugging test failures
- When reviewing test results
- When presenting test outcomes to visual learners
- When organizing tests into logical groups

## Requirements
- Enable verbose output logging for all test runs
- Display input data, actual output, and expected output in visually distinct formats
- Use color coding when available to distinguish between different types of data
- Include visual indicators for success/failure states
- Employ tables, formatted JSON, and other visual structures to improve readability
- Add clear visual separation between test cases
- Implement rich diff displays for failed assertions
- Group tests logically by category or functionality
- Provide category-based summaries at the end of test runs
- Include line numbers in test output for easier navigation in the IDE
- Use file:line::Class.test_name format for test identifiers
- Install necessary visualization libraries in project dependencies:
  - `rich`: For colored, formatted console output with tables and panels
  - `tabulate`: For simple ASCII tables when rich is not available
  - `pytest-clarity`: For improved assertion failure messages
  - `pytest-sugar`: For progress visualization during test runs

## Test Environment Setup
```python
# requirements.txt or pyproject.toml dependency section
pytest>=7.0.0
pytest-xdist  # For parallel test execution
rich>=12.0.0  # For visual output formatting
pytest-clarity  # For better assertion failure messages
pytest-sugar  # For progress visualization
tabulate  # For simple table output

# Alternative with pip
# pip install pytest rich pytest-clarity pytest-sugar tabulate

# Alternative with uv
# uv pip install pytest rich pytest-clarity pytest-sugar tabulate
```

## Test Grouping Setup

Create a pytest conftest.py file with group-aware hooks:

```python
# conftest.py
import pytest
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from collections import defaultdict
import time

# Initialize rich console
console = Console()

# Dictionary to store test results by category
test_results = defaultdict(list)

# Mapping of test file names to categories
file_to_category = {
    "test_api.py": "API",
    "test_cache.py": "Cache",
    "test_integration.py": "Integration",
    # Add more mappings as needed
}

# Track the current category
current_category = None
current_category_start_time = None
current_category_tests = []

@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """Add markers for test categories."""
    config.addinivalue_line("markers", "api: API related tests")
    config.addinivalue_line("markers", "cache: Cache related tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    # Add more category markers as needed

# Store item to category mapping
item_to_category = {}

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Set up test run and print test group headers."""
    global current_category, current_category_start_time, current_category_tests
    
    # Get test file name
    file_name = item.fspath.basename
    category = file_to_category.get(file_name, "Other")
    
    # Store the category with the item for later use
    item_to_category[item.nodeid] = category
    
    # Check if we need to print a category header
    if current_category != category:
        # If there was a previous category, print its summary
        if current_category is not None:
            print_category_summary(current_category, current_category_tests)
            current_category_tests = []
        
        console.print()
        console.print(Panel(f"[bold blue]Starting {category} Tests[/bold blue]", 
                           border_style="blue", expand=False))
        current_category = category
        current_category_start_time = time.time()
        
    # Add the current test to the category tests
    current_category_tests.append(item.nodeid)

@pytest.hookimpl(trylast=True)
def pytest_runtest_logreport(report):
    """Process test results and categorize them."""
    if report.when == "call":
        # Get the test category from stored mapping
        category = item_to_category.get(report.nodeid, "Other")
        test_name = report.nodeid.split("::")[-1]
        
        # Store result
        test_results[category].append((test_name, report.passed))

@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print summary of test results by category."""
    global current_category, current_category_tests
    
    # Print summary for the last category if it exists
    if current_category is not None and current_category_tests:
        print_category_summary(current_category, current_category_tests)
    
    console.print("\n[bold]Overall Test Results Summary by Category[/bold]")
    
    all_passed = True
    
    for category, results in test_results.items():
        table = Table(title=f"{category} Tests Summary", show_header=True, header_style="bold")
        table.add_column("Test Name")
        table.add_column("Result")
        
        category_passed = True
        
        for test_name, passed in results:
            result_text = "✅ PASSED" if passed else "❌ FAILED"
            result_style = "green" if passed else "red"
            table.add_row(test_name, f"[{result_style}]{result_text}[/{result_style}]")
            
            if not passed:
                category_passed = False
                all_passed = False
        
        # Add category summary row
        summary_style = "green" if category_passed else "red"
        summary_text = "ALL PASSED" if category_passed else "SOME FAILED"
        table.add_row("[bold]Category Summary[/bold]", f"[bold {summary_style}]{summary_text}[/bold {summary_style}]")
        
        console.print(table)
        console.print()
    
    # Print overall summary
    overall_style = "green" if all_passed else "red"
    overall_text = "ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"
    console.print(Panel(f"[bold {overall_style}]{overall_text}[/bold {overall_style}]", 
                       border_style=overall_style, expand=False))

def print_category_summary(category, test_nodeid_list):
    """Print a summary for the just-completed category."""
    end_time = time.time()
    duration = end_time - current_category_start_time
    
    # Get results just for this category
    category_results = test_results.get(category, [])
    test_count = len(category_results)
    passed_count = sum(1 for _, passed in category_results if passed)
    failed_count = test_count - passed_count
    
    # Only print summary if we have results
    if test_count > 0:
        console.print()
        console.print(Panel(
            f"[bold blue]Completed {category} Tests[/bold blue]\n"
            f"Tests: {test_count} | Passed: [green]{passed_count}[/green] | "
            f"Failed: [red]{failed_count}[/red] | "
            f"Duration: {duration:.2f}s",
            border_style="blue",
            expand=False
        ))
        console.print()

# Helper function to print test group headers
def print_test_group(group_name):
    """Print a visually distinct group header for related tests."""
    console.print()
    console.print(Panel(f"[bold blue]{group_name}[/bold blue]", 
                       border_style="blue", expand=False))
```

## Line Number Display for Tests

Add a script to format test output with line numbers for better IDE navigation:

```python
#!/usr/bin/env python
"""Format test output with line numbers for better IDE navigation."""

import sys
import os
import re
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table

def get_test_class_name(module_path):
    """Get the class name from the test file."""
    test_class_map = {
        'tests/test_cache.py': 'TestCacheLogic',
        'tests/test_data_validation.py': 'TestDataValidation',
        'tests/test_integration.py': 'TestExternalIntegration',
        'tests/test_retry.py': 'TestRetryLogic',
        # Add more mappings as needed
    }
    
    # Use the predefined mapping if available
    rel_path = os.path.relpath(module_path)
    if rel_path in test_class_map:
        return test_class_map[rel_path]
    
    # Otherwise, try to detect class name directly
    try:
        cmd = ['grep', '-n', 'class Test', module_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            for line in result.stdout.splitlines():
                match = re.search(r'class (\w+):', line)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"Error finding class name: {e}", file=sys.stderr)
    
    # Default to None if no class found (for module-level tests)
    return None

def get_test_line_numbers_from_grep(module_path, test_names):
    """Get line numbers for test methods using grep."""
    test_info = {}
    
    try:
        # First try class methods with async def
        cmd = ['grep', '-n', '    async def test_', module_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # If no async tests, try regular class methods
        if result.returncode != 0 or not result.stdout:
            cmd = ['grep', '-n', '    def test_', module_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        # If still nothing, try module-level test functions
        if result.returncode != 0 or not result.stdout:
            cmd = ['grep', '-n', '^def test_', module_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                # Format: "44:    async def test_rate_limit_handling(self):"
                parts = line.split(':', 1)
                if len(parts) < 2:
                    continue
                    
                line_number = int(parts[0])
                line_content = parts[1]
                
                # Extract the test name
                match = re.search(r'(?:async )?def test_(\w+)\(', line_content)
                if match:
                    test_name = match.group(1)
                    if test_name in test_names:
                        test_info[test_name] = line_number
    except Exception as e:
        print(f"Error running grep: {e}", file=sys.stderr)
    
    return test_info

def main():
    """Format test output with line numbers."""
    if len(sys.argv) < 3:
        print("Usage: format_test_output.py <test_file> <category_name> <test_name1> <test_name2> ...", file=sys.stderr)
        sys.exit(1)
    
    test_file = sys.argv[1]
    category_name = sys.argv[2]
    test_names = sys.argv[3:]
    
    # Get test class name from the file
    class_name = get_test_class_name(test_file)
    
    # Get test line numbers using grep
    test_info = get_test_line_numbers_from_grep(test_file, test_names)
    
    # Create a rich console and table
    console = Console()
    table = Table(title=f"{category_name} Tests Summary")
    table.add_column("Test Name", style="cyan")
    table.add_column("Line", style="yellow")
    table.add_column("Result", style="green")
    
    # Add rows to the table
    for test_name in test_names:
        # Get the line number, defaulting to "?" if not found
        line_num = str(test_info.get(test_name, "?"))
        table.add_row(f"test_{test_name}", line_num, "✅ PASSED")
    
    # Create file:line::Class.test_name format strings for IDE navigation
    ide_locations = []
    rel_path = os.path.relpath(test_file)
    for test_name in test_names:
        if test_name in test_info:
            line_number = test_info[test_name]
            # Format with line number directly in the nodeid
            if class_name:
                # Class method test (most common case)
                nodeid = f"{rel_path}:{line_number}::{class_name}.test_{test_name}"
            else:
                # Module-level test function
                nodeid = f"{rel_path}:{line_number}::test_{test_name}"
            ide_locations.append(nodeid)
    
    # Print category summary
    console.print("\n\nOverall Test Results Summary by Category")
    console.print(table)
    console.print("[green]ALL TESTS PASSED[/green]")
    
    # Print locations for IDE navigation
    if ide_locations:
        console.print("\n[bold]Test Locations for IDE Navigation:[/bold]")
        for nodeid in ide_locations:
            console.print(nodeid)

if __name__ == "__main__":
    main()
```

Update your Makefile to use the line number script:

```makefile
# Set up script paths
SCRIPTS_DIR = scripts
FORMAT_TEST_OUTPUT = $(SCRIPTS_DIR)/format_test_output.py

# Run category-specific tests with line numbers
test-api:
	@echo "🧪 Running API tests with visual output..."
	$(PYTHON) -m pytest -v tests/test_api.py
	@$(PYTHON) $(FORMAT_TEST_OUTPUT) tests/test_api.py "API" api_test1 api_test2

test-cache:
	@echo "🧪 Running cache tests with visual output..."
	$(PYTHON) -m pytest -v tests/test_cache.py
	@$(PYTHON) $(FORMAT_TEST_OUTPUT) tests/test_cache.py "Cache" cache_test1 cache_test2

test-integration:
	@echo "🧪 Running integration tests with visual output..."
	$(PYTHON) -m pytest -v tests/test_integration.py
	@$(PYTHON) $(FORMAT_TEST_OUTPUT) tests/test_integration.py "Integration" integration_test1 integration_test2
```

## Makefile Targets for Test Categories

Include these targets in your Makefile:

```makefile
# Run all tests with visual output
test:
	@echo "🧪 Running all tests with visual output..."
	$(PYTHON) -m pytest $(TEST_FLAGS) tests/

# Run category-specific tests
test-api:
	@echo "🧪 Running API tests with visual output..."
	$(PYTHON) -m pytest $(TEST_FLAGS) tests/test_api.py

test-cache:
	@echo "🧪 Running cache tests with visual output..."
	$(PYTHON) -m pytest $(TEST_FLAGS) tests/test_cache.py

test-integration:
	@echo "🧪 Running integration tests..."
	$(PYTHON) -m pytest $(TEST_FLAGS) tests/test_integration.py

# Run all test categories sequentially
test-all: test-api test-cache test-integration
	@echo "✅ All tests complete!"

# Run tests with detailed visual output (disables sugar for better rich output)
test-detailed:
	@echo "🧪 Running tests with detailed visual output..."
	$(PYTHON) -m pytest $(TEST_FLAGS) -p no:sugar --capture=no --no-header tests/
```

## Examples
<example>
✅ Standard pytest with verbose output:
```python
@pytest.mark.parametrize("input_value, expected", [
    ({"symbol": "AAPL", "metric": "price"}, 150.25),
    ({"symbol": "GOOG", "metric": "price"}, 2100.50),
])
def test_get_stock_metric(input_value, expected, mock_service):
    """Test fetching stock metrics."""
    # ARRANGE - Display test inputs
    print(f"\n📥 Input: {json.dumps(input_value, indent=2)}")
    
    # ACT - Run the function being tested
    result = get_stock_metric(input_value["symbol"], input_value["metric"])
    print(f"📤 Output: {json.dumps(result, indent=2)}")
    
    # ASSERT - Compare with expected results
    print(f"🎯 Expected: {json.dumps(expected, indent=2)}")
    
    # Visual comparison
    if result != expected:
        print("❌ DIFFERENCE:")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {result}")
        print(f"  Diff:     {expected - result if isinstance(result, (int, float)) else 'complex diff'}")
    else:
        print("✅ MATCH")
        
    assert result == expected
```

✅ Using Rich for advanced formatting with test grouping:
```python
@pytest.mark.api
def test_with_grouped_output():
    """Test with rich visual output and logical grouping."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from conftest import print_test_group
    
    console = Console()
    
    # Print test group header for related tests
    print_test_group("API Validation Tests")
    
    # Display test header
    console.print(Panel.fit(
        "[bold cyan]TEST: API Response Validation[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
        title="API Test Case",
        subtitle="Testing response format and values"
    ))
    
    # Input data
    test_data = {"id": 123, "values": [1, 2, 3]}
    console.print(Panel(json.dumps(test_data, indent=2), title="📥 Input"))
    
    # Process data
    result = process_data(test_data)
    
    # Output table
    table = Table(title="📊 Results Comparison")
    table.add_column("Type", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Expected", "6")
    table.add_row("Actual", str(result))
    table.add_row("Status", "✅ PASS" if result == 6 else "❌ FAIL")
    
    console.print(table)
    
    # Test Summary Panel
    console.print(Panel.fit(
        f"[bold green]TEST COMPLETED: test_with_grouped_output[/bold green]\n"
        f"✅ Successfully validated API response\n"
        f"- Verified response format\n"
        f"- Confirmed calculation correctness\n"
        f"- Validated expected output",
        border_style="green",
        title="Test Summary",
        subtitle="API Response Test"
    ))
    
    assert result == 6
```

✅ Test output with line numbers for better navigation:
```
Overall Test Results Summary by Category
            Integration Tests Summary            
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━┓
┃ Test Name                  ┃ Line ┃ Result    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━┩
│ test_rate_limit_handling   │ 44   │ ✅ PASSED │
│ test_concurrent_requests   │ 137  │ ✅ PASSED │
│ test_api_latency           │ 231  │ ✅ PASSED │
│ test_market_hours_behavior │ 308  │ ✅ PASSED │
└────────────────────────────┴──────┴───────────┘
ALL TESTS PASSED

Test Locations for IDE Navigation:
tests/test_integration.py:44::TestExternalIntegration.test_rate_limit_handling
tests/test_integration.py:137::TestExternalIntegration.test_concurrent_requests
tests/test_integration.py:231::TestExternalIntegration.test_api_latency
tests/test_integration.py:308::TestExternalIntegration.test_market_hours_behavior
```

✅ Detailed test run with category grouping:
```bash
$ make test-detailed

╭──────────────────────╮
│ Starting API Tests   │
╰──────────────────────╯

╭────────────────────────╮
│ API Validation Tests   │
╰────────────────────────╯

╭─────────── API Test Case ───────────╮
│                                     │
│  TEST: API Response Validation      │
│                                     │
╰─ Testing response format and values─╯

... test details ...

╭─────────────────── Test Summary ──────────────────╮
│ TEST COMPLETED: test_with_grouped_output          │
│ ✅ Successfully validated API response            │
│ - Verified response format                        │
│ - Confirmed calculation correctness               │
│ - Validated expected output                       │
╰──────────────── API Response Test ────────────────╯

╭────────────────────────────────────────────────╮
│ Completed API Tests                            │
│ Tests: 5 | Passed: 5 | Failed: 0 | Duration: 0.5s │
╰────────────────────────────────────────────────╯
```
</example>

<example type="invalid">
❌ Test without visual outputs or grouping:
```python
def test_function():
    result = my_function(1, 2)
    assert result == 3
```

❌ Poor data presentation without categorization:
```python
def test_api_response():
    response = api_call()
    print(response)  # Dumps a complex nested structure without formatting or categories
    assert response["status"] == "success"
```

❌ Disorganized test output without clear grouping:
```
test_function_1: PASSED
test_api_call: PASSED
test_database: FAILED
```

❌ Test output without line numbers:
```
Overall Test Results Summary by Category
            Integration Tests Summary            
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Test Name                  ┃ Result    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ test_rate_limit_handling   │ ✅ PASSED │
│ test_concurrent_requests   │ ✅ PASSED │
│ test_api_latency           │ ✅ PASSED │
│ test_market_hours_behavior │ ✅ PASSED │
└────────────────────────────┴───────────┘
```
</example>

## Critical Rules
- Always enable verbose output for test runs
- Always display test inputs in a clearly formatted way
- Always display actual results in a clearly formatted way
- Always display expected results in a clearly formatted way
- Use visual differences for failed assertions
- Prefer tabular or structured formats for complex data
- Clearly separate different test cases with visual breaks
- Don't rely solely on text-based assertions without visual context
- Consider accessibility when choosing visual representations
- Include custom assertion helpers in test utilities
- Always add visualization libraries to project dependencies
- Use conditional imports for visualization libraries to make tests still run without them
- Document required dependencies in requirements.txt, pyproject.toml, or similar
- Organize tests into logical categories (API, Cache, Integration, etc.)
- Use pytest markers to explicitly categorize tests
- Implement category-based summaries at the end of test runs
- Create clear visual boundaries between test categories
- Add per-test summary panels for key findings and validations
- Include per-category completion summaries with statistics
- Provide both standard and detailed output options in Makefile
- Include line numbers in test output for easier IDE navigation
- Format test identifiers in a consistent path:line::Class.test_name format
- Use grep or similar tools to extract test line numbers reliably
- Support both class-based and module-level test functions 