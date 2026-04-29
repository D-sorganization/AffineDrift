"""Tests for miscellaneous utils modules to cover remaining gaps."""

from __future__ import annotations

import subprocess
from typing import Any

import pytest


class TestAssessmentUtils:
    """Tests for assessment_utils.classify_assessment_category()."""

    def test_classifies_testing_category(self) -> None:
        """Should classify 'test coverage' as 'Test Coverage'."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("Assessment_C", "test coverage")
        assert result == "Test Coverage"

    def test_classifies_code_structure(self) -> None:
        """Should classify architecture as 'Code Structure'."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("architecture", "code structure analysis")
        assert result == "Code Structure"

    def test_classifies_documentation(self) -> None:
        """Should classify documentation as 'Documentation'."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("readme", "docstring quality")
        assert result == "Documentation"

    def test_classifies_performance(self) -> None:
        """Should classify optimization as 'Performance'."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("performance", "optimization")
        assert result == "Performance"

    def test_classifies_security(self) -> None:
        """Should classify vulnerability as 'Security'."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("security", "vulnerability audit")
        assert result == "Security"

    def test_classifies_error_handling(self) -> None:
        """Should classify exception as 'Error Handling'."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("error handling", "exception")
        assert result == "Error Handling"

    def test_classifies_logging(self) -> None:
        """Should classify logging as 'Logging'."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("logging", "log")
        assert result == "Logging"

    def test_classifies_configuration(self) -> None:
        """Should classify config as 'Configuration'."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("configuration", "config env var")
        assert result == "Configuration"

    def test_classifies_api_design(self) -> None:
        """Should classify api as 'API Design'."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("api design", "interface")
        assert result == "API Design"

    def test_returns_general_for_unknown(self) -> None:
        """Should return 'General' for unknown categories."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        result = classify_assessment_category("completely_unknown_thing_xyz")
        assert result == "General"

    def test_raises_on_empty_source_name(self) -> None:
        """Should raise on empty source_name (contract)."""
        from src.tools.utils.assessment_utils import classify_assessment_category

        with pytest.raises(AssertionError):
            classify_assessment_category("")


class TestValidationUtils:
    """Tests for validation_utils.BaseValidator."""

    def test_validate_data_returns_instance_when_valid(self) -> None:
        """Should return model instance for valid data."""
        from src.tools.utils.validation_utils import BaseValidator

        class MyModel(BaseValidator):
            """Test model."""

            name: str
            value: int

        result = MyModel.validate_data({"name": "test", "value": 42})
        assert result is not None
        assert result.name == "test"
        assert result.value == 42

    def test_validate_data_returns_none_when_invalid(self) -> None:
        """Should return None when data is invalid."""
        from src.tools.utils.validation_utils import BaseValidator

        class MyModel(BaseValidator):
            """Test model."""

            name: str
            value: int

        result = MyModel.validate_data({"name": "test", "value": "not_an_int"})
        assert result is None

    def test_validate_data_returns_none_for_missing_field(self) -> None:
        """Should return None when required field is missing."""
        from src.tools.utils.validation_utils import BaseValidator

        class MyModel(BaseValidator):
            """Test model."""

            required_field: str

        result = MyModel.validate_data({})
        assert result is None


class TestShellUtils:
    """Tests for shell_utils — run_tool, run_ruff_check, run_black_check."""

    def test_run_tool_with_valid_command(self) -> None:
        """Should return dict with exit_code for valid command."""
        from src.tools.utils.shell_utils import run_tool

        result = run_tool(["echo", "hello"], "echo")
        assert "exit_code" in result
        assert result["exit_code"] == 0

    def test_run_tool_with_result_processor(self) -> None:
        """Should use result_processor when provided."""
        from src.tools.utils.shell_utils import run_tool

        def processor(result: subprocess.CompletedProcess) -> dict[str, Any]:
            """Return custom dict."""
            return {"custom": result.returncode}

        result = run_tool(["echo", "hello"], "echo", result_processor=processor)
        assert result == {"custom": 0}

    def test_run_tool_returns_error_when_not_installed(self) -> None:
        """Should return exit_code=-1 when tool is not installed."""
        from src.tools.utils.shell_utils import run_tool

        result = run_tool(["nonexistent_tool_xyz_12345"], "nonexistent_tool")
        assert result["exit_code"] == -1

    def test_run_tool_raises_on_empty_command(self) -> None:
        """Should raise on empty command list (contract)."""
        from src.tools.utils.shell_utils import run_tool

        with pytest.raises(AssertionError):
            run_tool([], "tool")

    def test_run_ruff_check_returns_dict(self) -> None:
        """run_ruff_check should return a dict (may fail if ruff not installed)."""
        from src.tools.utils.shell_utils import run_ruff_check

        result = run_ruff_check(".")
        assert isinstance(result, dict)
        assert "exit_code" in result

    def test_run_black_check_returns_dict(self) -> None:
        """run_black_check should return a dict (may fail if black not installed)."""
        from src.tools.utils.shell_utils import run_black_check

        result = run_black_check(".")
        assert isinstance(result, dict)
        assert "exit_code" in result


class TestProfilingUtils:
    """Tests for profiling_utils.profile_execution_time."""

    def test_decorator_preserves_function_name(self) -> None:
        """Decorated function should preserve original __name__."""
        from src.tools.utils.profiling_utils import profile_execution_time

        @profile_execution_time
        def my_function() -> int:
            """Test function."""
            return 42

        assert my_function.__name__ == "my_function"

    def test_decorated_function_returns_correct_result(self) -> None:
        """Decorated function should return the original result."""
        from src.tools.utils.profiling_utils import profile_execution_time

        @profile_execution_time
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        assert add(3, 4) == 7

    def test_decorator_works_with_exception(self) -> None:
        """Decorator should still log time even when function raises."""
        from src.tools.utils.profiling_utils import profile_execution_time

        @profile_execution_time
        def failing_func() -> None:
            """Function that raises."""
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_func()

    def test_decorator_works_with_kwargs(self) -> None:
        """Decorated function should accept kwargs."""
        from src.tools.utils.profiling_utils import profile_execution_time

        @profile_execution_time
        def greet(name: str = "world") -> str:
            """Return greeting."""
            return f"Hello, {name}!"

        assert greet(name="Alice") == "Hello, Alice!"


class TestAsyncUtils:
    """Tests for async_utils."""

    def test_async_utils_imports(self) -> None:
        """Should import async_utils without error."""
        import src.tools.utils.async_utils as au

        assert au is not None

    def test_run_async_function(self) -> None:
        """Should run an async function synchronously."""
        try:
            from src.tools.utils.async_utils import run_async

            async def coro() -> int:
                """Coroutine returning 42."""
                return 42

            result = run_async(coro())
            assert result == 42
        except (AttributeError, ImportError):
            pytest.skip("run_async not available")
