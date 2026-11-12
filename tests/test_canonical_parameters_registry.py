"""Tests for the canonical parameter registry (issue #5595)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.canonical_parameters_registry import (
    DATA_PATH,
    load_registry,
    match_literal,
    render_parameters_markdown,
    stale_markers,
)

pytestmark = pytest.mark.content_lint


def test_registry_loads() -> None:
    payload = load_registry(DATA_PATH)
    assert payload["schema_version"] == "1.0.0"
    assert len(payload["entries"]) >= 10


def test_render_includes_sourced_ball_mass() -> None:
    rendered = render_parameters_markdown(load_registry(DATA_PATH))
    assert "0.04593" in rendered
    assert "GOLF_BALL_MASS_KG" in rendered
    assert "Ch 10-12" not in rendered


def test_stale_markers_cover_old_parameters_bugs() -> None:
    patterns = {item["pattern"] for item in stale_markers(load_registry(DATA_PATH))}
    assert "Ch 10-12" in patterns
    assert "m or M" in patterns


def test_match_literal_within_tolerance() -> None:
    assert match_literal("0.02135", 0.021335, 1e-4)
    assert not match_literal("0.046", 0.04593, 1e-6)


def test_registry_entry_ids_unique() -> None:
    payload = load_registry(DATA_PATH)
    ids = [entry["id"] for entry in payload["entries"]]
    assert len(ids) == len(set(ids))


def test_render_writes_expected_path(tmp_path: Path) -> None:
    payload = load_registry(DATA_PATH)
    out = tmp_path / "PARAMETERS.md"
    out.write_text(render_parameters_markdown(payload), encoding="utf-8")
    assert "UpstreamDrift" in out.read_text(encoding="utf-8")
