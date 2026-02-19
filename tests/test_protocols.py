"""Tests for Protocol interfaces and dataclass adoption.

Verifies that:
- Protocol interfaces are runtime-checkable where appropriate
- Existing concrete classes satisfy their respective Protocols
- New dataclasses are frozen, correctly constructed, and hashable
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.protocols import (
    DynamicalSystemProtocol,
)
from src.tangent_models.examples import (
    PlanarQuadrotor,
    RobotArm,
    SimplePendulum,
    SpacecraftRendezvous,
)
from src.tools.utils.analysis_utils import (
    ErrorHandlingMetrics,
    FunctionDetail,
    LoggingMetrics,
    PythonFileMetrics,
    collect_error_handling_metrics,
    collect_function_details,
    collect_logging_metrics,
    collect_python_file_metrics,
)
from src.tools.utils.report_utils import AssessmentFinding
from src.tools.utils.shell_utils import ToolResult

# ---------------------------------------------------------------------------
# DynamicalSystemProtocol
# ---------------------------------------------------------------------------


class TestDynamicalSystemProtocol:
    """Verify all dynamical system classes satisfy the Protocol."""

    @pytest.mark.parametrize(
        "cls",
        [SimplePendulum, SpacecraftRendezvous, PlanarQuadrotor, RobotArm],
        ids=["pendulum", "spacecraft", "quadrotor", "robot_arm"],
    )
    def test_isinstance_check(self, cls: type) -> None:
        """Concrete dynamical systems pass runtime isinstance check."""
        instance = cls()
        assert isinstance(instance, DynamicalSystemProtocol)


# ---------------------------------------------------------------------------
# FileValidator Protocol
# ---------------------------------------------------------------------------


class TestFileValidatorProtocol:
    """Verify code-quality checkers match the FileValidator protocol."""

    def test_banned_patterns_satisfies_protocol(self) -> None:
        """check_banned_patterns has the FileValidator signature."""
        from src.tools.code_quality.pattern_checker import check_banned_patterns

        # Calling with correct args should not raise
        result = check_banned_patterns(["# some code"], Path("test.py"))
        assert isinstance(result, list)

    def test_magic_numbers_satisfies_protocol(self) -> None:
        """check_magic_numbers has the FileValidator signature."""
        from src.tools.code_quality.pattern_checker import check_magic_numbers

        result = check_magic_numbers(["x = 42"], Path("test.py"))
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Dataclass tests: PythonFileMetrics
# ---------------------------------------------------------------------------


class TestPythonFileMetrics:
    """Verify PythonFileMetrics dataclass behavior."""

    def test_defaults(self) -> None:
        """Default construction yields zero counters."""
        m = PythonFileMetrics()
        assert m.functions == 0
        assert m.classes == 0
        assert m.docstrings == 0
        assert m.typed_returns == 0
        assert m.branches == 0

    def test_frozen(self) -> None:
        """PythonFileMetrics is immutable."""
        m = PythonFileMetrics(functions=5)
        with pytest.raises(AttributeError):
            m.functions = 10  # type: ignore[misc]

    def test_hashable(self) -> None:
        """Frozen dataclass is hashable (usable in sets/dicts)."""
        m1 = PythonFileMetrics(functions=3, classes=1)
        m2 = PythonFileMetrics(functions=3, classes=1)
        assert hash(m1) == hash(m2)
        assert m1 == m2

    def test_collect_returns_dataclass(self, tmp_path: Path) -> None:
        """collect_python_file_metrics returns a PythonFileMetrics instance."""
        source = tmp_path / "sample.py"
        source.write_text(
            'def foo() -> int:\n    """Docstring."""\n    return 42\n',
            encoding="utf-8",
        )
        result = collect_python_file_metrics(source)
        assert isinstance(result, PythonFileMetrics)
        assert result.functions == 1
        assert result.docstrings == 1
        assert result.typed_returns == 1


# ---------------------------------------------------------------------------
# Dataclass tests: FunctionDetail
# ---------------------------------------------------------------------------


class TestFunctionDetail:
    """Verify FunctionDetail dataclass behavior."""

    def test_construction(self) -> None:
        """FunctionDetail stores all fields correctly."""
        fd = FunctionDetail(name="my_func", lineno=10, args=3, body_lines=5, has_docstring=True)
        assert fd.name == "my_func"
        assert fd.lineno == 10
        assert fd.args == 3
        assert fd.body_lines == 5
        assert fd.has_docstring is True

    def test_frozen(self) -> None:
        """FunctionDetail is immutable."""
        fd = FunctionDetail(name="f", lineno=1, args=0, body_lines=1, has_docstring=False)
        with pytest.raises(AttributeError):
            fd.name = "g"  # type: ignore[misc]

    def test_collect_returns_list_of_dataclasses(self) -> None:
        """collect_function_details returns FunctionDetail instances."""
        source = 'def foo():\n    """Doc."""\n    pass\ndef bar(x):\n    return x\n'
        result = collect_function_details(source)
        assert len(result) == 2
        assert all(isinstance(d, FunctionDetail) for d in result)
        assert result[0].name == "foo"
        assert result[1].name == "bar"


# ---------------------------------------------------------------------------
# Dataclass tests: ErrorHandlingMetrics
# ---------------------------------------------------------------------------


class TestErrorHandlingMetrics:
    """Verify ErrorHandlingMetrics dataclass behavior."""

    def test_collect(self) -> None:
        """collect_error_handling_metrics returns correct counts."""
        content = (
            "try:\n    pass\nexcept:\n    pass\ntry:\n    pass\nexcept ValueError:\n    pass\n"
        )
        result = collect_error_handling_metrics(content)
        assert isinstance(result, ErrorHandlingMetrics)
        assert result.try_count == 2
        assert result.bare_except_count == 1


# ---------------------------------------------------------------------------
# Dataclass tests: LoggingMetrics
# ---------------------------------------------------------------------------


class TestLoggingMetrics:
    """Verify LoggingMetrics dataclass behavior."""

    def test_collect_logging(self) -> None:
        """Detects logging usage correctly."""
        result = collect_logging_metrics("logger.info('hello')")
        assert isinstance(result, LoggingMetrics)
        assert result.logging_usage == 1
        assert result.print_usage == 0

    def test_collect_print(self) -> None:
        """Detects print usage correctly."""
        result = collect_logging_metrics("print('hello')")
        assert result.logging_usage == 0
        assert result.print_usage == 1


# ---------------------------------------------------------------------------
# Dataclass tests: ToolResult
# ---------------------------------------------------------------------------


class TestToolResult:
    """Verify ToolResult dataclass behavior."""

    def test_construction(self) -> None:
        """ToolResult stores all fields correctly."""
        tr = ToolResult(exit_code=0, output="ok", errors="")
        assert tr.exit_code == 0
        assert tr.output == "ok"
        assert tr.errors == ""

    def test_frozen(self) -> None:
        """ToolResult is immutable."""
        tr = ToolResult(exit_code=0, output="", errors="")
        with pytest.raises(AttributeError):
            tr.exit_code = 1  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Dataclass tests: AssessmentFinding
# ---------------------------------------------------------------------------


class TestAssessmentFinding:
    """Verify AssessmentFinding dataclass behavior."""

    def test_construction(self) -> None:
        """AssessmentFinding stores all fields correctly."""
        af = AssessmentFinding(
            category_id="A",
            category_name="Architecture",
            grade=8.5,
            details="Well structured",
            recommendations=["Add more tests"],
        )
        assert af.category_id == "A"
        assert af.grade == 8.5
        assert len(af.recommendations) == 1

    def test_default_recommendations(self) -> None:
        """recommendations defaults to empty list."""
        af = AssessmentFinding(
            category_id="B",
            category_name="Quality",
            grade=7.0,
            details="Good",
        )
        assert af.recommendations == []

    def test_frozen(self) -> None:
        """AssessmentFinding is immutable."""
        af = AssessmentFinding(
            category_id="A",
            category_name="Arch",
            grade=5.0,
            details="OK",
        )
        with pytest.raises(AttributeError):
            af.grade = 9.0  # type: ignore[misc]
