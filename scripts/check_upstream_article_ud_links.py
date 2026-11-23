"""Verify governed UpstreamDrift article permalinks (#5601)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout
from src.tools.upstream_article_ud_links import load_contract, verify_contract, verify_remote_paths

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "data/companion/upstream_article_link_pins.json"


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument(
        "--skip-remote",
        action="store_true",
        help="Skip raw.githubusercontent.com existence checks for contract paths.",
    )
    args = parser.parse_args(argv)

    try:
        document = load_contract(args.contract)
    except (OSError, ValueError) as error:
        write_stderr(str(error))
        return 1

    findings = verify_contract(document, args.root)
    if not args.skip_remote:
        findings.extend(verify_remote_paths(document))
    if findings:
        for line in findings:
            write_stderr(line)
        return 1

    count = len(document.get("governed_sources") or [])
    write_stdout(f"upstream article UD links verified: {count} governed sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
