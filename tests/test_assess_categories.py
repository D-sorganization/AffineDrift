"""Tests for scripts.assess_categories - the 15 A-O assessment functions.

These mirror and extend the existing tests in test_assess_repo.py, but
target the new assess_categories module directly.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.assess_categories import (
    assess_api_design,
    assess_cicd,
    assess_code_structure,
    assess_code_style,
    assess_configuration,
    assess_data_handling,
    assess_dependencies,
    assess_documentation,
    assess_error_handling,
    assess_logging,
    assess_maintainability,
    assess_performance,
    assess_scalability,
    assess_security,
    assess_test_coverage,
)


def _mock_file(content: str, name: str = "module.py", parts: tuple = ("src", "module.py")):
    """Create a MagicMock that looks like a Path with given content."""
    f = MagicMock(spec=Path)
    f.read_text.return_value = content
    f.name = name
    f.relative_to.return_value.parts = parts
    return f


class TestAssessCodeStructure:
    def test_perfect_score_small_file(self):
        f = _mock_file("x = 1\n" * 10, parts=("src", "m.py"))
        result = assess_code_structure([f])
        assert result["grade"] == 10

    def test_penalty_large_avg_loc(self):
        f = _mock_file("x = 1\n" * 201, parts=("src", "m.py"))
        result = assess_code_structure([f])
        # avg > 200 => -2; max 201 is not > 500 so no extra penalty => 8
        assert result["grade"] == 8

    def test_penalty_large_avg_and_max_loc(self):
        f = _mock_file("x = 1\n" * 501, parts=("src", "m.py"))
        result = assess_code_structure([f])
        # avg > 200 => -2; max > 500 => -2; total => 6
        assert result["grade"] == 6

    def test_penalty_deep_directory(self):
        f = _mock_file("x = 1\n", parts=("a", "b", "c", "d", "e", "f", "g.py"))
        result = assess_code_structure([f])
        # depth 7 > 5 => -2
        assert result["grade"] <= 8


class TestAssessDocumentation:
    def test_full_coverage(self):
        content = '''
def foo():
    """Docstring."""
    return True

class Bar:
    """Class docstring."""
    pass
'''
        f = _mock_file(content)
        with patch("pathlib.Path.rglob", return_value=[]):
            result = assess_documentation([f])
        assert result["grade"] == 10

    def test_zero_coverage(self):
        f = _mock_file("def foo(): return True\n\nclass Bar: pass\n")
        with patch("pathlib.Path.rglob", return_value=[]):
            result = assess_documentation([f])
        assert result["grade"] == 0

    def test_readme_bonus(self):
        f = _mock_file("def foo():\n    '''doc'''\n    return True\n")
        with patch("pathlib.Path.rglob", return_value=[Path(f"r{i}.md") for i in range(6)]):
            result = assess_documentation([f])
        # 100% coverage => 10, plus bonus => still min 10
        assert result["grade"] == 10


class TestAssessTestCoverage:
    def test_few_files_no_bonus(self):
        with patch("pathlib.Path.rglob", return_value=[Path("test_a.py")]):
            result = assess_test_coverage(Path("/tmp"))  # nosec B108
        assert result["grade"] == 3

    def test_many_files_bonus(self):
        with patch("pathlib.Path.rglob", return_value=[Path(f"test_{i}.py") for i in range(25)]):
            with patch("pathlib.Path.read_text", return_value="pytest-cov"):
                with patch("pathlib.Path.exists", return_value=True):
                    result = assess_test_coverage(Path("/tmp"))  # nosec B108
        # 3 + 1(>5) + 2(>20) + 2(pytest-cov) = 8
        assert result["grade"] == 8


class TestAssessErrorHandling:
    def test_good_error_handling(self):
        f = _mock_file("try:\n    x()\nexcept Exception:\n    pass\n")
        result = assess_error_handling([f])
        assert result["grade"] == 7

    def test_bare_except_penalty(self):
        content = "try:\n    x()\nexcept:\n    pass\n" * 6
        f = _mock_file(content)
        result = assess_error_handling([f])
        # 6 bare excepts => -2, base 7 => 5
        assert result["grade"] == 5


class TestAssessPerformance:
    def test_no_profiling_tools(self):
        f = _mock_file("x = 1\n")
        result = assess_performance([f])
        assert result["grade"] == 7.0

    def test_with_profiling_tool(self):
        f = _mock_file("import cProfile\n")
        result = assess_performance([f])
        assert result["grade"] == 8.0


class TestAssessSecurity:
    def test_no_audit_tools(self):
        with patch("pathlib.Path.glob", return_value=[]):
            result = assess_security(Path("/tmp"))  # nosec B108
        assert result["grade"] == 7

    def test_with_pip_audit(self):
        w = MagicMock()
        w.read_text.return_value = "uses: pypa/gh-action-pip-audit"
        with patch("pathlib.Path.glob", return_value=[w]):
            result = assess_security(Path("/tmp"))  # nosec B108
        assert result["grade"] == 9


class TestAssessDependencies:
    def test_all_present_and_pinned(self):
        root = MagicMock()
        req = root / "requirements.txt"
        req.exists.return_value = True
        req.read_text.return_value = "flask==2.0.0\nrequests==2.0.0"
        pkg = root / "package.json"
        pkg.exists.return_value = True
        result = assess_dependencies(root)
        assert result["grade"] == 10

    def test_missing_requirements(self):
        root = MagicMock()
        req = root / "requirements.txt"
        req.exists.return_value = False
        pkg = root / "package.json"
        pkg.exists.return_value = False
        result = assess_dependencies(root)
        assert result["grade"] == 0


class TestAssessCicd:
    def test_workflows_with_tests(self):
        root = MagicMock()
        wdir = root / ".github" / "workflows"
        wdir.exists.return_value = True
        w = MagicMock()
        w.read_text.return_value = "run: pytest"
        wdir.glob.return_value = [w]
        result = assess_cicd(root)
        assert result["grade"] == 8

    def test_no_workflows_dir(self):
        root = MagicMock()
        wdir = root / ".github" / "workflows"
        wdir.exists.return_value = False
        result = assess_cicd(root)
        assert result["grade"] == 0


class TestAssessCodeStyle:
    def test_ruff_and_precommit(self, tmp_path):
        (tmp_path / "ruff.toml").write_text("", encoding="utf-8")
        (tmp_path / ".pre-commit-config.yaml").write_text("", encoding="utf-8")
        result = assess_code_style(tmp_path)
        assert result["grade"] == 8

    def test_nothing_found(self, tmp_path):
        result = assess_code_style(tmp_path)
        assert result["grade"] == 0

    def test_flake8_only(self, tmp_path):
        (tmp_path / ".flake8").write_text("", encoding="utf-8")
        result = assess_code_style(tmp_path)
        assert result["grade"] == 5


class TestAssessApiDesign:
    def test_fully_typed(self):
        f = _mock_file("def foo() -> int:\n    return 1\n")
        result = assess_api_design([f])
        assert result["grade"] == 10

    def test_no_functions(self):
        f = _mock_file("x = 1\n")
        result = assess_api_design([f])
        assert result["grade"] == 5  # base score


class TestAssessDataHandling:
    def test_io_without_validation(self):
        f = _mock_file("json.load(fp)\n")
        result = assess_data_handling([f])
        assert result["grade"] == 7

    def test_with_pydantic(self):
        f = _mock_file("from pydantic import BaseModel\njson.load(fp)\n")
        result = assess_data_handling([f])
        assert result["grade"] == 8


class TestAssessLogging:
    def test_logging_preferred(self):
        f = _mock_file("logging.info('msg')\n", name="app.py")
        result = assess_logging([f])
        assert result["grade"] == 8

    def test_print_only(self):
        f = _mock_file("print('msg')\n", name="app.py")
        result = assess_logging([f])
        assert result["grade"] == 5

    def test_test_files_skipped(self):
        f = _mock_file("print('msg')\n", name="test_app.py")
        result = assess_logging([f])
        # test file is skipped => no usage counted => score 5
        assert result["grade"] == 5


class TestAssessConfiguration:
    def test_config_and_env(self, tmp_path):
        (tmp_path / ".env.example").write_text("", encoding="utf-8")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("os.environ['KEY']", encoding="utf-8")
        result = assess_configuration(tmp_path)
        # .env.example => +5, env var found => +3
        assert result["grade"] == 8


class TestAssessScalability:
    def test_async_pattern(self):
        f = _mock_file("import asyncio\nasync def foo(): pass\n")
        result = assess_scalability([f])
        assert result["grade"] == 7

    def test_no_patterns(self):
        f = _mock_file("x = 1\n")
        result = assess_scalability([f])
        assert result["grade"] == 5


class TestAssessMaintainability:
    def test_low_complexity(self):
        f = _mock_file("def foo():\n    return 1\n")
        result = assess_maintainability([f])
        assert result["grade"] == 10

    def test_high_complexity(self):
        branches = "\n".join(f"    if x{i}: pass" for i in range(11))
        f = _mock_file(f"def foo():\n{branches}\n")
        result = assess_maintainability([f])
        # avg 11 > 10 => -5
        assert result["grade"] == 5
