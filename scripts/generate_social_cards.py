#!/usr/bin/env python3
"""Generate per-book/series Open Graph social card images at build time.

The site-wide card (`logo/og-card.png`, see `scripts/optimize_images.py`) is
used as the fallback for every page. Book and series landing pages override it
with a card carrying that book's title, a badge, and the site signature
graphic, so a link to a specific book renders distinctly in a social preview.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CARD_SIZE = (1200, 630)
LOGO_SIZE = (160, 160)
MARGIN = 80
BACKGROUND = (248, 250, 252)
BADGE_BACKGROUND = (30, 64, 175)
BADGE_TEXT_COLOR = (255, 255, 255)
BADGE_FONT_SIZE = 28
BADGE_PADDING = (20, 10)
TITLE_COLOR = (15, 23, 42)
TITLE_FONT_SIZE = 56
TITLE_LINE_HEIGHT = 68
PNG_COMPRESS_LEVEL = 9


@dataclass(frozen=True)
class SocialCard:
    """One book or series social card definition."""

    card_id: str
    title: str
    badge: str


# The proximal-to-distal monograph is omitted: its index.qmd is a locked
# publication source (scripts/verify_proximal_distal_projection.py), so its
# front matter cannot gain an Open Graph override outside a projection bump.
SOCIAL_CARDS: tuple[SocialCard, ...] = (
    SocialCard("physics-of-golf", "The Physics of Golf", "Textbook"),
    SocialCard("geometry-of-motion", "The Geometry of Motion", "Book Series"),
)


def _resolve(repo_root: Path, relative_path: str) -> Path:
    """Resolve a repo-relative path and reject paths outside the repo."""
    resolved = (repo_root / relative_path).resolve()
    if not resolved.is_relative_to(repo_root.resolve()):
        raise ValueError(f"path escapes repository root: {relative_path}")
    return resolved


def output_path(repo_root: Path, card: SocialCard) -> Path:
    """Return the checked-in output path for a given social card."""
    return _resolve(repo_root, f"logo/social-cards/{card.card_id}.png")


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load a scalable default font, avoiding a dependency on system fonts."""
    return ImageFont.load_default(size=size)


def _wrap_title(
    draw: ImageDraw.ImageDraw, title: str, font: ImageFont.FreeTypeFont, max_width: int
) -> list[str]:
    """Wrap a title into lines that fit within the card's text column."""
    words = title.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_card(logo_source: Path, card: SocialCard) -> Image.Image:
    """Compose a single per-book/series Open Graph card image."""
    if not logo_source.is_file():
        raise FileNotFoundError(logo_source)

    canvas = Image.new("RGB", CARD_SIZE, BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    logo = Image.open(logo_source).convert("RGBA").resize(LOGO_SIZE, Image.Resampling.LANCZOS)
    logo_position = (
        CARD_SIZE[0] - MARGIN - LOGO_SIZE[0],
        CARD_SIZE[1] - MARGIN - LOGO_SIZE[1],
    )
    canvas.paste(logo, logo_position, logo)

    badge_font = _load_font(BADGE_FONT_SIZE)
    badge_text = card.badge.upper()
    badge_padding_x, badge_padding_y = BADGE_PADDING
    badge_text_width = draw.textlength(badge_text, font=badge_font)
    badge_box = (
        MARGIN,
        MARGIN,
        MARGIN + badge_text_width + 2 * badge_padding_x,
        MARGIN + BADGE_FONT_SIZE + 2 * badge_padding_y,
    )
    draw.rounded_rectangle(badge_box, radius=8, fill=BADGE_BACKGROUND)
    draw.text(
        (MARGIN + badge_padding_x, MARGIN + badge_padding_y),
        badge_text,
        font=badge_font,
        fill=BADGE_TEXT_COLOR,
    )

    title_font = _load_font(TITLE_FONT_SIZE)
    title_top = badge_box[3] + 40
    max_title_width = CARD_SIZE[0] - 2 * MARGIN
    for line_index, line in enumerate(_wrap_title(draw, card.title, title_font, max_title_width)):
        draw.text(
            (MARGIN, title_top + line_index * TITLE_LINE_HEIGHT),
            line,
            font=title_font,
            fill=TITLE_COLOR,
        )

    return canvas


def generate(repo_root: Path, logo_source: Path) -> None:
    """Render and write every configured social card into the repository."""
    for card in SOCIAL_CARDS:
        image = render_card(logo_source, card)
        path = output_path(repo_root, card)
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, format="PNG", optimize=True, compress_level=PNG_COMPRESS_LEVEL)


def check(repo_root: Path) -> list[str]:
    """Return validation errors for checked-in per-book/series social cards."""
    errors: list[str] = []
    for card in SOCIAL_CARDS:
        path = output_path(repo_root, card)
        if not path.is_file():
            errors.append(f"missing social card: {path.relative_to(repo_root)}")
    return errors


def main() -> int:
    """Generate or check per-book/series social card derivatives."""
    parser = argparse.ArgumentParser(description="Generate per-book/series social cards")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate checked-in social cards without rewriting binary files",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    logo_source = _resolve(repo_root, "logo/logo-icon-512.png")

    if args.check:
        errors = check(repo_root)
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        if errors:
            return 1
        print("Social cards are present.")
        return 0

    generate(repo_root, logo_source)
    return 0


if __name__ == "__main__":
    sys.exit(main())
