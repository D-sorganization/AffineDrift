"""Tests for the animated fish WebP derivative and its page markup."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from scripts.optimize_images import EXPECTED_OUTPUTS, build_manifest, check_manifest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_manifest_includes_animated_webp() -> None:
    """The optimizer manifest must list the animated WebP as an output."""
    manifest = build_manifest(REPO_ROOT)

    assert "fish_webp" in EXPECTED_OUTPUTS
    assert manifest.fish_webp.name == "A-Dead-Fish-Swims.webp"
    assert manifest.fish_webp.is_file()
    assert check_manifest(manifest, REPO_ROOT) == []


def test_animated_webp_is_animated_and_smaller_than_gif() -> None:
    """The WebP must have several frames and beat the optimized GIF on size."""
    manifest = build_manifest(REPO_ROOT)

    with Image.open(manifest.fish_webp) as webp:
        assert getattr(webp, "n_frames", 1) > 1
    assert manifest.fish_webp.stat().st_size < manifest.fish_gif.stat().st_size


def test_daydreams_page_uses_picture_with_reduced_motion_source() -> None:
    """The fish figure must serve the static poster under reduced motion."""
    page = (REPO_ROOT / "pages" / "daydreams-doodles.qmd").read_text(encoding="utf-8")

    assert "<picture>" in page
    assert 'media="(prefers-reduced-motion: reduce)"' in page
    assert "A-Dead-Fish-Swims-poster.webp" in page
    assert "static/images/A-Dead-Fish-Swims.webp" in page
    assert 'alt="Dead fish swimming upstream"' in page
