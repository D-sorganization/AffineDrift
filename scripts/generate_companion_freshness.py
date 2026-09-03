"""Generate the Software Freshness Dashboard page from the companion lock and pins.

``models/programming/freshness.qmd`` shows exactly which UpstreamDrift
revision the site represents (the active lock), the provider's own
publication verdict, the acquisition receipt, and every other UpstreamDrift
SHA the site links with its review state (#4027 via #4123). Deterministic:
the only dates are the ones recorded in the inputs.

Usage:
    python3 -m scripts.generate_companion_freshness [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout
from src.affine_control.programming_companion import SnapshotStore

ROOT = Path(__file__).resolve().parent.parent
STORE_PATH = ROOT / "data/companion"
OUTPUT_PATH = ROOT / "models/programming/freshness.qmd"
PROVIDER = "https://github.com/D-sorganization/UpstreamDrift"
STATE_LABELS = {
    "active": "Active (installed pin)",
    "pinned": "Pinned (reviewed)",
    "review-required": "Review required (unqualified)",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def load_inputs(store: Path) -> dict[str, Any]:
    """Load the lock (verified against its snapshot), receipt, pins, and manifest."""
    snapshot_store = SnapshotStore(store)
    lock = snapshot_store.active_lock()
    manifest: dict[str, Any] = {}
    if lock is not None:
        manifest = json.loads(snapshot_store.snapshot_bytes(lock)["manifest.json"].decode("utf-8"))
    return {
        "lock": lock,
        "manifest": manifest,
        "receipt": _load_json(store / "acquisition.json"),
        "pins": _load_json(store / "pins.json").get("pins", []),
    }


def _commit_link(commit: str) -> str:
    return f"[`{commit[:12]}`]({PROVIDER}/tree/{commit})"


def render_active_section(inputs: dict[str, Any]) -> str:
    """Render the active-pin block (or the honest absence of one)."""
    lock = inputs["lock"]
    if lock is None:
        return (
            '::: {.callout-warning title="No Active Pin"}\n'
            "No provider-published companion artifact is installed. The catalog pages are\n"
            "generated from a test fixture and carry a PREVIEW notice.\n"
            ":::\n"
        )
    manifest = inputs["manifest"]
    receipt = inputs["receipt"]
    publication = manifest.get("publication", {})
    blockers = [str(item) for item in publication.get("blockers", [])]
    summary = manifest.get("summary", {})
    rows = [
        ("Provider commit", _commit_link(lock.source_commit)),
        ("Artifact", f"`{receipt.get('artifact_name', 'unrecorded')}`"),
        ("Manifest SHA-256", f"`{lock.manifest_sha256}`"),
        ("Schema SHA-256", f"`{lock.schema_sha256}`"),
        ("Snapshot", f"`{lock.snapshot_id}`"),
        ("Installed", str(receipt.get("fetched_on", "unrecorded"))),
        ("Attestation", str(receipt.get("attestation", "unrecorded"))),
        ("Provider publication state", f"**{publication.get('state', 'unknown')}**"),
        (
            "Programs / features / workflows / engines",
            f"{summary.get('program_records', '?')} / {summary.get('feature_records', '?')} / "
            f"{summary.get('workflow_records', '?')} / {len(manifest.get('engines', []))}",
        ),
    ]
    table = "| Field | Value |\n| --- | --- |\n" + "\n".join(f"| {k} | {v} |" for k, v in rows)
    blocker_text = "\n".join(f"- {item}" for item in blockers) if blockers else "- None declared"
    return (
        f"{table}\n\n"
        "### Provider Blockers\n\n"
        "The provider's own publication verdict travels with the manifest; AffineDrift\n"
        "does not upgrade it.\n\n"
        f"{blocker_text}\n"
    )


def render_pins_section(pins: list[dict[str, Any]]) -> str:
    """Render the pin table and per-pin route lists."""
    if not pins:
        return "No UpstreamDrift pins are recorded.\n"
    header = (
        "| Commit | State | Routes | Last Reviewed | Review Due | Note |\n"
        "| --- | --- | ---: | --- | --- | --- |\n"
    )
    lines = []
    details = []
    for pin in pins:
        commit = str(pin["commit"])
        routes = list(pin.get("routes", []))
        lines.append(
            f"| {_commit_link(commit)} | {STATE_LABELS.get(str(pin['state']), pin['state'])} | "
            f"{len(routes)} | {pin.get('last_reviewed') or '—'} | {pin.get('review_due') or '—'} | "
            f"{pin.get('note', '')} |"
        )
        if routes:
            details.append(
                f"#### `{commit[:12]}`\n\n" + "\n".join(f"- [{r}]({r})" for r in routes) + "\n"
            )
    return header + "\n".join(lines) + "\n\n### Routes by Pin\n\n" + "\n".join(details)


def render_page(inputs: dict[str, Any]) -> str:
    """Render the complete Quarto page."""
    counts = {state: 0 for state in STATE_LABELS}
    for pin in inputs["pins"]:
        counts[str(pin.get("state"))] = counts.get(str(pin.get("state")), 0) + 1
    return (
        "---\n"
        'title: "Software Freshness Dashboard"\n'
        'description: "Which UpstreamDrift revision the site represents, every pinned SHA, '
        'review dates, and the provider publication state"\n'
        "---\n\n"
        "Generated by `scripts/generate_companion_freshness.py` from\n"
        "`data/companion/active-lock.json`, `data/companion/acquisition.json`, and\n"
        "`data/companion/pins.json`. Newer is not approved: the active pin only advances by an\n"
        "explicit, digest-guarded replacement, and pins marked *review required* stay\n"
        "unqualified until reviewed.\n\n"
        "## Active Provider Pin\n\n"
        f"{render_active_section(inputs)}\n"
        "## UpstreamDrift Pins Across the Site\n\n"
        f"{counts['active']} active, {counts['pinned']} pinned, "
        f"{counts['review-required']} review required. Every UpstreamDrift `tree`/`blob`/`commit`\n"
        "link in a rendered source must appear here (`scripts/check_companion_pins.py`).\n\n"
        f"{render_pins_section(inputs['pins'])}"
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    parser.add_argument("--store", type=Path, default=STORE_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    content = render_page(load_inputs(args.store))
    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.is_file() else None
        if current != content:
            write_stderr(
                f"{args.output} is stale; run python3 -m scripts.generate_companion_freshness"
            )
            return 1
        write_stdout("freshness dashboard is up to date")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8", newline="\n")
    write_stdout(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
