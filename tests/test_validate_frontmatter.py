"""Tests for validate_frontmatter.py's title rule.

The check requires every article to have a title. It used to require it in the
YAML frontmatter specifically, which is wrong for a Quarto book: a
`{#sec-...}` anchor can only attach to a heading, never to a YAML key, so a
chapter that other chapters cross-reference has to carry its title in the body.
Demanding both rendered the title twice, which is what the book shipped until
#3702.
"""

from __future__ import annotations

from pathlib import Path

from scripts.validate_frontmatter import has_body_h1, validate_file


class TestHasBodyH1:
    """A title in the body counts, but only a real one."""

    def test_finds_a_level_one_heading(self) -> None:
        assert has_body_h1("\n# The Language of Motion\n\nSome prose.\n")

    def test_finds_a_heading_carrying_an_anchor(self) -> None:
        assert has_body_h1("\n# The Language of Motion {#sec-02_language_of_motion}\n")

    def test_rejects_a_level_two_heading(self) -> None:
        assert not has_body_h1("\n## A Section, Not A Title\n")

    def test_rejects_a_hash_inside_fenced_code(self) -> None:
        """`# comment` in a Python cell is not a heading.

        ch23 looked like it had four headings; all four were comments in code
        blocks, which is why it shipped with no anchor at all.
        """
        body = "\n```{python}\n# compute the mass matrix\nM = build()\n```\n"
        assert not has_body_h1(body)

    def test_rejects_a_bare_hash(self) -> None:
        assert not has_body_h1("\n#\n#notatag\n")

    def test_finds_a_heading_after_a_closed_fence(self) -> None:
        body = "\n```\n# not a heading\n```\n\n# A Real Heading\n"
        assert has_body_h1(body)


class TestValidateFile:
    """The file-level rule: titled somewhere, not titled twice."""

    def _write(self, tmp_path: Path, text: str) -> Path:
        path = tmp_path / "chapter.qmd"
        path.write_text(text, encoding="utf-8")
        return path

    def test_accepts_a_yaml_title(self, tmp_path: Path) -> None:
        path = self._write(tmp_path, '---\ntitle: "A Chapter"\n---\n\nProse.\n')
        assert validate_file(path) == []

    def test_accepts_a_body_h1_with_no_yaml_title(self, tmp_path: Path) -> None:
        path = self._write(tmp_path, '---\ndescription: "d"\n---\n\n# A Chapter {#sec-a}\n')
        assert validate_file(path) == []

    def test_rejects_frontmatter_with_no_title_anywhere(self, tmp_path: Path) -> None:
        path = self._write(tmp_path, '---\ndescription: "d"\n---\n\n## Only A Section\n')
        errors = validate_file(path)
        assert len(errors) == 1
        assert "title" in errors[0]

    def test_skips_a_file_with_no_frontmatter(self, tmp_path: Path) -> None:
        path = self._write(tmp_path, "Just prose, no frontmatter at all.\n")
        assert validate_file(path) == []
