"""Tests for the advisory readability checker (WEB-12.5).

Flesch-Kincaid grade level for lay blocks, the ``summary-plain``
frontmatter field, and hub pages, per the WEB-12.1 threshold (lay block
<= grade 10). See CLAUDE.md "Content Authoring" and epic E12.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_readability import (
    DEFAULT_HUB_PAGES,
    ReadabilityConfig,
    check_repository,
    count_syllables,
    extract_lay_blocks,
    extract_summary_plain,
    main,
    score_prose,
    strip_code_and_math,
    write_json_report,
)

SIMPLE_TEXT = "The cat sat on the mat. It was a warm day. The dog ran fast."
COMPLEX_TEXT = (
    "The affine control-theoretic decomposition disambiguates autonomous "
    "drift dynamics from declared-input superposition contributions within "
    "the constrained multibody biomechanical system."
)

REAL_LAY_SECTION = """
```{=html}
<section class="laymans-terms">
  <h2>
  <button type="button" class="laymans-terms-header" aria-expanded="false">
    <span class="laymans-terms-header-title">In Layman's Terms</span>
  </button>
  </h2>
  <div class="laymans-terms-content">
    <div class="laymans-terms-inner">
      <p class="laymans-terms-intro">A plain-language overview.</p>
      <div class="laymans-item">
        <h3>Why It Matters</h3>
        <p>The cat sat on the mat. It was a warm day.</p>
      </div>
    </div>
  </div>
</section>
```
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestCountSyllables:
    def test_single_vowel_group(self) -> None:
        assert count_syllables("cat") == 1

    def test_silent_trailing_e_is_dropped(self) -> None:
        assert count_syllables("like") == 1

    def test_le_ending_keeps_final_syllable(self) -> None:
        assert count_syllables("simple") == 2

    def test_never_returns_zero(self) -> None:
        assert count_syllables("a") == 1


class TestStripCodeAndMath:
    def test_removes_fenced_code(self) -> None:
        text = "Prose before.\n```python\nx = 1\n```\nProse after."
        stripped = strip_code_and_math(text)
        assert "x = 1" not in stripped

    def test_removes_inline_math(self) -> None:
        assert "\\dot{x}" not in strip_code_and_math("The rate $\\dot{x} = f(x)$ is drift.")

    def test_removes_display_math(self) -> None:
        assert "mc^2" not in strip_code_and_math("Energy: $$E = mc^2$$ follows.")

    def test_removes_quarto_shortcode(self) -> None:
        text = "{{< include ../_includes/boundary.qmd >}}\nReal prose here."
        stripped = strip_code_and_math(text)
        assert "include" not in stripped
        assert "Real prose here." in stripped


class TestScoreProse:
    def test_simple_sentences_score_low(self) -> None:
        score = score_prose(SIMPLE_TEXT)
        assert score is not None
        assert score.grade < 10

    def test_complex_sentence_scores_high(self) -> None:
        score = score_prose(COMPLEX_TEXT)
        assert score is not None
        assert score.grade > 10

    def test_code_and_math_only_returns_none(self) -> None:
        assert score_prose("```python\nx = 1\n```\n$$E = mc^2$$") is None

    def test_word_count_reflects_prose_only(self) -> None:
        score = score_prose(SIMPLE_TEXT)
        assert score is not None
        assert score.word_count == 15

    def test_html_tags_are_stripped(self) -> None:
        score = score_prose('<div class="x"><p>The cat sat on the mat.</p></div>')
        assert score is not None
        assert score.word_count == 6

    def test_markdown_link_keeps_link_text(self) -> None:
        score = score_prose("See [the glossary](glossary.html) for more detail on this topic.")
        assert score is not None
        assert score.word_count == 9


class TestExtractLayBlocks:
    def test_extracts_prose_from_section(self) -> None:
        blocks = extract_lay_blocks(REAL_LAY_SECTION)
        assert len(blocks) == 1
        assert "cat sat on the mat" in blocks[0]

    def test_excludes_header_chrome_before_content_marker(self) -> None:
        blocks = extract_lay_blocks(REAL_LAY_SECTION)
        assert (
            "laymans-terms-header-title" not in blocks[0]
            or "In Layman" not in blocks[0].split('laymans-terms-content"')[0]
        )

    def test_no_section_returns_empty_list(self) -> None:
        assert extract_lay_blocks("Just an ordinary paragraph.") == []


class TestExtractSummaryPlain:
    def test_reads_frontmatter_field(self) -> None:
        content = '---\ntitle: "X"\nsummary-plain: "A short plain summary."\n---\nBody.\n'
        assert extract_summary_plain(content) == "A short plain summary."

    def test_missing_field_returns_none(self) -> None:
        content = '---\ntitle: "X"\n---\nBody.\n'
        assert extract_summary_plain(content) is None

    def test_no_frontmatter_returns_none(self) -> None:
        assert extract_summary_plain("No frontmatter here.") is None


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "articles").mkdir()
    (tmp_path / "pages").mkdir()
    return tmp_path


