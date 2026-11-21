"""Oracles 1, 5, 6, 7, and 8 for result contracts and lifecycle vocabulary gates (Part of #5565)."""

from __future__ import annotations

import ast
import math
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any

import pytest

from src.core.result_contract import (
    SOLVER_TRUTH_TABLE,
    ResultMixin,
    ResultStatus,
    SolverTruthTable,
    derive_solver_status,
    find_status_enums_ast,
    require_finite_value,
    validate_lifecycle_vocabulary,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
_TARGET_FIELDS = frozenset({"success", "converged", "ok"})
_CLASS_SUFFIXES = ("Result", "Response", "Output")


def _find_default_true_in_class(node: ast.ClassDef, file_rel: str) -> list[tuple[str, str, str]]:
    """Return findings if node defaults success, converged, or ok to True."""
    if not any(node.name.endswith(sfx) for sfx in _CLASS_SUFFIXES):
        return []
    findings: list[tuple[str, str, str]] = []
    for item in node.body:
        val = getattr(item, "value", None)
        if isinstance(val, ast.Constant) and val.value is True:
            targets = (
                [item.target.id]
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)
                else [t.id for t in getattr(item, "targets", []) if isinstance(t, ast.Name)]
            )
            for tid in targets:
                if tid in _TARGET_FIELDS:
                    findings.append((file_rel, node.name, tid))
    return findings


class TestOracle1NoDefaultTrueResults:
    """Oracle 1: No Result, Response, or Output class defaults success, ok, or converged to True."""

    def test_ast_scan_no_default_true_in_src(self) -> None:
        offending: list[tuple[str, str, str]] = []
        for py_file in SRC_DIR.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            file_rel = str(py_file.relative_to(REPO_ROOT))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    offending.extend(_find_default_true_in_class(node, file_rel))

        assert not offending, f"Classes with default-true: {offending}"

    def test_swing_optimization_result_requires_explicit_converged(self) -> None:
        from src.affine_control.swing_types import SwingOptimizationResult

        with pytest.raises(TypeError):
            SwingOptimizationResult(  # type: ignore[call-arg]
                optimal_controls=[],
                optimal_trajectory=[],
                final_velocity=10.0,
                cost=1.0,
                iterations=5,
            )


class TestOracle5SolverTruthTable:
    """Oracle 5: Solver truth table (converged x feasible x finite)."""

    def test_truth_table_entries(self) -> None:
        assert SolverTruthTable is SOLVER_TRUTH_TABLE
        expected = {
            (True, True, True): ResultStatus.SUCCEEDED,
            (False, True, True): ResultStatus.ITERATION_LIMIT,
            (True, False, True): ResultStatus.INFEASIBLE,
            (False, False, True): ResultStatus.FAILED,
        }
        for k, v in expected.items():
            assert SOLVER_TRUTH_TABLE[k] is v
        for conv in (True, False):
            for feas in (True, False):
                assert SOLVER_TRUTH_TABLE[(conv, feas, False)] is ResultStatus.NUMERICAL_FAILURE

    def test_derive_solver_status(self) -> None:
        pairs = (
            ((True, True, True), ResultStatus.SUCCEEDED),
            ((False, True, True), ResultStatus.ITERATION_LIMIT),
            ((True, False, True), ResultStatus.INFEASIBLE),
            ((False, False, True), ResultStatus.FAILED),
            ((True, True, False), ResultStatus.NUMERICAL_FAILURE),
            ((False, False, False), ResultStatus.NUMERICAL_FAILURE),
        )
        for (c, fe, fi), expected in pairs:
            assert derive_solver_status(c, fe, fi) is expected


class TestOracle6NonFiniteRejection:
    """Oracle 6: Non-finite values rejected, never coerced to 0.0."""

    def test_require_finite_value_success(self) -> None:
        assert require_finite_value(0.0) == 0.0
        assert require_finite_value(42.5, "speed") == 42.5
        assert require_finite_value(-10) == -10.0

    def test_require_finite_value_rejects_nan_and_inf(self) -> None:
        for non_finite in (float("nan"), float("inf"), float("-inf")):
            with pytest.raises(ValueError, match="value must be finite"):
                require_finite_value(non_finite, "cost")

    def test_require_finite_value_rejects_non_floats(self) -> None:
        for bad in ("0.0", True, False, None, [1.0]):
            with pytest.raises(TypeError, match="expected float"):
                require_finite_value(bad, "metric")  # type: ignore[arg-type]

    def test_non_finite_solver_yields_numerical_failure(self) -> None:
        finite = math.isfinite(float("nan"))
        assert derive_solver_status(True, True, finite) is ResultStatus.NUMERICAL_FAILURE


class TestOracle7LifecycleVocabularyGate:
    """Oracle 7: Canonical lifecycle vocabulary gate."""

    def test_ast_scan_status_enums_in_src(self) -> None:
        status_enums = find_status_enums_ast(SRC_DIR)
        for name, members in status_enums.items():
            assert validate_lifecycle_vocabulary(members), f"{name}: {members}"

    def test_validate_lifecycle_vocabulary(self) -> None:
        conforming = ["QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED"]
        assert validate_lifecycle_vocabulary(conforming) is True
        for legacy in (["COMPLETED"], ["DONE"], ["ERROR"], ["FINISHED"], ["ABORTED"]):
            assert validate_lifecycle_vocabulary(legacy) is False

    def test_synthetic_enum_validation(self) -> None:
        class ValidJobStatus(StrEnum):
            QUEUED = "QUEUED"
            RUNNING = "RUNNING"
            SUCCEEDED = "SUCCEEDED"

        class LegacyRunStatus(Enum):
            QUEUED = 1
            DONE = 2

        assert validate_lifecycle_vocabulary([m.name for m in ValidJobStatus]) is True
        assert validate_lifecycle_vocabulary([m.name for m in LegacyRunStatus]) is False


class TestOracle8BackwardsCompatibleBooleanProperties:
    """Oracle 8: Backwards-compatible derived boolean properties."""

    def test_properties_match_succeeded_status(self) -> None:
        for status in ResultStatus:
            obj = ResultMixin(status=status)
            is_succeeded = status is ResultStatus.SUCCEEDED
            assert obj.success is is_succeeded
            assert obj.ok is is_succeeded
            assert obj.converged is is_succeeded

    def test_properties_are_read_only(self) -> None:
        obj = ResultMixin(status=ResultStatus.SUCCEEDED)
        for attr in ("success", "ok", "converged"):
            with pytest.raises(AttributeError):
                setattr(obj, attr, False)

    def test_mixin_status_validation(self) -> None:
        bad_status: Any = "SUCCEEDED"
        with pytest.raises(TypeError, match="instance of ResultStatus"):
            ResultMixin(status=bad_status)
