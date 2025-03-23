"""
IDE Rules Initialization Tool for MCP Agile Flow

This module provides functionality to initialize and migrate rules between different IDE formats,
primarily from Cursor's .mdc files to Windsurf's .windsurfrules file.
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logger = logging.getLogger(__name__)


def find_cursor_rules_dir(project_path: str = None) -> Path:
    """
    Find the Cursor rules directory.

    Args:
        project_path: Optional path to the project directory.
                     If None, uses current working directory.

    Returns:
        Path to the Cursor rules directory
    """
    base_path = Path(project_path or os.getcwd())
    cursor_dir = base_path / ".cursor"
    rules_dir = cursor_dir / "rules"

    if not rules_dir.exists():
        logger.warning(f"Cursor rules directory not found: {rules_dir}")
        if not cursor_dir.exists():
            logger.info(f"Creating cursor directory: {cursor_dir}")
            cursor_dir.mkdir(exist_ok=True)
        logger.info(f"Creating rules directory: {rules_dir}")
        rules_dir.mkdir(exist_ok=True)

    return rules_dir


def get_windsurf_rules_path(project_path: str = None) -> Path:
    """
    Get the path to the Windsurf rules file.

    Args:
        project_path: Optional path to the project directory.
                     If None, uses current working directory.

    Returns:
        Path to the Windsurf rules file
    """
    base_path = Path(project_path or os.getcwd())
    return base_path / ".windsurfrules"


def read_mdc_files(rules_dir: Path, specific_file: str = None) -> List[Tuple[str, str]]:
    """
    Read MDC files from the Cursor rules directory.

    Args:
        rules_dir: Path to the Cursor rules directory
        specific_file: Optional specific file to read

    Returns:
        List of tuples (filename, content)
    """
    result = []

    # Get all MDC files
    mdc_files = [f for f in os.listdir(rules_dir) if f.endswith(".mdc")]

    # Filter for specific file if provided
    if specific_file:
        file_name = (
            specific_file if specific_file.endswith(".mdc") else f"{specific_file}.mdc"
        )
        if file_name in mdc_files:
            mdc_files = [file_name]
        else:
            logger.error(
                f"Specified file '{specific_file}' not found in Cursor rules directory."
            )
            logger.info(f"Available files: {', '.join(mdc_files)}")
            return []

    # Process each file
    for file_name in mdc_files:
        file_path = rules_dir / file_name
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                result.append((file_name, content))
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")

    return result


def process_mdc_content(file_name: str, content: str) -> str:
    """
    Process MDC file content:
    - Remove YAML frontmatter
    - Add file name as section header

    Args:
        file_name: Name of the MDC file
        content: Content of the MDC file

    Returns:
        Processed content
    """
    # Extract content, removing YAML frontmatter (between --- markers)
    processed_content = content
    if content.startswith("---"):
        second_separator_index = content.find("---", 3)
        if second_separator_index != -1:
            processed_content = content[second_separator_index + 3 :].strip()

    # Remove .mdc extension from file name for the header
    header_name = file_name.replace(".mdc", "")

    # Add file name as section header
    return f"## {header_name}\n\n{processed_content}\n\n"


def smart_truncate(content: str, max_length: int) -> str:
    """
    Smartly truncate content at logical break points.

    Args:
        content: Content to truncate
        max_length: Maximum length in characters

    Returns:
        Truncated content
    """
    content_bytes = len(content.encode("utf-8"))
    if content_bytes <= max_length:
        return content

    # Target length slightly below max to leave room for truncation note
    truncation_note = "\n\n# NOTE: Content was truncated due to size limit"
    target_length = max_length - len(truncation_note.encode("utf-8"))

    # Ensure we have some minimum content
    if target_length < 10:
        return truncation_note

    # Try to find paragraph break
    paragraph_break = content.rfind("\n\n", 0, target_length)
    if paragraph_break > 0 and paragraph_break > target_length - 500:
        truncated = content[:paragraph_break]
        return truncated + truncation_note + " (ended at paragraph break)"

    # Try to find sentence end
    sentence_end_candidates = [
        m.end() for m in re.finditer(r"[.!?]\s+", content[:target_length])
    ]
    if sentence_end_candidates and sentence_end_candidates[-1] > 0:
        last_sentence_end = sentence_end_candidates[-1]
        if last_sentence_end > target_length - 300:
            truncated = content[:last_sentence_end]
            return truncated + truncation_note + " (ended at sentence break)"

    # Try word boundary
    last_space = content.rfind(" ", 0, target_length)
    if last_space > 0:
        truncated = content[:last_space]
        return truncated + truncation_note + " (ended at word break)"

    # Last resort - hard truncate
    truncated = content[:target_length]
    return truncated + truncation_note + " (hard truncation)"


def migrate_cursor_to_windsurf(
    project_path: str = None,
    specific_file: str = None,
    verbose: bool = False,
    no_truncate: bool = False,
) -> Dict:
    """
    Migrate rules from Cursor to Windsurf.

    Args:
        project_path: Path to the project directory
        specific_file: Optional specific file to migrate
        verbose: Whether to show detailed information
        no_truncate: Skip truncation even if content exceeds character limit

    Returns:
        Dictionary with status and messages
    """
    try:
        # Find cursor rules directory
        rules_dir = find_cursor_rules_dir(project_path)

        # Get windsurf rules file path
        windsurf_file = get_windsurf_rules_path(project_path)

        # Read MDC files
        mdc_files = read_mdc_files(rules_dir, specific_file)

        if not mdc_files:
            return {
                "success": False,
                "error": "No MDC files found in Cursor rules directory",
                "files_processed": 0,
            }

        # Start with header
        combined_content = "# Windsurf Rules\n\n"

        # Process each file
        for file_name, content in mdc_files:
            if verbose:
                logger.info(f"Processing {file_name} ({len(content)} bytes)")

            processed_content = process_mdc_content(file_name, content)
            combined_content += processed_content

        # Check character limit
        content_length = len(combined_content.encode("utf-8"))
        if content_length > 6000:
            logger.warning(
                f"Content length ({content_length} chars) exceeds Windsurf's 6000 character limit"
            )

            if not no_truncate:
                logger.info("Truncating content to fit within character limit")
                combined_content = smart_truncate(combined_content, 6000)

        # Create parent directory if needed
        windsurf_file.parent.mkdir(exist_ok=True)

        # Write to Windsurf rules file
        with open(windsurf_file, "w", encoding="utf-8") as f:
            f.write(combined_content)

        return {
            "success": True,
            "message": f"Successfully migrated rules to {windsurf_file}",
            "files_processed": len(mdc_files),
            "character_count": len(combined_content.encode("utf-8")),
            "truncated": content_length > 6000 and not no_truncate,
        }

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return {"success": False, "error": str(e), "files_processed": 0}
