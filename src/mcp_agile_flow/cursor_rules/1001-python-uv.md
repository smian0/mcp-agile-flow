---
description: Use UV for all Python project operations to ensure fast, consistent dependency management and always maintain pyproject.toml as the source of truth
globs: **/*.py, **/pyproject.toml, **/requirements.txt
alwaysApply: false
---

# Python UV Lifecycle Management

## Context
- When working with Python projects
- When setting up environments, installing dependencies, or running Python scripts
- When project requires consistent, reproducible environments
- Applied to any Python codebase that benefits from modern, fast package management
- When discovering missing dependencies during development or testing

## Requirements
- Use pyproject.toml as the primary dependency definition file
- IMMEDIATELY update pyproject.toml when any new dependency is discovered
- Use UV for all virtual environment creation
- Use UV for all package installation operations 
- Use UV for executing Python scripts
- Prefer UV's lockfile approach for deterministic builds
- Document UV setup in README for new contributors

## Examples
<example>
# Creating a virtual environment
uv venv .venv

# Installing dependencies from pyproject.toml
uv pip install -e .

# Running Python code
uv run -m my_module
uv run script.py

# Installing a package and updating pyproject.toml
uv pip install package-name --update-pyproject

# When discovering a missing dependency, immediately add it to pyproject.toml
# First, add to pyproject.toml:
[project]
dependencies = [
    # ...existing dependencies...
    "newly-discovered-package>=1.0.0",
]

# Then install with:
uv pip install -e .

# Using a lockfile for deterministic builds
uv pip compile pyproject.toml -o uv.lock

# Running with arguments
uv run -m fastmcp_server --mode http --port 8000

# Defining dependencies in pyproject.toml
[project]
name = "my-project"
version = "0.1.0"
dependencies = [
    "fastapi>=0.95.0",
    "uvicorn>=0.21.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3.1",
    "black>=23.3.0",
]
</example>

<example type="invalid">
# Don't use standard venv
python -m venv env  

# Don't use pip directly
pip install -r requirements.txt

# Don't run Python directly
python -m my_module
python script.py

# Don't use pip for dependency resolution
pip install package-name

# Don't install packages without updating pyproject.toml
uv pip install package-name  # Missing --update-pyproject flag

# Don't use packages without adding them to pyproject.toml first
import new_package  # Package not declared in pyproject.toml

# Don't use setup.py or requirements.txt as primary dependency files
setup(
    name="my-project",
    install_requires=["fastapi", "uvicorn"],
)
</example>

## Critical Rules
- ALWAYS use pyproject.toml as the primary dependency definition file
- ALWAYS IMMEDIATELY update pyproject.toml when discovering any missing dependency
- NEVER import or use a package that isn't declared in pyproject.toml
- When discovering a missing dependency during development, add it to pyproject.toml FIRST, then install
- Use `uv pip install --update-pyproject` when adding new dependencies to automatically update pyproject.toml
- ALWAYS use `uv venv` for virtual environment creation instead of `python -m venv`
- ALWAYS use `uv pip` instead of `pip` for package management
- ALWAYS use `uv run` instead of direct `python` invocation
- Document UV installation requirements in project README
- Include UV in CI/CD pipelines for testing and deployment
- Prefer `uv.lock` for deterministic dependency resolution
- Avoid using requirements.txt except for compatibility or when generating from pyproject.toml
- After implementing code that requires new dependencies, VERIFY that all dependencies are properly documented in pyproject.toml