"""Synthetic fixtures for the closed-chain hand-load loader. Not recorded swings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest

from src.affine_control.closed_chain_hand_load import load_closed_chain_hand_load
from src.affine_control.closed_chain_hand_load_schema import (
    UNAVAILABLE,
    ClosedChainHandLoadError,
    ClosedChainHandLoadRecord,
    Quantity,
    to_document,
)

_TOLERANCE = 1e-4


def _axis(component: float) -> list[float]:
    return [component, 0.0, 0.0]


def _sample(
    left: float, right: float, alpha: float | str, status: str, infeasible: bool
) -> dict[str, object]:
    cancellation: float | str = 0.0 if isinstance(alpha, float) else UNAVAILABLE
    return {
        "f_L_N": _axis(left),
        "f_R_N": _axis(right),
        "m_L_Nm": _axis(0.0),
        "m_R_Nm": _axis(0.0),
        "alpha": alpha,
        "opposing_force_cancellation": cancellation,
        "status": status,
        "infeasible": infeasible,
    }


def _frame(
    time_s: float,
    phase: str,
    couples: tuple[list[float] | str, list[float] | str, list[float] | str],
    min_alpha: float | str,
) -> dict[str, object]:
    total_couple, ztcf_couple, zvcf_couple = couples
    return {
        "time_s": time_s,
        "swing_phase": phase,
        "p_L_m": [0.0, 1.0, 0.0],
        "p_R_m": [0.08, 1.0, 0.0],
        "midhands": {
            "total": {"force_N": _axis(4.0), "couple_Nm": total_couple},
            "ztcf": {"force_N": _axis(1.0), "couple_Nm": ztcf_couple},
            "zvcf": {"force_N": _axis(3.0), "couple_Nm": zvcf_couple},
        },
        "baseline": _sample(3.0, 1.0, 0.25, "allocation-only", True),
        "min_squared_force": _sample(2.0, 2.0, min_alpha, "forward-replayed", False),
    }


def _provenance() -> dict[str, str]:
    names = ("model_sha256", "subject_sha256", "match_sha256", "tensor_sha256", "settings_sha256")
    hashes = {name: str(index) * 64 for index, name in enumerate(names, 1)}
    return {"git_sha": "a" * 40, **hashes}


def _document() -> dict[str, object]:
    """Return a fresh two-frame synthetic export."""
    numeric = (_axis(0.2), _axis(0.05), _axis(0.15))
    blank = (UNAVAILABLE, UNAVAILABLE, UNAVAILABLE)
    return {
        "schema_version": "affinedrift.closed-chain-hand-load/v1",
        "example_data": True,
        "couple_policy": "axial-only",
        "superposition_tolerance": _TOLERANCE,
        "j_f": {"baseline": 1.5, "min_squared_force": 0.75},
        "frames": [
            _frame(0.0, "synthetic-address", numeric, 0.0),
            _frame(0.5, "synthetic-top", blank, UNAVAILABLE),
        ],
        "provenance": _provenance(),
    }


def _manifest() -> dict[str, object]:
    return {
        "schema_version": "upstreamdrift.closed-chain-hand-load-manifest/v1",
        "provenance": _provenance(),
    }


def _load(
    tmp_path: Path,
    document: dict[str, object],
    manifest: dict[str, object],
    name: str = "hand_load.json",
) -> ClosedChainHandLoadRecord:
    document_path = tmp_path / name
    manifest_path = tmp_path / f"{name}.manifest.json"
    document_path.write_text(json.dumps(document), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return load_closed_chain_hand_load(document_path, manifest_path)


def _part(document: dict[str, object], name: str) -> dict[str, object]:
    frames = cast(list[dict[str, object]], document["frames"])
    midhands = cast(dict[str, object], frames[0]["midhands"])
    return cast(dict[str, object], midhands[name])


def _residual(total: Quantity, ztcf: Quantity, zvcf: Quantity) -> None:
    if total == UNAVAILABLE:
        assert ztcf == UNAVAILABLE and zvcf == UNAVAILABLE
        return
    assert isinstance(total, tuple) and isinstance(ztcf, tuple) and isinstance(zvcf, tuple)
    for index, component in enumerate(total):
        assert abs(ztcf[index] + zvcf[index] - component) <= _TOLERANCE


def test_round_trip_synthetic_fixture(tmp_path: Path) -> None:
    """A synthetic export loads and serializes back to the same object."""
    document = _document()
    loaded = _load(tmp_path, document, _manifest())
    assert loaded.example_data is True
    assert loaded.couple_policy == "axial-only"
    assert to_document(loaded) == document
    again = _load(tmp_path, to_document(loaded), _manifest(), name="round_trip.json")
    assert again == loaded
    top = loaded.frames[1]
    assert top.total.couple_nm == UNAVAILABLE
    assert top.min_squared_force.alpha == UNAVAILABLE


def test_loader_rejects_manifest_hash_mismatch(tmp_path: Path) -> None:
    """A tensor digest that disagrees with manifest.json is rejected."""
    manifest = _manifest()
    provenance = cast(dict[str, str], manifest["provenance"])
    provenance["tensor_sha256"] = "e" * 64
    with pytest.raises(ClosedChainHandLoadError, match="tensor_sha256"):
        _load(tmp_path, _document(), manifest)


@pytest.mark.parametrize("which", ["document", "manifest"])
def test_loader_rejects_unknown_schema_version(tmp_path: Path, which: str) -> None:
    """Unknown document and manifest schema versions fail closed."""
    document = _document()
    manifest = _manifest()
    target = document if which == "document" else manifest
    target["schema_version"] = f"{target['schema_version']}-rejected"
    with pytest.raises(ClosedChainHandLoadError, match="schema version"):
        _load(tmp_path, document, manifest)


def test_ztcf_plus_zvcf_equals_total_within_tolerance(tmp_path: Path) -> None:
    """Numeric midhands channels satisfy ZTCF + ZVCF = Total, and breaks fail."""
    loaded = _load(tmp_path, _document(), _manifest())
    for frame in loaded.frames:
        _residual(frame.total.force_n, frame.ztcf.force_n, frame.zvcf.force_n)
        _residual(frame.total.couple_nm, frame.ztcf.couple_nm, frame.zvcf.couple_nm)
    broken = _document()
    _part(broken, "zvcf")["force_N"] = _axis(0.0)
    with pytest.raises(ClosedChainHandLoadError, match="ZTCF \\+ ZVCF"):
        _load(tmp_path, broken, _manifest(), name="broken.json")
    mixed = _document()
    _part(mixed, "total")["couple_Nm"] = UNAVAILABLE
    with pytest.raises(ClosedChainHandLoadError, match="UNAVAILABLE"):
        _load(tmp_path, mixed, _manifest(), name="mixed.json")


def test_infeasible_flag_passes_through(tmp_path: Path) -> None:
    """The loader keeps each candidate's infeasible flag and replay status."""
    loaded = _load(tmp_path, _document(), _manifest())
    baseline = loaded.frames[0].baseline
    minimum = loaded.frames[0].min_squared_force
    assert baseline.infeasible is True
    assert minimum.infeasible is False
    assert baseline.status == "allocation-only"
    assert minimum.status == "forward-replayed"


def test_loader_rejects_missing_required_field(tmp_path: Path) -> None:
    """A missing required field is an error, not a zero fill."""
    document = _document()
    frames = cast(list[dict[str, object]], document["frames"])
    del frames[0]["time_s"]
    with pytest.raises(ClosedChainHandLoadError, match="time_s"):
        _load(tmp_path, document, _manifest())
