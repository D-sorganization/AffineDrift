"""CLI for UpstreamDrift implementation bridge ledger verification (#5601)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout
from src.tools.upstream_implementation_bridge import load_ledger, verify_document

ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = ROOT / "data/companion/upstream_implementation_links.json"


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Verify textbook UpstreamDrift bridge includes against the ledger."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--ledger", type=Path, default=None)
    args = parser.parse_args(argv)
    ledger_path = args.ledger or args.root / LEDGER_PATH.relative_to(ROOT)

    try:
        document = load_ledger(ledger_path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        write_stderr(str(error))
        return 1

    findings = verify_document(document, args.root)
    if findings:
        for line in findings:
            write_stderr(line)
        return 1

    count = len(document["bridges"])
    write_stdout(f"upstream implementation bridges verified: {count} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
