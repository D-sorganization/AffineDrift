#!/usr/bin/env python3
"""Fail if #5590 core-theory figures lack pin provenance or regress to hand-drawn curves."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from scripts.core_theory_figure_provenance_data import load_manifest, pinned_figures

REPO_ROOT = Path(__file__).resolve().parent.parent
_MANIFEST = load_manifest()
ISSUE_5590_PINNED_FIGURES = pinned_figures()
HAND_DRAWN_LITERAL_MARKERS = tuple(_MANIFEST.get("forbidden_generator_literals", []))
FIGURES_DIR = REPO_ROOT / "articles/figures/core_theory"
GENERATORS = tuple(REPO_ROOT / rel for rel in _MANIFEST.get("generator_modules", []))
MODEL_LADDER = REPO_ROOT / "models/model-ladder.qmd"
FORBIDDEN_LADDER_PHRASE = str(_MANIFEST.get("model_ladder_forbidden_phrase", ""))
REQUIRED_LADDER_PHRASE = str(_MANIFEST.get("model_ladder_required_phrase", ""))


def _figure_embed_pattern(fig_name: str) -> re.Pattern[str]:
    escaped = re.escape(fig_name)
    return re.compile(
        rf"!\[([^\]]+)\]\([^\)]*{escaped}[^\)]*\)"
        rf"(?:\{{[^\}}]*fig-alt=\"(?P<alt>[^\"]+)\"[^\}}]*\}})?",
        re.DOTALL,
    )


def _iter_article_embeds(fig_name: str) -> list[tuple[str, str, str]]:
    pattern = _figure_embed_pattern(fig_name)
    embeds: list[tuple[str, str, str]] = []
    for article_path in sorted((REPO_ROOT / "articles").rglob("*.qmd")):
        content = article_path.read_text(encoding="utf-8")
        for match in pattern.finditer(content):
            rel = article_path.relative_to(REPO_ROOT).as_posix()
            embeds.append((rel, match.group(1), (match.group("alt") or "")))
    return embeds


def _declares_pin_provenance(caption: str, alt_text: str, pin_path: str) -> bool:
    wording = f"{caption} {alt_text}".lower()
    return pin_path.lower() in wording


def _declares_schematic_label(caption: str, alt_text: str) -> bool:
    return "schematic" in caption.lower() and "schematic" in alt_text.lower()


def check_pin_records() -> list[str]:
    errors: list[str] = []
    for pin_rel in set(ISSUE_5590_PINNED_FIGURES.values()):
        pin_path = REPO_ROOT / pin_rel
        if not pin_path.is_file():
            errors.append(f"Missing provenance record: {pin_rel}")
    return errors


def check_embed_provenance() -> list[str]:
    errors: list[str] = []
    for fig_name, pin_path in ISSUE_5590_PINNED_FIGURES.items():
        svg_path = FIGURES_DIR / fig_name
        if not svg_path.is_file():
            errors.append(f"Missing figure file: {svg_path.relative_to(REPO_ROOT)}")
        embeds = _iter_article_embeds(fig_name)
        if not embeds:
            errors.append(f"No Quarto embed found for {fig_name}")
            continue
        for article, caption, alt_text in embeds:
            if not (
                _declares_pin_provenance(caption, alt_text, pin_path)
                or _declares_schematic_label(caption, alt_text)
            ):
                errors.append(
                    f"{fig_name} in {article}: cite {pin_path} in caption/fig-alt "
                    "or declare schematic in both"
                )
    return errors


def check_generators_not_hand_drawn() -> list[str]:
    errors: list[str] = []
    for gen_path in GENERATORS:
        text = gen_path.read_text(encoding="utf-8")
        for marker in HAND_DRAWN_LITERAL_MARKERS:
            if marker in text:
                errors.append(f"Hand-drawn literal still present in {gen_path.name}: {marker!r}")
    return errors


def check_model_ladder_caption() -> list[str]:
    if not MODEL_LADDER.is_file():
        return [f"Missing {MODEL_LADDER.relative_to(REPO_ROOT)}"]
    text = MODEL_LADDER.read_text(encoding="utf-8")
    if FORBIDDEN_LADDER_PHRASE in text:
        return [
            "models/model-ladder.qmd still equates drift colour with "
            f"'{FORBIDDEN_LADDER_PHRASE}' (issue #5590 F15)"
        ]
    if REQUIRED_LADDER_PHRASE and REQUIRED_LADDER_PHRASE not in text:
        return [f"models/model-ladder.qmd missing required phrase: {REQUIRED_LADDER_PHRASE!r}"]
    return []


def run_checks() -> list[str]:
    errors: list[str] = []
    errors.extend(check_pin_records())
    errors.extend(check_embed_provenance())
    errors.extend(check_generators_not_hand_drawn())
    errors.extend(check_model_ladder_caption())
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors = run_checks()
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    print("core-theory figure provenance OK (#5590)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
