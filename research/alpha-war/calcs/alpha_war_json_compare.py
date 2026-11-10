"""Tolerance comparison for Alpha War ``study_*`` JSON blocks (#5465)."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

COMPARE_RTOL = 1e-9
COMPARE_ATOL = 1e-12


class JsonCompareError(RuntimeError):
    """Raised when regenerated studies diverge beyond the stated tolerance."""


def study_blocks(payload: dict[str, Any]) -> dict[str, Any]:
    """Return only ``study_*`` top-level blocks from an export."""
    return {key: value for key, value in payload.items() if key.startswith("study_")}


def _walk_numeric_paths(value: Any, prefix: str = "") -> list[tuple[str, float]]:
    """Collect floating-point leaves with dotted path names."""
    out: list[tuple[str, float]] = []
    if isinstance(value, bool):
        return out
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return out
        out.append((prefix, float(value)))
        return out
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            out.extend(_walk_numeric_paths(child, path))
        return out
    if isinstance(value, list):
        for idx, child in enumerate(value):
            path = f"{prefix}[{idx}]"
            out.extend(_walk_numeric_paths(child, path))
    return out


def compare_study_blocks(
    committed: dict[str, Any],
    candidate: dict[str, Any],
    *,
    rtol: float = COMPARE_RTOL,
    atol: float = COMPARE_ATOL,
) -> dict[str, float | int]:
    """Compare numeric leaves in two study payloads; return deviation summary."""
    left = study_blocks(committed)
    right = study_blocks(candidate)
    if set(left) != set(right):
        missing = sorted(set(left) - set(right))
        extra = sorted(set(right) - set(left))
        raise JsonCompareError(f"study block keys differ: missing={missing} extra={extra}")

    max_abs = 0.0
    max_rel = 0.0
    mismatch_count = 0
    for study_key in sorted(left):
        paths_left = dict(_walk_numeric_paths(left[study_key], study_key))
        paths_right = dict(_walk_numeric_paths(right[study_key], study_key))
        if paths_left.keys() != paths_right.keys():
            raise JsonCompareError(f"path mismatch under {study_key}")
        for path, a_val in paths_left.items():
            b_val = paths_right[path]
            delta = abs(a_val - b_val)
            scale = max(abs(a_val), abs(b_val), 1.0)
            rel = delta / scale
            if delta > atol + rtol * scale:
                mismatch_count += 1
            max_abs = max(max_abs, delta)
            max_rel = max(max_rel, rel)
    return {
        "max_abs_deviation": max_abs,
        "max_rel_deviation": max_rel,
        "mismatch_count": mismatch_count,
        "rtol": rtol,
        "atol": atol,
    }


def load_export(path: Path) -> dict[str, Any]:
    """Load a calculation JSON export."""
    return json.loads(path.read_text(encoding="utf-8"))


def compare_export_files(
    committed_path: Path,
    candidate_path: Path,
    *,
    rtol: float = COMPARE_RTOL,
    atol: float = COMPARE_ATOL,
) -> dict[str, float | int]:
    """Compare two on-disk exports."""
    return compare_study_blocks(
        load_export(committed_path),
        load_export(candidate_path),
        rtol=rtol,
        atol=atol,
    )
