"""Reconcile every UpstreamDrift commit linked from the site with the pin file.

``data/companion/pins.json`` is the single record of which UpstreamDrift
revisions the public site represents (#4027, #4123). This gate fails when a
rendered source links an UpstreamDrift ``tree|blob|commit`` SHA that the pin
file does not list, when a link uses an abbreviated SHA, when the recorded
routes drift from the sources, when the active lock's commit is not the one
``active`` pin, or when a pin's dates contradict each other.

Usage:
    python3 scripts/check_companion_pins.py          # verify (CI)
    python3 scripts/check_companion_pins.py --write  # refresh routes / add unreviewed pins
"""

from __future__ import annotations

import argparse
import datetime as dt
import functools
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout
from src.affine_control.programming_companion import SnapshotStore

ROOT = Path(__file__).resolve().parent.parent
PINS_PATH = ROOT / "data/companion/pins.json"
STORE_PATH = ROOT / "data/companion"
PINS_SCHEMA = "affinedrift/companion-pins/v1"
PROVIDER = "https://github.com/D-sorganization/UpstreamDrift"
STATES = ("active", "pinned", "review-required")
LINK_PATTERN = re.compile(
    r"github\.com/D-sorganization/UpstreamDrift/(?:tree|blob|commit)/([0-9a-fA-F]{7,40})\b"
)
INCLUDE_PATTERN = re.compile(r"\{\{<\s*include\s+([^>}]+?)\s*>\}\}")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
# Mirrors the _quarto.yml render set: every .qmd plus the two Markdown families
# that render, minus the excluded workspaces.
EXCLUDED_PARTS = ("docs", "node_modules", "_freeze", ".quarto", "Drafts_Original_Articles")
EXCLUDED_SUFFIXES = ("_CRITIC.qmd", "INLINE_SUGGESTIONS.md")
# The freshness dashboard is generated *from* the pin file, so it must not feed it.
EXCLUDED_FILES = ("models/programming/freshness.qmd",)
DEFAULT_RENDER_RULES: tuple[str, ...] = (
    "*.qmd",
    "pages/**/*.qmd",
    "reports/scientific-claim-audit.md",
    "resources/**/*.qmd",
    "models/**/*.qmd",
    "repositories/**/*.qmd",
    "articles/**/*.qmd",
    "!articles/tangent-hyperplane-contraction/**/*.qmd",
    "!articles/tangent-hyperplane-articles/CRITICS_CORNER.qmd",
    "!articles/tangent-hyperplane-articles/Drafts_Original_Articles/**/*.qmd",
    "!articles/tangent-hyperplane-articles/Advanced/*_CRITIC.qmd",
    "!articles/proximal_distal_companion/chapters/**/*.qmd",
    "!articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
    "books/**/*.qmd",
    "critiques/index.qmd",
    "critiques/*.md",
    "!critiques/INLINE_SUGGESTIONS.md",
)


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    parts: list[str] = []
    i = 0
    n = len(pattern)
    while i < n:
        if pattern[i : i + 4] == "/**/":
            parts.append(r"/(?:.+/)?")
            i += 4
        elif pattern[i : i + 3] == "/**":
            parts.append(r"(?:/.*)?")
            i += 3
        elif pattern[i : i + 2] == "**/":
            parts.append(r"(?:.*/)?")
            i += 2
        elif pattern[i : i + 2] == "**":
            parts.append(r".*")
            i += 2
        elif pattern[i] == "*":
            parts.append(r"[^/]*")
            i += 1
        elif pattern[i] == "?":
            parts.append(r"[^/]")
            i += 1
        else:
            parts.append(re.escape(pattern[i]))
            i += 1
    return re.compile(r"^" + "".join(parts) + r"$")


