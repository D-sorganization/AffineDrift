"""Regression checks for Gemini panel follow-ups (#5642)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MOTION = ROOT / "articles/technology-motion-capture.qmd"
LAUNCH = ROOT / "articles/technology-launch-monitors.qmd"
FORCE = ROOT / "articles/technology-force-measurement.qmd"
REFERENCE = ROOT / "articles/reference-point-problem.qmd"
FIGURE_SCRIPT = ROOT / "scripts/build_launch_monitor_figures.py"


def _split_references(text: str) -> tuple[str, str]:
    body, _sep, refs = text.partition("## References and Further Reading")
    return body, refs


def _pubmed_ids(section: str) -> set[str]:
    return set(re.findall(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", section))


@pytest.mark.content_lint
def test_reference_point_cheetham_correlation_significance() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    assert "r=-0.14" in text.replace(" ", "") or "r = -0.14" in text
    assert "not statistically significant" in text
    assert "304" in text and "652" in text and "2432" in text


@pytest.mark.content_lint
def test_launch_monitor_figures_have_committed_generator() -> None:
    assert FIGURE_SCRIPT.is_file()
    source = LAUNCH.read_text(encoding="utf-8")
    assert "scripts/build_launch_monitor_figures.py" in source


def test_launch_monitor_figure_script_runs() -> None:
    subprocess.check_call([sys.executable, str(FIGURE_SCRIPT)], cwd=ROOT)
    for name in ("launch-monitor-doppler-rank.svg", "launch-monitor-groove-ambiguity.svg"):
        assert (ROOT / "static/images" / name).is_file()


@pytest.mark.content_lint
def test_force_measurement_inline_citations_listed_in_references() -> None:
    body, refs = _split_references(FORCE.read_text(encoding="utf-8"))
    missing = sorted(_pubmed_ids(body) - _pubmed_ids(refs))
    assert not missing, f"Inline PubMed IDs missing from references: {missing}"


@pytest.mark.content_lint
def test_motion_capture_kim_protocol_details() -> None:
    text = MOTION.read_text(encoding="utf-8")
    assert "four reflective markers" in text.lower()
    assert "103 swings" in text
    assert "28° ± 13°" in text
