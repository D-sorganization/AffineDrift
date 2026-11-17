import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.tools.utils import shell_utils
from src.tools.utils.shell_utils import run_black_check, run_ruff_check, run_tool


def test_imports():
    assert shell_utils


def test_run_tool_echo():
    # Simple test using echo to verify structure
    result = shell_utils.run_tool(["echo", "hello"], "echo")
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

    result = run_tool(["echo", "test"], "echo", result_processor=processor)
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


def test_black_counts_stderr_file_diagnostics(monkeypatch: pytest.MonkeyPatch) -> None:
    def completed(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command == ["black", "--check", "example"]
        assert kwargs == {"capture_output": True, "text": True, "timeout": 300}
        return subprocess.CompletedProcess(
            command,
            1,
            "",
            "would reformat first.py\nwould reformat would reformat second.py\n"
            "2 files would be reformatted, 1 file would be left unchanged.\n",
        )

    monkeypatch.setattr(shell_utils.subprocess, "run", completed)

    assert run_black_check("example") == {"exit_code": 1, "files_to_format": 2}


@pytest.mark.skipif(shutil.which("black") is None, reason="Black executable is not installed")
@pytest.mark.parametrize("dirty_count", [0, 2])
def test_black_counts_real_files_without_modifying_them(tmp_path: Path, dirty_count: int) -> None:
    before = {tmp_path / "clean.py": "value = 1\n"}
    before.update({tmp_path / f"dirty {i}.py": "value=  1\n" for i in range(dirty_count)})
    for path, text in before.items():
        path.write_text(text, encoding="utf-8")

    assert run_black_check(str(tmp_path)) == {
        "exit_code": 1 if dirty_count else 0,
        "files_to_format": dirty_count,
    }
    assert {path: path.read_text(encoding="utf-8") for path in before} == before


def test_run_tool_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(command, 300)

    monkeypatch.setattr(shell_utils.subprocess, "run", timeout)

    assert run_tool(["slow"], "slow tool") == {
        "exit_code": -1,
        "output": "",
        "errors": "slow tool timed out after 300 seconds",
    }


@pytest.mark.parametrize("process_result", [False, True])
def test_windows_builtin_echo_fallback(
    monkeypatch: pytest.MonkeyPatch, process_result: bool
) -> None:
    monkeypatch.setattr(shell_utils, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(shell_utils.shutil, "which", lambda command: None)

    def processor(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
        assert result.args == ["ECHO", "a", "b"]
        return {"processed": result.stdout, "code": result.returncode}

    result = run_tool(["ECHO", "a", "b"], "echo", processor if process_result else None)

    assert result == (
        {"processed": "a b\n", "code": 0}
        if process_result
        else {"exit_code": 0, "output": "a b\n", "errors": ""}
    )


def test_tool_name_must_not_be_empty() -> None:
    with pytest.raises(AssertionError, match="tool_name must not be empty"):
        run_tool(["echo"], "")
