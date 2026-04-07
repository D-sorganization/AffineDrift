"""Helpers for explicit CLI stdout and stderr output."""

from __future__ import annotations

import sys


def write_stdout(message: str = "") -> None:
    """Write a single line to stdout."""
    sys.stdout.write(f"{message}\n" if message else "\n")


def write_stderr(message: str = "") -> None:
    """Write a single line to stderr."""
    sys.stderr.write(f"{message}\n" if message else "\n")
