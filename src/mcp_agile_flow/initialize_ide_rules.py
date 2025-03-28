"""
Initialize IDE Rules Module

This module handles initialization of IDE rules and configurations.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


def initialize_ide_rules(ide: str = "cursor", project_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Initialize IDE rules for a project.

    Args:
        ide: IDE to initialize rules for ("cursor", "windsurf", "cline", "copilot")
        project_path: Optional path to project directory

    Returns:
        Dictionary containing initialization results
    """
    if project_path is None:
        project_path = os.getcwd()

    project_path = Path(project_path)

    # Create rules directory for Cursor
    if ide == "cursor":
        rules_dir = project_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        # Copy default rules from installed package
        src_rules_dir = Path(__file__).parent / "cursor_rules"
        if src_rules_dir.exists():
            for rule_file in src_rules_dir.glob("*.md"):
                shutil.copy2(rule_file, rules_dir)

        # Always create default rules to ensure there are files
        rules = [
            (
                "001-project-basics.md",
                """# Project Basics
- Follow standard project structure
- Use consistent coding style
- Document key decisions""",
            ),
            (
                "002-code-guidelines.md",
                """# Code Guidelines
- Write clear and maintainable code
- Add comprehensive tests
- Keep documentation up to date""",
            ),
            (
                "003-best-practices.md",
                """# Best Practices
- Review code before committing
- Handle errors appropriately
- Optimize performance when needed""",
            ),
        ]

        for filename, content in rules:
            rule_file = rules_dir / filename
            if not rule_file.exists():
                rule_file.write_text(content)

        return {
            "success": True,
            "initialized_rules": True,
            "project_path": str(project_path),
            "rules_directory": str(rules_dir),
            "templates_directory": str(project_path / ".ai-templates"),
            "rules_file": None,
            "message": f"Initialized cursor project in {project_path}",
        }

    # Create rules file for other IDEs
    rules_file = project_path / (
        ".windsurfrules"
        if ide == "windsurf"
        else (
            ".clinerules"
            if ide == "cline"
            else ".github/copilot-instructions.md" if ide == "copilot" else None
        )
    )

    if rules_file is None:
        return {
            "success": False,
            "error": f"Unknown IDE: {ide}",
            "message": "Supported IDEs are: cursor, windsurf, cline, copilot",
        }

    # Create parent directory for GitHub Copilot
    if ide == "copilot":
        rules_file.parent.mkdir(parents=True, exist_ok=True)

    # Write initial content
    rules_file.write_text(
        f"""# {ide.title()} Rules

This file contains default rules for the {ide.title()} IDE.

## Project Organization
- Place source code in src/ directory
- Place tests in tests/ directory
- Document APIs in docs/ directory

## Code Style
- Follow PEP 8 guidelines for Python code
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes

## Testing
- Write unit tests for new functionality
- Ensure tests pass before committing changes
- Maintain test coverage above 80%

## Documentation
- Keep documentation up to date with code changes
- Document significant design decisions
- Include examples in documentation
"""
    )

    return {
        "success": True,
        "initialized_rules": True,
        "project_path": str(project_path),
        "rules_directory": None,
        "templates_directory": str(project_path / ".ai-templates"),
        "rules_file": str(rules_file),
        "message": f"Initialized {ide} project in {project_path}",
    }
