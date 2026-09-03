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
import json
import re
import sys
from pathlib import Path

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
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
# Mirrors the _quarto.yml render set: every .qmd plus the two Markdown families
# that render, minus the excluded workspaces.
EXCLUDED_PARTS = ("docs", "node_modules", "_freeze", ".quarto", "Drafts_Original_Articles")
EXCLUDED_SUFFIXES = ("_CRITIC.qmd", "INLINE_SUGGESTIONS.md")
# The freshness dashboard is generated *from* the pin file, so it must not feed it.
EXCLUDED_FILES = ("models/programming/freshness.qmd",)


def _is_site_source(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if path.name.endswith(EXCLUDED_SUFFIXES):
        return False
    if path.as_posix() in EXCLUDED_FILES:
        return False
    if path.suffix == ".qmd":
        return (
            "tangent-hyperplane-contraction" not in path.parts or path.name != "textbook-main.qmd"
        )
    rel = path.as_posix()
    return rel.startswith("critiques/") or rel == "reports/scientific-claim-audit.md"


def site_sources(root: Path) -> list[Path]:
    """Return rendered source files, repository-relative, in a stable order."""
    candidates = [*root.rglob("*.qmd"), *(root / "critiques").glob("*.md")]
    audit = root / "reports/scientific-claim-audit.md"
    if audit.is_file():
        candidates.append(audit)
    return sorted(
        path.relative_to(root)
        for path in candidates
        if path.is_file() and _is_site_source(path.relative_to(root))
    )


def route_for(source: Path) -> str:
    """Map a rendered source path to its public route."""
    return "/" + source.with_suffix(".html").as_posix()


def scan_site_pins(root: Path) -> tuple[dict[str, list[str]], list[str]]:
    """Return {full_sha: [routes]} and findings for abbreviated SHAs."""
    pins: dict[str, set[str]] = {}
    findings: list[str] = []
    for source in site_sources(root):
        text = (root / source).read_text(encoding="utf-8", errors="replace")
        for match in LINK_PATTERN.finditer(text):
            sha = match.group(1).lower()
            if not FULL_SHA.fullmatch(sha):
                findings.append(f"{source.as_posix()}: abbreviated UpstreamDrift pin {sha}")
                continue
            pins.setdefault(sha, set()).add(route_for(source))
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
