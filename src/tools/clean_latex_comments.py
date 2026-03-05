#!/usr/bin/env python3
"""Clean LaTeX comments from converted Quarto files."""

import logging
import re
from pathlib import Path

from src.core.contracts import require

logger = logging.getLogger(__name__)


def remove_latex_comments(content: str) -> str:
    """Remove LaTeX comments (lines starting with %) from string content."""
    require(isinstance(content, str), "content must be a string")

    # Remove lines that are just LaTeX comments (with optional whitespace)
    lines = content.split("\n")
    cleaned_lines = []
    for line in lines:
        # Skip lines that are just LaTeX comments (with optional leading whitespace)
        stripped = line.lstrip()
        if stripped.startswith("%") and not stripped.startswith("%%"):
            # Skip this line (it's a LaTeX comment)
            continue
        cleaned_lines.append(line)

    cleaned_content = "\n".join(cleaned_lines)
    # Also remove standalone comment blocks like "%=="
    cleaned_content = re.sub(r"^\s*% =+.*$", "", cleaned_content, flags=re.MULTILINE)
    # Remove empty lines that were left by comment removal (max 2 consecutive)
    cleaned_content = re.sub(r"\n{4,}", "\n\n\n", cleaned_content)

    return cleaned_content


def clean_latex_comments_in_file(file_path: Path) -> bool:
    """Remove LaTeX comments from a file in-place."""
    require(isinstance(file_path, Path), "file_path must be a Path")
    require(file_path.exists(), f"File does not exist: {file_path}")
    require(file_path.is_file(), f"Path is not a file: {file_path}")

    try:
        content = file_path.read_text(encoding="utf-8")
        cleaned_content = remove_latex_comments(content)

        if content != cleaned_content:
            file_path.write_text(cleaned_content, encoding="utf-8")
        return True
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return False


def main() -> None:
    """Clean all .qmd files in predefined content directories."""
    directories = [
        Path("content/Affine Background Articles"),
        Path("content/Affine Nature of the Golf Swing"),
    ]

    files_cleaned = 0
    for directory in directories:
        if not directory.exists() or not directory.is_dir():
            continue

        for qmd_file in directory.glob("*.qmd"):
            if clean_latex_comments_in_file(qmd_file):
                files_cleaned += 1

    logger.info(f"Processed {files_cleaned} files successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
