"""Tests for the service-worker cache-version updater.

Written first (TDD) for the 2026-06-09 quality audit. They pin down two
contracts that were previously violated silently:

1. Every entry in ``HASH_SOURCES`` must exist in the repository. Before this
   audit, three of eight entries pointed at non-existent paths
   (``js/script.js``, ``css/styles.css``, ``css/base.css``) and were skipped
   with a debug-level log, so editing ``styles.css`` did NOT change the cache
   version and users kept stale assets.
2. ``compute_asset_hash`` must fail loudly (DbC) when a configured hash
   source is missing instead of silently producing a hash over a subset.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.update_sw_cache_version import (
    HASH_SOURCES,
    ROOT,
    compute_asset_hash,
    update_cache_version,
)

SW_TEMPLATE = "const CACHE_NAME = 'affinedrift-{version}';\n"


def _make_repo(tmp_path: Path, assets: dict[str, str], sw_version: str = "v4-old") -> Path:
    """Create a minimal repo layout with the given assets and a service worker."""
    for rel_path, content in assets.items():
        target = tmp_path / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    (tmp_path / "service-worker.js").write_text(
        SW_TEMPLATE.format(version=sw_version), encoding="utf-8"
    )
    return tmp_path


def _full_assets(marker: str = "a") -> dict[str, str]:
    return {rel: f"/* {rel} {marker} */" for rel in HASH_SOURCES}


def test_all_hash_sources_exist_in_repo() -> None:
    """Contract: every configured hash source must exist in the repository.

    This is the regression test for the silent stale-cache bug where
    HASH_SOURCES listed paths that do not exist.
    """
    missing = [rel for rel in HASH_SOURCES if not (ROOT / rel).exists()]
    assert not missing, (
        "HASH_SOURCES entries do not exist; cache busting would silently " f"ignore them: {missing}"
    )


def test_compute_asset_hash_raises_on_missing_source(tmp_path: Path) -> None:
    """DbC: a missing hash source must raise with context, not be skipped."""
    assets = _full_assets()
    assets.pop(HASH_SOURCES[0])
    repo = _make_repo(tmp_path, assets)
    with pytest.raises(ValueError, match=HASH_SOURCES[0].replace(".", r"\.")):
        compute_asset_hash(root=repo)


def test_compute_asset_hash_changes_when_asset_changes(tmp_path: Path) -> None:
    """Editing any hashed asset must change the computed hash."""
    repo = _make_repo(tmp_path, _full_assets("a"))
    before = compute_asset_hash(root=repo)
    (repo / HASH_SOURCES[-1]).write_text("/* changed */", encoding="utf-8")
    after = compute_asset_hash(root=repo)
    assert before != after


def test_compute_asset_hash_is_deterministic(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, _full_assets())
    assert compute_asset_hash(root=repo) == compute_asset_hash(root=repo)


def test_update_cache_version_rewrites_cache_name(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, _full_assets(), sw_version="v4-deadbeef")
    assert update_cache_version(root=repo) == 0
    content = (repo / "service-worker.js").read_text(encoding="utf-8")
    expected = f"v4-{compute_asset_hash(root=repo)}"
    assert f"const CACHE_NAME = 'affinedrift-{expected}';" in content


def test_update_cache_version_is_idempotent(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, _full_assets())
    assert update_cache_version(root=repo) == 0
    first = (repo / "service-worker.js").read_text(encoding="utf-8")
    assert update_cache_version(root=repo) == 0
    assert (repo / "service-worker.js").read_text(encoding="utf-8") == first


def test_update_cache_version_dry_run_does_not_write(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, _full_assets(), sw_version="v4-deadbeef")
    before = (repo / "service-worker.js").read_text(encoding="utf-8")
    assert update_cache_version(dry_run=True, root=repo) == 0
    assert (repo / "service-worker.js").read_text(encoding="utf-8") == before


def test_update_cache_version_errors_without_service_worker(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, _full_assets())
    (repo / "service-worker.js").unlink()
    assert update_cache_version(root=repo) == 1


def test_update_cache_version_errors_on_unmatched_pattern(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, _full_assets())
    (repo / "service-worker.js").write_text("// no cache name here\n", encoding="utf-8")
    assert update_cache_version(root=repo) == 1


def test_update_cache_version_errors_on_missing_asset(tmp_path: Path) -> None:
    """A missing hash source surfaces as a non-zero exit, not silence."""
    assets = _full_assets()
    assets.pop(HASH_SOURCES[0])
    repo = _make_repo(tmp_path, assets)
    assert update_cache_version(root=repo) == 1
