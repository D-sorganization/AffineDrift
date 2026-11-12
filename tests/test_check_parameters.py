"""Tests for scripts/check_parameters.py (issue #5595)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.canonical_parameters_registry import load_registry, render_parameters_markdown
from scripts.check_parameters import key, scan_literal_checks, verify_markdown

pytestmark = pytest.mark.content_lint

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestVerifyMarkdown:
    def test_fresh_parameters_md_passes(self, tmp_path: Path) -> None:
        payload = load_registry()
        parameters = tmp_path / "PARAMETERS.md"
        parameters.write_text(render_parameters_markdown(payload), encoding="utf-8")
        assert verify_markdown(payload, parameters_path=parameters) == []

    def test_stale_pointer_fails(self, tmp_path: Path) -> None:
        payload = load_registry()
        stale = render_parameters_markdown(payload) + "\n| bad | Ch 10-12 |\n"
        path = tmp_path / "PARAMETERS.md"
        path.write_text(stale, encoding="utf-8")
        errors = verify_markdown(payload, parameters_path=path)
        assert any("Ch 10-12" in err for err in errors)


class TestLiteralChecks:
    def test_fixture_ball_mass_matches_registry(self) -> None:
        payload = load_registry()
        findings = scan_literal_checks(REPO_ROOT, payload)
        assert not any("golf_ball_mass_max" in str(f["rule"]) for f in findings)

    def test_wrong_literal_is_detected(self, tmp_path: Path) -> None:
        module = tmp_path / "src/affine_control/impact_contact_fixtures.py"
        module.parent.mkdir(parents=True)
        module.write_text("BALL_MASS_KG = 0.050\n", encoding="utf-8")
        payload = json.loads((REPO_ROOT / "data/canonical_parameters.json").read_text())
        findings = scan_literal_checks(tmp_path, payload)
        assert findings
        assert findings[0]["rule"] == "golf_ball_mass_max literal mismatch"

    def test_baseline_key_ignores_line_number(self) -> None:
        finding = {
            "file": "a.py",
            "line": 9,
            "rule": "golf_ball_mass_max literal mismatch",
            "fix": "",
        }
        assert key(finding) == "a.py::golf_ball_mass_max literal mismatch"
