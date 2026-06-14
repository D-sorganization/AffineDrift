"""Tests for rendered-page image asset budgets."""

from __future__ import annotations

from pathlib import Path

from scripts import check_image_budget
from scripts.optimize_images import build_manifest


def test_image_budget_flags_referenced_oversized_asset(tmp_path: Path) -> None:
    """A referenced image over the byte budget should fail the guard."""
    image_dir = tmp_path / "static" / "images"
    page_dir = tmp_path / "pages"
    image_dir.mkdir(parents=True)
    page_dir.mkdir()
    oversized_image = image_dir / "too-large.png"
    oversized_image.write_bytes(b"x" * (check_image_budget.DEFAULT_BUDGET_BYTES + 1))
    (page_dir / "example.qmd").write_text(
        '<img src="../static/images/too-large.png" alt="Oversized fixture">',
        encoding="utf-8",
    )

    result = check_image_budget.check_image_budget(tmp_path)

    assert result.has_errors
    assert "static/images/too-large.png" in result.errors[0]


def test_image_budget_passes_for_repository() -> None:
    """The checked-in rendered-page image references should fit the budget."""
    repo_root = Path(__file__).resolve().parents[1]

    result = check_image_budget.check_image_budget(repo_root)

    assert not result.has_errors, result.errors


def test_navbar_logo_asset_stays_small() -> None:
    """The site-wide navbar logo should remain small enough for every page."""
    repo_root = Path(__file__).resolve().parents[1]
    logo_path = repo_root / "logo" / "logo-navbar.png"

    assert logo_path.stat().st_size <= check_image_budget.NAVBAR_LOGO_BUDGET_BYTES


def test_app_icon_512_asset_stays_small() -> None:
    """The PWA 512px icon should stay palette-compressed for deploy."""
    repo_root = Path(__file__).resolve().parents[1]
    icon_path = repo_root / "logo" / "logo-icon-512.png"

    assert icon_path.stat().st_size <= check_image_budget.APP_ICON_512_BUDGET_BYTES


def test_image_optimizer_uses_existing_logo_source() -> None:
    """The optimizer manifest must not point at deleted high-resolution logos."""
    repo_root = Path(__file__).resolve().parents[1]
    manifest = build_manifest(repo_root)

    assert manifest.logo_source.is_file()
    assert manifest.logo_source.name == "logo-icon-512.png"
