from src.tools.utils import shell_utils


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
