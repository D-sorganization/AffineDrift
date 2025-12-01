#!/usr/bin/env python3
"""
Clean LaTeX comments from converted Quarto files.
"""

import re
from pathlib import Path


def clean_latex_comments(file_path: Path) -> bool:
    """Remove LaTeX comments (lines starting with %) from a file."""
    try:
        content = file_path.read_text(encoding="utf-8")
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
        cleaned_content = re.sub(
            r"^\s*% =+.*$", "", cleaned_content, flags=re.MULTILINE
        )
        # Remove empty lines that were left by comment removal (max 2 consecutive)
        cleaned_content = re.sub(r"\n{4,}", "\n\n\n", cleaned_content)

        file_path.write_text(cleaned_content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main() -> None:
    """Clean all .qmd files in the content directories."""
    directories = [
        Path("content/Affine Background Articles"),
        Path("content/Affine Nature of the Golf Swing"),
    ]

    files_cleaned = 0
    for directory in directories:
        if not directory.exists():
            print(f"Directory not found: {directory}")
            continue

        for qmd_file in directory.glob("*.qmd"):
            if clean_latex_comments(qmd_file):
                files_cleaned += 1
                print(f"Cleaned: {qmd_file.name}")

    print(f"\nCleaned {files_cleaned} file(s).")


if __name__ == "__main__":
    main()
