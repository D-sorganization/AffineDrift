#!/usr/bin/env python3
"""Enforce byte budgets for image assets referenced by rendered pages."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BUDGET_BYTES = 500 * 1024
NAVBAR_LOGO_BUDGET_BYTES = 20 * 1024
IMAGE_ROOTS = ("logo", "pics", "static/images")
IMAGE_SUFFIXES = (".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp")
PAGE_ROOTS = (
    "_includes",
    "articles",
    "books",
    "critiques",
    "index.qmd",
    "manifest.json",
    "models",
    "pages",
    "repositories",
    "resources",
    "service-worker.js",
    "_quarto.yml",
)
PAGE_SUFFIXES = (".html", ".js", ".json", ".md", ".qmd", ".yml", ".yaml")

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImageBudgetResult:
    """Image budget check result.

    Attributes:
        checked_files: Number of referenced image files checked.
        errors: Human-readable budget violations.
    """

    checked_files: int
    errors: list[str]

    @property
    def has_errors(self) -> bool:
        """Return whether any image budget violations were found."""
        return bool(self.errors)


def _to_posix_relative(path: Path, repo_root: Path) -> str:
    """Return a repo-relative path with URL-compatible separators."""
    return path.relative_to(repo_root).as_posix()


def _is_under_page_root(path: Path, repo_root: Path) -> bool:
    """Return whether the path is a source page or page-level config file."""
    relative = _to_posix_relative(path, repo_root)
    return any(relative == root or relative.startswith(f"{root}/") for root in PAGE_ROOTS)


def _iter_page_sources(repo_root: Path) -> list[Path]:
    """Collect page source files that can reference shipped image assets."""
    return [
        path
        for path in repo_root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in PAGE_SUFFIXES
        and _is_under_page_root(path, repo_root)
    ]


def _iter_candidate_images(repo_root: Path) -> list[Path]:
    """Collect local images from roots that are eligible for page references."""
    images: list[Path] = []
    for root in IMAGE_ROOTS:
        image_root = repo_root / root
        if not image_root.exists():
            continue
        images.extend(
            path
            for path in image_root.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )
    return sorted(images)


def _read_page_texts(repo_root: Path) -> list[str]:
    """Read source page text, skipping files that are not UTF-8 text."""
    texts: list[str] = []
    for source_path in _iter_page_sources(repo_root):
        try:
            texts.append(source_path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            LOGGER.warning("Skipping non-UTF-8 page source: %s", source_path)
    return texts


def _is_referenced(relative_path: str, page_texts: list[str]) -> bool:
    """Return whether an image path appears in any page source."""
    return any(relative_path in page_text for page_text in page_texts)


def _budget_error(relative_path: str, size_bytes: int, budget_bytes: int) -> str:
    """Format a deterministic image budget violation."""
    return f"{relative_path}: {size_bytes} bytes exceeds {budget_bytes} byte budget"


def check_image_budget(
    repo_root: Path,
    budget_bytes: int = DEFAULT_BUDGET_BYTES,
) -> ImageBudgetResult:
    """Check referenced images under configured roots against a byte budget.

    Args:
        repo_root: Repository root to scan.
        budget_bytes: Maximum allowed byte size for referenced images.

    Returns:
        The count of referenced images checked and any violations.

    Raises:
        ValueError: If the budget is not positive.
    """
    if budget_bytes <= 0:
        raise ValueError("budget_bytes must be positive")

    page_texts = _read_page_texts(repo_root)
    errors: list[str] = []
    checked_files = 0
    for image_path in _iter_candidate_images(repo_root):
        relative_path = _to_posix_relative(image_path, repo_root)
        if not _is_referenced(relative_path, page_texts):
            continue
        checked_files += 1
        size_bytes = image_path.stat().st_size
        if size_bytes > budget_bytes:
            errors.append(_budget_error(relative_path, size_bytes, budget_bytes))

    return ImageBudgetResult(checked_files=checked_files, errors=errors)


def main() -> int:
    """Run the image budget check for the current repository."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    repo_root = Path(__file__).resolve().parent.parent
    result = check_image_budget(repo_root)
    LOGGER.info("Image budget check scanned %d referenced image(s)", result.checked_files)
    for error in result.errors:
        LOGGER.error(error)
    return 1 if result.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
