"""Unit tests for markdown and Qmd formatting linting rules (Issue #3919 and #3923).

Validates:
- No double section numbering in documents with `number-sections: true`.
- Table math pipes are properly escaped or written using norm notation (\\lVert...\\rVert).
- Heading levels do not skip levels (e.g. H1 -> H3, H2 -> H4, H3 -> H5).
- No orphan defense/rebuttal headings exist at the top section level under subsections.
- Repository and model pages contain canonical GitHub repository URLs and clone commands.
- Emoji consistency in learning paths and development roadmap.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def extract_yaml_metadata(lines: list[str]) -> tuple[dict[str, str], int]:
    """Extract frontmatter metadata and the starting line index of the body."""
    yaml_lines: list[str] = []
    yaml_count = 0
    body_start = 0

    for idx, line in enumerate(lines):
        if line.strip() == "---":
            yaml_count += 1
            if yaml_count == 2:
                body_start = idx + 1
                break
            continue
        if yaml_count == 1:
            yaml_lines.append(line)

    metadata: dict[str, str] = {}
    for yl in yaml_lines:
        if ":" in yl:
            k, v = yl.split(":", 1)
            metadata[k.strip()] = v.strip()
    return metadata, body_start


def extract_qmd_headings(lines: list[str], body_start: int) -> list[tuple[int, int, str, bool]]:
    """Extract headings with (line_number, heading_level, title, in_callout)."""
    headings: list[tuple[int, int, str, bool]] = []
    in_code = False
    in_callout = False

    for idx, line in enumerate(lines[body_start:], start=body_start + 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.strip().startswith(("::: {.callout-", "::: callout-")):
            in_callout = True
            continue
        if line.strip() == ":::" and in_callout:
            in_callout = False
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            headings.append((idx, len(m.group(1)), m.group(2).strip(), in_callout))

    return headings


def parse_qmd_structure(
    content: str,
) -> tuple[dict[str, str], list[tuple[int, int, str, bool]]]:
    """Parse YAML metadata and headings (line_num, level, title, in_callout) from Qmd."""
    lines = content.splitlines()
    metadata, body_start = extract_yaml_metadata(lines)
    headings = extract_qmd_headings(lines, body_start)
    return metadata, headings


class TestDoubleSectionNumbering:
    """Verify that articles with number-sections do not hand-number headings."""

    @pytest.mark.parametrize(
        "rel_path",
        [
            "articles/sources-of-nonlinearity.qmd",
            "articles/superposition.qmd",
            "articles/controllability-drift-ratio.qmd",
            "articles/intentional-constraint-collapse.qmd",
        ],
    )
    def test_no_manual_heading_numbers_when_numbered(self, rel_path: str) -> None:
        file_path = REPO_ROOT / rel_path
        assert file_path.exists(), f"File {rel_path} not found"

        content = file_path.read_text(encoding="utf-8")
        _, headings = parse_qmd_structure(content)

        defects = []
        for line_num, level, title, in_callout in headings:
            if not in_callout:
                if re.match(r"^\d+(\.\d+)*\.?\s+", title):
                    defects.append(f"Line {line_num} (H{level}): '{title}'")

        assert not defects, (
            f"Found manual section numbering in {rel_path} where Quarto auto-numbering is enabled:\n"
            + "\n".join(defects)
        )


class TestTableMathPipeIntegrity:
    """Verify tables with math formulas do not break due to unescaped pipes."""

    def test_rotation_converter_table_pipes(self) -> None:
        file_path = REPO_ROOT / "articles/rotation-converter.qmd"
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Find the representations table
        in_table = False
        expected_cols = 3
        for idx, line in enumerate(lines, 1):
            if "| Representation | Parameters | Key property |" in line:
                in_table = True
                continue
            if in_table:
                if not line.strip().startswith("|"):
                    break
                if line.strip().startswith("|---"):
                    continue
                # Split cells excluding outer empty tokens
                cells = [c.strip() for c in line.split("|")[1:-1]]
                assert len(cells) == expected_cols, (
                    f"Line {idx} in rotation-converter.qmd has {len(cells)} columns, "
                    f"expected {expected_cols}: {line}"
                )
                # Verify math uses norm notation instead of bare pipes
                if "Quaternion" in line:
                    assert r"\lVert\mathbf{q}\rVert" in line
                if "Exponential coordinates" in line:
                    assert r"\lVert\boldsymbol{\omega}\rVert" in line

    def test_rotation_converter_has_named_responsive_grid(self) -> None:
        content = (REPO_ROOT / "articles/rotation-converter.qmd").read_text(encoding="utf-8")
        assert 'class="rc-main-grid"' in content


class TestHeadingLevelProgression:
    """Verify heading levels step linearly without skipping levels."""

    @pytest.mark.parametrize(
        "rel_path",
        [
            "articles/affine-nature-golf-swing.qmd",
            "articles/wrist-universal-joint.qmd",
            "articles/drifter-manifesto.qmd",
            "articles/secondary-axis-stability.qmd",
            "articles/controllability-drift-ratio.qmd",
        ],
    )
    def test_heading_levels_do_not_skip(self, rel_path: str) -> None:
        file_path = REPO_ROOT / rel_path
        content = file_path.read_text(encoding="utf-8")
        _, headings = parse_qmd_structure(content)

        skips = []
        prev_level = 0
        for line_num, level, title, in_callout in headings:
            if in_callout:
                continue
            if prev_level > 0 and level > prev_level + 1:
                skips.append(
                    f"Line {line_num}: jumped from H{prev_level} to H{level} for '{title}'"
                )
            prev_level = level

        assert not skips, f"Heading skips detected in {rel_path}:\n" + "\n".join(skips)


class TestOrphanHeadings:
    """Verify orphan defense/rebuttal headings are not top-level sections."""

    def test_no_orphan_defense_headings_in_affine_nature(self) -> None:
        file_path = REPO_ROOT / "articles/affine-nature-golf-swing.qmd"
        content = file_path.read_text(encoding="utf-8")
        _, headings = parse_qmd_structure(content)

        orphan_defense_h2 = [
            (line_num, title)
            for line_num, level, title, in_callout in headings
            if level == 2 and not in_callout and title.startswith("Defense")
        ]

        assert not orphan_defense_h2, (
            "Found orphan '## Defense' headings at H2 in affine-nature-golf-swing.qmd: "
            f"{orphan_defense_h2}"
        )


class TestRepositoryPageLinks:
    """Verify the 5 repository/model pages contain canonical GitHub links (Issue #3923)."""

    @pytest.mark.parametrize(
        "rel_path",
        [
            "repositories/repositories-drake.qmd",
            "repositories/repositories-pinocchio.qmd",
            "repositories/repositories-2d-model.qmd",
            "repositories/repositories-3d-model.qmd",
            "models/models-pendulum.qmd",
        ],
    )
    def test_repository_pages_contain_upstreamdrift_url(self, rel_path: str) -> None:
        file_path = REPO_ROOT / rel_path
        assert file_path.exists(), f"File {rel_path} not found"

        content = file_path.read_text(encoding="utf-8")
        canonical_repo = "https://github.com/D-sorganization/UpstreamDrift"
        clone_cmd = "git clone https://github.com/D-sorganization/UpstreamDrift.git"

        assert (
            canonical_repo in content
        ), f"{rel_path} is missing the canonical repository URL {canonical_repo}"
        assert clone_cmd in content, f"{rel_path} is missing the git clone command {clone_cmd}"


class TestEmojiConsistency:
    """Verify removal of emoji glyphs from learning paths and roadmap."""

    def test_learning_paths_headings_emoji_free(self) -> None:
        file_path = REPO_ROOT / "resources/learning-paths.qmd"
        content = file_path.read_text(encoding="utf-8")
        _, headings = parse_qmd_structure(content)

        emoji_pattern = re.compile(
            r"[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]"
        )

        for line_num, _, title, _ in headings:
            match = emoji_pattern.search(title)
            assert (
                match is None
            ), f"Line {line_num} in learning-paths.qmd has emoji '{match.group()}' in heading '{title}'"

    def test_development_roadmap_status_legend_emoji_free(self) -> None:
        file_path = REPO_ROOT / "pages/development-roadmap.qmd"
        content = file_path.read_text(encoding="utf-8")

        assert "🔴 **Planned**" not in content
        assert "🟡 **In Progress**" not in content
        assert "🟢 **Usable**" not in content
