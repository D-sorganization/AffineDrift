"""Tests for src.tools.utils.analysis_utils — Python code analysis utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.utils.analysis_utils import (
    ErrorHandlingMetrics,
    FunctionDetail,
    LoggingMetrics,
    PythonFileMetrics,
    assess_error_handling_content,
    assess_logging_content,
    calculate_complexity,
    collect_error_handling_metrics,
    collect_function_details,
    collect_logging_metrics,
    collect_python_file_metrics,
    get_detailed_function_metrics,
    get_python_metrics,
)


class TestGetPythonMetrics:
    """Tests for get_python_metrics()."""

    def test_returns_dict_for_valid_file(self, tmp_path: Path) -> None:
        """Should return a dict with expected keys for a valid Python file."""
        f = tmp_path / "module.py"
        f.write_text('def foo():\n    """Docstring."""\n    return 1\n', encoding="utf-8")
        result = get_python_metrics(f)
        assert isinstance(result, dict)
        assert "functions" in result
        assert "classes" in result
        assert result["functions"] == 1

    def test_counts_classes(self, tmp_path: Path) -> None:
        """Should count classes in Python file."""
        f = tmp_path / "module.py"
        f.write_text('class Foo:\n    """Class."""\n    pass\n', encoding="utf-8")
        result = get_python_metrics(f)
        assert result["classes"] == 1

    def test_counts_docstrings(self, tmp_path: Path) -> None:
        """Should count functions with docstrings."""
        f = tmp_path / "module.py"
        f.write_text('def foo():\n    """Doc."""\n    pass\n', encoding="utf-8")
        result = get_python_metrics(f)
        assert result["docstrings"] >= 1

    def test_raises_on_none_filepath(self) -> None:
        """Should raise when filepath is None (contract)."""
        with pytest.raises(AssertionError):
            get_python_metrics(None)  # type: ignore[arg-type]

    def test_handles_syntax_error_file(self, tmp_path: Path) -> None:
        """Should return zeroed metrics for files with syntax errors."""
        f = tmp_path / "bad.py"
        f.write_text("def foo(\n", encoding="utf-8")
        result = get_python_metrics(f)
        assert isinstance(result, dict)


class TestCollectPythonFileMetrics:
    """Tests for collect_python_file_metrics()."""

    def test_returns_python_file_metrics_dataclass(self, tmp_path: Path) -> None:
        """Should return PythonFileMetrics instance."""
        f = tmp_path / "module.py"
        f.write_text('def foo() -> int:\n    """Doc."""\n    return 1\n', encoding="utf-8")
        result = collect_python_file_metrics(f)
        assert isinstance(result, PythonFileMetrics)

    def test_counts_typed_returns(self, tmp_path: Path) -> None:
        """Should count functions with return type annotations."""
        f = tmp_path / "module.py"
        f.write_text("def foo() -> int:\n    return 1\n", encoding="utf-8")
        result = collect_python_file_metrics(f)
        assert result.typed_returns == 1

    def test_counts_branches(self, tmp_path: Path) -> None:
        """Should count branch statements."""
        f = tmp_path / "module.py"
        f.write_text(
            "def foo(x: int) -> int:\n    if x > 0:\n        return 1\n    return 0\n",
            encoding="utf-8",
        )
        result = collect_python_file_metrics(f)
        assert result.branches >= 1

    def test_handles_missing_file(self, tmp_path: Path) -> None:
        """Should return zeroed metrics for missing file."""
        f = tmp_path / "nonexistent.py"
        result = collect_python_file_metrics(f)
        assert isinstance(result, PythonFileMetrics)

    def test_logs_missing_file_fallback(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        """Should log a debug message when a file cannot be read."""
        f = tmp_path / "missing.py"
        with caplog.at_level("DEBUG"):
            result = collect_python_file_metrics(f)
        assert isinstance(result, PythonFileMetrics)
        assert "Falling back to zeroed Python metrics" in caplog.text

    def test_async_functions_counted(self, tmp_path: Path) -> None:
        """Should count async functions."""
        f = tmp_path / "module.py"
        f.write_text("async def afoo():\n    pass\n", encoding="utf-8")
        result = collect_python_file_metrics(f)
        assert result.functions == 1


class TestGetDetailedFunctionMetrics:
    """Tests for get_detailed_function_metrics()."""

    def test_returns_list_of_dicts(self) -> None:
        """Should return list of dicts with function details."""
        code = "def foo(a, b):\n    '''doc'''\n    return a + b\n"
        result = get_detailed_function_metrics(code)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "foo"

    def test_empty_code_returns_empty_list(self) -> None:
        """Should return empty list for code with no functions."""
        result = get_detailed_function_metrics("x = 1")
        assert result == []

    def test_has_docstring_field(self) -> None:
        """Should include has_docstring field."""
        code = "def foo():\n    '''doc'''\n    pass\n"
        result = get_detailed_function_metrics(code)
        assert result[0]["has_docstring"] is True

    def test_no_docstring_field_false(self) -> None:
        """Should return has_docstring=False for function without docstring."""
        code = "def foo():\n    pass\n"
        result = get_detailed_function_metrics(code)
        assert result[0]["has_docstring"] is False


class TestCollectFunctionDetails:
    """Tests for collect_function_details()."""

    def test_returns_function_detail_dataclass(self) -> None:
        """Should return list of FunctionDetail instances."""
        code = "def foo(a, b):\n    pass\n"
        result = collect_function_details(code)
        assert isinstance(result[0], FunctionDetail)

    def test_correct_arg_count(self) -> None:
        """Should count function arguments correctly."""
        code = "def foo(a, b, c):\n    pass\n"
        result = collect_function_details(code)
        assert result[0].args == 3

    def test_handles_syntax_error(self) -> None:
        """Should return empty list for invalid Python."""
        result = collect_function_details("def foo(\n")
        assert result == []

    def test_logs_function_detail_parse_fallback(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should log a debug message when function-detail parsing fails."""
        with caplog.at_level("DEBUG"):
            result = collect_function_details("def foo(\n")
        assert result == []
        assert "Falling back to empty function details" in caplog.text


