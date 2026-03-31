"""Tests for scripts.mypy_runner - agent loop and reporting."""

import logging
from unittest.mock import patch

from scripts.mypy_models import AgentReport, MypyError
from scripts.mypy_runner import _apply_fixes_to_file, _group_errors_by_file, log_report, run_agent


def _make_error(**kwargs) -> MypyError:
    defaults = dict(file="src/x.py", line=1, column=1, severity="error", message="", code="")
    defaults.update(kwargs)
    return MypyError(**defaults)


class TestGroupErrorsByFile:
    def test_safe_path_included(self):
        err = _make_error(file="src/foo.py", line=1, code="arg-type")
        report = AgentReport()
        grouped = _group_errors_by_file([err], report)
        assert "src/foo.py" in grouped
        assert len(report.skipped_reasons) == 0

    def test_unsafe_path_skipped(self):
        err = _make_error(file="scripts/foo.py", line=1, code="arg-type")
        report = AgentReport()
        grouped = _group_errors_by_file([err], report)
        assert grouped == {}
        assert len(report.skipped_reasons) == 1

    def test_mixed_paths(self):
        safe = _make_error(file="src/a.py", line=1, code="arg-type")
        unsafe = _make_error(file="scripts/b.py", line=1, code="arg-type")
        report = AgentReport()
        grouped = _group_errors_by_file([safe, unsafe], report)
        assert len(grouped) == 1
        assert "src/a.py" in grouped
        assert len(report.skipped_reasons) == 1


class TestApplyFixesToFile:
    def test_fixes_applied_to_lines(self):
        lines = ["import scipy\n", "x = 1\n"]
        err = _make_error(file="src/x.py", line=1, code="import-untyped", message="msg")
        report = AgentReport()
        changed, total = _apply_fixes_to_file(
            lines, [err], report, max_fixes=10, total_fixes=0, verbose=False
        )
        assert changed
        assert total == 1
        assert report.suppressions == 1

    def test_respects_max_fixes(self):
        lines = ["import scipy\n"]
        err = _make_error(file="src/x.py", line=1, code="import-untyped", message="msg")
        report = AgentReport()
        changed, total = _apply_fixes_to_file(
            lines, [err], report, max_fixes=0, total_fixes=0, verbose=False
        )
        assert not changed
        assert total == 0

    def test_unfixable_error_recorded(self):
        lines = ["x = 1\n"]
        err = _make_error(file="src/x.py", line=1, code="unsupported-code", message="Some msg")
        report = AgentReport()
        changed, total = _apply_fixes_to_file(
            lines, [err], report, max_fixes=10, total_fixes=0, verbose=False
        )
        assert not changed
        assert total == 0
        assert len(report.skipped_reasons) == 1


class TestLogReport:
    def test_logs_summary(self, caplog):
        report = AgentReport(
            total_errors=5,
            errors_fixed=3,
            real_fixes=2,
            suppressions=1,
            files_modified=["src/a.py"],
        )
        with caplog.at_level(logging.INFO, logger="scripts.mypy_runner"):
            log_report(report)
        combined = " ".join(caplog.messages)
        assert "5" in combined  # total errors
        assert "3" in combined  # errors fixed

    def test_skipped_reasons_truncated_after_10(self, caplog):
        report = AgentReport(
            skipped_reasons=[f"reason {i}" for i in range(15)],
        )
        with caplog.at_level(logging.INFO, logger="scripts.mypy_runner"):
            log_report(report)
        combined = " ".join(caplog.messages)
        assert "5 more" in combined


class TestRunAgent:
    @patch("scripts.mypy_runner.run_mypy", return_value="")
    def test_no_errors(self, mock_mypy):
        report = run_agent(targets=["src"])
        assert report.total_errors == 0
        assert report.errors_fixed == 0

    @patch("scripts.mypy_runner.write_file_lines")
    @patch("scripts.mypy_runner.read_file_lines", return_value=["import scipy\n"])
    @patch(
        "scripts.mypy_runner.run_mypy",
        return_value="src/foo.py:1:1: error: Import untyped  [import-untyped]\n",
    )
    def test_dry_run_does_not_write(self, mock_mypy, mock_read, mock_write):
        run_agent(dry_run=True, targets=["src"])
        mock_write.assert_not_called()

    @patch("scripts.mypy_runner.write_file_lines")
    @patch("scripts.mypy_runner.read_file_lines", return_value=["import scipy\n"])
    @patch(
        "scripts.mypy_runner.run_mypy",
        return_value="src/foo.py:1:1: error: Import untyped  [import-untyped]\n",
    )
    def test_writes_when_not_dry_run(self, mock_mypy, mock_read, mock_write):
        run_agent(dry_run=False, targets=["src"])
        mock_write.assert_called_once()
