"""Tests for scripts/update_sw_cache_version.py hash-source integrity.

Regression tests for the 2026-06-09 web audit: the previous HASH_SOURCES
list pointed at files that do not exist (js/script.js, css/styles.css,
css/base.css), which were silently skipped — so editing the site's CSS
never changed the service-worker cache version and returning PWA visitors
could be served stale styles.
"""

from __future__ import annotations

from pathlib import Path

from scripts.update_sw_cache_version import (
    HASH_GLOBS,
    HASH_SOURCES,
    compute_asset_hash,
    iter_hash_files,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_every_explicit_hash_source_exists() -> None:
    """Each explicitly listed hash source must be a real file."""
    missing = [rel for rel in HASH_SOURCES if not (REPO_ROOT / rel).is_file()]
    assert not missing, f"HASH_SOURCES entries do not exist: {missing}"


def test_hash_globs_match_runtime_assets() -> None:
    """Globs must cover the canonical stylesheet tree and JS modules."""
    files = {p.relative_to(REPO_ROOT).as_posix() for p in iter_hash_files(REPO_ROOT)}
    assert "styles.css" in files
    assert "js/main.js" in files
    assert (
        "css/tokens/design-tokens.css" in files
    ), "css/**/*.css glob must include token stylesheets so CSS edits bump the cache version"


def test_service_worker_not_hashed() -> None:
    """Hashing the file this script rewrites would be non-idempotent."""
    files = {p.relative_to(REPO_ROOT).as_posix() for p in iter_hash_files(REPO_ROOT)}
    assert "service-worker.js" not in files
    assert all(not pattern.startswith("service-worker") for pattern in HASH_GLOBS)


def test_hash_changes_when_css_changes(tmp_path: Path) -> None:
    """Editing any hashed stylesheet must change the computed version hash."""
    (tmp_path / "css").mkdir()
    (tmp_path / "js").mkdir()
    (tmp_path / "styles.css").write_text("body { color: red; }", encoding="utf-8")
    (tmp_path / "custom.scss").write_text("// scss", encoding="utf-8")
    (tmp_path / "js" / "main.js").write_text("export {};", encoding="utf-8")
    (tmp_path / "css" / "tokens.css").write_text(":root { --x: 1; }", encoding="utf-8")

    before = compute_asset_hash(tmp_path)
    (tmp_path / "css" / "tokens.css").write_text(":root { --x: 2; }", encoding="utf-8")
    after = compute_asset_hash(tmp_path)

    assert before != after


def test_hash_is_deterministic(tmp_path: Path) -> None:
    """Same inputs must produce the same hash on repeated runs."""
    (tmp_path / "styles.css").write_text("body {}", encoding="utf-8")
    (tmp_path / "custom.scss").write_text("// scss", encoding="utf-8")
    assert compute_asset_hash(tmp_path) == compute_asset_hash(tmp_path)
