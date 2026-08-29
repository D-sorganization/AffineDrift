"""Contracts for the deterministic public-site render manifest (WEB-A)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.public_site_manifest import (
    MANIFEST_SCHEMA_VERSION,
    build_manifest,
    write_manifest,
)


def _write_page(path: Path, *, title: str, h1: str, extra: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        (
            "<!doctype html><html><head>"
            f'<title>{title}</title><link rel="canonical" href="https://affinedrift.com/{path.name}">'
            '</head><body><main id="quarto-document-content">'
            f"<h1>{h1}</h1>{extra}</main></body></html>"
        ),
        encoding="utf-8",
    )


def test_build_manifest_classifies_and_sorts_every_public_html_page(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _write_page(docs / "index.html", title="AffineDrift", h1="AffineDrift")
    _write_page(docs / "pages/technology.html", title="Technology", h1="Technology")
    _write_page(docs / "articles/example.html", title="Example", h1="Example")
    _write_page(
        docs / "articles/The_Physics_of_Golf/quarto/ch01.html",
        title="Chapter 1",
        h1="Chapter 1",
    )
    _write_page(docs / "404.html", title="Not Found", h1="Page Not Found")
    _write_page(docs / "site_libs/quarto-nav/help.html", title="Support", h1="Support")

    manifest = build_manifest(docs, source_root=tmp_path, source_revision="abc123")

    assert manifest["schema_version"] == MANIFEST_SCHEMA_VERSION
    assert manifest["source_revision"] == "abc123"
    assert manifest["page_count"] == 5
    assert [page["route"] for page in manifest["pages"]] == [
        "/",
        "/404.html",
        "/articles/example.html",
        "/articles/The_Physics_of_Golf/quarto/ch01.html",
        "/pages/technology.html",
    ]
    assert [page["page_kind"] for page in manifest["pages"]] == [
        "home",
        "system",
        "article",
        "textbook",
        "hub",
    ]
    assert manifest["verification"]["every_page"] == {
        "viewports": ["mobile", "desktop"],
        "themes": ["light", "dark"],
    }


def test_manifest_maps_route_to_existing_canonical_source(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    source = tmp_path / "pages/technology.qmd"
    source.parent.mkdir(parents=True)
    source.write_text('---\ntitle: "Technology"\n---\n', encoding="utf-8")
    _write_page(docs / "pages/technology.html", title="Technology", h1="Technology")

    manifest = build_manifest(docs, source_root=tmp_path)

    assert manifest["pages"][0]["source"] == "pages/technology.qmd"


@pytest.mark.parametrize("missing", ["docs", "empty"])
def test_manifest_fails_closed_for_missing_or_empty_render(tmp_path: Path, missing: str) -> None:
    docs = tmp_path / "docs"
    if missing == "empty":
        docs.mkdir()

    with pytest.raises(ValueError, match="rendered public HTML"):
        build_manifest(docs, source_root=tmp_path)


def test_manifest_records_static_h1_count_for_browser_visibility_gate(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _write_page(
        docs / "index.html",
        title="AffineDrift",
        h1="AffineDrift",
        extra="<h1>Duplicate</h1>",
    )

    manifest = build_manifest(docs, source_root=tmp_path)

    assert manifest["pages"][0]["static_h1_count"] == 2


def test_write_manifest_is_deterministic_and_round_trippable(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    _write_page(docs / "index.html", title="AffineDrift", h1="AffineDrift")
    target = tmp_path / "artifacts/public-site-manifest.json"

    first = write_manifest(build_manifest(docs, source_root=tmp_path), target)
    second = write_manifest(build_manifest(docs, source_root=tmp_path), target)

    assert first == second
    assert json.loads(target.read_text(encoding="utf-8"))["page_count"] == 1
