# Contributing to MCP Agile Flow

We love your input! We want to make contributing to MCP Agile Flow as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

### Issues

We use GitHub issues to track public bugs. Report a bug by opening a new issue. 

### Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-agile-flow.git
cd mcp-agile-flow

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install development dependencies
uv pip install -e ".[dev]"
```

## Testing

Run the test suite with:

```bash
python -m pytest
```

## Coding Style

* We use PEP 8 style guidelines
* Use type hints where possible
* Include docstrings for all public functions and classes

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 