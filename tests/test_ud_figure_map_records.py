"""Tests for UD figure-map records (VIS-EVIDENCE-5, #5454).

Enforces:
1. A figure listed in a ``ud_figure_map`` record is traced when its bytes match
   the record and the record agrees with the pinned UpstreamDrift
   ``figure_run_map.json`` (run_id, model_id and source label).
2. A simulation figure needs a run_id; an analytic or diagram figure never has
   one and must cite its evidence.
3. The record type does not relax the markerless-mocap projection checks.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from scripts import check_figure_projection_records as gate
from scripts import ud_figure_map_records as records
from scripts.mocap_projection_primitives import MocapProjectionError
from tests.test_markerless_mocap_projection_contract import _valid_manifest

FIGURE = "articles/figures/swing.svg"
SCHEMATIC = "articles/figures/schematic.svg"
SVG = b'<svg xmlns="http://www.w3.org/2000/svg"/>\n'
QUARTO = 'project:\n  render:\n    - "articles/**/*.qmd"\n'
RUN_ID = "a" * 64
UD_ROOT = "docs/research/release"


def _site(tmp_path: Path) -> Path:
    (tmp_path / "_quarto.yml").write_text(QUARTO, encoding="utf-8")
    (tmp_path / "articles/figures").mkdir(parents=True)
    (tmp_path / FIGURE).write_bytes(SVG)
    (tmp_path / SCHEMATIC).write_bytes(SVG)
    body = "![A swing](figures/swing.svg)\n\n![A schematic](figures/schematic.svg)"
    (tmp_path / "articles/page.qmd").write_text(f"---\ntitle: P\n---\n\n{body}\n")
    return tmp_path


def _ud_map() -> bytes:
    figures = {
        f"{UD_ROOT}/figures/swing.svg": {"model_id": "release-preset/s", "run_id": RUN_ID},
        f"{UD_ROOT}/figures/schematic.svg": {
            "model_id": "release-preset/m",
            "run_id": None,
            "source": "diagram",
            "source_evidence": "m.fig_schematic draws fixed geometry",
        },
    }
    return json.dumps({"figures": figures, "schema_version": 1}).encode()


def _record(**overrides: Any) -> dict[str, Any]:
    digest = hashlib.sha256(SVG).hexdigest()
    record: dict[str, Any] = {
        "schema": records.SCHEMA,
        "ud_repository": "D-sorganization/UpstreamDrift",
        "ud_commit": "b" * 40,
        "ud_root": UD_ROOT,
        "map_sha256": hashlib.sha256(_ud_map()).hexdigest(),
        "independent_review": "open",
        "figures": {
            FIGURE: {
                "ud_path": "figures/swing.svg",
                "sha256": digest,
                "source": "simulation_run",
                "run_id": RUN_ID,
                "model_id": "release-preset/s",
            },
            SCHEMATIC: {
                "ud_path": "figures/schematic.svg",
                "sha256": digest,
                "source": "diagram",
                "run_id": None,
                "model_id": "release-preset/m",
                "source_evidence": "m.fig_schematic draws fixed geometry",
            },
        },
    }
    record.update(overrides)
    return record


def _projections(tmp_path: Path, record: dict[str, Any]) -> Path:
    directory = tmp_path / "projections" / records.RECORD_DIR
    directory.mkdir(parents=True)
    (directory / "release.json").write_text(json.dumps(record), encoding="utf-8")
    return directory.parent


def _exemptions(tmp_path: Path) -> Path:
    path = tmp_path / "exemptions.json"
    path.write_text(json.dumps({"exemptions": []}), encoding="utf-8")
    return path


def _check(root: Path, record: dict[str, Any]) -> gate.FigureReport:
    return gate.check_site(root, _projections(root, record), _exemptions(root))


def test_ud_figure_map_record_traces_run_and_diagram_figures(tmp_path: Path) -> None:
    assert _check(_site(tmp_path), _record()).failures == []


def test_changed_figure_bytes_fail_closed(tmp_path: Path) -> None:
    root = _site(tmp_path)
    (root / FIGURE).write_bytes(b"<svg/>")
    with pytest.raises(ValueError, match="sha256"):
        _check(root, _record())


@pytest.mark.parametrize(
    ("figure", "change", "message"),
    [
        (FIGURE, {"run_id": None}, "run_id"),
        (SCHEMATIC, {"run_id": RUN_ID}, "run_id"),
        (SCHEMATIC, {"source_evidence": " "}, "evidence"),
        (FIGURE, {"source": "sketch"}, "source"),
    ],
)
def test_malformed_figure_entry_is_rejected(
    figure: str, change: dict[str, Any], message: str
) -> None:
    record = _record()
    record["figures"][figure].update(change)
    with pytest.raises(ValueError, match=message):
        records.verify_record_fields(record)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [({"ud_commit": "main"}, "ud_commit"), ({"independent_review": ""}, "independent_review")],
)
def test_malformed_record_header_is_rejected(overrides: dict[str, str], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        records.verify_record_fields(_record(**overrides))


def test_record_agrees_with_the_pinned_map() -> None:
    records.verify_against_map(_record(), _ud_map())


def test_map_with_other_bytes_is_rejected() -> None:
    with pytest.raises(ValueError, match="map_sha256"):
        records.verify_against_map(_record(), _ud_map() + b" ")


def test_run_id_that_differs_from_the_map_is_rejected() -> None:
    record = _record(map_sha256=hashlib.sha256(_ud_map()).hexdigest())
    record["figures"][FIGURE]["run_id"] = "c" * 64
    with pytest.raises(ValueError, match="run_id"):
        records.verify_against_map(record, _ud_map())


def test_mocap_manifest_without_reviews_still_fails(tmp_path: Path) -> None:
    root = _site(tmp_path)
    projections = _projections(root, _record())
    manifest: dict[str, Any] = _valid_manifest(tmp_path)[0]
    del manifest["privacy"]
    (projections / "swing.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(MocapProjectionError):
        gate.check_site(root, projections, _exemptions(root))


def test_build_record_covers_only_figures_the_map_lists(tmp_path: Path) -> None:
    root = _site(tmp_path)
    (root / "articles/figures/unmapped.svg").write_bytes(SVG)
    digest = {"sha256": hashlib.sha256(SVG).hexdigest()}
    names = ("swing.svg", "schematic.svg")
    release = records.UdRelease(
        repository="D-sorganization/UpstreamDrift",
        commit="b" * 40,
        root=UD_ROOT,
        map_bytes=_ud_map(),
        artifacts={f"{UD_ROOT}/figures/{name}": digest for name in names},
    )
    assert records.build_record(release, root, "articles/figures") == _record()
