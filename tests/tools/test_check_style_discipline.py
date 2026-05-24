"""Tests for the website style-discipline checker.

The checker forbids visual-language drift in the website layout:
inline ``style="..."`` attributes in QMD pages outside ``articles/**``,
``linear-gradient`` declarations outside the design-token modules, and
6-digit hex colors outside ``css/tokens/**``. See EPIC #3140 task E2.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_style_discipline import (
    DEFAULT_CONFIG,
    StyleDisciplineConfig,
    check_repository,
    find_violations_in_text,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A minimal fake repo with the directory layout the checker expects."""
    (tmp_path / "css" / "tokens").mkdir(parents=True)
    (tmp_path / "css" / "components").mkdir(parents=True)
    (tmp_path / "pages").mkdir()
    (tmp_path / "articles" / "deep").mkdir(parents=True)
    return tmp_path


class TestFindViolationsInText:
    """find_violations_in_text classifies a single file's source."""

    def test_clean_qmd_returns_no_violations(self) -> None:
        text = '---\ntitle: "Home"\n---\n\nSome prose with no decoration.\n'
        assert find_violations_in_text(text, suffix=".qmd") == []

    def test_inline_style_attribute_is_flagged(self) -> None:
        text = '<div style="color: red">x</div>'
        violations = find_violations_in_text(text, suffix=".qmd")
        assert any(v.rule == "inline-style" for v in violations)

    def test_linear_gradient_is_flagged_in_qmd(self) -> None:
        text = "background: linear-gradient(135deg, #fff 0%, #000 100%);"
        violations = find_violations_in_text(text, suffix=".qmd")
        assert any(v.rule == "gradient" for v in violations)

    def test_hardcoded_hex_is_flagged_in_qmd(self) -> None:
        text = "<p>color: #2563eb</p>"
        violations = find_violations_in_text(text, suffix=".qmd")
        assert any(v.rule == "hardcoded-hex" for v in violations)

    def test_three_digit_hex_is_flagged(self) -> None:
        text = "<p>color: #abc</p>"
        violations = find_violations_in_text(text, suffix=".qmd")
        assert any(v.rule == "hardcoded-hex" for v in violations)

    def test_var_token_reference_is_not_flagged(self) -> None:
        text = '<p style="x">var(--color-primary-main)</p>'
        violations = find_violations_in_text(text, suffix=".qmd")
        assert not any(v.rule == "hardcoded-hex" for v in violations)

    def test_violation_carries_line_number(self) -> None:
        text = "line one\nline two with #abc123\nline three\n"
        violations = find_violations_in_text(text, suffix=".qmd")
        assert violations
        assert violations[0].line == 2


class TestCheckRepository:
    """check_repository walks the tree, honoring scope rules."""

    def test_clean_repo_passes(self, repo: Path) -> None:
        _write(repo / "index.qmd", "Clean home page.\n")
        _write(repo / "css" / "tokens" / "colors.css", ":root { --x: #abc; }\n")
        config = StyleDisciplineConfig(repo_root=repo)
        assert check_repository(config) == []

    def test_inline_style_in_top_level_qmd_fails(self, repo: Path) -> None:
        _write(repo / "index.qmd", '<div style="color: red">x</div>\n')
        violations = check_repository(StyleDisciplineConfig(repo_root=repo))
        assert any(v.rule == "inline-style" for v in violations)

    def test_articles_directory_is_allowlisted(self, repo: Path) -> None:
        _write(
            repo / "articles" / "deep" / "chapter.qmd",
            '<div style="color: red">x</div>\n',
        )
        violations = check_repository(StyleDisciplineConfig(repo_root=repo))
        assert not any(v.rule == "inline-style" for v in violations)

    def test_hardcoded_hex_in_css_outside_tokens_fails(self, repo: Path) -> None:
        _write(
            repo / "css" / "components" / "card.css",
            ".card { color: #2563eb; }\n",
        )
        violations = check_repository(StyleDisciplineConfig(repo_root=repo))
        assert any(v.rule == "hardcoded-hex" for v in violations)

    def test_hardcoded_hex_inside_tokens_is_allowed(self, repo: Path) -> None:
        _write(
            repo / "css" / "tokens" / "colors.css",
            ":root { --color-primary-main: #0f4c75; }\n",
        )
        violations = check_repository(StyleDisciplineConfig(repo_root=repo))
        assert not any(v.rule == "hardcoded-hex" for v in violations)

    def test_gradient_in_qmd_fails(self, repo: Path) -> None:
        _write(
            repo / "pages" / "x.qmd",
            "<style>div { background: linear-gradient(135deg,#fff,#000); }</style>\n",
        )
        violations = check_repository(StyleDisciplineConfig(repo_root=repo))
        assert any(v.rule == "gradient" for v in violations)

    def test_violation_record_includes_relative_path(self, repo: Path) -> None:
        _write(repo / "index.qmd", '<div style="x">y</div>\n')
        violations = check_repository(StyleDisciplineConfig(repo_root=repo))
        flagged = [v for v in violations if v.rule == "inline-style"]
        assert flagged
        assert flagged[0].path == "index.qmd"


class TestContractEnforcement:
    """DbC: check_repository pre-conditions reject nonsense inputs."""

    def test_missing_repo_root_raises(self, tmp_path: Path) -> None:
        bogus = tmp_path / "does-not-exist"
        from src.core.contracts import ContractViolationError

        with pytest.raises(ContractViolationError):
            check_repository(StyleDisciplineConfig(repo_root=bogus))


class TestDefaultConfig:
    """The shipped DEFAULT_CONFIG matches the epic's scope."""

    def test_scans_top_level_qmd_pages(self) -> None:
        assert "*.qmd" in DEFAULT_CONFIG.qmd_globs
        assert any("pages/" in g for g in DEFAULT_CONFIG.qmd_globs)

    def test_excludes_articles_directory(self) -> None:
        assert any("articles" in pattern for pattern in DEFAULT_CONFIG.qmd_exclude_globs)

    def test_token_directory_is_allowed_for_hex(self) -> None:
        assert any("tokens" in pattern for pattern in DEFAULT_CONFIG.hex_allow_globs)
