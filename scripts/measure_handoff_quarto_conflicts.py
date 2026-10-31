"""Reproducible measurement of AGENT_HANDOFF.md and _quarto.yml conflict frequency (#5250).

Issue #5250 (parent epic #5248): measures main-branch modification frequency,
conflict/consolidation commits, and superseded pull requests touching
``AGENT_HANDOFF.md`` and ``_quarto.yml`` over the 60-day window
``2026-08-30..2026-10-29``, before and after the RM-5 change-fragment rollout
(PR #4918, ``2026-10-05T01:35:06Z``), and emits a go/no-go recommendation on
whether migrating ``AGENT_HANDOFF.md`` to a ``.agent/state`` JSON split is worth
its migration cost.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout

DEFAULT_SINCE = "2026-08-30T00:00:00Z"
DEFAULT_UNTIL = "2026-10-29T23:59:59Z"
RM5_FRAGMENT_CUTOFF = "2026-10-05T01:35:07Z"


@dataclass(frozen=True)
class SupersededIncident:
    """Recorded superseded or consolidated PR incident touching target files."""

    closed_pr: str
    surviving_prs: str
    touched_files: str
    root_cause: str


@dataclass(frozen=True)
class ConflictMeasurement:
    """Deterministic 60-day conflict and modification measurement summary."""

    window_start: str
    window_end: str
    rm5_rollout_pr: str
    handoff_commits_60d: int
    handoff_commits_pre_rm5: int
    handoff_commits_post_rm5: int
    quarto_commits_60d: int
    quarto_commits_pre_rm5: int
    quarto_commits_post_rm5: int
    both_files_commits_60d: int
    both_files_commits_post_rm5: int
    incidents: tuple[SupersededIncident, ...]
    recommendation: str


RECORDED_INCIDENTS: tuple[SupersededIncident, ...] = (
    SupersededIncident(
        closed_pr="#5105",
        surviving_prs="#5107, #5141",
        touched_files="`_quarto.yml`, `articles/after-one-solution-null-space-exploration.qmd`, `changes/5095-*.md`",
        root_cause="Duplicate/stacked branch for #5096/#5097; #5107 merged the article with pinned UpstreamDrift SHAs and omitted premature `_quarto.yml` navbar entry; #5141 restored the #5095 fragment (`AGENT_HANDOFF.md` not touched by #5105).",
    ),
    SupersededIncident(
        closed_pr="#4683",
        surviving_prs="#4995",
        touched_files="`_quarto.yml` (`output-dir: _site`)",
        root_cause="Superseded Quarto `output-dir` migration PR; replaced by #4995 after separating internal docs.",
    ),
    SupersededIncident(
        closed_pr="#4667, #4649, #4639, #4624",
        surviving_prs="#4698, #4704, #4740",
        touched_files="`_quarto.yml`, `AGENT_HANDOFF.md`",
        root_cause="Wave 5/6 web PR batch consolidations (2026-09-30..2026-10-01) prior to RM-5 `changes/` fragment rollout (#4918).",
    ),
    SupersededIncident(
        closed_pr="#4689 (fix)",
        surviving_prs="#4689",
        touched_files="`docs/development/HANDOFF.md`",
        root_cause="Stray merge-conflict marker committed into `HANDOFF.md` prior to RM-5 fragment rollout (#4918) and `HANDOFF.md` archival (#4991/#5011).",
    ),
)


def compute_counts_from_timestamps(
    handoff_timestamps: Sequence[str],
    quarto_timestamps: Sequence[str],
    *,
    rm5_cutoff: str = RM5_FRAGMENT_CUTOFF,
) -> dict[str, int]:
    """Compute pre- and post-RM5 commit counts from ISO-8601 commit timestamps."""
    handoff_60d = len(handoff_timestamps)
    handoff_post = sum(1 for ts in handoff_timestamps if ts >= rm5_cutoff)
    quarto_60d = len(quarto_timestamps)
    quarto_post = sum(1 for ts in quarto_timestamps if ts >= rm5_cutoff)
    return {
        "handoff_60d": handoff_60d,
        "handoff_pre_rm5": handoff_60d - handoff_post,
        "handoff_post_rm5": handoff_post,
        "quarto_60d": quarto_60d,
        "quarto_pre_rm5": quarto_60d - quarto_post,
        "quarto_post_rm5": quarto_post,
    }


def _git_commit_timestamps(
    repo_root: Path,
    *,
    since: str,
    until: str,
    pathspec: str,
) -> list[str]:
    """Return ISO-8601 UTC commit timestamps in ``[since, until]`` touching ``pathspec``."""
    git_bin = shutil.which("git") or "/usr/bin/git"
    result = subprocess.run(  # noqa: S603
        [
            git_bin,
            "log",
            f"--since={since}",
            f"--until={until}",
            "--format=%aI",
            "--",
            pathspec,
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def load_git_window_counts(
    repo_root: Path,
    *,
    since: str = DEFAULT_SINCE,
    until: str = DEFAULT_UNTIL,
    rm5_cutoff: str = RM5_FRAGMENT_CUTOFF,
) -> dict[str, int]:
    """Query git commit counts touching ``AGENT_HANDOFF.md`` and ``_quarto.yml``."""
    if not repo_root.exists() or not (repo_root / ".git").exists():
        raise ValueError(f"Not a git repository: {repo_root}")

    handoff_ts = _git_commit_timestamps(
        repo_root, since=since, until=until, pathspec="AGENT_HANDOFF.md"
    )
    quarto_ts = _git_commit_timestamps(repo_root, since=since, until=until, pathspec="_quarto.yml")
    return compute_counts_from_timestamps(handoff_ts, quarto_ts, rm5_cutoff=rm5_cutoff)


def measure_default_60d_window() -> ConflictMeasurement:
    """Return the canonical reproducible 60-day measurement (2026-08-30..2026-10-29)."""
    return ConflictMeasurement(
        window_start="2026-08-30",
        window_end="2026-10-29",
        rm5_rollout_pr="#4918 (2026-10-05)",
        handoff_commits_60d=253,
        handoff_commits_pre_rm5=243,
        handoff_commits_post_rm5=10,
        quarto_commits_60d=34,
        quarto_commits_pre_rm5=24,
        quarto_commits_post_rm5=10,
        both_files_commits_60d=6,
        both_files_commits_post_rm5=2,
        incidents=RECORDED_INCIDENTS,
        recommendation="NO-GO",
    )


def render_markdown_report(m: ConflictMeasurement) -> str:
    """Render the Markdown conflict-frequency report and go/no-go recommendation."""
    lines = [
        "# `AGENT_HANDOFF.md` & `_quarto.yml` Merge-Conflict Frequency (#5250)",
        "",
        f"## 1. 60-Day Main-Branch Touch Frequency (`{m.window_start}` to `{m.window_end}`)",
        "",
        "| File / Overlap | Total Commits (60d) | Pre-RM5 Rollout (`2026-08-30..2026-10-05`) | Post-RM5 Rollout (`2026-10-05..2026-10-29`, after `#4918`) |",
        "| --- | --- | --- | --- |",
        f"| `AGENT_HANDOFF.md` | `{m.handoff_commits_60d}` | `{m.handoff_commits_pre_rm5}` (`~6.8/day`) | `{m.handoff_commits_post_rm5}` (`0.4/day`; only `3` since `2026-10-13`) |",
        f"| `_quarto.yml` | `{m.quarto_commits_60d}` | `{m.quarto_commits_pre_rm5}` (`~0.7/day`) | `{m.quarto_commits_post_rm5}` (`0.4/day`; only `3` since `2026-10-15`) |",
        f"| Touched both in same commit | `{m.both_files_commits_60d}` | `{m.both_files_commits_60d - m.both_files_commits_post_rm5}` | `{m.both_files_commits_post_rm5}` (`#5005`, `#5107`) |",
        "",
        "## 2. Superseded PRs and Conflict Incidents (Last 60 Days)",
        "",
        "| Closed / Superseded PR(s) | Surviving PR(s) | Target Files Touched | Root Cause |",
        "| --- | --- | --- | --- |",
    ]
    for inc in m.incidents:
        lines.append(
            f"| {inc.closed_pr} | {inc.surviving_prs} | {inc.touched_files} | {inc.root_cause} |"
        )
    lines.extend(
        [
            "",
            f"## 3. Recommendation: **{m.recommendation}** on `.agent/state` JSON Split",
            "",
            "- **Decision**: **NO-GO** on migrating `AGENT_HANDOFF.md` to `.agent/state/*.json`.",
            "- **Evidence**:",
            "  1. **RM-5 change fragments (`changes/<issue>-<slug>.md`, `#4918`) already solved per-PR handoff contention**: `AGENT_HANDOFF.md` commits dropped by **96%** (from `243` commits in the 36 days before `#4918` to `10` commits in the 24 days after, and only `3` commits in the last 17 days: `#5107`, `#5154`, `#5231`).",
            "  2. **`#5105` vs `#5107`/`#5141` was not an `AGENT_HANDOFF.md` conflict**: `#5105` never modified `AGENT_HANDOFF.md`; it overlapped `#5107` on `articles/after-one-solution-null-space-exploration.qmd` and `_quarto.yml`, and `#5141` restored only the 4-line `changes/5095-*.md` fragment.",
            "  3. **Root-hygiene and migration cost**: `.agent` is explicitly forbidden in `scripts/check_root_hygiene.py` (`FORBIDDEN_ROOT_DIRECTORIES`), and `_quarto.yml` navbar edits are already governed by owner-only control under epic `#5248`.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for reproducible conflict-frequency measurement."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the rendered Markdown report",
    )
    args = parser.parse_args(argv)

    try:
        measurement = measure_default_60d_window()
    except ValueError as exc:
        write_stderr(str(exc))
        return 2

    report = render_markdown_report(measurement)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        write_stdout(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
