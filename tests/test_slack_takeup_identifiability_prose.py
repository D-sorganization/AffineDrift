"""Regression and contract tests for Feynman review corrections on Slack Take-Up (#5476)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_PATH = ROOT / "articles/slack-takeup-identifiability.qmd"


def test_item_1_status_and_publish_state() -> None:
    """Item 1: Status reflects offline draft decision per Dieter's call (#5362/#5476)."""
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "draft: true" in text
    assert "listing: false" in text
    assert "Unpublished Draft Source" in text or "published as draft" in text
    assert "#5284" in text or "#5362" in text


def test_item_2_unit_count_and_damping() -> None:
    """Item 2: Section 3 unit count has seven unknowns and damping is not a Toy B parameter."""
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "**seven** unknowns" in text or "seven unknowns" in text
    assert "damping" in text.lower()
    assert (
        "omits a separate damping parameter" in text
        or "damping is not a toy b parameter" in text.lower()
    )


def test_item_3_abstract_dangling_only_when_clause() -> None:
    """Item 3: Abstract resolves the dangling 'only when' clause after 'seeing results'."""
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    # 'seeing results only when' was dangling; should be separated by parenthetical or punctuation
    assert "seeing results only when" not in text
    assert "pass bar (set by the author after seeing results) only when" in text or (
        "pass bar" in text and "after seeing results" in text and "only when" in text
    )


def test_item_4_stray_comma_after_row_space_of_j() -> None:
    """Item 4: Remove stray comma after 'row space of J,'."""
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "row space of $J$," not in text
    assert "row space of J," not in text


def test_item_5_critique_severity_wording() -> None:
    """Item 5: Critique severity uses 'open, High-severity critique'."""
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "open, **High**-severity critique" in text or "open, High-severity critique" in text
    # Ensure line 80 does not omit the severity tier or hyphen
    assert "open High critique" not in text


def test_item_6_bandwidth_bullet_links_to_clanks() -> None:
    """Item 6: Bandwidth bullet links impact contact to take-up clanks or @sec-toy-a."""
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    bandwidth_lines = [line for line in text.splitlines() if line.startswith("6. **Bandwidth.**")]
    assert bandwidth_lines, "Bandwidth bullet must be present"
    assert "take-up clanks" in bandwidth_lines[0] or "@sec-toy-a" in bandwidth_lines[0]
    assert "shorter than both the take-up clanks" in bandwidth_lines[0]


def test_item_7_each_movers_grip() -> None:
    """Item 7: 'each mover's grip' instead of 'each man's grip'."""
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "each mover's grip" in text
    assert "each man's grip" not in text


def test_item_8_us_spelling_pass() -> None:
    """Item 8: US spelling pass (wrench instead of spanner; centered, modeled, summarize)."""
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    assert "spanner" not in text.lower(), "Use US term 'wrench' instead of UK 'spanner'"
    assert "centred" not in text
    assert "modelled" not in text
    assert "summarise" not in text
    assert "wrench" in text.lower()
    assert "centered" in text
    assert "modeled" in text
    assert "summarize" in text


def test_item_9_appendix_renders_before_references_and_dates() -> None:
    """Item 9: Appendix renders before References, and dates record revisions."""
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    app_idx = text.find("## Appendix")
    ref_idx = text.find("## References")
    assert app_idx != -1 and ref_idx != -1, "Both Appendix and References must exist"
    assert app_idx < ref_idx, "Appendix must be placed before References so References is at end"
    assert 'date-modified: "2026-11-06"' in text
    assert 'last-reviewed: "2026-11-06"' in text
    assert "2026-11-01" in text, "Revision history should record the Nov 1 revision"
