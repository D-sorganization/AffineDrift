"""Regression tests for CLI boundary validation across critical scripts."""

from pathlib import Path

from scripts import generate_completist_data, pragmatic_programmer_review, run_assessment


def test_generate_completist_data_fails_for_missing_repo_root(tmp_path: Path) -> None:
    """CLI should fail fast when --repo-root does not exist."""
    missing = tmp_path / "missing-repo"
    exit_code = generate_completist_data.main(["--repo-root", str(missing)])
    assert exit_code == 2


def test_generate_completist_data_fails_for_missing_output_parent(tmp_path: Path) -> None:
    """CLI should reject output files under non-existent parent directories."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "sample.py").write_text("print('ok')\n", encoding="utf-8")
    bad_output = repo_root / "missing-parent" / "out.txt"
    exit_code = generate_completist_data.main(
        ["--repo-root", str(repo_root), "--output-dir", str(bad_output)],
    )
    assert exit_code == 2


def test_generate_completist_data_succeeds_for_valid_paths(tmp_path: Path) -> None:
    """CLI should write output data files when both boundaries are valid."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "sample.py").write_text("# TODO: sample\n", encoding="utf-8")
    output_dir = repo_root / "output"
    output_dir.mkdir()

    exit_code = generate_completist_data.main(
        ["--repo-root", str(repo_root), "--output-dir", str(output_dir)],
    )
    assert exit_code == 0
    assert (output_dir / "todo_markers.txt").exists()


def test_run_assessment_fails_for_missing_output_parent(tmp_path: Path) -> None:
    """CLI should reject --output paths whose parent dir does not exist."""
    bad_output = tmp_path / "missing" / "assessment.md"
    exit_code = run_assessment.main(["--assessment", "C", "--output", str(bad_output)])
    assert exit_code == 2


def test_run_assessment_writes_report_for_valid_output(tmp_path: Path) -> None:
    """CLI should generate report for valid output paths."""
    output_file = tmp_path / "assessment.md"
    exit_code = run_assessment.main(["--assessment", "C", "--output", str(output_file)])
    assert exit_code == 0
    assert output_file.exists()


def test_pragmatic_review_fails_for_missing_output_parent(tmp_path: Path) -> None:
    """CLI should fail-fast for non-writable output boundary."""
    bad_output = tmp_path / "missing" / "review.md"
    exit_code = pragmatic_programmer_review.main(["--output", str(bad_output)])
    assert exit_code == 2
