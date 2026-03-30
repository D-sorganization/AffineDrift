"""Tests for textbook unsupported-claim guardrails."""

from pathlib import Path

from scripts.check_textbook_claims import (
    AddedLine,
    _is_textbook_path,
    _parse_added_lines,
    find_unsupported_claims,
)


def test_is_textbook_path_accepts_repo_content_roots() -> None:
    """Known textbook/content roots should be included."""
    assert _is_textbook_path("articles/The_Physics_of_Golf/main.tex")
    assert _is_textbook_path("pages/about.qmd")
    assert _is_textbook_path("index.qmd")
    assert not _is_textbook_path("src/tools/reference_audit.py")


def test_parse_added_lines_tracks_file_and_line_numbers() -> None:
    """Unified diff parsing should recover added file lines."""
    diff_text = """diff --git a/articles/example.qmd b/articles/example.qmd
+++ b/articles/example.qmd
@@ -9,0 +10,2 @@
+A 200-pound golfer experiences 1200 N of force.
+The model is illustrative.
"""
    added = _parse_added_lines(diff_text)
    assert added == [
        AddedLine(
            path="articles/example.qmd",
            line_number=10,
            text="A 200-pound golfer experiences 1200 N of force.",
        ),
        AddedLine(
            path="articles/example.qmd",
            line_number=11,
            text="The model is illustrative.",
        ),
    ]


def test_find_unsupported_claims_flags_uncited_quantitative_claim(
    tmp_path: Path,
) -> None:
    """Quantitative textbook claims without support should fail."""
    article = tmp_path / "articles" / "example.qmd"
    article.parent.mkdir(parents=True)
    article.write_text(
        "Intro\nA 200-pound golfer experiences 1200--1500 N during the downswing.\n",
        encoding="utf-8",
    )
    findings = find_unsupported_claims(
        tmp_path,
        [
            AddedLine(
                path="articles/example.qmd",
                line_number=2,
                text="A 200-pound golfer experiences 1200--1500 N during the downswing.",
            )
        ],
    )
    assert findings == [
        "articles/example.qmd:2: unsupported quantitative/study claim without citation or caveat"
    ]


def test_find_unsupported_claims_allows_cited_or_illustrative_lines(
    tmp_path: Path,
) -> None:
    """Citations and explicit caveats should satisfy the guardrail."""
    cited = tmp_path / "articles" / "cited.qmd"
    cited.parent.mkdir(parents=True, exist_ok=True)
    cited.write_text(
        "A 200-pound golfer experiences 1200 N in this dataset \\citep{Smith2020}.\n",
        encoding="utf-8",
    )
    illustrative = tmp_path / "articles" / "illustrative.qmd"
    illustrative.write_text(
        "For an illustrative example, suppose a golfer weighs 90 kg.\n",
        encoding="utf-8",
    )

    findings = find_unsupported_claims(
        tmp_path,
        [
            AddedLine(
                path="articles/cited.qmd",
                line_number=1,
                text="A 200-pound golfer experiences 1200 N in this dataset \\citep{Smith2020}.",
            ),
            AddedLine(
                path="articles/illustrative.qmd",
                line_number=1,
                text="For an illustrative example, suppose a golfer weighs 90 kg.",
            ),
        ],
    )
    assert findings == []


def test_find_unsupported_claims_ignores_symbolic_math_without_claim_language(
    tmp_path: Path,
) -> None:
    """Symbolic dimensions like 2n should not be treated as magic-number prose."""
    article = tmp_path / "articles" / "symbolic.tex"
    article.parent.mkdir(parents=True, exist_ok=True)
    article.write_text(
        "A smooth manifold of dimension $2n$ has tangent bundle dimension $4n$.\n",
        encoding="utf-8",
    )
    findings = find_unsupported_claims(
        tmp_path,
        [
            AddedLine(
                path="articles/symbolic.tex",
                line_number=1,
                text="A smooth manifold of dimension $2n$ has tangent bundle dimension $4n$.",
            )
        ],
    )
    assert findings == []
