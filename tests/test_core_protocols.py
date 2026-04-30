"""Tests for src.core.protocols structural typing contracts.

Verifies isinstance checks against runtime-checkable Protocol
``DynamicalSystemProtocol`` and that the documented Protocol classes are
importable, properly typed, and accept compliant duck-typed implementations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from src.core.protocols import (
    ContentTransformer,
    DynamicalSystemProtocol,
    FileDiscoverer,
    FileValidator,
    IssueRecord,
    MetricsCollector,
    ReportGenerator,
)


class _GoodSystem:
    """Minimal duck-typed dynamical system (no inheritance)."""

    def dynamics(
        self,
        x: np.ndarray[Any, Any],
        u: np.ndarray[Any, Any] | float | list[float],
    ) -> np.ndarray[Any, Any]:
        u_val = u if isinstance(u, float | int) else float(np.asarray(u).ravel()[0])
        return np.array([x[1], -x[0] + u_val])

    def linearize(
        self,
        x: np.ndarray[Any, Any],
        u: np.ndarray[Any, Any] | float | list[float],
    ) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
        return np.array([[0.0, 1.0], [-1.0, 0.0]]), np.array([[0.0], [1.0]])


class _MissingLinearize:
    def dynamics(self, x: Any, u: Any) -> np.ndarray[Any, Any]:
        return np.zeros_like(x)


class _NotASystem:
    pass


class TestDynamicalSystemProtocol:
    def test_compliant_duck_type_passes_isinstance(self) -> None:
        # runtime_checkable Protocol allows isinstance check
        assert isinstance(_GoodSystem(), DynamicalSystemProtocol)

    def test_missing_linearize_fails_isinstance(self) -> None:
        assert not isinstance(_MissingLinearize(), DynamicalSystemProtocol)

    def test_unrelated_object_fails_isinstance(self) -> None:
        assert not isinstance(_NotASystem(), DynamicalSystemProtocol)
        assert not isinstance(object(), DynamicalSystemProtocol)

    def test_protocol_call_via_duck_typed_object_returns_correct_shape(self) -> None:
        sys_: DynamicalSystemProtocol = _GoodSystem()
        x = np.array([1.0, 2.0])
        dx = sys_.dynamics(x, 0.5)
        A, B = sys_.linearize(x, 0.5)
        assert dx.shape == (2,)
        assert A.shape == (2, 2)
        assert B.shape == (2, 1)

    def test_concrete_pendulum_satisfies_protocol(self) -> None:
        # The repo's SimplePendulum should satisfy the structural contract.
        from src.tangent_models.examples import SimplePendulum

        assert isinstance(SimplePendulum(), DynamicalSystemProtocol)


class TestNonRuntimeCheckableProtocols:
    """The pipeline protocols are not runtime_checkable; verify importability and shape."""

    def test_issue_record_alias_is_tuple_type(self) -> None:
        # IssueRecord is a tuple alias — instances should match the structure
        rec: IssueRecord = (10, "msg", "snippet")
        assert isinstance(rec, tuple) and len(rec) == 3

    def test_file_validator_callable_signature(self) -> None:
        def my_validator(lines: list[str], filepath: Path) -> list[IssueRecord]:
            return [(i, "warn", line) for i, line in enumerate(lines) if "TODO" in line]

        # Type check via Protocol assignment (structural)
        v: FileValidator = my_validator  # type: ignore[assignment]
        out = v(["x = 1", "# TODO fix"], Path("a.py"))
        assert out == [(1, "warn", "# TODO fix")]

    def test_content_transformer_pipeline(self) -> None:
        def upper(s: str) -> str:
            return s.upper()

        def reverse(s: str) -> str:
            return s[::-1]

        t1: ContentTransformer = upper  # type: ignore[assignment]
        t2: ContentTransformer = reverse  # type: ignore[assignment]
        assert t2(t1("abc")) == "CBA"

    def test_report_generator_writes_file(self, tmp_path: Path) -> None:
        def gen(
            category_id: str,
            category_name: str,
            grade: float,
            details: str,
            output_dir: str | Path,
        ) -> Path:
            out = Path(output_dir) / f"{category_id}.md"
            out.write_text(f"# {category_name} ({grade})\n{details}", encoding="utf-8")
            return out

        rg: ReportGenerator = gen  # type: ignore[assignment]
        path = rg("A1", "Quality", 9.5, "ok", tmp_path)
        assert path.exists() and "A1" in path.name and "9.5" in path.read_text()

    def test_file_discoverer_lists_paths(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("")
        (tmp_path / "b.py").write_text("")

        def discover(root_dir: str | Path, **_: Any) -> list[Path]:
            return sorted(Path(root_dir).glob("*.py"))

        fd: FileDiscoverer = discover  # type: ignore[assignment]
        files = fd(tmp_path)
        assert len(files) == 2
        assert all(p.suffix == ".py" for p in files)

    def test_metrics_collector_returns_int_dict(self, tmp_path: Path) -> None:
        f = tmp_path / "x.py"
        f.write_text("a = 1\nb = 2\n")

        def collect(filepath: Path) -> dict[str, int]:
            text = filepath.read_text()
            return {"lines": text.count("\n"), "chars": len(text)}

        mc: MetricsCollector = collect  # type: ignore[assignment]
        m = mc(f)
        assert m["lines"] == 2
        assert m["chars"] == len("a = 1\nb = 2\n")
        assert all(isinstance(v, int) for v in m.values())
