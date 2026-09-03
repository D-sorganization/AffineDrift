"""Generate the Programming Companion catalog pages (ISSUE-4023, #4123).

Sources, in order of authority:

* ``--source lock`` (default when ``data/companion/active-lock.json`` exists):
  the provider-published manifest installed by
  ``scripts/install_programming_companion.py``; pages carry the provider-pin
  notice and the exact artifact/digest they were generated from.
* ``--source fixture`` (default otherwise): the test fixture manifest; every
  page is stamped PREVIEW because nothing provider-published backs it.
* ``--source <path>``: an explicit manifest file (PREVIEW-stamped).

Usage:
    python -m scripts.generate_programming_catalog [--check] [--source lock|fixture|PATH]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from src.affine_control.programming_companion import AcquisitionError, SnapshotStore
from src.affine_control.programming_companion.catalog_generator import (
    CatalogGenerator,
    CatalogGeneratorError,
)

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_MANIFEST_PATH = ROOT / "tests/fixtures/companion/manifest_v1_0_0_authoritative.json"
DEFAULT_MANIFEST_PATH = FIXTURE_MANIFEST_PATH
DEFAULT_OUTPUT_DIR = ROOT / "models/programming"
DEFAULT_STORE = ROOT / "data/companion"
ACQUISITION_NAME = "acquisition.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def resolve_source(source: str | None, store: Path) -> str:
    """Pick ``lock`` when an active pin exists, else ``fixture``; honour explicit choices."""
    if source is not None:
        return source
    return "lock" if (store / "active-lock.json").is_file() else "fixture"


def load_locked_manifest(store: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return the verified active manifest and the provenance the pages must cite."""
    snapshot_store = SnapshotStore(store)
    lock = snapshot_store.active_lock()
    if lock is None:
        raise CatalogGeneratorError(f"no active companion pin under {store}")
    payloads = snapshot_store.snapshot_bytes(lock)
    manifest = json.loads(payloads["manifest.json"].decode("utf-8"))
    receipt_path = store / ACQUISITION_NAME
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {}
    if receipt.get("provider", {}).get("commit") not in {None, lock.source_commit}:
        raise CatalogGeneratorError("acquisition receipt commit does not match the active lock")
    provenance = {
        "artifact_name": receipt.get(
            "artifact_name", f"upstreamdrift-companion-{lock.source_commit}"
        ),
        "manifest_sha256": lock.manifest_sha256,
        "fetched_on": receipt.get("fetched_on", "unknown"),
        "attestation": receipt.get("attestation", "unrecorded"),
        "publication_state": lock.publication_state,
    }
    return manifest, provenance


def build_generator(source: str, store: Path) -> CatalogGenerator:
    """Construct the generator for one source selection."""
    if source == "lock":
        manifest, provenance = load_locked_manifest(store)
        return CatalogGenerator(manifest, preview=False, provenance=provenance)
    manifest_path = FIXTURE_MANIFEST_PATH if source == "fixture" else Path(source)
    if not manifest_path.is_file():
        raise CatalogGeneratorError(f"manifest file not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return CatalogGenerator(manifest, preview=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate or verify Programming Companion catalog QMD pages."
    )
    parser.add_argument(
        "--source",
        default=None,
        help="lock | fixture | <manifest path> (default: lock when an active pin exists)",
    )
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE, help="companion store dir")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="explicit manifest path (alias for --source <path>; PREVIEW-stamped)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Target output directory for QMD pages (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether existing files are up-to-date without writing changes",
    )
    args = parser.parse_args(argv)
    if args.manifest is not None and args.source is not None:
        parser.error("--manifest and --source are mutually exclusive")
    source = resolve_source(str(args.manifest) if args.manifest else args.source, args.store)

    try:
        generator = build_generator(source, args.store)
        if args.check:
            is_clean, drifts = generator.check(args.output_dir)
            if not is_clean:
                logger.error(
                    "Programming Companion catalog is stale (%d drift(s) detected):", len(drifts)
                )
                for d in drifts:
                    logger.error("  - %s (%s)", d.path, d.reason)
                return 1
            logger.info(
                "Programming Companion catalog is up to date in %s (source: %s)",
                args.output_dir,
                source,
            )
            return 0

        files = generator.generate_all(args.output_dir)
        logger.info(
            "Generated %d Programming Companion pages in %s (source: %s)",
            len(files),
            args.output_dir,
            source,
        )
        return 0
    except (CatalogGeneratorError, AcquisitionError) as exc:
        logger.error("Catalog generation error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
