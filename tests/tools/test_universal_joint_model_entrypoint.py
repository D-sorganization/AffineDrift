"""Structural tests for the enhanced wrist-model Qt entrypoint split."""

from __future__ import annotations

import py_compile
from pathlib import Path

import pytest

WRIST_ENTRYPOINTS = [
    "content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py",
    "docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py",
]


@pytest.mark.parametrize("relative_path", WRIST_ENTRYPOINTS)
def test_entrypoints_are_now_thin(relative_path: str) -> None:
    """Legacy wrist launchers should stay thin after the module split."""
    repo_root = Path(__file__).resolve().parents[2]
    entrypoint = repo_root / relative_path
    line_count = len(entrypoint.read_text(encoding="utf-8").splitlines())
    assert line_count <= 80


def test_split_modules_compile() -> None:
    """New split modules should compile as standalone Python source files."""
    repo_root = Path(__file__).resolve().parents[2]
    module_paths = [
        *(repo_root / relative_path for relative_path in WRIST_ENTRYPOINTS),
        repo_root / "src" / "tools" / "wrist_universal_joint" / "enhanced_model_geometry.py",
        repo_root / "src" / "tools" / "wrist_universal_joint" / "enhanced_model_kinematics.py",
        repo_root / "src" / "tools" / "wrist_universal_joint" / "qt_canvases.py",
        repo_root / "src" / "tools" / "wrist_universal_joint" / "qt_dialogs.py",
        repo_root / "src" / "tools" / "wrist_universal_joint" / "qt_ui_sections.py",
        repo_root / "src" / "tools" / "wrist_universal_joint" / "qt_widgets.py",
        repo_root / "src" / "tools" / "wrist_universal_joint" / "qt_window.py",
    ]
    for path in module_paths:
        py_compile.compile(str(path), doraise=True)
