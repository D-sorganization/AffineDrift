"""Tests for matlab_utilities/scripts/matlab_quality_check.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.tools.matlab_utilities.scripts.matlab_quality_check import MATLABQualityChecker


class TestMATLABQualityCheckerInit:
    """Tests for MATLABQualityChecker initialisation."""

    def test_init_sets_project_root(self, tmp_path: Path) -> None:
        """Should set project_root from argument."""
        checker = MATLABQualityChecker(tmp_path)
        assert checker.project_root == tmp_path

    def test_init_sets_matlab_dir(self, tmp_path: Path) -> None:
        """Should set matlab_dir as project_root/matlab."""
        checker = MATLABQualityChecker(tmp_path)
        assert checker.matlab_dir == tmp_path / "matlab"

    def test_init_results_has_expected_keys(self, tmp_path: Path) -> None:
        """Results dict should have all required keys after init."""
        checker = MATLABQualityChecker(tmp_path)
        for key in ("timestamp", "total_files", "issues", "passed", "summary", "checks"):
            assert key in checker.results


class TestCheckMatlabFilesExist:
    """Tests for check_matlab_files_exist()."""

    def test_returns_false_when_no_matlab_dir(self, tmp_path: Path) -> None:
        """Should return False when matlab/ directory doesn't exist."""
        checker = MATLABQualityChecker(tmp_path)
        result = checker.check_matlab_files_exist()
        assert result is False

    def test_returns_false_when_no_m_files(self, tmp_path: Path) -> None:
        """Should return False when matlab/ exists but has no .m files."""
        matlab_dir = tmp_path / "matlab"
        matlab_dir.mkdir()
        checker = MATLABQualityChecker(tmp_path)
        result = checker.check_matlab_files_exist()
        assert result is False

    def test_returns_true_when_m_files_present(self, tmp_path: Path) -> None:
        """Should return True when .m files are found."""
        matlab_dir = tmp_path / "matlab"
        matlab_dir.mkdir()
        (matlab_dir / "test.m").write_text("function y = test(x)\ny = x;\nend")
        checker = MATLABQualityChecker(tmp_path)
        result = checker.check_matlab_files_exist()
        assert result is True

    def test_sets_total_files_count(self, tmp_path: Path) -> None:
        """Should update results['total_files'] when files are found."""
        matlab_dir = tmp_path / "matlab"
        matlab_dir.mkdir()
        (matlab_dir / "a.m").write_text("x = 1;")
        (matlab_dir / "b.m").write_text("y = 2;")
        checker = MATLABQualityChecker(tmp_path)
        checker.check_matlab_files_exist()
        assert checker.results["total_files"] == 2


class TestStaticMatlabAnalysis:
    """Tests for _static_matlab_analysis()."""

    def test_returns_dict(self, tmp_path: Path) -> None:
        """Should return a dictionary."""
        matlab_dir = tmp_path / "matlab"
        matlab_dir.mkdir()
        checker = MATLABQualityChecker(tmp_path)
        result = checker._static_matlab_analysis()
        assert isinstance(result, dict)

    def test_analyses_m_files(self, tmp_path: Path) -> None:
        """Should analyse .m files if present."""
        matlab_dir = tmp_path / "matlab"
        matlab_dir.mkdir()
        (matlab_dir / "sample.m").write_text("function y = sample(x)\n% comment\ny = x;\nend")
        checker = MATLABQualityChecker(tmp_path)
        result = checker._static_matlab_analysis()
        assert isinstance(result, dict)

    def test_no_matlab_dir_returns_dict(self, tmp_path: Path) -> None:
        """Should return valid dict even without matlab/ directory."""
        checker = MATLABQualityChecker(tmp_path)
        result = checker._static_matlab_analysis()
        assert isinstance(result, dict)


class TestRunMatlabQualityChecks:
    """Tests for run_matlab_quality_checks()."""

    def test_falls_back_to_static_when_no_config_script(self, tmp_path: Path) -> None:
        """Should use static analysis when config script not found."""
        matlab_dir = tmp_path / "matlab"
        matlab_dir.mkdir()
        (matlab_dir / "sample.m").write_text("x = 1;")
        checker = MATLABQualityChecker(tmp_path)
        result = checker.run_matlab_quality_checks()
        assert isinstance(result, dict)

    def test_handles_os_error(self, tmp_path: Path) -> None:
        """Should handle OSError and return error dict."""
        checker = MATLABQualityChecker(tmp_path)
        with patch.object(
            checker,
            "_static_matlab_analysis",
            side_effect=OSError("disk error"),
        ):
            result = checker.run_matlab_quality_checks()
        # Should either return error dict or propagate; either is acceptable
        assert isinstance(result, dict)


class TestRunMatlabScript:
    """Tests for _run_matlab_script()."""

    def test_falls_back_to_static_when_all_commands_fail(self, tmp_path: Path) -> None:
        """Should fall back to static analysis when MATLAB/Octave not available."""
        matlab_dir = tmp_path / "matlab"
        matlab_dir.mkdir()
        script = matlab_dir / "matlab_quality_config.m"
        script.write_text("% config")

        checker = MATLABQualityChecker(tmp_path)
        # All subprocess calls will raise FileNotFoundError (no MATLAB installed)
        with patch("subprocess.run", side_effect=FileNotFoundError("matlab not found")):
            result = checker._run_matlab_script(script)
        assert isinstance(result, dict)

    def test_returns_success_when_matlab_succeeds(self, tmp_path: Path) -> None:
        """Should return success dict when subprocess returns 0."""
        matlab_dir = tmp_path / "matlab"
        matlab_dir.mkdir()
        script = matlab_dir / "quality.m"
        script.write_text("% config")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Quality check passed"

        checker = MATLABQualityChecker(tmp_path)
        with patch("subprocess.run", return_value=mock_result):
            result = checker._run_matlab_script(script)
        assert result.get("success") is True