class TestCalculateComplexity:
    """Tests for calculate_complexity()."""

    def test_returns_zero_for_no_functions(self) -> None:
        """Should return 0.0 when no functions."""
        result = calculate_complexity({"functions": 0, "branches": 0})
        assert result == pytest.approx(0.0)

    def test_calculates_branches_per_function(self) -> None:
        """Should calculate branches / functions."""
        result = calculate_complexity({"functions": 2, "branches": 4})
        assert result == pytest.approx(2.0)

    def test_raises_on_none_metrics(self) -> None:
        """Should raise when metrics is None (contract)."""
        with pytest.raises(AssertionError):
            calculate_complexity(None)  # type: ignore[arg-type]


class TestAssessErrorHandlingContent:
    """Tests for assess_error_handling_content()."""

    def test_counts_try_blocks(self) -> None:
        """Should count try: blocks."""
        code = "try:\n    x = 1\nexcept:\n    pass\n"
        result = assess_error_handling_content(code)
        assert result["try_count"] == 1

    def test_counts_bare_excepts(self) -> None:
        """Should count bare except: clauses."""
        code = "try:\n    x = 1\nexcept:\n    pass\n"
        result = assess_error_handling_content(code)
        assert result["bare_except_count"] == 1

    def test_no_exceptions_returns_zeros(self) -> None:
        """Should return zeros for code without try/except."""
        code = "x = 1\ny = 2\n"
        result = assess_error_handling_content(code)
        assert result["try_count"] == 0
        assert result["bare_except_count"] == 0


class TestCollectErrorHandlingMetrics:
    """Tests for collect_error_handling_metrics()."""

    def test_returns_error_handling_metrics_dataclass(self) -> None:
        """Should return ErrorHandlingMetrics instance."""
        result = collect_error_handling_metrics("try:\n    pass\nexcept:\n    pass\n")
        assert isinstance(result, ErrorHandlingMetrics)

    def test_specific_except_not_counted_as_bare(self) -> None:
        """Should not count 'except ValueError:' as bare except."""
        code = "try:\n    pass\nexcept ValueError:\n    pass\n"
        result = collect_error_handling_metrics(code)
        assert result.bare_except_count == 0


class TestAssessLoggingContent:
    """Tests for assess_logging_content()."""

    def test_detects_logging_usage(self) -> None:
        """Should detect logging.info() usage."""
        code = "import logging\nlogging.info('msg')\n"
        result = assess_logging_content(code)
        assert result["logging_usage"] == 1

    def test_detects_print_usage(self) -> None:
        """Should detect print() usage."""
        code = "print('hello')\n"
        result = assess_logging_content(code)
        assert result["print_usage"] == 1

    def test_no_logging_or_print_returns_zeros(self) -> None:
        """Should return zeros when neither logging nor print used."""
        code = "x = 1\n"
        result = assess_logging_content(code)
        assert result["logging_usage"] == 0
        assert result["print_usage"] == 0

    def test_detects_logger_dot_usage(self) -> None:
        """Should detect logger.info() usage."""
        code = "logger.info('msg')\n"
        result = assess_logging_content(code)
        assert result["logging_usage"] == 1


class TestCollectLoggingMetrics:
    """Tests for collect_logging_metrics()."""

    def test_returns_logging_metrics_dataclass(self) -> None:
        """Should return LoggingMetrics instance."""
        result = collect_logging_metrics("logger.info('msg')\n")
        assert isinstance(result, LoggingMetrics)

    def test_both_usage_detected(self) -> None:
        """Should detect both logging and print when both present."""
        code = "logger.info('msg')\nprint('debug')\n"
        result = collect_logging_metrics(code)
        assert result.logging_usage == 1
        assert result.print_usage == 1
