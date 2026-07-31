"""Tests for the LaTeX/Quarto cross-tree parity checker.

The negative cases carry most of the weight here. An earlier draft of this
checker extracted every number matching a units pattern and diffed the sets;
that reported "18 g" of centripetal acceleration as a golf-ball mass and
produced 16 findings of which none was actionable. These tests pin the
narrower, known-regression design that replaced it.
"""

from __future__ import annotations

from pathlib import Path

from scripts.check_tree_parity import (
    Finding,
    check_coverage,
    check_superseded_values,
    fingerprint,
    main,
    strip_latex_comments,
)


def build_tree(root: Path, tex: dict[str, str], qmd: dict[str, str]) -> None:
    """Lay out a miniature Physics of Golf tree."""
    tex_dir = root / "articles/The_Physics_of_Golf/chapters"
    qmd_dir = root / "articles/The_Physics_of_Golf/quarto"
    tex_dir.mkdir(parents=True, exist_ok=True)
    qmd_dir.mkdir(parents=True, exist_ok=True)
    for name, body in tex.items():
        (tex_dir / f"{name}.tex").write_text(body, encoding="utf-8")
    for name, body in qmd.items():
        (qmd_dir / f"{name}.qmd").write_text(body, encoding="utf-8")


def kinds(findings: list[Finding]) -> list[str]:
    return [item.kind for item in findings]


class TestCoverage:
    def test_flags_chapter_missing_from_the_website(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch32_putting": "Putting."}, {})
        assert kinds(check_coverage(tmp_path)) == ["latex-only"]

    def test_flags_page_with_no_latex_source(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {}, {"ch99_orphan": "Orphan."})
        assert kinds(check_coverage(tmp_path)) == ["quarto-only"]

    def test_paired_chapters_are_clean(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch01_intro": "Intro."}, {"ch01_intro": "Intro."})
        assert check_coverage(tmp_path) == []

    def test_landing_pages_are_not_treated_as_chapters(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch01_intro": "Intro."}, {"ch01_intro": "Intro.", "index": "Home."})
        assert check_coverage(tmp_path) == []

    def test_front_and_back_matter_need_no_mirror(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"main": "Root.", "nomenclature": "Symbols."}, {})
        assert check_coverage(tmp_path) == []

    def test_shared_quarto_directory_is_not_reported_per_volume(self, tmp_path: Path) -> None:
        """Regression: several LaTeX volumes share one Quarto directory.

        Judging orphans per-pair reported every Volume 0 mirror as missing from
        Volume I -- 18 false positives.
        """
        gom = tmp_path / "articles/The_Geometry_of_Motion"
        (gom / "Volume_0/chapters").mkdir(parents=True)
        (gom / "Volume_I/chapters").mkdir(parents=True)
        (gom / "quarto").mkdir(parents=True)
        (gom / "Volume_0/chapters/ch01_linear_algebra.tex").write_text("A.", encoding="utf-8")
        (gom / "quarto/vol0_ch01_linear_algebra.qmd").write_text("A.", encoding="utf-8")
        (gom / "Volume_I/chapters/ch01_foundations.tex").write_text("B.", encoding="utf-8")
        (gom / "quarto/ch01_foundations.qmd").write_text("B.", encoding="utf-8")
        assert check_coverage(tmp_path) == []


class TestSupersededValues:
    def test_flags_the_150_gram_ball(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch10_energy": "A 150-gram ball leaves at 150 mph."}, {})
        findings = check_superseded_values(tmp_path)
        assert kinds(findings) == ["superseded-value"]
        assert "45.93" in findings[0].detail

    def test_regulation_mass_is_clean(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch10_energy": "A regulation 45.93-gram ball."}, {})
        assert check_superseded_values(tmp_path) == []

    def test_flags_stale_shaft_frequencies(self, tmp_path: Path) -> None:
        build_tree(
            tmp_path,
            {"ch11_shaft": "The mode is 15--25 Hz."},
            {"ch24_brain": "Shaft dynamics at 50--200 Hz."},
        )
        assert kinds(check_superseded_values(tmp_path)) == [
            "superseded-value",
            "superseded-value",
        ]

    def test_corrected_shaft_frequency_is_clean(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch11_shaft": "The first bending mode is 3--5 Hz."}, {})
        assert check_superseded_values(tmp_path) == []

    def test_does_not_confuse_g_force_with_ball_mass(self, tmp_path: Path) -> None:
        """Regression: a loose units pattern read '18 g' of acceleration as a mass."""
        build_tree(
            tmp_path, {"ch04_forces": "Centripetal acceleration reaches 18 g at impact."}, {}
        )
        assert check_superseded_values(tmp_path) == []

    def test_flags_cor_stated_as_an_energy_ratio_in_latex(self, tmp_path: Path) -> None:
        # Real LaTeX escapes the percent sign; a bare % would comment out the
        # rest of the line, which is why comment-stripping runs first.
        build_tree(
            tmp_path,
            {"glossary": "COR: the ball returns 82\\% of the impact kinetic energy."},
            {},
        )
        assert kinds(check_superseded_values(tmp_path)) == ["superseded-value"]

    def test_flags_cor_stated_as_an_energy_ratio_in_quarto(self, tmp_path: Path) -> None:
        # Markdown needs no escape, so the bare form is the realistic one there.
        build_tree(
            tmp_path,
            {},
            {"glossary": "COR: the ball returns 82% of the kinetic energy."},
        )
        assert kinds(check_superseded_values(tmp_path)) == ["superseded-value"]

    def test_a_superseded_value_inside_a_latex_comment_is_ignored(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch10_energy": "% old text said a 150-gram ball\nFixed."}, {})
        assert check_superseded_values(tmp_path) == []

    def test_scans_both_trees(self, tmp_path: Path) -> None:
        """A superseded value is wrong wherever it appears, mirrored or not."""
        build_tree(tmp_path, {}, {"ch24_brain": "Shaft dynamics at 50--200 Hz."})
        assert kinds(check_superseded_values(tmp_path)) == ["superseded-value"]


class TestCommentStripping:
    def test_removes_trailing_comment(self) -> None:
        assert strip_latex_comments("text % note").strip() == "text"

    def test_keeps_escaped_percent(self) -> None:
        assert "5\\%" in strip_latex_comments("about 5\\% of the total")


class TestBaselineRatchet:
    def test_known_divergence_passes_once_baselined(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch32_putting": "Putting."}, {})
        baseline = tmp_path / "baseline.json"
        assert main(["--root", str(tmp_path), "--baseline", str(baseline), "--write-baseline"]) == 0
        assert main(["--root", str(tmp_path), "--baseline", str(baseline)]) == 0

    def test_new_divergence_still_fails(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch32_putting": "Putting."}, {})
        baseline = tmp_path / "baseline.json"
        main(["--root", str(tmp_path), "--baseline", str(baseline), "--write-baseline"])
        build_tree(tmp_path, {"ch10_energy": "A 150-gram ball."}, {})
        assert main(["--root", str(tmp_path), "--baseline", str(baseline)]) == 1

    def test_clean_tree_passes_without_a_baseline(self, tmp_path: Path) -> None:
        build_tree(tmp_path, {"ch01_intro": "Intro."}, {"ch01_intro": "Intro."})
        assert main(["--root", str(tmp_path)]) == 0

    def test_fingerprint_is_stable(self) -> None:
        finding = Finding(kind="latex-only", detail="d", tex="a.tex")
        assert fingerprint(finding) == fingerprint(Finding(kind="latex-only", detail="d"))
