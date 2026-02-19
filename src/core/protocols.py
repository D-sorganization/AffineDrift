"""Protocol interfaces for key AffineDrift abstractions.

This module defines structural typing contracts (PEP 544 Protocols) for the
main abstractions used across the codebase.  Protocol classes enable static
type checking without requiring inheritance, promoting loose coupling and
making the implicit interfaces explicit.

Protocols defined
-----------------
``DynamicalSystemProtocol``
    Any object that provides ``dynamics`` and ``linearize`` methods.  This
    captures the contract currently embodied by the ABC
    ``tangent_models.examples.DynamicalSystem`` without forcing concrete
    classes to inherit from it.

``FileValidator``
    Any callable that accepts file content (lines + path) and returns a list
    of issue tuples.  This is the pattern shared by every checker in
    ``code_quality/`` (banned patterns, magic numbers, AST issues).

``ReportGenerator``
    Any callable that accepts structured assessment data and writes a report
    file.  Captures the shared shape of ``generate_markdown_report`` and
    ``generate_issue_document``.

``ContentTransformer``
    Any callable that transforms a string and returns a string.  Used
    pervasively in LaTeX/HTML/QMD conversion pipelines.

``FileDiscoverer``
    Any callable that discovers files under a root directory and returns
    a list of ``Path`` objects.

``MetricsCollector``
    Any object that can collect metrics from a file path and return
    structured results.

Usage
-----
::

    from src.core.protocols import DynamicalSystemProtocol

    def simulate(system: DynamicalSystemProtocol, x0, u0, steps: int): ...

References
----------
- PEP 544 -- Protocols: Structural subtyping (static duck typing)
- Pragmatic Programmer: "Program to an Interface, Not an Implementation"
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import numpy as np

# ---------------------------------------------------------------------------
# Physics / Control
# ---------------------------------------------------------------------------


@runtime_checkable
class DynamicalSystemProtocol(Protocol):
    """Structural interface for dynamical system models.

    Any class that implements ``dynamics`` and ``linearize`` with the
    correct signatures satisfies this protocol -- no inheritance required.
    """

    def dynamics(
        self,
        x: np.ndarray[Any, Any],
        u: np.ndarray[Any, Any] | float | list[float],
    ) -> np.ndarray[Any, Any]:
        """Compute dx/dt = f(x, u)."""
        ...

    def linearize(
        self,
        x: np.ndarray[Any, Any],
        u: np.ndarray[Any, Any] | float | list[float],
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        """Return (A, B) linearization matrices around (x, u)."""
        ...


# ---------------------------------------------------------------------------
# Code Quality Pipeline
# ---------------------------------------------------------------------------

# Issue tuple: (line_number, message, code_snippet)
IssueRecord = tuple[int, str, str]


class FileValidator(Protocol):
    """Structural interface for file-level quality validators.

    Validators accept source lines and a filepath, returning a list of
    issue records.  All checkers in ``src/tools/code_quality/`` satisfy
    this protocol (``check_banned_patterns``, ``check_magic_numbers``,
    ``check_ast_issues``).
    """

    def __call__(
        self,
        lines: list[str],
        filepath: Path,
    ) -> list[IssueRecord]:
        """Validate *lines* from *filepath* and return found issues."""
        ...


class ContentTransformer(Protocol):
    """Structural interface for string-to-string content transformations.

    Used throughout the LaTeX, HTML, and QMD conversion pipelines where
    each stage is a pure function ``str -> str``.
    """

    def __call__(self, content: str) -> str:
        """Transform *content* and return the result."""
        ...


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


class ReportGenerator(Protocol):
    """Structural interface for assessment report generators.

    Captures the shared shape of ``generate_markdown_report`` and
    ``generate_issue_document`` in ``report_utils``.
    """

    def __call__(
        self,
        category_id: str,
        category_name: str,
        grade: float,
        details: str,
        output_dir: str | Path,
    ) -> Path:
        """Generate a report file and return its path."""
        ...


# ---------------------------------------------------------------------------
# File Discovery
# ---------------------------------------------------------------------------


class FileDiscoverer(Protocol):
    """Structural interface for file discovery functions.

    Captures the pattern shared by ``find_qmd_files``, ``find_html_files``,
    ``find_markdown_files``, and ``get_python_files``.
    """

    def __call__(
        self,
        root_dir: str | Path,
        **kwargs: Any,
    ) -> list[Path]:
        """Discover files under *root_dir* and return their paths."""
        ...


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


class MetricsCollector(Protocol):
    """Structural interface for source-file metrics collectors.

    Any callable that accepts a ``Path`` and returns a mapping of metric
    names to numeric values satisfies this protocol.
    """

    def __call__(self, filepath: Path) -> dict[str, int]:
        """Collect metrics from *filepath*."""
        ...


__all__ = [
    "ContentTransformer",
    "DynamicalSystemProtocol",
    "FileDiscoverer",
    "FileValidator",
    "IssueRecord",
    "MetricsCollector",
    "ReportGenerator",
]
