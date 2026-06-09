"""Regression tests for assessment source-file hygiene."""

from pathlib import Path

from scripts.assessment_quality_files import filter_quality_metric_python_files


def test_filter_quality_metric_python_files_excludes_generated_site_artifacts(
    tmp_path: Path,
) -> None:
    """Generated site and coverage files must not affect repository quality metrics."""
    source_file = tmp_path / "src" / "affine_control" / "model.py"
    test_file = tmp_path / "tests" / "test_model.py"
    generated_files = [
        tmp_path / "docs" / "generated_launcher.py",
        tmp_path / "_site" / "generated_page.py",
        tmp_path / ".quarto" / "cache" / "generated_cell.py",
        tmp_path / "htmlcov" / "coverage_index.py",
        tmp_path / "coverage" / "lcov-report" / "generated_report.py",
        tmp_path / "lcov-report" / "bundle_report.py",
    ]
    candidates = [source_file, *generated_files, test_file]

    result = filter_quality_metric_python_files(tmp_path, candidates)

    assert result == [source_file, test_file]


def test_filter_quality_metric_python_files_keeps_non_artifact_python_files(
    tmp_path: Path,
) -> None:
    """Repository scripts and source modules remain in the assessment input."""
    candidates = [
        tmp_path / "scripts" / "assess_repo.py",
        tmp_path / "src" / "tools" / "utils" / "analysis_utils.py",
    ]

    result = filter_quality_metric_python_files(tmp_path, candidates)

    assert result == candidates
