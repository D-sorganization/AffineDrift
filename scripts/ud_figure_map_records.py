#!/usr/bin/env python3
"""Verify UD figure-map records against figure bytes and the pinned UD map (#5454).

A ``ud_figure_map`` record traces figures projected from an UpstreamDrift
release to the run that wrote each one, as recorded in that release's
``data/figure_run_map.json`` at a pinned commit. It is a separate record kind
from the markerless-mocap projection manifest: it carries no privacy, security
or qualification attestation, and it never relaxes the manifest checks. A
simulation figure cites its run_id; an analytic or diagram figure has no run_id
and cites the code evidence instead. ``independent_review`` states the review
status of the source release.

``python scripts/ud_figure_map_records.py`` fetches the pinned map for every
record and checks the binding; the site gate checks the figure bytes offline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.mocap_projection_primitives import (  # noqa: E402 -- reason: sys.path modified above
    DIGEST,
    REVISION,
)
from scripts.verify_proximal_distal_projection import (  # noqa: E402 -- reason: sys.path modified above
    _read_bounded,
    manifest_digest_matches,
)

logger = logging.getLogger(__name__)

SCHEMA = "ud-figure-map-record-v1"
RECORD_DIR = "ud_figure_maps"
MAP_PATH = "data/figure_run_map.json"
MAX_MAP_BYTES = 2_000_000
RUN_SOURCE = "simulation_run"
LABEL_SOURCES = frozenset({"analytic", "diagram"})
HEADER = ("ud_repository", "ud_root", "independent_review")


def _text(entry: Mapping[str, Any], key: str, label: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: {key} must be a non-empty string")
    return value


def _require_relative(path: str, label: str) -> None:
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts or "\\" in path:
        raise ValueError(f"{label}: {path!r} must be a relative path inside the repository")


def _verify_figure(path: str, entry: Mapping[str, Any]) -> None:
    label = f"ud_figure_map figure {path}"
    _require_relative(path, label)
    if not DIGEST.fullmatch(_text(entry, "sha256", label)):
        raise ValueError(f"{label}: sha256 must be 64 lowercase hex characters")
    _require_relative(_text(entry, "ud_path", label), label)
    source = entry.get("source")
    run_id = entry.get("run_id")
    if source == RUN_SOURCE:
        if not isinstance(run_id, str) or not DIGEST.fullmatch(run_id):
            raise ValueError(f"{label}: a simulation_run figure needs a 64-hex run_id")
        _text(entry, "model_id", label)
    elif source in LABEL_SOURCES:
        if run_id is not None:
            raise ValueError(f"{label}: a {source} figure has no run_id")
        _text(entry, "source_evidence", label)
    else:
        raise ValueError(f"{label}: unknown source {source!r}")


def verify_record_fields(record: Mapping[str, Any]) -> None:
    """Raise ``ValueError`` unless the record header and every figure entry are coherent."""
    if record.get("schema") != SCHEMA:
        raise ValueError(f"ud_figure_map: schema must be {SCHEMA}")
    for key in HEADER:
        _text(record, key, "ud_figure_map")
    _require_relative(record["ud_root"], "ud_figure_map")
    if not REVISION.fullmatch(str(record.get("ud_commit", ""))):
        raise ValueError("ud_figure_map: ud_commit must be a 40-hex commit")
    if not DIGEST.fullmatch(str(record.get("map_sha256", ""))):
        raise ValueError("ud_figure_map: map_sha256 must be 64 lowercase hex characters")
    figures = record.get("figures")
    if not isinstance(figures, dict) or not figures:
        raise ValueError("ud_figure_map: figures must be a non-empty object")
    for path, entry in figures.items():
        _verify_figure(path, entry)


def verify_record_bytes(record: Mapping[str, Any], root: Path) -> set[str]:
    """Return the record's figure paths after checking each file's bytes.

    Raises:
        ValueError: if a field is malformed, or a figure is missing or its bytes
            differ from the recorded sha256.
    """
    verify_record_fields(record)
    for path, entry in record["figures"].items():
        figure = root / path
        if not figure.is_file() or not manifest_digest_matches(
            figure.read_bytes(), entry["sha256"]
        ):
            raise ValueError(f"ud_figure_map figure {path}: bytes do not match sha256")
    return set(record["figures"])


def _expected(entry: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return entry.get("source") or RUN_SOURCE, entry.get("run_id"), entry.get("model_id")


def verify_against_map(record: Mapping[str, Any], map_bytes: bytes) -> None:
    """Raise ``ValueError`` unless the record matches the pinned UD figure-run map."""
    if hashlib.sha256(map_bytes).hexdigest() != record["map_sha256"]:
        raise ValueError("ud_figure_map: UD map bytes do not match map_sha256")
    ud_figures = json.loads(map_bytes)["figures"]
    for path, entry in record["figures"].items():
        ud_path = f"{record['ud_root']}/{entry['ud_path']}"
        if ud_path not in ud_figures:
            raise ValueError(f"ud_figure_map figure {path}: {ud_path} is not in the UD map")
        if _expected(ud_figures[ud_path]) != _expected(entry):
            raise ValueError(f"ud_figure_map figure {path}: source, run_id or model_id differ")


@dataclass(frozen=True)
class UdRelease:
    """A pinned UD release: its map bytes and its release-manifest artifact digests."""

    repository: str
    commit: str
    root: str
    map_bytes: bytes
    artifacts: Mapping[str, Mapping[str, Any]]


def _figure_entry(release: UdRelease, ud_path: str) -> dict[str, Any]:
    key = f"{release.root}/{ud_path}"
    source, run_id, model_id = _expected(json.loads(release.map_bytes)["figures"][key])
    entry = {"ud_path": ud_path, "sha256": release.artifacts[key]["sha256"]}
    entry.update(source=source, run_id=run_id, model_id=model_id)
    if source in LABEL_SOURCES:
        entry["source_evidence"] = json.loads(release.map_bytes)["figures"][key]["source_evidence"]
    return entry


def build_record(release: UdRelease, root: Path, figures_dir: str) -> dict[str, Any]:
    """Build a record for every file in ``figures_dir`` that the UD map lists.

    A file is matched to ``figures/<name>`` in the release; files the map does
    not list are left out, so they stay untraced. The result is verified
    against ``root`` and the map before it is returned.
    """
    ud_figures = json.loads(release.map_bytes)["figures"]
    figures = {
        f"{figures_dir}/{path.name}": _figure_entry(release, f"figures/{path.name}")
        for path in sorted((root / figures_dir).iterdir())
        if path.is_file() and f"{release.root}/figures/{path.name}" in ud_figures
    }
    record = {
        "schema": SCHEMA,
        "ud_repository": release.repository,
        "ud_commit": release.commit,
        "ud_root": release.root,
        "map_sha256": hashlib.sha256(release.map_bytes).hexdigest(),
        "independent_review": "open",
        "figures": figures,
    }
    verify_record_bytes(record, root)
    verify_against_map(record, release.map_bytes)
    return record


def map_url(record: Mapping[str, Any]) -> str:
    """Return the raw URL of the pinned UD figure-run map."""
    repository, commit, root = record["ud_repository"], record["ud_commit"], record["ud_root"]
    return f"https://raw.githubusercontent.com/{repository}/{commit}/{root}/{MAP_PATH}"


def main(argv: Sequence[str] | None = None) -> int:
    """Check every checked-in record against its pinned UD map; return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--records", type=Path, default=REPO_ROOT / "evidence/projections")
    parser.add_argument("--ud-map", help="local copy of the pinned map (default: fetch it)")
    args = parser.parse_args(argv)
    for path in sorted((args.records / RECORD_DIR).glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        verify_record_fields(record)
        location = args.ud_map or map_url(record)
        verify_against_map(record, _read_bounded(location, MAX_MAP_BYTES))
        logger.info("%s matches the UD map at %s", path.name, record["ud_commit"])
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raise SystemExit(main())
