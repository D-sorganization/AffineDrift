"""Batch-update LaTeX book formatting for the textbook sources."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.cli_output import write_stdout


def _update_file(path: Path) -> bool:
    """Update a single LaTeX file in place and return True when changed."""
    content = path.read_text(encoding="utf-8")
    if r"\documentclass" not in content and r"\usepackage" not in content:
        return False

    new_content = re.sub(
        r"\\documentclass\[([^\]]*)11pt([^\]]*)\]\{book\}",
        r"\\documentclass[\g<1>10pt\g<2>]{book}",
        content,
    )
    new_content = re.sub(
        r"\\documentclass\[([^\]]*)12pt([^\]]*)\]\{book\}",
        r"\\documentclass[\g<1>10pt\g<2>]{book}",
        new_content,
    )
    new_content = re.sub(
        r"\\usepackage\[margin=[0-9.]+in\]\{geometry\}",
        r"\\usepackage[margin=1.5in]{geometry}",
        new_content,
    )
    new_content = re.sub(
        r"\\geometry\{margin=[0-9.]+in\}",
        r"\\geometry{margin=1.5in}",
        new_content,
    )
    new_content = re.sub(
        r"\\geometry\{a4paper, margin=[0-9.]+in\}",
        r"\\geometry{a4paper, margin=1.5in}",
        new_content,
    )

    if new_content == content:
        return False

    path.write_text(new_content, encoding="utf-8")
    write_stdout(f"Updated {path}")
    return True


def main(repo_root: Path | None = None) -> int:
    """Batch-update textbook formatting files."""
    repo_root = repo_root or Path(__file__).resolve().parent.parent
    directories = [
        repo_root / "articles" / "The_Physics_of_Golf",
        repo_root / "articles" / "The_Geometry_of_Motion",
    ]

    for directory in directories:
        for path in directory.rglob("*"):
            if path.suffix in {".tex", ".sty"}:
                _update_file(path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
