"""Standalone regeneration manifest builder (#5465)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from alpha_war_upstream import (
    CALCS_DIR,
    LOCK_PATH,
    sha256_file,
)

MANIFEST_PATH = CALCS_DIR / "alpha_war_regeneration_manifest.json"
OUTPUT_JSON = CALCS_DIR / "alpha_war_calculations.json"

GENERATOR_SOURCE_REL = (
    "alpha_war_sensitivity_suite.py",
    "alpha_war_upstream.py",
    "alpha_war_manifest.py",
    "alpha_war_json_compare.py",
    "alpha_war_roll_projection.py",
    "alpha_war_hand_force_bounds.py",
    "alpha_war_figures.py",
)


def generator_source_sha256() -> dict[str, str]:
    """Hash generator modules under ``research/alpha-war/calcs``."""
    return {
        rel: sha256_file(CALCS_DIR / rel)
        for rel in GENERATOR_SOURCE_REL
        if (CALCS_DIR / rel).is_file()
    }


def write_standalone_manifest(
    provenance: dict[str, Any],
    *,
    output_json_path: Path = OUTPUT_JSON,
    compare_summary: dict[str, float | int] | None = None,
) -> Path:
    """Write manifest beside JSON; provenance must not be nested inside the export."""
    manifest = dict(provenance)
    manifest["manifest_schema"] = "alpha-war-regen-manifest/v2"
    manifest["generator_source_sha256"] = generator_source_sha256()
    manifest["upstream_drift_lock_sha256"] = sha256_file(LOCK_PATH)
    manifest["output_json_sha256"] = sha256_file(output_json_path)
    if compare_summary is not None:
        manifest["regeneration_compare"] = compare_summary
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return MANIFEST_PATH
