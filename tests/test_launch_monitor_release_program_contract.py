"""Publication contract for the governed launch-monitor research program."""

from pathlib import Path

ROOT = Path(__file__).parents[1]
ARTICLE = ROOT / "articles" / "Launch_Monitor_Technology_Review"


def test_professional_release_chapter_is_registered() -> None:
    main = (ARTICLE / "main.tex").read_text(encoding="utf-8")
    assert r"\input{sections/11-validation-program}" in main


def test_release_boundary_and_statistical_authority_are_explicit() -> None:
    chapter = (ARTICLE / "sections" / "11-validation-program.tex").read_text(encoding="utf-8")
    normalized_chapter = chapter.replace(r"\allowbreak{}", "")
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
        "8cd8ad04bf2904eedd0d8f10d2aa202e437e91fd",
        "70feeb4889ef4d030bdb426bd7ecb465c36ba41b",
        "5ea0d08821ee8a1cacb93d22239abddee4813fca",
        "08b4b013d8f58feb0a788fc67add29f64750da23",
        "fb4e6e41ac4980309e32dacceb957f4da02616b3",
        "a7b6dc437b45857e27cd07cccb56ff665826e342",
        "10d7f6fc38d27dd04324160090a7290f46d0cfd4",
        "6699129037d0adf8152e73bdae3fc2b75a2e15bfb16e25a4b3cfcec2448ac00e",
        "No expected-strokes baseline is bundled",
        "does not independently endorse",
        r"\path{is_strokes_gained=false}",
        "exact lie, context, target, and distance",
        "outside baseline support",
        "presentation and accessibility",
        "not statistical correctness or baseline validity",
        "1906d19fcace3284ae99d9dd8de213a0",
        "e2dabe8c062e4d63edc06c98f7eaf92e",
        "252 total",
        "72b06c034e73751dbacce8468505517a8500754d4d769cc89fed846611790173",
        "ebc1a24100b0e09ea39978127d6f1bcad3bd26bf6c4f3ae042680a833281d9c9",
        "zero analyzed pairs",
        "confirmatory_ready=false",
        "specialized grouped estimators",
        "not yet UpstreamDrift API operations",
        "protocol readiness is not reported",
    )
    for phrase in required:
        assert phrase in normalized_chapter


def test_running_header_uses_compact_chapter_mark() -> None:
    preamble = (ARTICLE / "preamble.tex").read_text(encoding="utf-8")
    assert r"\renewcommand{\chaptermark}[1]" in preamble
    assert r"\chaptername\ \thechapter" in preamble
