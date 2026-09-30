"""Generate the fixture manifest consumed by the browser Dataset Explorer.

Lists every JSON fixture under the dataset families the explorer browses
(``data/ztcf``, ``data/population_generalization``,
``data/proximal_distal_energy_transfer``) and records, per file, the
``schema_version`` it declares and whether a matching ``*.schema.json`` file
is actually published alongside it. The explorer must never claim a fixture
validates against a schema that does not exist in the repository.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_TARGET = ROOT / "data" / "dataset_explorer_manifest.json"

# (family id, directory relative to repo root, display label)
FAMILIES: tuple[tuple[str, str, str], ...] = (
    ("ztcf", "data/ztcf", "ZTCF Counterfactual Fixtures"),
    (
        "population_generalization",
        "data/population_generalization",
        "Population Generalization Reports",
    ),
    (
        "proximal_distal_energy_transfer",
        "data/proximal_distal_energy_transfer",
        "Proximal-Distal Energy Transfer Snapshots",
    ),
)


def _schema_path_for(fixture: Path, family_dir: Path) -> str | None:
    """Return the repo-relative schema path for ``fixture`` if one is published.

    A schema is only reported when a ``*.schema.json`` file actually exists in
    the same family directory; a fixture's ``schema_version`` field is a claim,
    not proof that a schema was published.
    """
    candidates = sorted(family_dir.glob("*.schema.json"))
    if not candidates:
        return None
    # A family directory may host more than one schema in the future; a single
    # schema file today is unambiguous, so only report it when unambiguous.
    if len(candidates) != 1:
        return None
    return candidates[0].relative_to(ROOT).as_posix()


def build_manifest() -> dict[str, Any]:
    """Return the manifest payload describing every browsable fixture."""
    families_payload = []
    for family_id, family_rel_dir, label in FAMILIES:
        family_dir = ROOT / family_rel_dir
        if not family_dir.is_dir():
            raise FileNotFoundError(f"dataset family directory missing: {family_rel_dir}")
        schema_path = _schema_path_for(family_dir, family_dir)
        fixtures = []
        for fixture in sorted(family_dir.glob("*.json")):
            if fixture.name.endswith(".schema.json"):
                continue
            declared = json.loads(fixture.read_text(encoding="utf-8"))
            fixtures.append(
                {
                    "path": fixture.relative_to(ROOT).as_posix(),
                    "schema_version": declared.get("schema_version"),
                }
            )
        families_payload.append(
            {
                "family_id": family_id,
                "label": label,
                "directory": family_rel_dir,
                "schema_path": schema_path,
                "fixtures": fixtures,
            }
        )
    return {
        "schema_version": "affinedrift.dataset-explorer-manifest/v1",
        "families": families_payload,
    }


def render(check_only: bool) -> int:
    """Write (or check) the manifest file; return a process exit code."""
    manifest = build_manifest()
    serialized = json.dumps(manifest, indent=2, sort_keys=False) + "\n"

    if check_only:
        if not MANIFEST_TARGET.exists():
            logger.error("manifest missing: %s", MANIFEST_TARGET)
            return 1
        current = MANIFEST_TARGET.read_text(encoding="utf-8")
        if current != serialized:
            logger.error("manifest is stale: %s", MANIFEST_TARGET)
            return 1
        logger.info("manifest is up to date")
        return 0

    MANIFEST_TARGET.write_text(serialized, encoding="utf-8")
    logger.info("wrote %s", MANIFEST_TARGET)
    return 0


def main() -> int:
    """CLI entry point."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: fail if the committed manifest is stale, without writing.",
    )
    args = parser.parse_args()
    return render(check_only=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
