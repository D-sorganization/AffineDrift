"""Tests to verify no duplicate constant definitions exist."""

import ast
import inspect
from pathlib import Path

from src.core import constants


def test_no_duplicate_constant_names() -> None:
    """Verify that no constant is defined more than once in the module."""
    source_path = Path(inspect.getfile(constants))
    tree = ast.parse(source_path.read_text(encoding="utf-8"))

    assignments: dict[str, int] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    name = target.id
                    assignments[name] = assignments.get(name, 0) + 1

    duplicates = {name: count for name, count in assignments.items() if count > 1}
    assert not duplicates, f"Duplicate constant definitions found: {duplicates}"


def test_regulation_hole_radius_exists() -> None:
    """Verify the regulation hole radius constant exists and is reasonable."""
    assert hasattr(constants, "REGULATION_HOLE_RADIUS_M")
    assert 0.05 < constants.REGULATION_HOLE_RADIUS_M < 0.06


def test_hole_capture_speed_exists() -> None:
    """Verify the hole capture speed constant exists and is reasonable."""
    assert hasattr(constants, "HOLE_CAPTURE_SPEED_MS")
    assert 1.0 < constants.HOLE_CAPTURE_SPEED_MS < 2.0
