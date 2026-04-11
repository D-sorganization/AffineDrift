"""Mypy error output parsers - extracted from mypy_autofix_agent.py."""

from __future__ import annotations

import re


def parse_mypy_output(output: str) -> list[dict]:
    """Parse mypy stdout into structured error dicts."""
    errors = []
    pattern = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+): (?P<severity>\w+): (?P<msg>.+)$")
    for line in output.splitlines():
        m = pattern.match(line.strip())
        if m:
            errors.append(m.groupdict())
    return errors
