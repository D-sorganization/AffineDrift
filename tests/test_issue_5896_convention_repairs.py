"""Regression locks for convention repairs in #5896.

The checks fail while the published pages still reverse canonical-v2 base
velocity against the spatial Jacobian, contradict the camera extrinsic name,
shift the Pinocchio integrator evidence cell, leak source-path syntax, or
label unverified JaxSim rows as if a pass had recorded adapter behavior.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONVENTIONS = ROOT / "pages" / "upstreamdrift-conventions.qmd"
PROTOCOL = ROOT / "pages" / "upstreamdrift-engine-protocol.qmd"
CANONICAL_V2_BASE_V = "[base_linear_world_m/s, base_angular_body_rad/s, joint_rates…]"
REVERSED_BASE_V = "canonical-v2 base `v`: **angular then linear**"
UNVERIFIED_CELL = "Unverified at this pin"
_SEPARATOR_CHARS = set("-: ")


def _read(path: Path) -> str:
    """Return page text, rejecting a missing source."""
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Return the body under one Markdown heading."""
    marker = f"\n{heading}"
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"missing heading: {heading}")
    rest = text[start + len(marker) :]
    nxt = rest.find("\n## ")
    return rest if nxt < 0 else rest[:nxt]


def _cells(line: str) -> list[str]:
    """Split one Markdown table row into stripped cells."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(cell and set(cell) <= _SEPARATOR_CHARS for cell in cells)


def _table_rows(section: str) -> list[list[str]]:
    """Parse the first Markdown table in a section."""
    rows: list[list[str]] = []
    started = False
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            if started:
                break
            continue
        started = True
        cells = _cells(line)
        if _is_separator(cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        raise AssertionError("markdown table not found")
    return rows


def _row(rows: list[list[str]], label: str) -> list[str]:
    """Return the first body row whose first cell contains label."""
    for row in rows[1:]:
        if row and label in row[0]:
            return row
    raise AssertionError(f"missing row {label}")


def _labeled_rows(text: str, label: str) -> list[list[str]]:
    """Return every table row whose first cell contains label."""
    found = [
        cells
        for line in text.splitlines()
        if line.strip().startswith("|")
        and (cells := _cells(line))
        and label in cells[0]
        and not _is_separator(cells)
    ]
    if not found:
        raise AssertionError(f"no table row labeled {label}")
    return found


def test_camera_storage_names_the_inverse_pose() -> None:
    """Extrinsics are T_world_from_camera, not the camera-from-world inverse."""
    text = _read(CONVENTIONS)
    if "T_camera_from_world" not in text:
        raise AssertionError("page never names T_camera_from_world")
    if "not world-from-camera" in text:
        raise AssertionError("camera sentence still negates its own name")


def test_canonical_v2_base_velocity_stays_linear_then_angular() -> None:
    """Canonical-v2 v is linear-then-angular and is not the spatial Jacobian."""
    text = _read(CONVENTIONS)
    if CANONICAL_V2_BASE_V not in text:
        raise AssertionError("canonical-v2 base velocity layout was dropped")
    if REVERSED_BASE_V in text:
        raise AssertionError("site table still reverses canonical-v2 base velocity")
    if "linear then angular" not in text:
        raise AssertionError("page does not state linear-then-angular base velocity")
    if "reverse block order of `SPATIAL_JACOBIAN_ORDER`" not in text:
        raise AssertionError("page does not separate base velocity from the spatial Jacobian")


def test_jaxsim_adapter_order_is_distinguished_from_canonical_v2() -> None:
    """JaxSim's angular-then-linear stack is the reverse of canonical-v2 v."""
    section = _section(_read(CONVENTIONS), "## Per-Engine Native vs Canonical-V2")
    row = _row(_table_rows(section), "**JaxSim**")
    converted = row[4]
    if "[angular; linear]" not in converted:
        raise AssertionError("JaxSim adapter order was dropped")
    if "reverses canonical-v2" not in converted:
        raise AssertionError("JaxSim cell still calls the spatial stack canonical-v2")


def test_pinocchio_integrator_evidence_stays_in_the_evidence_column() -> None:
    """The Pinocchio integrator row has one cell per header column."""
    section = _section(_read(PROTOCOL), "## Integrator and Timestep Defaults")
    rows = _table_rows(section)
    header = rows[0]
    row = _row(rows, "Pinocchio")
    if len(row) != len(header):
        raise AssertionError(f"Pinocchio row width {len(row)} != header {len(header)}")
    if "DEFAULT_TIME_STEP" not in row[1] or "integrator=" in row[1] or "http" in row[1]:
        raise AssertionError(f"default-step cell is shifted: {row[1]}")
    if "rk4" not in row[2] or "http" in row[2]:
        raise AssertionError(f"integrator-notes cell is shifted: {row[2]}")
    if "pinocchio_physics_engine.py" not in row[3]:
        raise AssertionError(f"evidence link is not in the evidence column: {row[3]}")


def test_engine_protocol_does_not_leak_source_paths_or_refs() -> None:
    """Published protocol prose does not carry repo paths or Refs lines."""
    text = _read(PROTOCOL)
    if ".qmd" in text:
        raise AssertionError("leaked .qmd path")
    if re.search(r"(?m)^Refs #", text):
        raise AssertionError("leaked Refs line")


def test_engine_protocol_jaxsim_rows_do_not_claim_adapter_behavior() -> None:
    """JaxSim rows stay unlabeled claims: every data cell is the unverified label."""
    rows = _labeled_rows(_read(PROTOCOL), "JaxSim")
    if len(rows) != 2:
        raise AssertionError(f"expected 2 JaxSim rows, found {len(rows)}")
    for row in rows:
        for cell in row[1:]:
            if cell != UNVERIFIED_CELL:
                raise AssertionError(f"JaxSim cell claims content: {cell}")
