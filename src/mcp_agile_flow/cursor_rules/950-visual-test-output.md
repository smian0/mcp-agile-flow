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
- Add clear visual separation between test cases using panels with descriptive titles
- Implement rich diff displays for failed assertions
- Group tests logically by category or functionality
- Provide category-based summaries at the end of test runs
- Include line numbers in test output for easier navigation in the IDE
- Use file:line::Class.test_name format for test identifiers
- Include both test descriptions and test outputs within the same panel for improved clarity
- Display actual outputs directly below expected outputs for easier comparison
- Use check marks (✅) or X marks (❌) as visual indicators for pass/fail status
- Install necessary visualization libraries in project dependencies:
  - `rich`: For colored, formatted console output with tables and panels
  - `tabulate`: For simple ASCII tables when rich is not available
  - `pytest-clarity`: For improved assertion failure messages
  - `pytest-sugar`: For progress visualization during test runs

## Test Environment Setup
```python
# pyproject.toml dependency section
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

## Standard Test Case Panel Template

Create consistent test description panels for improved readability, using this pattern:

```python
# In your run_tests.py or similar file
def print_test_descriptions(test_category):
    """Print detailed descriptions of test scenarios in a category."""
    # Example for a single test case panel
    console.print(Panel(
        "[bold]Test: {Test Name}[/bold]\n\n"
        "{Descriptive paragraph explaining what this test verifies and why it's important.}\n\n"
        "[dim]Expected outcomes:[/dim]\n"
        "• {Expected outcome 1}\n"
        "• {Expected outcome 2}\n"
        "• {Expected outcome 3}\n\n"
        "[dim cyan]Test Output:[/dim cyan]\n"
        "{Include actual test output here with relevant details}\n"
        "→ {Specific test output line 1} ✅\n"
        "→ {Specific test output line 2} ✅\n"
        "→ {Specific test output line 3} ✅",
        title="Test Case {Number}",
        border_style="blue",  # Use different colors for different test categories
        padding=(1, 2)
    ))
```

## Practical Test Case Panel Examples

### Example: API Test Panel
```python
console.print(Panel(
    "[bold]Test: API Authentication Flow[/bold]\n\n"
    "This test verifies that the API authentication process correctly validates credentials "
    "and returns appropriate tokens for valid users while rejecting invalid credentials.\n\n"
    "[dim]Expected outcomes:[/dim]\n"
    "• Valid credentials receive a 200 response with auth token\n"
    "• Invalid credentials receive a 401 response\n"
    "• Malformed requests receive a 400 response\n\n"
    "[dim cyan]Test Output:[/dim cyan]\n"
    "Valid Credentials Test:\n"
    "→ Request: POST /auth {username: 'valid_user', password: '********'}\n"
    "→ Response: 200 {token: 'eyJhbGc...', expires_in: 3600} ✅\n\n"
    "Invalid Credentials Test:\n"
    "→ Request: POST /auth {username: 'invalid_user', password: '********'}\n"
    "→ Response: 401 {error: 'Invalid credentials'} ✅\n\n"
    "Malformed Request Test:\n"
    "→ Request: POST /auth {bad_field: 'value'}\n"
    "→ Response: 400 {error: 'Missing required fields'} ✅",
    title="Test Case 1",
    border_style="green",
    padding=(1, 2)
))
```

### Example: Data Processing Test Panel
```python
console.print(Panel(
    "[bold]Test: CSV Data Transformation[/bold]\n\n"
    "This test verifies that the data transformation pipeline correctly processes CSV data, "
    "applying all required transformations and generating the expected output format.\n\n"
    "[dim]Expected outcomes:[/dim]\n"
    "• Headers are properly normalized\n"
    "• Date columns are converted to ISO format\n"
    "• Numerical values are properly formatted\n"
    "• Empty cells are handled appropriately\n\n"
    "[dim cyan]Test Output:[/dim cyan]\n"
    "Header Normalization:\n"
    "→ Input: ['First Name', 'Last Name', 'DOB']\n"
    "→ Output: ['first_name', 'last_name', 'dob'] ✅\n\n"
    "Date Conversion:\n"
    "→ Input: '12/31/2023'\n"
    "→ Output: '2023-12-31' ✅\n\n"
    "Numerical Formatting:\n"
    "→ Input: '1,234.56'\n"
    "→ Output: 1234.56 ✅\n\n"
    "Empty Cell Handling:\n"
    "→ Input: ['', None, 'N/A']\n"
    "→ Output: [None, None, None] ✅",
    title="Test Case 2",
    border_style="blue",
    padding=(1, 2)
))
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

# Helper to display test input data
def display_input(title, data):
    """Display input data in a visually distinct format."""
    console.print(Panel(
        f"{data}",
        title=f"📥 {title}",
        border_style="cyan",
        padding=(1, 1)
    ))

