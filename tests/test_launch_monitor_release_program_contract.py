"""Publication contract for the governed launch-monitor research program."""

from pathlib import Path

ROOT = Path(__file__).parents[1]
ARTICLE = ROOT / "articles" / "Launch_Monitor_Technology_Review"


def test_professional_release_chapter_is_registered() -> None:
    main = (ARTICLE / "main.tex").read_text(encoding="utf-8")
    assert r"\input{sections/11-validation-program}" in main


def test_release_boundary_and_statistical_authority_are_explicit() -> None:
    chapter = (ARTICLE / "sections" / "11-validation-program.tex").read_text(encoding="utf-8")
    required = (
        "Release A",
        "Release B",
        "UpstreamDrift",
        "paired-device",
        "unavailable",
        "player identity",
        "ShotLink",
        "not eligible for vendor-model training",
        "96,901",
        "12.256",
        "source-stratified",
        "model_campaign_manifest.json",
        "retired_non_group_safe",
        "no vendor-labelled surrogate is currently eligible",
    )
    for phrase in required:
        assert phrase in chapter


def test_running_header_uses_compact_chapter_mark() -> None:
    preamble = (ARTICLE / "preamble.tex").read_text(encoding="utf-8")
    assert r"\renewcommand{\chaptermark}[1]" in preamble
    assert r"\chaptername\ \thechapter" in preamble
