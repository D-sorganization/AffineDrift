"""Tests for scripts/update_sw_cache_version.py hash-source integrity."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.update_sw_cache_version import (
    CACHE_SCHEMA_VERSION,
    HASH_GLOBS,
    HASH_SOURCES,
    ROOT,
    compute_asset_hash,
    iter_hash_files,
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
    """Every explicit hash source must be a real repository file."""
    missing = [rel for rel in HASH_SOURCES if not (ROOT / rel).is_file()]
    assert not missing, f"HASH_SOURCES entries do not exist: {missing}"


def test_hash_globs_match_runtime_assets() -> None:
    """Globs must cover the canonical stylesheet tree and JS modules."""
    files = {p.relative_to(ROOT).as_posix() for p in iter_hash_files(ROOT)}
    assert "styles.css" in files
    assert "js/main.js" in files
    assert (
        "css/tokens/design-tokens.css" in files
    ), "css/**/*.css glob must include token stylesheets so CSS edits bump the cache version"


def test_service_worker_not_hashed() -> None:
    """Hashing the file this script rewrites would be non-idempotent."""
    files = {p.relative_to(ROOT).as_posix() for p in iter_hash_files(ROOT)}
    assert "service-worker.js" not in files
    assert all(not pattern.startswith("service-worker") for pattern in HASH_GLOBS)


def test_compute_asset_hash_raises_on_missing_source(tmp_path: Path) -> None:
    """DbC: a missing explicit hash source must raise with context."""
    assets = _full_assets()
    assets.pop(HASH_SOURCES[0])
    repo = _make_repo(tmp_path, assets)
    with pytest.raises(ValueError, match=HASH_SOURCES[0].replace(".", r"\.")):
        compute_asset_hash(root=repo)


def test_hash_changes_when_css_changes(tmp_path: Path) -> None:
    """Editing any hashed stylesheet must change the computed version hash."""
    assets = _full_assets()
    assets["css/tokens.css"] = ":root { --x: 1; }"
    repo = _make_repo(tmp_path, assets)

    before = compute_asset_hash(repo)
    (repo / "css" / "tokens.css").write_text(":root { --x: 2; }", encoding="utf-8")
    after = compute_asset_hash(repo)

    assert before != after


def test_compute_asset_hash_is_deterministic(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, _full_assets())
    assert compute_asset_hash(root=repo) == compute_asset_hash(root=repo)


def test_update_cache_version_rewrites_cache_name(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, _full_assets(), sw_version="v4-deadbeef")
    assert update_cache_version(root=repo) == 0
    content = (repo / "service-worker.js").read_text(encoding="utf-8")
    expected = f"{CACHE_SCHEMA_VERSION}-{compute_asset_hash(root=repo)}"
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
