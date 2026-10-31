"""Audit GitHub Actions workflows for permissions, untrusted run interpolations, and action pins.

Issue #5249 (parent epic #5248): produces a reproducible inventory of every workflow
under ``.github/workflows`` covering:
1. Top-level ``permissions`` declaration.
2. Any ``${{ github.event.* }}`` expression interpolated directly into a ``run:`` block.
3. Any unpinned ``uses:`` reference (reusing ``scripts.check_workflow_action_pins``).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.check_workflow_action_pins import WORKFLOW_DIR, find_unpinned_actions
from scripts.cli_output import write_stderr, write_stdout

EVENT_INTERPOLATION_PATTERN = re.compile(r"\$\{\{[^}]*\b(github\.event\.[A-Za-z0-9_.*-]+)[^}]*\}\}")
RUN_KEY_PATTERN = re.compile(r"^(\s*)(?:-\s*)?run:\s*(.*)$")
TOP_LEVEL_KEY_PATTERN = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
INDENTED_KV_PATTERN = re.compile(r"^\s+([A-Za-z0-9_-]+):\s*(.+?)\s*$")


@dataclass(frozen=True)
class WorkflowAuditRecord:
    """Audit summary for a single GitHub Actions workflow file."""

    workflow: str
    top_level_permissions: str
    untrusted_run_interpolations: tuple[str, ...]
    unpinned_uses: tuple[str, ...]

    @property
    def has_findings(self) -> bool:
        """Return True if the workflow has missing permissions, run interpolations, or unpinned uses."""
        return (
            self.top_level_permissions == "MISSING"
            or bool(self.untrusted_run_interpolations)
            or bool(self.unpinned_uses)
        )


def _extract_top_level_permissions(lines: list[str]) -> str:
    """Extract top-level ``permissions`` declaration from workflow YAML lines."""
    in_permissions = False
    Entries: list[str] = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not raw_line.startswith((" ", "\t")):
            match = TOP_LEVEL_KEY_PATTERN.match(raw_line)
            if in_permissions:
                break
            if match and match.group(1) == "permissions":
                inline_val = match.group(2).split("#", 1)[0].strip()
                if inline_val:
                    return inline_val
                in_permissions = True
            continue

        if in_permissions:
            kv_match = INDENTED_KV_PATTERN.match(raw_line.split("#", 1)[0])
            if kv_match:
                Entries.append(f"{kv_match.group(1)}: {kv_match.group(2)}")

    if in_permissions:
        return ", ".join(Entries) if Entries else "{}"
    return "MISSING"


def _find_run_event_interpolations(lines: list[str]) -> tuple[str, ...]:
    """Find ``${{ github.event.* }}`` expressions interpolated inside ``run:`` steps."""
    findings: list[str] = []
    in_run_block = False
    run_indent = 0

    for line_number, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()
        if in_run_block:
            if stripped and not stripped.startswith("#"):
                current_indent = len(raw_line) - len(raw_line.lstrip(" "))
                if current_indent <= run_indent:
                    in_run_block = False
                else:
                    for match in EVENT_INTERPOLATION_PATTERN.finditer(raw_line):
                        findings.append(f"L{line_number}: {match.group(1)}")
                    continue

        run_match = RUN_KEY_PATTERN.match(raw_line)
        if not run_match:
            continue

        indent_str, remainder = run_match.groups()
        # Account for `- run:` where list dash precedes `run:`
        dash_offset = raw_line.find("run:")
        run_indent = dash_offset if dash_offset >= 0 else len(indent_str)
        code_part = remainder.split("#", 1)[0].strip()

        for match in EVENT_INTERPOLATION_PATTERN.finditer(remainder):
            findings.append(f"L{line_number}: {match.group(1)}")

        if code_part in {"|", ">", "|-", ">-", "|+", ">+"} or code_part == "":
            in_run_block = True

    return tuple(findings)


def audit_workflows(workflow_dir: Path = WORKFLOW_DIR) -> list[WorkflowAuditRecord]:
    """Audit all workflow files in ``workflow_dir`` and return structured records."""
    if not workflow_dir.exists() or not workflow_dir.is_dir():
        raise ValueError(f"Workflow directory does not exist: {workflow_dir}")

    workflow_paths = sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml"))
    raw_unpinned = find_unpinned_actions(workflow_dir)
    unpinned_by_name: dict[str, list[str]] = {}
    for item in raw_unpinned:
        for wf_path in workflow_paths:
            prefix = f"{wf_path}:"
            if item.startswith(prefix):
                unpinned_by_name.setdefault(wf_path.name, []).append(item[len(prefix) :])
                break

    records: list[WorkflowAuditRecord] = []
    for wf_path in workflow_paths:
        lines = wf_path.read_text(encoding="utf-8").splitlines()
        permissions = _extract_top_level_permissions(lines)
        interpolations = _find_run_event_interpolations(lines)
        unpinned = tuple(unpinned_by_name.get(wf_path.name, []))
        records.append(
            WorkflowAuditRecord(
                workflow=wf_path.name,
                top_level_permissions=permissions,
                untrusted_run_interpolations=interpolations,
                unpinned_uses=unpinned,
            )
        )

    return records


def render_markdown_report(records: list[WorkflowAuditRecord]) -> str:
    """Render a Markdown inventory table for all audited workflow records."""
    lines = [
        "# CI Workflow Hardening Gap Inventory (#5249)",
        "",
        "| Workflow | Top-Level `permissions` | `${{ github.event.* }}` in `run:` | Unpinned `uses:` |",
        "| --- | --- | --- | --- |",
    ]
    for rec in records:
        perms = f"`{rec.top_level_permissions}`"
        interp = (
            "; ".join(f"`{item}`" for item in rec.untrusted_run_interpolations)
            if rec.untrusted_run_interpolations
            else "none"
        )
        unpinned = (
            "; ".join(f"`{item}`" for item in rec.unpinned_uses) if rec.unpinned_uses else "none"
        )
        lines.append(f"| `{rec.workflow}` | {perms} | {interp} | {unpinned} |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for workflow hardening audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workflow-dir",
        type=Path,
        default=WORKFLOW_DIR,
        help="Path to .github/workflows directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional file path to write the Markdown report",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit non-zero if any workflow has findings",
    )
    args = parser.parse_args(argv)

    try:
        records = audit_workflows(args.workflow_dir)
    except ValueError as exc:
        write_stderr(str(exc))
        return 2

    report = render_markdown_report(records)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        write_stdout(report)

    if args.fail_on_findings and any(rec.has_findings for rec in records):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
