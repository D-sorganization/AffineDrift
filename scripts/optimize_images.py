#!/usr/bin/env python3
"""Generate optimized site images from checked-in source assets."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageSequence

NAVBAR_LOGO_HEIGHT = 80
OG_CARD_SIZE = (1200, 630)
OG_LOGO_SIZE = (420, 420)
GIF_SIZE = (300, 184)
GIF_FRAME_STEP = 2
GIF_COLOR_COUNT = 128
GIF_DURATION_MS = 40
PNG_COMPRESS_LEVEL = 9
WEBP_QUALITY = 82
OG_BACKGROUND = (248, 250, 252)


@dataclass(frozen=True)
class OptimizationManifest:
    """Explicit source and output paths for site image derivatives."""

    logo_source: Path
    navbar_png: Path
    navbar_webp: Path
    og_card_png: Path
    fish_source: Path
    fish_gif: Path
    fish_poster_png: Path
    fish_poster_webp: Path


def _resolve(repo_root: Path, relative_path: str) -> Path:
    """Resolve a repo-relative path and reject paths outside the repo."""
    resolved = (repo_root / relative_path).resolve()
    if not resolved.is_relative_to(repo_root.resolve()):
        raise ValueError(f"path escapes repository root: {relative_path}")
    return resolved


def build_manifest(repo_root: Path) -> OptimizationManifest:
    """Build the explicit image optimization manifest."""
    return OptimizationManifest(
        logo_source=_resolve(repo_root, "logo/logo_transparent_1.png"),
        navbar_png=_resolve(repo_root, "logo/logo-navbar.png"),
        navbar_webp=_resolve(repo_root, "logo/logo-navbar.webp"),
        og_card_png=_resolve(repo_root, "logo/og-card.png"),
        fish_source=_resolve(repo_root, "static/images/A-Dead-Fish-Swims.gif"),
        fish_gif=_resolve(repo_root, "static/images/A-Dead-Fish-Swims-optimized.gif"),
        fish_poster_png=_resolve(repo_root, "static/images/A-Dead-Fish-Swims-poster.png"),
        fish_poster_webp=_resolve(repo_root, "static/images/A-Dead-Fish-Swims-poster.webp"),
    )


def _load_image(path: Path) -> Image.Image:
    """Load an image after validating that the source asset exists."""
    if not path.is_file():
        raise FileNotFoundError(path)
    return Image.open(path)


def _resize_by_height(image: Image.Image, height: int) -> Image.Image:
    """Resize an image to a target height while preserving aspect ratio."""
    if height <= 0:
        raise ValueError("height must be positive")
    width = round(image.width * (height / image.height))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _save_png(image: Image.Image, path: Path) -> None:
    """Save a PNG derivative with deterministic compression settings."""
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True, compress_level=PNG_COMPRESS_LEVEL)


def _save_webp(image: Image.Image, path: Path) -> None:
    """Save a WebP derivative for browsers that support it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="WEBP", quality=WEBP_QUALITY, method=6)


def optimize_navbar_logo(manifest: OptimizationManifest) -> None:
    """Create small navbar PNG and WebP logo derivatives."""
    logo = _load_image(manifest.logo_source).convert("RGBA")
    navbar_logo = _resize_by_height(logo, NAVBAR_LOGO_HEIGHT)
    _save_png(navbar_logo, manifest.navbar_png)
    _save_webp(navbar_logo, manifest.navbar_webp)


def optimize_og_card(manifest: OptimizationManifest) -> None:
    """Create an Open Graph PNG card with a centered logo."""
    logo = _load_image(manifest.logo_source).convert("RGBA")
    resized_logo = logo.resize(OG_LOGO_SIZE, Image.Resampling.LANCZOS)
    card = Image.new("RGB", OG_CARD_SIZE, OG_BACKGROUND)
    left = (OG_CARD_SIZE[0] - resized_logo.width) // 2
    top = (OG_CARD_SIZE[1] - resized_logo.height) // 2
    card.paste(resized_logo, (left, top), resized_logo)
    _save_png(card, manifest.og_card_png)


def _optimized_gif_frames(source: Image.Image) -> tuple[list[Image.Image], list[int]]:
    """Build a decimated and palette-reduced GIF frame sequence."""
    frames: list[Image.Image] = []
    durations: list[int] = []
    source_duration = int(source.info.get("duration", GIF_DURATION_MS))
    for frame_index, frame in enumerate(ImageSequence.Iterator(source)):
        if frame_index % GIF_FRAME_STEP != 0:
            continue
        resized_frame = frame.convert("RGBA").resize(GIF_SIZE, Image.Resampling.LANCZOS)
        palette_frame = resized_frame.convert(
            "P",
            palette=Image.Palette.ADAPTIVE,
            colors=GIF_COLOR_COUNT,
        )
        frames.append(palette_frame)
        durations.append(source_duration * GIF_FRAME_STEP)
    return frames, durations


def optimize_fish_animation(manifest: OptimizationManifest) -> None:
    """Create a smaller animated GIF and static poster derivatives."""
    source = _load_image(manifest.fish_source)
    frames, durations = _optimized_gif_frames(source)
    if not frames:
        raise ValueError("animated GIF did not produce any frames")
    manifest.fish_gif.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        manifest.fish_gif,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=durations,
        loop=0,
        disposal=2,
    )
    poster = frames[0].convert("RGBA")
    _save_png(poster, manifest.fish_poster_png)
    _save_webp(poster, manifest.fish_poster_webp)


def main() -> int:
    """Generate optimized image derivatives for the repository."""
    repo_root = Path(__file__).resolve().parent.parent
    manifest = build_manifest(repo_root)
    optimize_navbar_logo(manifest)
    optimize_og_card(manifest)
    optimize_fish_animation(manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
