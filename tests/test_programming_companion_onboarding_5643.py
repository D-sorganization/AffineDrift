"""Regression guards for Programming Companion onboarding and datasets ledger (#5643)."""

from __future__ import annotations

from pathlib import Path

from scripts.generate_datasets_catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]


def test_models_hub_does_not_cite_closed_issue_4024() -> None:
    hub = (ROOT / "models" / "models.qmd").read_text(encoding="utf-8")
    assert "AffineDrift/issues/4024" not in hub
    assert "Unavailable until reviewed evidence is pinned" not in hub
    assert "verify_installation.py" in hub


def test_datasets_yml_declares_cc_by_for_first_party_data() -> None:
    catalog = load_catalog(ROOT / "data" / "datasets.yml")
    for entry in catalog.affinedrift:
        licence = entry.licence.lower()
        assert "cc by 4.0" in licence, entry.id
        assert "not yet declared" not in licence
        assert "web-07.8" not in licence


def test_resources_datasets_page_matches_catalog_licences() -> None:
    qmd = (ROOT / "resources" / "resources-datasets.qmd").read_text(encoding="utf-8")
    assert "WEB-07.8" not in qmd
    assert "Not yet declared" not in qmd
    assert "CC BY 4.0" in qmd


def test_datasets_catalog_header_points_at_copyright() -> None:
    text = (ROOT / "data" / "datasets.yml").read_text(encoding="utf-8")
    assert "COPYRIGHT.md" in text
    assert "WEB-07.7" in text
    assert "WEB-07.8" not in text
