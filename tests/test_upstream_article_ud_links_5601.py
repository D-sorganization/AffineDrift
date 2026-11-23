"""Regression guards for governed UpstreamDrift article permalinks (#5601)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import check_upstream_article_ud_links as article_cli
from src.tools import upstream_article_ud_links as article_links

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/companion/upstream_article_link_pins.json"
PDE = ROOT / "articles/proximal-distal-energy-transfer.qmd"
SHOT_README = ROOT / "articles/shot_pattern_analysis/generators/README.md"
NULL_CHAPTER = ROOT / "articles/after-one-solution-null-space-exploration.qmd"
CANONICAL_PDE = "b700e58941205af6f673f13ebbffcd30f8cca9d8"
CANONICAL_SHOT = "d56e3709e65a01f70dbd1a8db86856a160a8559d"


@pytest.mark.unit
def test_contract_loads() -> None:
    document = article_links.load_contract(CONTRACT)
    assert document["schema_version"] == article_links.SCHEMA
    assert len(document["governed_sources"]) >= 2


@pytest.mark.unit
def test_no_floating_main_under_articles() -> None:
    document = article_links.load_contract(CONTRACT)
    scan_roots = list(document.get("floating_main_scan_roots") or ["articles"])
    findings = article_links.find_floating_main_links(ROOT, scan_roots)
    assert findings == [], "\n".join(findings)


@pytest.mark.unit
def test_proximal_distal_monograph_uses_governed_pin() -> None:
    text = PDE.read_text(encoding="utf-8")
    assert CANONICAL_PDE in text
    assert "UpstreamDrift/tree/main/" not in text
    assert "UpstreamDrift/blob/main/" not in text


@pytest.mark.unit
def test_shot_pattern_readme_pins_release_assets() -> None:
    text = SHOT_README.read_text(encoding="utf-8")
    assert CANONICAL_SHOT in text
    assert "RELEASE_ASSETS.json" in text
    assert "UpstreamDrift/blob/main/" not in text


@pytest.mark.unit
def test_null_space_article_includes_implementation_bridge() -> None:
    text = NULL_CHAPTER.read_text(encoding="utf-8")
    assert "upstream-implementation/null-space-after-one-solution" in text
    assert "ed446ef480147110cc2d3058b707525507f4cb86" in text


@pytest.mark.unit
def test_checker_cli_passes_skip_remote() -> None:
    assert (
        article_cli.main(["--root", str(ROOT), "--contract", str(CONTRACT), "--skip-remote"]) == 0
    )


@pytest.mark.integration
def test_governed_remote_paths_exist() -> None:
    document = article_links.load_contract(CONTRACT)
    findings = article_links.verify_remote_paths(document)
    assert findings == [], "\n".join(findings)
