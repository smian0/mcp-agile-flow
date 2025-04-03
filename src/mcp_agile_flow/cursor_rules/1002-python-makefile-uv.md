---
description: Standardize Python project management using UV for dependency management and Makefiles for automation to ensure consistent builds, tests, and deployments
globs: null
alwaysApply: false
---

# Python Project Management with UV and Makefiles

## Context
- When working with Python projects that require consistent builds and dependency management
- When setting up environments, installing dependencies, or running Python scripts
- When project requires consistent, reproducible environments across team members
- When automating build, test, or deployment processes for Python projects
- When discovering missing dependencies during development or testing
- When standardizing Python project workflows across an organization

## Requirements
- Use pyproject.toml as the primary dependency definition file
- IMMEDIATELY update pyproject.toml when any new dependency is discovered
- Use UV for all virtual environment creation and package management
- Use Makefiles to standardize and automate common project tasks
- Create Makefile targets that wrap UV commands for consistency
- Structure Makefiles with clear sections for setup, build, test, and quality
- Ensure all Python execution happens through UV
- Document both UV and Makefile usage in README for new contributors
- Combine code quality targets into a single `quality` target
- Use Makefile to enforce consistent project workflows

## Examples
<example>
# Proper Makefile structure for Python projects using UV

```makefile
# Python project management with UV
PYTHON = uv run python
VENV_DIR = .venv

.PHONY: all setup clean test quality lint format type-check run help

#################################################
# DEFAULT TARGET
#################################################
all: setup test quality
	@echo "✅ Project verified successfully!"

help:
	@echo "Available commands:"
	@echo "  make setup      - Create virtualenv and install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make quality    - Run linting, formatting and type checking"
	@echo "  make run        - Run the application"
	@echo "  make clean      - Remove build artifacts and virtualenv"

#################################################
# SETUP TARGETS
#################################################
setup: $(VENV_DIR)
	@echo "✅ Project setup complete"

$(VENV_DIR):
	@echo "🔧 Creating virtual environment using UV"
	uv venv $(VENV_DIR)
	@echo "📦 Installing dependencies from pyproject.toml"
	uv pip install -e .
	@echo "📦 Installing dev dependencies"
	uv pip install -e ".[dev]"

clean:
	@echo "🧹 Cleaning up build artifacts"
	rm -rf build/ dist/ *.egg-info/ .coverage .pytest_cache/ __pycache__/ .ruff_cache/
	@echo "🧹 Removing virtual environment"
	rm -rf $(VENV_DIR)

#################################################
# DEPENDENCY MANAGEMENT
#################################################
lock:
	@echo "🔒 Generating lock file"
	uv pip compile pyproject.toml -o uv.lock

add-dep:
	@echo "📦 Adding dependency"
	uv pip install $(pkg) --update-pyproject

add-dev-dep:
	@echo "📦 Adding dev dependency"
	uv pip install $(pkg) --update-pyproject --dev

#################################################
# QUALITY TARGETS
#################################################
quality: lint format type-check
	@echo "✅ All quality checks passed!"

lint:
	@echo "🔍 Running linter"
	uv run -m ruff check .

format:
	@echo "✨ Running formatter"
	uv run -m ruff format .

type-check:
	@echo "🔍 Running type checker"
	uv run -m mypy .

#################################################
# TEST TARGETS
#################################################
test:
	@echo "🧪 Running tests"
	uv run -m pytest

test-cov:
	@echo "🧪 Running tests with coverage"
	uv run -m pytest --cov=src --cov-report=term --cov-report=html

#################################################
# RUN TARGETS
#################################################
run:
	@echo "🚀 Running application"
	uv run -m my_module

serve:
	@echo "🚀 Starting server"
	uv run -m uvicorn my_module.server:app --reload --port 8000
```

# Example pyproject.toml with clear dependency definitions

```toml
[project]
name = "my-python-project"
version = "0.1.0"
description = "A Python project using UV and Makefiles"
requires-python = ">=3.9"
dependencies = [
    # Always use >= for minimum version constraints
    "fastapi>=0.95.0",  # NEVER lower this version requirement
    "uvicorn>=0.21.1",  # Only increase version numbers when updating
    "pydantic>=2.0.0",  # Maintain version constraints when modifying
]

[project.optional-dependencies]
dev = [
    # Development dependencies follow the same version rules
    "pytest>=7.3.1",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

# Example of properly updating a dependency version
# Original: "pydantic>=2.0.0"
# Correct update: "pydantic>=2.1.0"  # Increasing minimum version
# INCORRECT update: "pydantic>=1.9.0"  # NEVER decrease minimum version

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

# Project README section for development setup

```markdown
## Development Setup

