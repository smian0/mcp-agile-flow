---
description: Use when asked to SET UP DEAD CODE ANALYSIS or FIND UNUSED CODE to implement Vulture for Python projects
globs: **/*.py, **/*.toml, **/Makefile
alwaysApply: false
---

# Vulture Dead Code Analysis Setup

## Context
- When the user wants to identify unused/dead code in Python projects
- When setting up code quality tools for Python projects
- When implementing CI/CD for code quality

## Requirements
- Install Vulture as a dev dependency
- Create a comprehensive script for dead code analysis
- Generate structured reports (text, HTML, JSON)
- Add Makefile targets for easy execution
- Support different confidence levels for analysis
- Integrate with existing project structure

## Examples

<example>
# Add Vulture as a development dependency in pyproject.toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.1.0",
    "vulture>=2.3",  # For dead code analysis
]

# Create a dead-code analysis script at scripts/quality/analyze_dead_code.py
#!/usr/bin/env python3
"""
Dead Code Analyzer using Vulture
"""
import subprocess
import sys
from pathlib import Path

def run_analysis(src_dir="src", min_confidence=60):
    result = subprocess.run(
        ["vulture", src_dir, f"--min-confidence={min_confidence}"],
        capture_output=True, text=True
    )
    print(result.stdout)
    return result.returncode

if __name__ == "__main__":
    run_analysis(sys.argv[1] if len(sys.argv) > 1 else "src")

# Add to Makefile
dead-code:
	@echo "Running dead code analysis..."
	python scripts/quality/analyze_dead_code.py
</example>

<example type="invalid">
# Installing Vulture globally (should be project-specific)
pip install vulture

# Running without configuration
vulture .

# No structured reports or integration with build system
# No confidence level management
</example>

## Critical Rules
  - Always install Vulture as a dev dependency, not a main dependency
  - Use confidence levels to manage false positives (60% for all, 100% for certain cases)
  - Generate both human-readable (HTML) and machine-readable (JSON) reports
  - Include the analysis in the CI/CD pipeline for automated checks
  - Provide whitelist mechanism for handling false positives
  - Implement the solution in a way that works with the existing build system (pip, poetry, etc.)