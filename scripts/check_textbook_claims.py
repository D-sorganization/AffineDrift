#!/usr/bin/env python3
"""Block newly added unsupported quantitative textbook claims in CI."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TEXTBOOK_EXTENSIONS = frozenset({".qmd", ".tex"})
TEXTBOOK_ROOT_PREFIXES = ("articles/", "books/", "pages/", "resources/")
TEXTBOOK_ROOT_EXACT = frozenset({"index.qmd"})

_CITATION_RE = re.compile(r"(\\cite(?:[a-z]*)?\{[^}]+\}|@\w+)")
_CAVEAT_RE = re.compile(
    r"\b("
    r"illustrative|for example|for an illustrative example|suppose|hypothetical|"
    r"placeholder|synthetic|toy|simplified|demonstration|replace with measured|"
    r"not real measured data|not derived from the model|varies|depends on|user-chosen"
    r")\b",
    re.IGNORECASE,
)
_STUDY_LANGUAGE_RE = re.compile(
    r"\b("
    r"study|studies|research(?:er|ers)?|experiment(?:s|al)?|measurement(?:s)?|"
    r"measured|reported|data show|data suggests"
    r")\b",
    re.IGNORECASE,
)
_NUMERIC_LITERAL_RE = re.compile(r"\d")
_QUANTITATIVE_UNITS_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:(?:N|Nm|N·m)|(?:kg|g|lb|lbs|pounds?|mph|m/s|rad/s|"
    r"ms|s|seconds?|degrees?)|°|%)\b"
)
_CLAIM_QUALIFIER_RE = re.compile(
    r"\b(typically|approximately|approx\.?|about|around|roughly|up to|"
    r"can reach|can exceed|times body weight)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AddedLine:
    """A single added diff line in a textbook file."""

    path: str
    line_number: int
    text: str


def _is_textbook_path(rel_path: str) -> bool:
    """Return whether *rel_path* is an article/content file we should scan."""
    normalized = rel_path.replace("\\", "/")
    if normalized in TEXTBOOK_ROOT_EXACT:
        return True
    return normalized.endswith(tuple(TEXTBOOK_EXTENSIONS)) and normalized.startswith(
        TEXTBOOK_ROOT_PREFIXES
    )


def _merge_base(repo_root: Path) -> str:
    """Resolve a stable merge base for changed-file comparisons."""
    event_path = os.getenv("GITHUB_EVENT_PATH", "").strip()
    if event_path:
        try:
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            event = {}
        pull_request = event.get("pull_request") if isinstance(event, dict) else None
        if isinstance(pull_request, dict):
            base = pull_request.get("base")
            if isinstance(base, dict):
                base_ref = str(base.get("ref", "")).strip()
                if base_ref:
                    subprocess.run(
                        ["git", "fetch", "--depth=200", "origin", base_ref],
                        cwd=repo_root,
                        check=False,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                    )
                    try:
                        result = subprocess.run(
                            ["git", "merge-base", "HEAD", f"origin/{base_ref}"],
                            cwd=repo_root,
                            check=True,
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                        )
                    except subprocess.CalledProcessError:
                        result = None
                    if result is not None:
                        sha = result.stdout.strip()
                        if sha:
                            return sha
                base_sha = str(base.get("sha", "")).strip()
                if base_sha:
                    return base_sha

    default_base = os.getenv("GITHUB_BASE_REF", "").strip() or "main"
    fetched_default = False
    candidates = [f"origin/{default_base}", default_base, "origin/main", "main", "HEAD~1"]
    for candidate in candidates:
        if candidate in {f"origin/{default_base}", default_base, "origin/main", "main"}:
            remote_ref = (
                default_base if candidate in {f"origin/{default_base}", default_base} else "main"
            )
            if not fetched_default or remote_ref != default_base:
                subprocess.run(
                    ["git", "fetch", "--depth=200", "origin", remote_ref],
                    cwd=repo_root,
                    check=False,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                if remote_ref == default_base:
                    fetched_default = True
        try:
            result = subprocess.run(
                ["git", "merge-base", "HEAD", candidate],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.CalledProcessError:
            continue
        sha = result.stdout.strip()
        if sha:
            return sha
    return "HEAD~1"


def _diff_text(repo_root: Path, base_ref: str) -> str:
    """Return unified diff text for candidate textbook changes."""
    ci_base_ref = os.getenv("GITHUB_BASE_REF", "").strip()
    if ci_base_ref:
        subprocess.run(
            ["git", "fetch", "--depth=1", "origin", ci_base_ref],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    commands: list[list[str]] = [
        ["git", "diff", "--unified=0", f"{base_ref}..HEAD"],
        ["git", "diff", "--unified=0", f"{base_ref}...HEAD"],
    ]
    if ci_base_ref:
        commands.append(["git", "diff", "--unified=0", f"origin/{ci_base_ref}..HEAD"])
        commands.append(["git", "diff", "--unified=0", f"origin/{ci_base_ref}...HEAD"])
    commands.extend(
        [
            ["git", "diff", "--unified=0", "HEAD^1...HEAD"],
            ["git", "show", "--unified=0", "--format=", "HEAD"],
        ]
    )

    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.CalledProcessError:
            continue
        if result.stdout.strip():
            return result.stdout
    return ""


def _parse_added_lines(diff_text: str) -> list[AddedLine]:
    """Parse added lines from a unified diff."""
    added: list[AddedLine] = []
    current_path: str | None = None
    next_line_number = 0

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("+++ b/"):
            candidate = raw_line[6:]
            current_path = candidate if _is_textbook_path(candidate) else None
            next_line_number = 0
            continue
        if current_path is None:
            continue
        if raw_line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", raw_line)
            if match is None:
                next_line_number = 0
                continue
            next_line_number = int(match.group(1))
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            added.append(
                AddedLine(
                    path=current_path,
                    line_number=next_line_number,
                    text=raw_line[1:],
                )
            )
            next_line_number += 1
            continue
        if raw_line.startswith(" "):
            next_line_number += 1

    return added


def _line_needs_support(text: str) -> bool:
    """Return whether *text* looks like an unsupported quantitative claim."""
    stripped = text.strip()
    if not stripped or stripped.startswith("%"):
        return False
    if _STUDY_LANGUAGE_RE.search(stripped):
        return True
    if not _NUMERIC_LITERAL_RE.search(stripped):
        return False
    return bool(_QUANTITATIVE_UNITS_RE.search(stripped) or _CLAIM_QUALIFIER_RE.search(stripped))


def _window_has_support(lines: list[str], line_number: int, radius: int = 1) -> bool:
    """Return whether nearby lines contain a citation or explicit caveat."""
    start = max(0, line_number - 1 - radius)
    end = min(len(lines), line_number + radius)
    window_text = "\n".join(lines[start:end])
    return bool(_CITATION_RE.search(window_text) or _CAVEAT_RE.search(window_text))


def find_unsupported_claims(repo_root: Path, added_lines: list[AddedLine]) -> list[str]:
    """Return CI errors for unsupported textbook claims."""
    findings: list[str] = []
    file_cache: dict[str, list[str]] = {}

    for added_line in added_lines:
        if not _line_needs_support(added_line.text):
            continue
        lines = file_cache.get(added_line.path)
        if lines is None:
            full_text = (repo_root / added_line.path).read_text(encoding="utf-8")
            lines = full_text.splitlines()
            file_cache[added_line.path] = lines
        if _window_has_support(lines, added_line.line_number):
            continue
        findings.append(
            f"{added_line.path}:{added_line.line_number}: unsupported quantitative/study "
            "claim without citation or caveat"
        )

    return findings


def main() -> int:
    """Check newly added textbook lines for unsupported quantitative claims."""
    from src.tools.utils.budget_check_utils import report_results

    repo_root = REPO_ROOT
    base_ref = _merge_base(repo_root)
    diff_text = _diff_text(repo_root, base_ref)
    added_lines = _parse_added_lines(diff_text)
    findings = find_unsupported_claims(repo_root, added_lines)
    textbook_files = sorted({line.path for line in added_lines})

    return report_results(
        "Textbook unsupported-claim check",
        files_scanned=len(textbook_files),
        details=[f"base_ref={base_ref}", f"added_lines={len(added_lines)}"],
        errors=findings,
    )


if __name__ == "__main__":
    sys.exit(main())
