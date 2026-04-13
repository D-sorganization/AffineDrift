"""Source-level caller consistency tests for wrist universal joint helpers."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _assert_keyword_calls(path: Path) -> None:
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))

    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "universal_joint_transmission_ratio"
    ]
    assert calls, f"Expected at least one call in {path}"

    for node in calls:
        assert not node.args, f"Positional args found in {path}:{node.lineno}"
        keywords = {kw.arg for kw in node.keywords if kw.arg is not None}
        assert keywords == {"phi_rad", "delta_rad"}, f"Bad keywords in {path}:{node.lineno}"


def test_python_call_sites_use_keyword_arguments() -> None:
    """The Python helpers should pass phi_rad and delta_rad explicitly."""
    for relative in [
        "src/tools/wrist_universal_joint/streamlit_app.py",
        "src/tools/wrist_universal_joint/enhanced_model_kinematics.py",
    ]:
        _assert_keyword_calls(REPO_ROOT / relative)


def test_legacy_universal_joint_launcher_reexports_public_api() -> None:
    """The legacy docs launcher should keep old imports working."""
    launcher = REPO_ROOT / "docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py"
    spec = importlib.util.spec_from_file_location("legacy_universal_joint_launcher", launcher)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for name in [
        "MainWindow",
        "DiagramCanvas",
        "PlotCanvas",
        "DocumentationDialog",
        "calculate_moments_of_inertia",
        "universal_joint_transmission_ratio",
        "distribute_torque_by_grip_angle",
        "run",
    ]:
        assert name in module.__all__
        assert hasattr(module, name)

    assert module.calculate_moments_of_inertia(200.0, 100.0, 1.0, 0.85) == (
        0.17783333333333332,
        0.08891666666666666,
    )
