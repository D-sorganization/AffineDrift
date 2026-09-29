"""Tests verifying robots.txt configuration and crawler renderability."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
ROBOTS_TXT_PATH = REPO_ROOT / "robots.txt"
QUARTO_YML_PATH = REPO_ROOT / "_quarto.yml"


def test_robots_txt_exists() -> None:
    """robots.txt must exist at repository root."""
    assert ROBOTS_TXT_PATH.is_file(), f"robots.txt not found at {ROBOTS_TXT_PATH}"


def test_robots_txt_basic_structure() -> None:
    """robots.txt must declare User-agent, Allow: /, and Sitemap."""
    content = ROBOTS_TXT_PATH.read_text(encoding="utf-8")
    lines = [
        line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")
    ]

    assert "User-agent: *" in lines, "robots.txt must include User-agent: *"
    assert "Allow: /" in lines, "robots.txt must include Allow: /"
    assert (
        "Sitemap: https://affinedrift.com/sitemap.xml" in lines
    ), "robots.txt must declare sitemap location"


def test_robots_txt_no_disallow_site_libs() -> None:
    """robots.txt must not disallow /site_libs/, which contains render-critical CSS and JS."""
    content = ROBOTS_TXT_PATH.read_text(encoding="utf-8")
    assert (
        "/site_libs" not in content
    ), "robots.txt must not disallow /site_libs/ (blocks search engine rendering)"


def test_robots_txt_no_crawl_delay() -> None:
    """robots.txt must not declare Crawl-delay, which Googlebot ignores."""
    content = ROBOTS_TXT_PATH.read_text(encoding="utf-8")
    assert not re.search(
        r"(?i)crawl-delay", content
    ), "robots.txt must not contain Crawl-delay directive"


def test_quarto_yml_declares_robots_txt_resource() -> None:
    """_quarto.yml must include robots.txt in project.resources for deployment."""
    assert QUARTO_YML_PATH.is_file(), f"_quarto.yml not found at {QUARTO_YML_PATH}"
    config = yaml.safe_load(QUARTO_YML_PATH.read_text(encoding="utf-8"))
    resources = config.get("project", {}).get("resources", [])
    assert "robots.txt" in resources, "robots.txt must be listed in _quarto.yml project.resources"


def test_render_critical_paths_are_crawlable() -> None:
    """Simulate URL inspection: critical render assets must not be blocked by any Disallow directive."""
    content = ROBOTS_TXT_PATH.read_text(encoding="utf-8")
    disallowed_paths: list[str] = []
    for line in content.splitlines():
        line = line.strip()
        if line.lower().startswith("disallow:"):
            parts = line.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                disallowed_paths.append(parts[1].strip())

    render_critical_paths = [
        "/site_libs/bootstrap/bootstrap.min.css",
        "/site_libs/quarto-html/quarto.js",
        "/css/machine-learning.css",
        "/js/mathjax-loader.js",
    ]

    for asset_path in render_critical_paths:
        for disallow in disallowed_paths:
            assert not asset_path.startswith(
                disallow
            ), f"Asset '{asset_path}' is blocked by 'Disallow: {disallow}' in robots.txt"
