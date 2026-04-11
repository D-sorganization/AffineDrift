"""Regression tests for wrist-model Matplotlib figure handling."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_wrist_plots_do_not_use_pyplot_state_machine() -> None:
    for relative_path in (
        "src/tools/wrist_universal_joint/diagram.py",
        "src/tools/wrist_universal_joint/plots.py",
    ):
        source = (ROOT / relative_path).read_text(encoding="utf-8")

        assert "import matplotlib.pyplot" not in source
        assert "plt.subplots" not in source
        assert "plt.tight_layout" not in source


def test_array_backed_plotters_are_not_resource_cached() -> None:
    source = (ROOT / "src/tools/wrist_universal_joint/plots.py").read_text(encoding="utf-8")

    for function_name in ("plot_torque", "plot_acceleration"):
        prefix = source.split(f"def {function_name}", maxsplit=1)[0]
        decorator_block = prefix.rsplit("\n\n", maxsplit=1)[-1]
        assert "cache_resource" not in decorator_block
