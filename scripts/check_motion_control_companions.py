"""Fail CI when motion-control companion files contradict rewritten chapters (#5615)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MOTION_DIR = REPO_ROOT / "articles" / "motion-control"

REMOVED_COMPANIONS = frozenset(
    {
        "chapter2_artifact.jsx",
        "chapter3_artifact.jsx",
        "chapter4_artifact.jsx",
        "Book Expansion and Writing.md",
    }
)

FORBIDDEN_EXTENSIONS = frozenset({".jsx"})

SUMMARY_FORBIDDEN_PHRASES = (
    "Throwing Away the Target",
    "15-DOF musculoskeletal",
    "revolutionary framework",
    "first comprehensive treatment",
    "Funnel synthesis for the complete swing",
    "Underactuation as Advantage",
)

SUMMARY_REQUIRED_PHRASES = (
    "Motion, Targets, and Timing",
    "Geometry, Feasible Dynamics, and Robust Outcomes",
)

COMPILE_FORBIDDEN_SUBSTRINGS = (
    "/mnt/project/",
    "/home/claude/",
    "A New Framework for Nonlinear Systems",
)

CONTRADICTION_MARKERS = (
    "minor axis and lowest at the ends of the major axis",
    "asymptotically orbitally stable if and only if",
    "if and only if the origin of the transverse linearization",
    "singularity at ‖ω‖ = π",
    "Numerical computation reveals the amplification",
    "~90% of total control effort",
    "gain margin [½, ∞)",
    "Skilled golfers are accurate because the trajectory's passive transverse dynamics",
)

SCAN_SUFFIXES = frozenset({".jsx", ".js", ".md", ".html", ".tsx", ".ts"})

_SKIP_SCAN_NAMES = frozenset({"BOOK_SUMMARY.md"})


def _scan_companion_file(path: Path) -> list[str]:
    try:
        body = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        return [f"{path.name}: unreadable companion ({exc})"]
    hits = [marker for marker in CONTRADICTION_MARKERS if marker in body]
    if not hits:
        return []
    return [f"{path.name}: contradiction marker {hit!r}" for hit in hits]


def check_motion_control_companions(motion_dir: Path) -> list[str]:
    """Return human-readable violations for motion-control companion hygiene."""
    violations: list[str] = []
    if not motion_dir.is_dir():
        return [f"motion-control directory missing: {motion_dir}"]

    for name in REMOVED_COMPANIONS:
        if (motion_dir / name).is_file():
            violations.append(f"removed companion still present: {name}")

    for path in sorted(motion_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix in FORBIDDEN_EXTENSIONS:
            violations.append(f"forbidden companion extension: {path.name}")
            continue
        if path.suffix not in SCAN_SUFFIXES or path.name in _SKIP_SCAN_NAMES:
            continue
        violations.extend(_scan_companion_file(path))

    summary = motion_dir / "BOOK_SUMMARY.md"
    if summary.is_file():
        text = summary.read_text(encoding="utf-8")
        for phrase in SUMMARY_FORBIDDEN_PHRASES:
            if phrase in text:
                violations.append(f"BOOK_SUMMARY.md: stale overclaim {phrase!r}")
        for phrase in SUMMARY_REQUIRED_PHRASES:
            if phrase not in text:
                violations.append(f"BOOK_SUMMARY.md: missing scoped phrase {phrase!r}")

    compile_script = motion_dir / "compile_book.py"
    if compile_script.is_file():
        source = compile_script.read_text(encoding="utf-8")
        for forbidden in COMPILE_FORBIDDEN_SUBSTRINGS:
            if forbidden in source:
                violations.append(f"compile_book.py: forbidden substring {forbidden!r}")
        if "_SCRIPT_DIR = Path(__file__).resolve().parent" not in source:
            violations.append("compile_book.py: missing repo-relative _SCRIPT_DIR anchor")

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--motion-dir",
        type=Path,
        default=DEFAULT_MOTION_DIR,
        help="Path to articles/motion-control (default: repo tree)",
    )
    args = parser.parse_args(argv)
    violations = check_motion_control_companions(args.motion_dir.resolve())
    if violations:
        for line in violations:
            print(line, file=sys.stderr)
        return 1
    print(f"OK: motion-control companions aligned ({args.motion_dir})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
