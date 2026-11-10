"""Result status contracts, solver truth tables, and vocabulary gates for AffineDrift.

Standard-library-only contract implementing Dieter's Owner Decision #1 & #2 on #5565.
"""

from __future__ import annotations

import ast
import math
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

__all__ = [
    "CANONICAL_LIFECYCLE_WORDS",
    "ResultMixin",
    "ResultStatus",
    "SOLVER_TRUTH_TABLE",
    "SolverTruthTable",
    "derive_solver_status",
    "find_status_enums_ast",
    "require_finite_value",
    "validate_lifecycle_vocabulary",
]


class ResultStatus(StrEnum):
    """Canonical result and solver outcome status."""

    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    INFEASIBLE = "INFEASIBLE"
    ITERATION_LIMIT = "ITERATION_LIMIT"
    STALLED = "STALLED"
    NUMERICAL_FAILURE = "NUMERICAL_FAILURE"
    UNAVAILABLE = "UNAVAILABLE"


# Truth table: (converged, feasible, finite) -> ResultStatus
SOLVER_TRUTH_TABLE: dict[tuple[bool, bool, bool], ResultStatus] = {
    (True, True, True): ResultStatus.SUCCEEDED,
    (False, True, True): ResultStatus.ITERATION_LIMIT,
    (True, False, True): ResultStatus.INFEASIBLE,
    (False, False, True): ResultStatus.FAILED,
    (True, True, False): ResultStatus.NUMERICAL_FAILURE,
    (False, True, False): ResultStatus.NUMERICAL_FAILURE,
    (True, False, False): ResultStatus.NUMERICAL_FAILURE,
    (False, False, False): ResultStatus.NUMERICAL_FAILURE,
}

SolverTruthTable = SOLVER_TRUTH_TABLE


def derive_solver_status(
    converged: bool,
    feasible: bool,
    finite: bool = True,
) -> ResultStatus:
    """Derive categorical ResultStatus from solver convergence, feasibility, and finiteness."""
    return SOLVER_TRUTH_TABLE[(bool(converged), bool(feasible), bool(finite))]


def require_finite_value(v: float, field_name: str = "") -> float:
    """Validate that a float value is finite, rejecting NaN and Inf."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        p = f"field {field_name!r}: " if field_name else ""
        raise TypeError(f"{p}expected float, got {type(v).__name__}")
    if not math.isfinite(f_val := float(v)):
        p = f"field {field_name!r}: " if field_name else ""
        raise ValueError(f"{p}value must be finite, got {f_val}")
    return f_val


@dataclass(frozen=True)
class ResultMixin:
    """Mixin or base providing backwards-compatible derived boolean properties."""

    status: ResultStatus

    def __post_init__(self) -> None:
        raw_status: object = self.status
        if not isinstance(raw_status, ResultStatus):
            t = type(raw_status).__name__
            raise TypeError(f"status must be an instance of ResultStatus: {t}")

    @property
    def success(self) -> bool:
        return self.status is ResultStatus.SUCCEEDED

    @property
    def ok(self) -> bool:
        return self.status is ResultStatus.SUCCEEDED

    @property
    def converged(self) -> bool:
        return self.status is ResultStatus.SUCCEEDED


CANONICAL_LIFECYCLE_WORDS: frozenset[str] = frozenset(
    {"QUEUED", "RUNNING", "CANCEL_REQUESTED", "SUCCEEDED", "FAILED", "CANCELLED"}
)


def validate_lifecycle_vocabulary(
    members: set[str] | frozenset[str] | list[str],
) -> bool:
    """Validate that all member names are a subset of CANONICAL_LIFECYCLE_WORDS."""
    return set(members).issubset(CANONICAL_LIFECYCLE_WORDS)


def find_status_enums_ast(
    directory: Path,
    suffixes: tuple[str, ...] = ("JobStatus", "RunStatus", "LifecycleStatus", "TaskStatus"),
) -> dict[str, list[str]]:
    """Scan directory using AST for Enum classes ending with designated suffixes."""
    found: dict[str, list[str]] = {}
    for py_file in directory.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith(suffixes):
                members = [
                    t.id
                    for item in node.body
                    if isinstance(item, ast.Assign)
                    for t in item.targets
                    if isinstance(t, ast.Name)
                ]
                found[node.name] = members
    return found