@functools.lru_cache(maxsize=32)
def load_render_rules(
    root: Path = ROOT,
) -> tuple[tuple[re.Pattern[str], ...], tuple[re.Pattern[str], ...]]:
    """Load include and exclude regexes from _quarto.yml, falling back to ROOT or defaults."""
    quarto_yml = root / "_quarto.yml"
    if not quarto_yml.is_file() and root != ROOT:
        quarto_yml = ROOT / "_quarto.yml"
    raw_rules: list[str] = []
    if quarto_yml.is_file():
        try:
            data = yaml.safe_load(quarto_yml.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                render = data.get("project", {}).get("render")
                if isinstance(render, list):
                    raw_rules = [str(r) for r in render]
        except (OSError, yaml.YAMLError):
            pass
    if not raw_rules:
        raw_rules = list(DEFAULT_RENDER_RULES)

    include_patterns: list[re.Pattern[str]] = []
    exclude_patterns: list[re.Pattern[str]] = []
    for rule in raw_rules:
        if rule.startswith("!"):
            exclude_patterns.append(_glob_to_regex(rule[1:]))
        else:
            include_patterns.append(_glob_to_regex(rule))
    return tuple(include_patterns), tuple(exclude_patterns)


def _is_scannable(path: Path) -> bool:
    """Return True if path is a candidate site document (rendered page or partial)."""
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if path.name.endswith(EXCLUDED_SUFFIXES):
        return False
    if path.as_posix() in EXCLUDED_FILES:
        return False
    if path.suffix == ".qmd":
        return True
    rel = path.as_posix()
    return rel.startswith("critiques/") or rel == "reports/scientific-claim-audit.md"


def _is_site_source(path: Path, root: Path = ROOT) -> bool:
    """Return True when Quarto renders path as a standalone page."""
    try:
        rel_path = path.relative_to(root)
    except ValueError:
        rel_path = path
    if any(part in EXCLUDED_PARTS for part in rel_path.parts):
        return False
    if rel_path.name.endswith(EXCLUDED_SUFFIXES):
        return False
    posix = rel_path.as_posix()
    if posix in EXCLUDED_FILES:
        return False
    if any(part.startswith("_") for part in rel_path.parts):
        return False
    include_patterns, exclude_patterns = load_render_rules(root)
    if any(rx.match(posix) for rx in exclude_patterns):
        return False
    return any(rx.match(posix) for rx in include_patterns)


def site_sources(root: Path, *, include_partials: bool = False) -> list[Path]:
    """Return site sources, repository-relative, in a stable order.

    When include_partials is True, include partials and excluded chapters are
    retained so scan_site_pins can discover pins within them. When False,
    only documents that Quarto renders as standalone public routes are returned.
    """
    candidates = [*root.rglob("*.qmd"), *(root / "critiques").glob("*.md")]
    audit = root / "reports/scientific-claim-audit.md"
    if audit.is_file():
        candidates.append(audit)
    predicate = _is_scannable if include_partials else (lambda p: _is_site_source(p, root=root))
    return sorted(
        path.relative_to(root)
        for path in candidates
        if path.is_file() and predicate(path.relative_to(root))
    )


def route_for(source: Path) -> str:
    """Map a rendered source path to its public route."""
    return "/" + source.with_suffix(".html").as_posix()


def renders_standalone(source: Path, root: Path = ROOT) -> bool:
    """Return True when Quarto renders this source as its own page.

    Quarto never renders a file or directory whose name begins with an
    underscore (those are include partials), nor documents excluded by the
    project render set in _quarto.yml.
    """
    return _is_site_source(source, root=root)


def include_parents(root: Path, sources: list[Path]) -> dict[Path, set[Path]]:
    """Map each included partial to the sources that include it."""
    parents: dict[Path, set[Path]] = {}
    for source in sources:
        text = (root / source).read_text(encoding="utf-8", errors="replace")
        for match in INCLUDE_PATTERN.finditer(text):
            target = match.group(1).strip().strip("\"'")
            if not target:
                continue
            try:
                child = (root / source.parent / target).resolve().relative_to(root.resolve())
            except ValueError:
                continue
            parents.setdefault(child, set()).add(source)
    return parents


def routes_for(source: Path, parents: dict[Path, set[Path]], root: Path = ROOT) -> list[str]:
    """Return the public routes that publish ``source``.

    A standalone source publishes itself; a partial publishes through every
    rendered document that includes it, transitively.
    """
    routes: set[str] = set()
    seen: set[Path] = set()
    pending = [source]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        if renders_standalone(current, root=root):
            routes.add(route_for(current))
            continue
        pending.extend(parents.get(current, set()))
    return sorted(routes)


def scan_site_pins(root: Path) -> tuple[dict[str, list[str]], list[str]]:
    """Return {full_sha: [routes]} and findings for abbreviated SHAs."""
    pins: dict[str, set[str]] = {}
    findings: list[str] = []
    sources = site_sources(root, include_partials=True)
    parents = include_parents(root, sources)
    for source in sources:
        text = (root / source).read_text(encoding="utf-8", errors="replace")
        for match in LINK_PATTERN.finditer(text):
            sha = match.group(1).lower()
            if not FULL_SHA.fullmatch(sha):
                findings.append(f"{source.as_posix()}: abbreviated UpstreamDrift pin {sha}")
                continue
            routes = routes_for(source, parents, root=root)
            if not routes:
                findings.append(
                    f"{source.as_posix()}: UpstreamDrift pin {sha[:8]} sits in a partial that "
                    "no rendered page includes"
                )
                continue
            pins.setdefault(sha, set()).update(routes)
    return {sha: sorted(routes) for sha, routes in sorted(pins.items())}, findings


def _date(value: object, label: str, findings: list[str]) -> dt.date | None:
    if value is None:
        return None
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        findings.append(f"{label} is not an ISO date: {value!r}")
        return None


def validate_pins(document: dict[str, object], active_commit: str | None) -> list[str]:
    """Validate the pin document's shape, dates, and active-lock agreement."""
    findings: list[str] = []
    if document.get("schema_version") != PINS_SCHEMA:
        findings.append(f"pins schema_version must be {PINS_SCHEMA}")
    if document.get("provider") != PROVIDER:
        findings.append(f"pins provider must be {PROVIDER}")
    pins = document.get("pins")
    if not isinstance(pins, list):
        return [*findings, "pins must be a list"]
    seen: set[str] = set()
    active: list[str] = []
    for pin in pins:
        if not isinstance(pin, dict):
            findings.append("every pin must be an object")
            continue
        commit = str(pin.get("commit", ""))
        label = f"pin {commit[:8] or '?'}"
        if not FULL_SHA.fullmatch(commit):
            findings.append(f"{label}: commit must be a 40-hex SHA")
        if commit in seen:
            findings.append(f"{label}: duplicate commit")
        seen.add(commit)
        state = pin.get("state")
        if state not in STATES:
            findings.append(f"{label}: state must be one of {', '.join(STATES)}")
        if state == "active":
            active.append(commit)
        reviewed = _date(pin.get("last_reviewed"), f"{label} last_reviewed", findings)
        due = _date(pin.get("review_due"), f"{label} review_due", findings)
        if state != "review-required" and (reviewed is None or due is None):
            findings.append(f"{label}: {state} pins need last_reviewed and review_due")
        if reviewed and due and due < reviewed:
            findings.append(f"{label}: review_due {due} precedes last_reviewed {reviewed}")
        if not isinstance(pin.get("routes"), list) or not isinstance(pin.get("note"), str):
            findings.append(f"{label}: routes must be a list and note a string")
    if active_commit is None:
        if active:
            findings.append("no active lock exists but a pin is marked active")
    elif active != [active_commit]:
        findings.append(f"exactly one active pin must equal the lock commit {active_commit[:8]}")
    return findings


def _new_pin(sha: str, routes: list[str], *, active: bool) -> dict[str, object]:
    """Describe a newly discovered pin: the lock commit is active, anything else unreviewed."""
    if active:
        today = dt.date.today()
        return {
            "commit": sha,
            "state": "active",
            "last_reviewed": today.isoformat(),
            "review_due": (today + dt.timedelta(days=90)).isoformat(),
            "note": "Installed provider artifact (data/companion/active-lock.json).",
            "routes": routes,
        }
    return {
        "commit": sha,
        "state": "review-required",
        "last_reviewed": None,
        "review_due": None,
        "note": "Linked from the site; not yet reviewed against the active pin.",
        "routes": routes,
    }


def reconcile(
    document: dict[str, object], scanned: dict[str, list[str]], active_commit: str | None
) -> tuple[dict[str, object], list[str]]:
    """Return the refreshed document and the findings the current one has."""
    findings: list[str] = []
    pins = [dict(pin) for pin in document.get("pins", []) if isinstance(pin, dict)]
    by_commit = {str(pin.get("commit")): pin for pin in pins}
    for sha, routes in scanned.items():
        pin = by_commit.get(sha)
        if pin is None:
            findings.append(f"UpstreamDrift {sha[:8]} is linked from the site but not pinned")
            pins.append(_new_pin(sha, routes, active=sha == active_commit))
        elif pin.get("routes") != routes:
            findings.append(f"pin {sha[:8]} routes drifted (run --write)")
            pin["routes"] = routes
    kept = []
    for pin in pins:
        commit = str(pin.get("commit"))
        if commit not in scanned and commit != active_commit:
            findings.append(f"pin {commit[:8]} is no longer linked from the site (run --write)")
            continue
        if commit == active_commit and commit not in scanned:
            pin["routes"] = []
        kept.append(pin)
    kept.sort(key=lambda pin: (pin.get("state") != "active", str(pin.get("commit"))))
    refreshed = {**document, "pins": kept}
    return refreshed, findings


def active_lock_commit(store: Path) -> str | None:
    """Return the active lock commit, or None when nothing is installed."""
    lock = SnapshotStore(store).active_lock()
    return None if lock is None else lock.source_commit


def dump(document: dict[str, object]) -> str:
    """Canonical JSON with a trailing newline."""
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def _format_with_prettier(path: Path) -> None:
    """Format path with prettier if npx is available."""
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if npx and path.is_file():
        try:
            subprocess.run(
                [npx, "prettier", "--write", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            pass


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--pins", type=Path, default=None)
    parser.add_argument("--store", type=Path, default=None)
    parser.add_argument("--write", action="store_true", help="refresh routes and add new pins")
    args = parser.parse_args(argv)
    pins_path = args.pins or args.root / "data/companion/pins.json"
    store = args.store or args.root / "data/companion"

    if pins_path.is_file():
        document = json.loads(pins_path.read_text(encoding="utf-8"))
    else:
        document = {"schema_version": PINS_SCHEMA, "provider": PROVIDER, "pins": []}
    active_commit = active_lock_commit(store)
    scanned, findings = scan_site_pins(args.root)
    refreshed, drift = reconcile(document, scanned, active_commit)
    findings.extend(validate_pins(refreshed, active_commit))

    if args.write:
        pins_path.parent.mkdir(parents=True, exist_ok=True)
        pins_path.write_text(dump(refreshed), encoding="utf-8", newline="\n")
        _format_with_prettier(pins_path)
        for line in drift:
            write_stdout(f"updated: {line}")
    else:
        findings = [*drift, *findings]
    if findings:
        for line in findings:
            write_stderr(line)
        return 1
    write_stdout(
        f"companion pins reconciled: {len(scanned)} UpstreamDrift commits across "
        f"{sum(len(r) for r in scanned.values())} route links; active {active_commit or 'none'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
