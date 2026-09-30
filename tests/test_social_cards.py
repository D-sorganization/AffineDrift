"""Tests for per-book/series Open Graph social card generation (issue #4578)."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scripts.generate_social_cards import (
    CARD_SIZE,
    SOCIAL_CARDS,
    check,
    generate,
    output_path,
    render_card,
)


def _make_logo(path: Path) -> None:
    """Write a minimal placeholder logo source image for tests."""
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (512, 512), (10, 20, 30, 255)).save(path)


def test_check_reports_every_missing_card(tmp_path: Path) -> None:
    """A repository with no generated cards should fail the check for each one."""
    errors = check(tmp_path)

    assert len(errors) == len(SOCIAL_CARDS)
    for card in SOCIAL_CARDS:
        assert any(card.card_id in error for error in errors)


def test_generate_writes_one_card_per_series(tmp_path: Path) -> None:
    """Generation should produce a correctly sized PNG for every configured card."""
    logo_source = tmp_path / "logo" / "logo-icon-512.png"
    _make_logo(logo_source)

    generate(tmp_path, logo_source)

    for card in SOCIAL_CARDS:
        path = output_path(tmp_path, card)
        assert path.is_file()
        with Image.open(path) as image:
            assert image.size == CARD_SIZE

    assert check(tmp_path) == []


def test_render_card_requires_existing_logo(tmp_path: Path) -> None:
    """Rendering must fail loudly rather than silently skip a missing source asset."""
    missing_logo = tmp_path / "missing-logo.png"

    with pytest.raises(FileNotFoundError):
        render_card(missing_logo, SOCIAL_CARDS[0])


def test_social_cards_checked_into_repository() -> None:
    """The generated per-book/series cards must be committed, like the site-wide card."""
    repo_root = Path(__file__).resolve().parents[1]

    assert check(repo_root) == []


@pytest.mark.parametrize(
    ("page_path", "card_id"),
    [
        ("articles/The_Physics_of_Golf/quarto/index.qmd", "physics-of-golf"),
        ("articles/The_Geometry_of_Motion/quarto/index.qmd", "geometry-of-motion"),
    ],
)
def test_landing_page_overrides_open_graph_image(page_path: str, card_id: str) -> None:
    """Each book/series landing page must override the site-wide OG/Twitter image."""
    repo_root = Path(__file__).resolve().parents[1]
    frontmatter = (repo_root / page_path).read_text(encoding="utf-8").split("---")[1]

    assert f"logo/social-cards/{card_id}.png" in frontmatter
