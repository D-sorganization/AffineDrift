from src.tools.utils import shell_utils
from src.tools.utils.shell_utils import run_black_check, run_ruff_check, run_tool


import sys


def test_imports():
    assert shell_utils


def test_run_tool_echo():
    # Use sys.executable to run a portable print command
    result = shell_utils.run_tool([sys.executable, "-c", "print('hello')"], "python")
    assert isinstance(result, dict)
    assert "exit_code" in result
    assert result["exit_code"] == 0
    # stdout might have newline
    assert "hello" in result["output"]


def test_run_tool_returns_error_when_command_not_found() -> None:
    """run_tool should return exit_code -1 and error message for missing commands."""
    result = run_tool(["__nonexistent_command_xyz__"], "nonexistent")
    assert result["exit_code"] == -1
    assert "not installed" in result["errors"]


def test_run_tool_with_result_processor() -> None:
    """run_tool should apply result_processor when provided."""

    def processor(result) -> dict:
        """Process result."""
        return {"custom": result.returncode}

    result = run_tool([sys.executable, "-c", "print('test')"], "python", result_processor=processor)
    assert "custom" in result
    assert result["custom"] == 0


def test_run_ruff_check_returns_dict() -> None:
    """run_ruff_check should return a dict with exit_code."""
    result = run_ruff_check(".")
    assert isinstance(result, dict)
    assert "exit_code" in result


def test_run_black_check_returns_dict() -> None:
    """run_black_check should return a dict with exit_code."""
    result = run_black_check(".")
    assert isinstance(result, dict)
    assert "exit_code" in result
