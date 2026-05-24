"""Tests to verify magic numbers have been replaced with named constants."""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize(
    "filepath,magic_value,description",
    [
        (
            ROOT / "src" / "golf_simulation" / "round_simulator.py",
            "0.054",
            "REGULATION_HOLE_RADIUS_M should be used instead of 0.054",
        ),
        (
            ROOT / "src" / "golf_simulation" / "putting.py",
            "1.5",
            "HOLE_CAPTURE_SPEED_MS should be used instead of 1.5 for capture speed",
        ),
    ],
)
def test_no_magic_number_in_logic(filepath: Path, magic_value: str, description: str) -> None:
    """Verify that specific magic numbers are not used in logic code."""
    content = filepath.read_text(encoding="utf-8")
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for comparator in [node.left, *node.comparators]:
                if isinstance(comparator, ast.Constant) and str(comparator.value) == magic_value:
                    pytest.fail(f"{description} in {filepath.name}")
