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

## Requirements
- Enable verbose output logging for all test runs
- Display input data, actual output, and expected output in visually distinct formats
- Use color coding when available to distinguish between different types of data
- Include visual indicators for success/failure states
- Employ tables, formatted JSON, and other visual structures to improve readability
- Add clear visual separation between test cases
- Implement rich diff displays for failed assertions
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

✅ Using Rich for advanced formatting:
```python
def test_with_rich_output():
    """Test with rich visual output."""
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
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
    
    assert result == 6
```
</example>

<example type="invalid">
❌ Test without visual outputs:
```python
def test_function():
    result = my_function(1, 2)
    assert result == 3
```

❌ Poor data presentation:
```python
def test_api_response():
    response = api_call()
    print(response)  # Dumps a complex nested structure without formatting
    assert response["status"] == "success"
```

❌ Using libraries without adding them to requirements:
```python
# This will fail if rich is not installed
from rich import print as rich_print
rich_print("[bold]Test output[/bold]")
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