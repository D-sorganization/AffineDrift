"""Decide how the benchmark workflow compares against committed baselines.

pytest-benchmark stores runs under ``.benchmarks/<machine_id>/`` where the
machine id is ``<System>-<Implementation>-<major.minor>-<bits>bit`` (for
example ``Linux-CPython-3.12-64bit``). A baseline recorded on other hardware or
another interpreter is not comparable, so the 15% regression gate only applies
when a baseline for *this* platform is committed. Otherwise the run is saved as
a candidate baseline and reported honestly as "no baseline", not as a failure.

Usage (stdlib only, so it runs before dependencies are installed)::

    python scripts/ci/benchmark_compare_args.py decide --github-output "$GITHUB_OUTPUT"
    python scripts/ci/benchmark_compare_args.py status --mode M --outcome O \
        --platform P --artifact A
"""

from __future__ import annotations

import argparse
import platform
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

BASELINE_NAME = "initial"
DEFAULT_THRESHOLD = "15%"
_SAFE_PLATFORM = re.compile(r"^[A-Za-z0-9_.+-]+$")
_THRESHOLD = re.compile(r"^(?:[1-9]\d*|\d+\.\d*[1-9]\d*)%$")
_MODES = ("compare", "save")


@dataclass(frozen=True)
class Decision:
    """Outcome of the baseline lookup."""

    mode: str  # "compare" or "save"
    platform: str
    args: list[str]
    artifact_name: str


def machine_id() -> str:
    """Return the id pytest-benchmark uses for the running interpreter."""
    major, minor = platform.python_version_tuple()[:2]
    bits = 8 * struct.calcsize("P")
    return f"{platform.system()}-{platform.python_implementation()}-{major}.{minor}-{bits}bit"


def _validate_platform(value: str) -> str:
    if not value or not _SAFE_PLATFORM.match(value):
        raise ValueError(f"invalid platform id {value!r}: expected [A-Za-z0-9_.+-]+")
    return value


def _validate_name(value: str) -> str:
    if not value or not _SAFE_PLATFORM.match(value):
        raise ValueError(f"invalid baseline name {value!r}")
    return value


def decide(
    root: Path,
    platform_id: str,
    name: str = BASELINE_NAME,
    threshold: str = DEFAULT_THRESHOLD,
) -> Decision:
    """Choose compare or save mode.

    Preconditions: ``platform_id``/``name`` are path-safe tokens and
    ``threshold`` is a positive percentage such as ``15%``; otherwise
    ``ValueError``. The threshold is never relaxed here: compare mode always
    emits ``--benchmark-compare-fail=mean:<threshold>``.
    """
    platform_id = _validate_platform(platform_id)
    name = _validate_name(name)
    if not _THRESHOLD.match(threshold):
        raise ValueError(f"invalid threshold {threshold!r}: expected e.g. '15%'")
    artifact = f"benchmark-baseline-{platform_id}"
    platform_dir = Path(root) / platform_id
    if platform_dir.is_dir() and any(platform_dir.glob(f"*_{name}.json")):
        return Decision(
            "compare",
            platform_id,
            [f"--benchmark-compare={name}", f"--benchmark-compare-fail=mean:{threshold}"],
            artifact,
        )
    return Decision("save", platform_id, [f"--benchmark-save={name}"], artifact)


def format_status(
    mode: str, outcome: str, platform_id: str, artifact: str, threshold: str = DEFAULT_THRESHOLD
) -> str:
    """Return the one-line PR comment status for a finished benchmark step."""
    if mode not in _MODES:
        raise ValueError(f"invalid mode {mode!r}: expected one of {_MODES}")
    if outcome not in ("success", "failure"):
        return "Benchmark run did not complete"
    if mode == "save":
        note = (
            f"no baseline for {platform_id}; saved one as artifact {artifact}, "
            f"commit it under .benchmarks/{platform_id}/ to enable regression gating"
        )
        if outcome == "success":
            return note
        return f"Benchmarks failed ({note.split(';')[0]})"
    if outcome == "success":
        return (
            f"All benchmarks passed against the {platform_id} baseline "
            f"(regression gate {threshold})"
        )
    return (
        f"Benchmarks failed: test failure or regression over {threshold} "
        f"against the {platform_id} baseline"
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point; returns 2 on invalid input."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decide")
    d.add_argument("--root", default=".benchmarks")
    d.add_argument("--platform", default=None)
    d.add_argument("--github-output", default=None)
    s = sub.add_parser("status")
    s.add_argument("--mode", required=True)
    s.add_argument("--outcome", required=True)
    s.add_argument("--platform", required=True)
    s.add_argument("--artifact", required=True)
    ns = parser.parse_args(argv)
    try:
        if ns.cmd == "decide":
            dec = decide(Path(ns.root), ns.platform or machine_id())
            lines = (
                f"mode={dec.mode}\nplatform={dec.platform}\n"
                f"artifact={dec.artifact_name}\nargs={' '.join(dec.args)}\n"
            )
            if ns.github_output:
                with open(ns.github_output, "a", encoding="utf-8") as fh:
                    fh.write(lines)
            else:
                sys.stdout.write(lines)
        else:
            sys.stdout.write(format_status(ns.mode, ns.outcome, ns.platform, ns.artifact) + "\n")
    except ValueError as exc:
        sys.stderr.write(f"benchmark_compare_args: {exc}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
