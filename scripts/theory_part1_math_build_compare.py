#!/usr/bin/env python3
"""Compare Quarto build time for Theory Part 1: default vs KaTeX profile (#5253)."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
THEORY_PART1 = REPO_ROOT / "articles" / "theory-part1.qmd"
KATEX_METADATA = "format.html.html-math-method:method:katex"
DEFAULT_LABEL = "mathjax_gate"
PROTOTYPE_LABEL = "katex_prototype"


@dataclass(frozen=True)
class RenderTiming:
    """Wall-clock seconds for one Quarto render."""

    label: str
    seconds: float
    profile: str | None


def _quarto_available() -> bool:
    return shutil.which("quarto") is not None


def _render_once(metadata_override: str | None, output_dir: Path) -> float:
    """Render Theory Part 1 to ``output_dir`` and return elapsed wall time."""
    if not THEORY_PART1.is_file():
        raise FileNotFoundError(f"missing source file: {THEORY_PART1}")
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "quarto",
        "render",
        str(THEORY_PART1),
        "--to",
        "html",
        "--output-dir",
        str(output_dir),
        "--no-cache",
    ]
    if metadata_override is not None:
        command.extend(["-M", metadata_override])
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start
    if completed.returncode != 0:
        raise RuntimeError(
            f"quarto render failed (override={metadata_override!r}): {completed.stderr[-2000:]}"
        )
    return elapsed


def compare_theory_part1_math_build(
    work_root: Path | None = None,
) -> dict[str, float]:
    """Render default and KaTeX-profile builds; return labelled wall-clock seconds."""
    if not _quarto_available():
        raise RuntimeError("quarto is not on PATH; install Quarto to run a live comparison")
    root = work_root or (REPO_ROOT / ".build-compare-5253")
    default_dir = root / DEFAULT_LABEL
    prototype_dir = root / PROTOTYPE_LABEL
    default_seconds = _render_once(None, default_dir)
    prototype_seconds = _render_once(KATEX_METADATA, prototype_dir)
    return {
        DEFAULT_LABEL: default_seconds,
        PROTOTYPE_LABEL: prototype_seconds,
        "delta_seconds": prototype_seconds - default_seconds,
    }


def build_comparison_payload(timings: dict[str, float]) -> dict[str, object]:
    """Return a JSON-serialisable summary for evidence attachment."""
    return {
        "source": str(THEORY_PART1.relative_to(REPO_ROOT)),
        "katex_metadata_override": KATEX_METADATA,
        "timings_seconds": timings,
        "note": (
            "KaTeX profile changes html-math-method only; it is not server-side math "
            "SSR. Delta is build wall time on this host, not a Lighthouse claim."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = sys.argv[1:] if argv is None else argv
    if "--dry-run" in args:
        payload = build_comparison_payload(
            {DEFAULT_LABEL: 0.0, PROTOTYPE_LABEL: 0.0, "delta_seconds": 0.0}
        )
        payload["dry_run"] = True
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return 0
    timings = compare_theory_part1_math_build()
    sys.stdout.write(json.dumps(build_comparison_payload(timings), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
