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
def test_reconcile_rejects_non_list_pin_collections() -> None:
    with pytest.raises(ValueError, match="companion pins must be a list"):
        pins.reconcile({"pins": "invalid"}, {}, None)


@pytest.mark.unit
def test_cli_write_rejects_malformed_pins_without_changing_file(tmp_path: Path) -> None:
    root = _site(tmp_path)
    pins_path = root / "data/companion/pins.json"
    pins_path.parent.mkdir(parents=True)
    original = b'{"pins": "invalid"}\n'
    pins_path.write_bytes(original)

    assert pins.main(["--root", str(root), "--pins", str(pins_path), "--write"]) == 1
    assert pins_path.read_bytes() == original


@pytest.mark.unit
def test_cli_write_then_check_round_trips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _site(tmp_path)
    pins_path = root / "data/companion/pins.json"
    store = root / "data/companion"
    calls: list[list[str]] = []

    def unexpected_formatter(*args: object, **kwargs: object) -> None:
        calls.append(list(args[0]))

    monkeypatch.setattr(
        pins.shutil,
        "which",
        lambda name: name if name in {"npx", "node"} else None,
    )
    monkeypatch.setattr(pins.subprocess, "run", unexpected_formatter)
    assert pins.main(["--root", str(root), "--pins", str(pins_path), "--store", str(store)]) == 1
    assert (
        pins.main(["--root", str(root), "--pins", str(pins_path), "--store", str(store), "--write"])
        == 0
    )
    document = json.loads(pins_path.read_text(encoding="utf-8"))
    assert [pin["state"] for pin in document["pins"]] == ["review-required"] * 2
    assert pins.main(["--root", str(root), "--pins", str(pins_path), "--store", str(store)]) == 0
    assert calls == []


@pytest.mark.unit
def test_local_prettier_runs_with_a_bounded_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "project"
    prettier = root / "node_modules/prettier/bin/prettier.cjs"
    prettier.parent.mkdir(parents=True)
    prettier.write_text("// local formatter fixture", encoding="utf-8")
    target = tmp_path / "pins.json"
    target.write_text("{}\n", encoding="utf-8")
    calls: list[tuple[list[str], dict[str, object]]] = []

    def record_run(args: list[str], **kwargs: object) -> pins.subprocess.CompletedProcess[str]:
        calls.append((args, kwargs))
        return pins.subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(pins.shutil, "which", lambda name: "node.exe" if name == "node" else None)
    monkeypatch.setattr(pins.subprocess, "run", record_run)

    pins._format_with_prettier(target, root)

    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args == ["node.exe", str(prettier), "--write", str(target)]
    assert kwargs["timeout"] == pins._FORMAT_TIMEOUT_SECONDS
    assert kwargs["check"] is False


@pytest.mark.parametrize("failure", ["timeout", "oserror", "nonzero"])
@pytest.mark.unit
def test_local_prettier_failures_are_optional(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    root = tmp_path / "project"
    prettier = root / "node_modules/prettier/bin/prettier.cjs"
    prettier.parent.mkdir(parents=True)
    prettier.write_text("// local formatter fixture", encoding="utf-8")
    target = tmp_path / "pins.json"
    original = b'{"pins": []}\n'
    target.write_bytes(original)

    def fail_run(args: list[str], **kwargs: object) -> pins.subprocess.CompletedProcess[str]:
        Path(args[-1]).write_bytes(b"partial formatter output")
        if failure == "timeout":
            raise pins.subprocess.TimeoutExpired(args, kwargs["timeout"])
        if failure == "oserror":
            raise OSError("node unavailable")
        return pins.subprocess.CompletedProcess(args, 17, "", "formatter failed")

    monkeypatch.setattr(pins.shutil, "which", lambda name: "node.exe" if name == "node" else None)
    monkeypatch.setattr(pins.subprocess, "run", fail_run)

    pins._format_with_prettier(target, root)
    assert target.read_bytes() == original


@pytest.mark.unit
def test_repository_pins_are_reconciled() -> None:
    """The committed pin file must match the live sources and the active lock."""
    assert pins.main(["--root", str(REPO_ROOT)]) == 0


@pytest.mark.unit
def test_render_excluded_chapters_do_not_produce_routes_and_are_reported(tmp_path: Path) -> None:
    """A link inside articles/proximal_distal_companion/chapters/ must not
    produce a route, and must be reported rather than silently dropped (#4145)."""
    root = tmp_path / "site"
    chapters_dir = root / "articles" / "proximal_distal_companion" / "chapters"
    chapters_dir.mkdir(parents=True)
    (chapters_dir / "ch01.qmd").write_text(
        f"https://github.com/D-sorganization/UpstreamDrift/blob/{SHA_A}/a.py\n",
        encoding="utf-8",
    )

    scanned, findings = pins.scan_site_pins(root)

    assert scanned == {}
    assert findings == [
        f"articles/proximal_distal_companion/chapters/ch01.qmd: UpstreamDrift pin {SHA_A[:8]} "
        "sits in a partial that no rendered page includes"
    ]


@pytest.mark.unit
def test_render_excluded_chapter_included_by_page_resolves_to_page_route(tmp_path: Path) -> None:
    """When a render-excluded chapter is included by a rendered page, its pins
    must resolve to the page route and not emit a dead chapter route (#4145)."""
    root = tmp_path / "site"
    chapters_dir = root / "articles" / "proximal_distal_companion" / "chapters"
    chapters_dir.mkdir(parents=True)
    (chapters_dir / "ch01.qmd").write_text(
        f"https://github.com/D-sorganization/UpstreamDrift/blob/{SHA_A}/a.py\n",
        encoding="utf-8",
    )
    (root / "articles" / "proximal-distal-a-journey-through-the-swing.qmd").write_text(
        "{{< include proximal_distal_companion/chapters/ch01.qmd >}}\n",
        encoding="utf-8",
    )

    scanned, findings = pins.scan_site_pins(root)

    assert scanned == {SHA_A: ["/articles/proximal-distal-a-journey-through-the-swing.html"]}
    assert "/articles/proximal_distal_companion/chapters/ch01.html" not in scanned[SHA_A]
    assert findings == []


@pytest.mark.unit
def test_is_site_source_respects_quarto_render_exclusions() -> None:
    """_is_site_source must reject excluded trees and partials while accepting rendered pages (#4145)."""
    assert not pins._is_site_source(
        Path("articles/proximal_distal_companion/chapters/ch01_follow_the_energy.qmd")
    )
    assert not pins._is_site_source(
        Path("articles/tangent-hyperplane-contraction/textbook-main.qmd")
    )
    assert not pins._is_site_source(
        Path("articles/The_Geometry_of_Motion/quarto/volume2_content.qmd")
    )
    assert not pins._is_site_source(Path("critiques/INLINE_SUGGESTIONS.md"))
    assert not pins._is_site_source(Path("articles/chapters/_ch01.qmd"))
    assert pins._is_site_source(Path("articles/proximal-distal-a-journey-through-the-swing.qmd"))
    assert pins._is_site_source(Path("pages/overview.qmd"))
    assert pins._is_site_source(Path("index.qmd"))
