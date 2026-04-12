"""Source-level structure tests for the Qt wrist plot canvases."""

from __future__ import annotations

import ast
from pathlib import Path

QT_CANVASES = Path("src/tools/wrist_universal_joint/qt_canvases.py")


def _function_lengths(path: Path) -> dict[str, int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name: node.end_lineno - node.lineno + 1
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.end_lineno is not None
    }


def test_transmission_sweep_plotter_is_decomposed() -> None:
    """The Qt transmission sweep plotter should stay split into focused helpers."""
    lengths = _function_lengths(QT_CANVASES)

    assert lengths["_plot_transmission_sweep"] <= 30
    assert lengths["_plot_transmission_sweep_lines"] <= 40
    assert lengths["_plot_current_wrist_marker"] <= 30
    assert lengths["_set_transmission_sweep_axes"] <= 20


def test_transmission_sweep_helpers_remain_present() -> None:
    """The extracted helpers document the plotting responsibilities explicitly."""
    source = QT_CANVASES.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(QT_CANVASES))
    helper_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

    assert {
        "_plot_transmission_sweep_lines",
        "_plot_current_wrist_marker",
        "_set_transmission_sweep_axes",
    } <= helper_names
