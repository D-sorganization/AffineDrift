"""Behavioral test for ``scripts/baseline_assessments.generate_assessment_report``.

The module has an import-time ``docs/assessments`` mkdir side effect, so import
happens inside ``tmp_path`` (via chdir) to avoid polluting the repo tree. The
test then exercises the pure single-file report writer (issue #3230).
"""

from __future__ import annotations

import importlib


def test_generate_assessment_report_writes_expected_content(tmp_path, monkeypatch) -> None:
    # Import under a temp cwd because module top-level creates docs/assessments.
    monkeypatch.chdir(tmp_path)
    mod = importlib.import_module("scripts.baseline_assessments")

    out = tmp_path / "Assessment_A.md"
    mod.generate_assessment_report("A", "Code Structure", "Looks solid.", out)

    content = out.read_text(encoding="utf-8")
    assert "# Assessment A for AffineDrift" in content
    assert "Category: Code Structure" in content
    assert "Looks solid." in content
    assert "## Score:" in content
