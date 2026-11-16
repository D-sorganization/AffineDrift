"""Tests for UpstreamDrift physics inventory contract (#5624)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_upstreamdrift_physics_models import (
    check_site_files,
    check_substrings,
    check_upstream_sources,
    load_contract,
    main,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.unit
def test_check_substrings_flags_missing_required() -> None:
    errors = check_substrings(
        "fixture",
        "alpha",
        required=("beta",),
        forbidden=(),
    )
    assert errors


@pytest.mark.unit
def test_check_substrings_flags_forbidden() -> None:
    errors = check_substrings(
        "fixture",
        "stale pin text",
        required=(),
        forbidden=("stale pin",),
    )
    assert errors


@pytest.mark.unit
def test_contract_schema_is_valid() -> None:
    contract = load_contract()
    assert contract["schema_version"].endswith("/v1")
    assert len(contract["upstream_commit"]) == 40


@pytest.mark.unit
def test_site_checks_fail_on_stale_g1_callout(tmp_path: Path) -> None:
    contract = load_contract()
    article = tmp_path / "articles"
    article.mkdir(parents=True)
    stale = (
        "MISMATCH (G1)\n"
        "applies the full small-slope gradient $-g\\nabla h$ in roll as well as slide\n"
    )
    (article / "upstreamdrift-physics-models.qmd").write_text(stale, encoding="utf-8")
    patched = dict(contract)
    patched["site_file_checks"] = [
        {
            "path": "articles/upstreamdrift-physics-models.qmd",
            "required_substrings": [],
            "forbidden_substrings": ["MISMATCH (G1)"],
        }
    ]
    repo = tmp_path
    (repo / "articles").mkdir(exist_ok=True)
    errors = check_site_files(patched, repo_root=repo)
    assert any("MISMATCH (G1)" in item for item in errors)


@pytest.mark.unit
def test_upstream_checks_require_roll_gravity_partition(monkeypatch: pytest.MonkeyPatch) -> None:
    contract = load_contract()
    monkeypatch.setattr(
        "scripts.check_upstreamdrift_physics_models.fetch_upstream_file",
        lambda _commit, path: {
            "src/shared/python/putting_dynamics/solver.py": (
                "_roll_g = 5.0 / 7.0\nHOLE_RADIUS_M = 0.054\ncapture_speed_mps\n"
            ),
            "src/shared/python/physics/flight_models.py": (
                "cd0=0.21\nPENNER_LIFT_EXPONENT\nMAX_GOLF_BALL_LIFT_COEFFICIENT = 0.155\n"
            ),
            "src/shared/python/core/physics_constants.py": (
                'SPIN_DECAY_RATE_S = PhysicalConstant(\n0.05\n"Trackman Data"\n'
            ),
            "src/shared/python/putting_dynamics/friction.py": (
                "STIMP_RELEASE_SPEED_MPS = 1.83\nDEFAULT_SLIDING_MU = 0.40\n"
                "DEFAULT_STATIC_MU = 0.08\n"
            ),
        }.get(path, ""),
    )
    errors = check_upstream_sources(contract)
    assert not errors


@pytest.mark.integration
def test_main_passes_with_live_upstream_and_current_site() -> None:
    assert main([]) == 0


@pytest.mark.unit
def test_contract_lists_issue_trackers() -> None:
    payload = json.loads(
        Path("data/upstreamdrift/physics_models_contract.json").read_text(encoding="utf-8")
    )
    inventory = (ROOT / "articles/upstreamdrift-physics-models.qmd").read_text(encoding="utf-8")
    assert "15010" in inventory
    assert payload["upstream_commit"].startswith("4a1c5f4")