class TestCheckRepository:
    def test_finds_lay_block_over_threshold(self, repo: Path) -> None:
        content = f'---\ntitle: "X"\n---\n\n{REAL_LAY_SECTION.replace("The cat sat on the mat. It was a warm day.", COMPLEX_TEXT)}\n'
        _write(repo / "articles" / "a.qmd", content)
        findings = check_repository(ReadabilityConfig(repo_root=repo))
        lay_findings = [f for f in findings if f.layer == "lay-block"]
        assert len(lay_findings) == 1
        assert lay_findings[0].over_threshold
        assert lay_findings[0].path == "articles/a.qmd"

    def test_finds_lay_block_under_threshold(self, repo: Path) -> None:
        _write(repo / "articles" / "a.qmd", f'---\ntitle: "X"\n---\n\n{REAL_LAY_SECTION}\n')
        findings = check_repository(ReadabilityConfig(repo_root=repo))
        lay_findings = [f for f in findings if f.layer == "lay-block"]
        assert len(lay_findings) == 1
        assert not lay_findings[0].over_threshold

    def test_finds_summary_plain(self, repo: Path) -> None:
        content = f'---\ntitle: "X"\nsummary-plain: "{COMPLEX_TEXT}"\n---\nBody.\n'
        _write(repo / "pages" / "hub.qmd", content)
        findings = check_repository(ReadabilityConfig(repo_root=repo))
        summary_findings = [f for f in findings if f.layer == "summary-plain"]
        assert len(summary_findings) == 1
        assert summary_findings[0].over_threshold

    def test_scores_hub_pages_by_body(self, repo: Path) -> None:
        _write(repo / "index.qmd", f'---\ntitle: "Home"\n---\n\n{COMPLEX_TEXT}\n')
        findings = check_repository(ReadabilityConfig(repo_root=repo, hub_pages=("index.qmd",)))
        hub_findings = [f for f in findings if f.layer == "hub-page"]
        assert len(hub_findings) == 1
        assert hub_findings[0].path == "index.qmd"
        assert hub_findings[0].over_threshold

    def test_non_hub_page_is_not_scored_as_hub_page(self, repo: Path) -> None:
        _write(repo / "articles" / "other.qmd", f'---\ntitle: "Other"\n---\n\n{COMPLEX_TEXT}\n')
        findings = check_repository(ReadabilityConfig(repo_root=repo, hub_pages=("index.qmd",)))
        assert not [f for f in findings if f.layer == "hub-page"]

    def test_clean_repo_returns_empty(self, repo: Path) -> None:
        _write(repo / "articles" / "a.qmd", '---\ntitle: "X"\n---\nOrdinary prose.\n')
        assert check_repository(ReadabilityConfig(repo_root=repo)) == []


class TestContractEnforcement:
    def test_missing_repo_root_raises(self, tmp_path: Path) -> None:
        from src.core.contracts import ContractViolationError

        with pytest.raises(ContractViolationError):
            check_repository(ReadabilityConfig(repo_root=tmp_path / "does-not-exist"))

    def test_non_positive_threshold_raises(self, repo: Path) -> None:
        from src.core.contracts import ContractViolationError

        with pytest.raises(ContractViolationError):
            check_repository(ReadabilityConfig(repo_root=repo, threshold=0))


class TestWriteJsonReport:
    def test_writes_expected_shape(self, tmp_path: Path, repo: Path) -> None:
        _write(repo / "articles" / "a.qmd", f'---\ntitle: "X"\n---\n\n{REAL_LAY_SECTION}\n')
        findings = check_repository(ReadabilityConfig(repo_root=repo))
        report_path = tmp_path / "out" / "readability-report.json"
        write_json_report(findings, report_path, threshold=10.0)
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        assert payload["threshold"] == 10.0
        assert payload["scored"] == len(findings)
        assert len(payload["findings"]) == len(findings)


class TestMain:
    def test_exit_zero_when_clean(
        self, repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _write(repo / "articles" / "a.qmd", f'---\ntitle: "X"\n---\n\n{REAL_LAY_SECTION}\n')
        report = tmp_path / "report.json"
        code = main([str(repo), "--report", str(report)])
        assert code == 0
        assert report.exists()

    def test_exit_one_when_over_threshold(self, repo: Path, tmp_path: Path) -> None:
        content = f'---\ntitle: "X"\n---\n\n{REAL_LAY_SECTION.replace("The cat sat on the mat. It was a warm day.", COMPLEX_TEXT)}\n'
        _write(repo / "articles" / "a.qmd", content)
        report = tmp_path / "report.json"
        code = main([str(repo), "--report", str(report)])
        assert code == 1


class TestDefaultHubPages:
    def test_includes_home_page(self) -> None:
        assert "index.qmd" in DEFAULT_HUB_PAGES

    def test_includes_overview_and_tools(self) -> None:
        assert "pages/overview.qmd" in DEFAULT_HUB_PAGES
        assert "pages/tools.qmd" in DEFAULT_HUB_PAGES
