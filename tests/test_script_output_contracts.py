"""Regression tests for the repository's CLI output contracts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from articles.The_Geometry_of_Motion.quarto.convert_tex_to_qmd import main as convert_tex_main
from scripts.check_coverage_gates import CoverageGate
from scripts.check_coverage_gates import main as coverage_gates_main
from scripts.convert_bibliography_to_bib import main as convert_bib_main
from scripts.create_issues import main as create_issues_main
from scripts.fix_formatting import main as fix_formatting_main
from scripts.split_vol2 import main as split_vol2_main
from scripts.validate_frontmatter import main as validate_frontmatter_main


def test_convert_bibliography_to_bib_reports_success_on_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The bibliography converter should keep its success message on stdout."""
    repo_root = tmp_path
    data_dir = repo_root / "data"
    data_dir.mkdir()
    (data_dir / "bibliography.json").write_text(
        json.dumps(
            [
                {
                    "id": "sample-entry",
                    "type": "paper",
                    "title": "Sample Paper",
                    "authors": ["Ada Lovelace"],
                    "year": 2024,
                    "venue": "Example Journal",
                }
            ]
        ),
        encoding="utf-8",
    )

    assert convert_bib_main(repo_root) == 0
    captured = capsys.readouterr()

    assert "Wrote 1 entries" in captured.out
    assert captured.err == ""
    assert (repo_root / "references" / "affine-drift.bib").exists()


def test_validate_frontmatter_reports_failure_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Frontmatter validation should report failures through stdout."""
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir()
    (articles_dir / "ok.qmd").write_text(
        "---\ntitle: Example\n---\nBody text.\n",
        encoding="utf-8",
    )
    (articles_dir / "missing.qmd").write_text(
        "---\ndescription: Missing title\n---\nBody text.\n",
        encoding="utf-8",
    )

    assert validate_frontmatter_main(articles_dir) == 1
    captured = capsys.readouterr()

    assert "Frontmatter validation FAILED:" in captured.out
    assert "missing required frontmatter field 'title'" in captured.out


def test_validate_frontmatter_reports_success(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Frontmatter validation should report success through stdout."""
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir()
    (articles_dir / "ok.qmd").write_text(
        "---\ntitle: Example\n---\nBody text.\n",
        encoding="utf-8",
    )

    assert validate_frontmatter_main(articles_dir) == 0
    captured = capsys.readouterr()

    assert "Frontmatter validation passed (1 files checked)." in captured.out


def test_coverage_gate_summary_uses_stdout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Coverage-gate summaries should remain stdout-facing."""
    gates = [
        CoverageGate(package="src.alpha", test_paths=("tests/test_alpha.py",), threshold=80),
        CoverageGate(package="src.beta", test_paths=("tests/test_beta.py",), threshold=70),
    ]
    monkeypatch.setattr("scripts.check_coverage_gates.COVERAGE_GATES", gates)

    def fake_run_gate(gate: CoverageGate) -> bool:
        return gate.package == "src.alpha"

    assert coverage_gates_main(run_gate=fake_run_gate) == 1
    captured = capsys.readouterr()

    assert "Coverage Gate Summary" in captured.out
    assert "[PASS] src.alpha" in captured.out
    assert "[FAIL] src.beta" in captured.out


def test_create_issues_reports_progress_and_parses_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The issue-creation script should stay import-safe and report progress on stdout."""
    repo_root = tmp_path
    (repo_root / "magic_numbers_report.txt").write_text(
        "--- chapter_one.qmd ---\n"
        "Total instances found: 2\n"
        "alpha\n"
        "beta\n"
        "--- chapter_two.qmd ---\n"
        "Total instances found: 0\n",
        encoding="utf-8",
    )

    calls: list[list[str]] = []

    def fake_run(cmd: list[str], check: bool) -> subprocess.CompletedProcess[object]:
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr("scripts.create_issues.subprocess.run", fake_run)

    assert create_issues_main(repo_root) == 0
    captured = capsys.readouterr()

    assert captured.out.count("Creating issue:") == 4
    assert "All issues created." in captured.out
    assert len(calls) == 4
    assert any("chapter_one.qmd" in arg for call in calls for arg in call)


def test_fix_formatting_updates_matching_files_and_reports_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The formatting helper should keep its path updates on stdout."""
    tex_file = tmp_path / "articles" / "The_Physics_of_Golf" / "chapter_one.tex"
    tex_file.parent.mkdir(parents=True)
    tex_file.write_text(
        "\\documentclass[11pt]{book}\n\\usepackage[margin=1.0in]{geometry}\n",
        encoding="utf-8",
    )

    assert fix_formatting_main(tmp_path) == 0
    captured = capsys.readouterr()

    assert "Updated" in captured.out
    assert "10pt" in tex_file.read_text(encoding="utf-8")
    assert "margin=1.5in" in tex_file.read_text(encoding="utf-8")


def test_split_vol2_splits_chapters_and_reports_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The Volume II splitter should emit a summary line instead of raw print calls."""
    main_tex = tmp_path / "articles" / "The_Geometry_of_Motion" / "Volume_II" / "main.tex"
    main_tex.parent.mkdir(parents=True)
    main_tex.write_text(
        "\\frontmatter\n"
        "\\chapter{First Chapter}\n"
        "First chapter body.\n"
        "\\chapter{Second Chapter}\n"
        "Second chapter body.\n"
        "\\backmatter\n",
        encoding="utf-8",
    )

    assert split_vol2_main(tmp_path) == 0
    captured = capsys.readouterr()

    chapters_dir = main_tex.parent / "chapters"
    assert "Split 2 chapters." in captured.out
    assert (chapters_dir / "ch01_first_chapter.tex").exists()
    assert (chapters_dir / "ch02_second_chapter.tex").exists()
    assert "\\include{chapters/ch01_first_chapter}" in main_tex.read_text(encoding="utf-8")


def test_convert_tex_to_qmd_main_builds_quarto_outputs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The article conversion script should remain runnable as a CLI helper."""
    main_tex = tmp_path / "articles" / "The_Geometry_of_Motion" / "Volume_II" / "main.tex"
    main_tex.parent.mkdir(parents=True)
    main_tex.write_text(
        "\\begin{document}\n"
        "\\chapter{Introduction}\n"
        "\\section{Basics}\n"
        "\\begin{lstlisting}\n"
        "print('hello')\n"
        "\\end{lstlisting}\n"
        "\\end{document}\n",
        encoding="utf-8",
    )

    assert convert_tex_main(tmp_path) == 0
    captured = capsys.readouterr()

    quarto_dir = tmp_path / "articles" / "The_Geometry_of_Motion" / "quarto"
    volume2_content = quarto_dir / "volume2_content.qmd"
    assert "Conversion complete!" in captured.out
    assert volume2_content.exists()
    assert "# Introduction" in volume2_content.read_text(encoding="utf-8")
    assert "```python" in volume2_content.read_text(encoding="utf-8")
    assert (quarto_dir / "volume2.qmd").exists()