This project uses UV for dependency management and Makefiles for automation.

### Prerequisites

- Install UV: `pip install uv`

### Getting Started

1. Clone the repository
2. Run `make setup` to create a virtual environment and install dependencies
3. Run `make test` to ensure everything is working correctly

### Common Commands

- `make help` - Show available commands
- `make setup` - Set up virtual environment and install dependencies
- `make test` - Run tests
- `make quality` - Run lint, format, and type checks
- `make run` - Run the application
- `make add-dep pkg=package-name` - Add a new dependency
- `make add-dev-dep pkg=dev-package-name` - Add a new dev dependency

### Dependency Management

When adding or updating dependencies:
- NEVER lower version requirements of existing dependencies in pyproject.toml
- Always specify minimum version constraints with `>=` syntax
- When updating dependencies, maintain or increase version requirements
```

# Example workflow showing consistent usage

1. Clone a new Python project:
   ```bash
   git clone git@github.com:example/python-project.git
   cd python-project
   ```

2. Set up the project environment:
   ```bash
   make setup
   ```

3. Discover a missing dependency during development:
   ```bash
   make add-dep pkg=requests
   ```

4. Run tests to ensure everything works:
   ```bash
   make test
   ```

5. Check code quality:
   ```bash
   make quality
   ```

6. Run the application:
   ```bash
   make run
   ```
</example>

<example type="invalid">
# Don't use pip directly or without Makefile targets
pip install -r requirements.txt

# Don't run Python directly without UV
python -m my_module
python script.py

# Don't add dependencies without updating pyproject.toml
import requests  # Not in pyproject.toml

# Don't use inconsistent environment setup
python -m venv env
pip install -e .

# Don't create scripts that duplicate Makefile functionality
# script.sh
#!/bin/bash
python -m venv .venv
pip install -r requirements.txt
pip install -e .
python -m pytest

# Don't bypass the Makefile for standard operations
uv venv .venv
uv pip install -e .
uv run -m pytest

# Don't use setup.py without pyproject.toml
setup(
    name="my-project",
    install_requires=["fastapi", "uvicorn"],
)

# Don't have incomplete Makefiles missing UV integration
```makefile
test:
	python -m pytest  # Should use uv run -m pytest

lint:
	flake8 .  # Should use uv run -m flake8

setup:
	python -m venv .venv  # Should use uv venv .venv
	pip install -r requirements.txt  # Should use uv pip install -e .
```

# Don't use disorganized Makefiles without clear sections and documentation
```makefile
setup:
	uv venv .venv
test:
	uv run -m pytest
lint:
	uv run -m ruff check .
# Missing documentation and organization
```
</example>

## Critical Rules
- ALWAYS use pyproject.toml as the primary dependency definition file
- ALWAYS wrap UV commands in Makefile targets for consistent execution
- NEVER run Python directly, ALWAYS use `uv run` through Makefile targets
- IMMEDIATELY update pyproject.toml when discovering any missing dependency using `make add-dep pkg=package-name`
- NEVER import or use a package that isn't declared in pyproject.toml
- NEVER lower version requirements of dependencies already specified in pyproject.toml unless absolutely necessary and fully tested
- Create a comprehensive Makefile with clear sections for setup, dependencies, quality, tests, and execution
- Document all Makefile targets with clear, helpful comments
- Add a `help` target that lists all available commands
- Combine all code quality tasks (lint, format, type-check) into a single `quality` target for convenience
- Include both UV and Makefile setup instructions in the project README
- Ensure core Makefile targets (`setup`, `test`, `quality`, `run`) are available in all Python projects
- Use descriptive output with visual indicators (emojis) in Makefile targets
- Add a `lock` target that generates a lockfile using `uv pip compile` for deterministic builds
- Ensure the `setup` target properly creates a virtual environment and installs all dependencies including dev dependencies
- Include separate targets for adding runtime (`add-dep`) and development (`add-dev-dep`) dependencies
- When updating dependencies, always maintain or increase version constraints, never decrease them
- In CI/CD pipelines, use the same Makefile targets to ensure consistency between development and CI environments