# Helper to display test output with expected values
def display_output(title, actual, expected=None):
    """Display output data with comparison to expected values."""
    panel_content = f"{actual}"
    if expected is not None:
        panel_content += f"\n\n[bold]Expected:[/bold]\n{expected}"
        # Add visual match indicator
        matches = actual == expected
        indicator = "✅ MATCH" if matches else "❌ MISMATCH"
        style = "green" if matches else "red"
        panel_content += f"\n\n[{style}]{indicator}[/{style}]"
    
    console.print(Panel(
        panel_content,
        title=f"📤 {title}",
        border_style="green",
        padding=(1, 1)
    ))

# Helper to display test summary with results
def display_test_summary(test_name, results):
    """Display a summary of the test case with results."""
    console.print(Panel(
        results,
        title=f"📋 {test_name} Summary",
        border_style="blue",
        padding=(1, 1)
    ))
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

# Run tests with descriptions and results in panels
test-with-descriptions:
	@echo "🧪 Running tests with detailed descriptions and results..."
	$(PYTHON) -m pytest $(TEST_FLAGS) --with-descriptions both
```

## Examples
<example>
✅ Test description panel with embedded output:
```python
def print_test_descriptions(test_category):
    console.print(Panel(
        "[bold]Test: Extract Screen Info from Filename[/bold]\n\n"
        "This test verifies that the system can correctly parse P123 screen filenames "
        "to extract the screen ID and date components. The filename format is expected "
        "to be 'P123_Screen_NNNNNN_YYYYMMDD.csv' where NNNNNN is the screen ID and "
        "YYYYMMDD is the date.\n\n"
        "[dim]Expected outcomes:[/dim]\n"
        "• Successfully extract screen ID and date from valid filenames\n"
        "• Handle typical screen filename formats properly\n"
        "• Return None values for invalid filename formats\n\n"
        "[dim cyan]Test Output:[/dim cyan]\n"
        "Test Case 1: 'P123_Screen_100000_20220101.csv'\n"
        "→ Extracted: screen_id='100000', date='2022-01-01' ✅\n\n"
        "Test Case 2: 'P123_Screen_987654_20221231.csv'\n"
        "→ Extracted: screen_id='987654', date='2022-12-31' ✅\n\n"
        "Test Case 3: 'invalid_filename.csv'\n"
        "→ Extracted: screen_id=None, date=None ✅",
        title="Test Case 1",
        border_style="blue",
        padding=(1, 2)
    ))
```

✅ Standard pytest with verbose output and embedded results:
```python
@pytest.mark.parametrize("input_value, expected", [
    ({"symbol": "AAPL", "metric": "price"}, 150.25),
    ({"symbol": "GOOG", "metric": "price"}, 2100.50),
])
def test_get_stock_metric(input_value, expected, mock_service, display_test_summary):
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
    
    # Add summarized results for the output panel
    test_output = (
        f"Input: {input_value['symbol']}, {input_value['metric']}\n"
        f"→ Expected: {expected}\n"
        f"→ Actual: {result}\n"
        f"→ Result: {'✅ MATCH' if result == expected else '❌ MISMATCH'}"
    )
    display_test_summary("Stock Metric Test", test_output)
        
    assert result == expected
```

✅ Using Rich for advanced formatting with test grouping and embedded results:
```python
@pytest.mark.api
def test_with_grouped_output(display_test_summary):
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
    test_output = (
        f"Input: {test_data}\n"
        f"→ Expected Sum: 6\n"
        f"→ Actual Sum: {result}\n"
        f"→ Result: {'✅ MATCH' if result == 6 else '❌ MISMATCH'}"
    )
    display_test_summary("API Response Test", test_output)
    
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

❌ Testing without embedded outputs and descriptions:
```python
# Missing description panel with integrated outputs
def test_feature():
    assert feature_function() == expected_result
```

❌ Separating test descriptions from their results:
```python
# Putting descriptions and results in different places makes it harder to follow
print("Test descriptions:")
print("Test 1: Tests feature A")
print("Test 2: Tests feature B")

# ... later in the output ...
print("Test results:")
print("Test 1: PASSED")
print("Test 2: FAILED")
```
</example>

## Critical Rules
- ALWAYS create test panels with both description and embedded output
- ALWAYS organize test output by category or functionality
- ALWAYS include clear test case descriptions explaining purpose and significance
- ALWAYS use visual indicators like ✅/❌ to show success/failure status
- ALWAYS display expected and actual results together for easy comparison
- ALWAYS use color coding to distinguish between different types of information
- Include full explanation, expected outcomes, and actual results in each test panel
- Format test output with line numbers for better IDE navigation
- Use rich library for consistent panel formatting and color schemes
- Maintain consistent color schemes across similar test categories
- Include context about why the test matters, not just what it tests
- Embed input data, output results, and comparisons within the same panel 