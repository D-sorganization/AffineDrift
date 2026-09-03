"""Contracts for the UpstreamDrift pin reconciliation gate (#4027, #4123)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import check_companion_pins as pins

REPO_ROOT = Path(__file__).resolve().parents[1]
SHA_A = "a" * 40
SHA_B = "b" * 40


def _site(tmp_path: Path) -> Path:
    root = tmp_path / "site"
    (root / "pages").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "pages" / "overview.qmd").write_text(
        f"see https://github.com/D-sorganization/UpstreamDrift/tree/{SHA_A}/src\n",
        encoding="utf-8",
    )
    (root / "index.qmd").write_text(
        f"[x](https://github.com/D-sorganization/UpstreamDrift/blob/{SHA_A}/README.md) and "
        f"https://github.com/D-sorganization/UpstreamDrift/commit/{SHA_B}\n",
        encoding="utf-8",
    )
    # Output directory copies must not count as sources.
    (root / "docs" / "index.qmd").write_text(
        "https://github.com/D-sorganization/UpstreamDrift/tree/" + "d" * 40, encoding="utf-8"
    )
    return root


def _document(*pin_specs: tuple[str, str, str | None, str | None, list[str]]) -> dict[str, object]:
    return {
        "schema_version": pins.PINS_SCHEMA,
        "provider": pins.PROVIDER,
        "pins": [
            {
                "commit": commit,
                "state": state,
                "last_reviewed": reviewed,
                "review_due": due,
                "note": "n",
                "routes": routes,
            }
            for commit, state, reviewed, due, routes in pin_specs
        ],
    }


@pytest.mark.unit
def test_scan_collects_full_shas_per_route_and_flags_short_ones(tmp_path: Path) -> None:
    root = _site(tmp_path)
    (root / "pages" / "short.qmd").write_text(
        "https://github.com/D-sorganization/UpstreamDrift/tree/abc1234/x", encoding="utf-8"
    )
    scanned, findings = pins.scan_site_pins(root)
    assert scanned == {
        SHA_A: ["/index.html", "/pages/overview.html"],
        SHA_B: ["/index.html"],
    }
    assert findings == ["pages/short.qmd: abbreviated UpstreamDrift pin abc1234"]


@pytest.mark.unit
def test_partial_sources_resolve_to_the_pages_that_include_them(tmp_path: Path) -> None:
    """Quarto never renders underscore-prefixed sources, so a pin in a partial
    must be attributed to the page that includes it (#4142)."""
    root = tmp_path / "site"
    (root / "articles" / "chapters").mkdir(parents=True)
    (root / "articles" / "_generated").mkdir()
    (root / "articles" / "monograph.qmd").write_text(
        "{{< include chapters/_ch01.qmd >}}\n{{< include _generated/atlas.qmd >}}\n",
        encoding="utf-8",
    )
    (root / "articles" / "chapters" / "_ch01.qmd").write_text(
        f"https://github.com/D-sorganization/UpstreamDrift/blob/{SHA_A}/a.py\n",
        encoding="utf-8",
    )
    (root / "articles" / "_generated" / "atlas.qmd").write_text(
        f"https://github.com/D-sorganization/UpstreamDrift/blob/{SHA_A}/b.py\n",
        encoding="utf-8",
    )

    scanned, findings = pins.scan_site_pins(root)

    assert scanned == {SHA_A: ["/articles/monograph.html"]}
    assert findings == []


@pytest.mark.unit
def test_pin_in_an_unincluded_partial_is_reported(tmp_path: Path) -> None:
    """A partial nothing includes never reaches the site, so it cannot carry a route."""
    root = tmp_path / "site"
    (root / "articles").mkdir(parents=True)
    (root / "articles" / "_orphan.qmd").write_text(
        f"https://github.com/D-sorganization/UpstreamDrift/blob/{SHA_A}/a.py\n",
        encoding="utf-8",
    )

    scanned, findings = pins.scan_site_pins(root)

    assert scanned == {}
    assert findings == [
        f"articles/_orphan.qmd: UpstreamDrift pin {SHA_A[:8]} sits in a partial that "
        "no rendered page includes"
    ]


@pytest.mark.unit
def test_validation_rejects_bad_states_dates_and_active_mismatch() -> None:
    doc = _document(
        (SHA_A, "pinned", "2026-09-03", "2026-09-01", ["/index.html"]),
        (SHA_B, "wild", None, None, []),
    )
    findings = pins.validate_pins(doc, active_commit=SHA_A)
    assert any("precedes" in f for f in findings)
    assert any("state must be one of" in f for f in findings)
    assert any("exactly one active pin" in f for f in findings)
    clean = _document((SHA_A, "active", "2026-09-03", "2026-12-03", []))
    assert pins.validate_pins(clean, active_commit=SHA_A) == []
    assert pins.validate_pins(clean, active_commit=None) == [
        "no active lock exists but a pin is marked active"
    ]
    unreviewed = _document((SHA_B, "review-required", None, None, ["/index.html"]))
    assert pins.validate_pins(unreviewed, active_commit=None) == []


@pytest.mark.unit
def test_reconcile_adds_unpinned_shas_refreshes_routes_and_drops_unlinked() -> None:
    doc = _document(
        (SHA_A, "pinned", "2026-09-03", "2026-12-03", ["/stale.html"]),
        ("e" * 40, "pinned", "2026-09-03", "2026-12-03", ["/gone.html"]),
    )
    scanned = {SHA_A: ["/index.html"], SHA_B: ["/index.html"]}
    refreshed, findings = pins.reconcile(doc, scanned, active_commit=None)
    commits = [pin["commit"] for pin in refreshed["pins"]]
    assert commits == [SHA_A, SHA_B]
    assert refreshed["pins"][0]["routes"] == ["/index.html"]
    assert refreshed["pins"][1]["state"] == "review-required"
    assert any("not pinned" in f for f in findings)
    assert any("routes drifted" in f for f in findings)
    assert any("no longer linked" in f for f in findings)


@pytest.mark.unit
def test_active_lock_commit_is_kept_even_without_routes() -> None:
    refreshed, _ = pins.reconcile(
        _document((SHA_A, "active", "2026-09-03", "2026-12-03", ["/x.html"])), {}, SHA_A
    )
    assert refreshed["pins"] == [
        {
            "commit": SHA_A,
            "state": "active",
            "last_reviewed": "2026-09-03",
            "review_due": "2026-12-03",
            "note": "n",
            "routes": [],
        }
    ]


@pytest.mark.unit
def test_cli_write_then_check_round_trips(tmp_path: Path) -> None:
    root = _site(tmp_path)
    pins_path = root / "data/companion/pins.json"
    store = root / "data/companion"
    assert pins.main(["--root", str(root), "--pins", str(pins_path), "--store", str(store)]) == 1
    assert (
        pins.main(["--root", str(root), "--pins", str(pins_path), "--store", str(store), "--write"])
        == 0
    )
    document = json.loads(pins_path.read_text(encoding="utf-8"))
    assert [pin["state"] for pin in document["pins"]] == ["review-required"] * 2
    assert pins.main(["--root", str(root), "--pins", str(pins_path), "--store", str(store)]) == 0


@pytest.mark.unit
def test_repository_pins_are_reconciled() -> None:
    """The committed pin file must match the live sources and the active lock."""
    assert pins.main(["--root", str(REPO_ROOT)]) == 0
