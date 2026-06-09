"""Select Python files that are valid inputs for repository quality metrics."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Final

QUALITY_METRIC_ARTIFACT_DIRS: Final[frozenset[str]] = frozenset(
    {
        ".codemap",
        ".quarto",
        "_site",
        "coverage",
        "docs",
        "htmlcov",
        "lcov-report",
    }
)


def filter_quality_metric_python_files(root: Path, paths: Iterable[Path]) -> list[Path]:
    """Return Python files that should count toward repository quality metrics.

    Args:
        root: Repository root used to identify generated or site artifact paths.
        paths: Candidate Python paths discovered in the repository.

    Returns:
        Candidate paths excluding generated site, coverage, and local artifact directories.

    Raises:
        TypeError: If root is not a Path, paths is None, or a candidate is not a Path.
    """
    if not isinstance(root, Path):
        raise TypeError("root must be a Path")
    if paths is None:
        raise TypeError("paths must not be None")

    root_path = root.resolve()
    return [path for path in paths if _is_quality_metric_python_file(root_path, path)]


def _is_quality_metric_python_file(root: Path, path: Path) -> bool:
    if not isinstance(path, Path):
        raise TypeError("paths must contain only Path instances")
    if path.suffix != ".py":
        return False

    relative_parts = _relative_parts(root, path)
    path_parts = {part.lower() for part in relative_parts}
    return path_parts.isdisjoint(QUALITY_METRIC_ARTIFACT_DIRS)


def _relative_parts(root: Path, path: Path) -> tuple[str, ...]:
    candidate = path if path.is_absolute() else root / path
    try:
        relative_path = candidate.resolve().relative_to(root)
    except ValueError:
        relative_path = path
    return relative_path.parts
