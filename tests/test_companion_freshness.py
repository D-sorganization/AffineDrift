"""Contracts for the Software Freshness Dashboard generator (#4027 via #4123)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import generate_companion_freshness as freshness
from scripts import install_programming_companion as installer
from tests.test_programming_companion_artifact_install import _write_bundle

REPO_ROOT = Path(__file__).resolve().parents[1]


def _installed_store(tmp_path: Path) -> Path:
    bundle, commit = _write_bundle(tmp_path)
    store = tmp_path / "store"
    args = installer.parse_args(
        [
            "--source",
            str(bundle),
            "--commit",
            commit,
            "--store",
            str(store),
            "--skip-attestation",
            "--fetched-on",
            "2026-09-03",
        ]
    )
    assert installer.install(args, bundle, commit) == 0
    (store / "pins.json").write_text(
        json.dumps(
            {
                "schema_version": "affinedrift/companion-pins/v1",
                "provider": freshness.PROVIDER,
                "pins": [
                    {
                        "commit": commit,
                        "state": "active",
                        "last_reviewed": "2026-09-03",
                        "review_due": "2026-12-03",
                        "note": "installed",
                        "routes": ["/models/programming/index.html"],
                    },
                    {
                        "commit": "b" * 40,
                        "state": "review-required",
                        "last_reviewed": None,
                        "review_due": None,
                        "note": "legacy",
                        "routes": ["/pages/overview.html"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return store


@pytest.mark.unit
def test_page_reports_active_pin_provider_verdict_and_every_pin(tmp_path: Path) -> None:
    store = _installed_store(tmp_path)
    page = freshness.render_page(freshness.load_inputs(store))
    assert page.startswith('---\ntitle: "Software Freshness Dashboard"')
    assert "## Active Provider Pin" in page
    assert "upstreamdrift-companion-" in page
    assert "Provider publication state | **draft**" in page
    assert "### Provider Blockers" in page
    assert "1 active, 0 pinned, 1 review required" in page
    assert "Review required (unqualified)" in page
    assert "- [/pages/overview.html](/pages/overview.html)" in page
    assert "Newer is not approved" in page
    # Deterministic: rendering twice yields identical bytes.
    assert page == freshness.render_page(freshness.load_inputs(store))


@pytest.mark.unit
def test_page_is_honest_when_nothing_is_installed(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    page = freshness.render_page(freshness.load_inputs(empty))
    assert "No Active Pin" in page
    assert "PREVIEW" in page


@pytest.mark.unit
def test_check_mode_detects_stale_output(tmp_path: Path) -> None:
    store = _installed_store(tmp_path)
    output = tmp_path / "freshness.qmd"
    assert freshness.main(["--store", str(store), "--output", str(output)]) == 0
    assert freshness.main(["--store", str(store), "--output", str(output), "--check"]) == 0
    output.write_text(output.read_text(encoding="utf-8") + "\nedited\n", encoding="utf-8")
    assert freshness.main(["--store", str(store), "--output", str(output), "--check"]) == 1


@pytest.mark.unit
def test_committed_dashboard_is_current() -> None:
    assert freshness.main(["--check"]) == 0
