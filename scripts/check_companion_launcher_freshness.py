"""Fail CI when the active companion pin omits launcher manifest tile IDs (#5626)."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "data" / "companion"
RAW_LAUNCHER = (
    "https://raw.githubusercontent.com/D-sorganization/UpstreamDrift/{commit}/"
    "src/config/launcher_manifest.json"
)


def _load_json_url(url: str) -> dict[str, object]:
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"failed to load {url}: {exc}") from exc


def active_provider_commit() -> str:
    lock = json.loads((STORE / "active-lock.json").read_text(encoding="utf-8"))
    commit = lock.get("provider", {}).get("commit")
    if not isinstance(commit, str) or len(commit) != 40:
        raise ValueError("active-lock.json missing provider.commit")
    return commit


def companion_program_ids(commit: str) -> set[str]:
    lock = json.loads((STORE / "active-lock.json").read_text(encoding="utf-8"))
    snapshot_id = lock.get("snapshot", {}).get("id")
    if not isinstance(snapshot_id, str):
        raise ValueError("active lock missing snapshot.id")
    manifest_path = STORE / "snapshots" / snapshot_id / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    programs = manifest.get("programs")
    if not isinstance(programs, list):
        raise ValueError("companion manifest missing programs[]")
    return {str(entry["id"]) for entry in programs if isinstance(entry, dict) and entry.get("id")}


def launcher_tile_ids(commit: str) -> set[str]:
    payload = _load_json_url(RAW_LAUNCHER.format(commit=commit))
    tiles = payload.get("tiles")
    if not isinstance(tiles, list):
        raise ValueError("launcher_manifest.json missing tiles[]")
    return {str(tile["id"]) for tile in tiles if isinstance(tile, dict) and tile.get("id")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    commit = active_provider_commit()
    program_ids = companion_program_ids(commit)
    tile_ids = launcher_tile_ids(commit)
    missing = sorted(tile_ids - program_ids)
    if missing:
        for tile_id in missing:
            print(
                f"companion pin {commit[:12]} missing launcher tile {tile_id!r}",
                file=sys.stderr,
            )
        return 1
    print(
        f"OK: {len(program_ids)} companion programs cover {len(tile_ids)} "
        f"launcher tiles at pin {commit[:12]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
