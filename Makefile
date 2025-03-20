# MCP Agile Flow - Makefile
# -------------------------

.PHONY: help venv install test test-coverage test-kg run-server setup-cursor clean clean-all quality all

# Configuration
# -------------
VENV_DIR := .venv
VENV_ACTIVATE := $(VENV_DIR)/bin/activate
UV := uv
PACKAGE_NAME := mcp_agile_flow
SOURCE_DIR := src
TESTS_DIR := tests
PYTEST_FLAGS := -v

# Help target
# -----------
help:
	@echo "MCP Agile Flow - Make Targets"
	@echo "---------------------------"
	@echo "help:             Show this help message"
	@echo "venv:             Create virtual environment"
	@echo "install:          Install package"
	@echo "test:             Run tests with detailed debug output"
	@echo "test-coverage:    Run tests with coverage report"
	@echo "test-kg:          Run only the knowledge graph creation test"
	@echo "run-server:       Run the MCP Agile Flow server"
	@echo "setup-cursor:     Set up Cursor MCP integration"
	@echo "clean:            Remove build artifacts and cache files"
	@echo "clean-all:        Remove build artifacts, cache files, and virtual environment"
	@echo "quality:          Run all code quality checks (formatting, linting, type checking)"
	@echo "all:              Install and run tests"

# Virtual environment
# ------------------
venv:
	$(UV) venv $(VENV_DIR) --python=$(shell which python3)

# Installation
# ------------
install: venv
	$(UV) pip install -e .

# Testing
# -------
test: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Running tests with debug output..."
	$(UV) run pytest $(PYTEST_FLAGS) -s --show-capture=all --tb=short $(TESTS_DIR)

test-coverage: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Running tests with coverage..."
	$(UV) run pytest $(PYTEST_FLAGS) --cov=$(PACKAGE_NAME) --cov-report=term --cov-report=html $(TESTS_DIR)

test-kg: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Running knowledge graph test..."
	$(UV) run python -c "from tests.test_mcp_via_agno_agent import test_fastapi_project_knowledge_graph; test_fastapi_project_knowledge_graph()"

# Server execution
# ---------------
run-server: install
	$(UV) run run_mcp_server.py

# Setup
# -----
setup-cursor: install
	$(UV) run setup_cursor_mcp.py

# Cleaning
# --------
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf **/__pycache__/
	rm -rf **/.pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

# Remove everything including the virtual environment
clean-all: clean
	rm -rf $(VENV_DIR)

# Code quality
# ------------
# Combined quality command that runs all checks in one go
quality: venv
	@echo "Installing development dependencies..."
	$(UV) pip install -e ".[test]"
	$(UV) pip install -e .
	@echo "Running code formatting with Black..."
	$(UV) run black $(SOURCE_DIR) $(TESTS_DIR)
	@echo "Running code linting with Flake8..."
	$(UV) run flake8 $(SOURCE_DIR) $(TESTS_DIR)
	@echo "Running type checking with MyPy..."
	$(UV) run mypy $(SOURCE_DIR)

# Default target
# --------------
all: install test