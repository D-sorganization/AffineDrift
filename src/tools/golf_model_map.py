"""Extract degree-of-freedom maps from vendored UpstreamDrift MuJoCo golf models."""

from __future__ import annotations

import hashlib
import json
import logging
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "data/upstreamdrift_golf_models/manifest.json"
DEFAULT_JSON_OUT = ROOT / "data/upstreamdrift_golf_models/generated/mujoco_maps.json"
DEFAULT_QMD_OUT = ROOT / "models/_generated/golf-model-maps-mujoco.qmd"

_JOINT_NQ = {0: 7, 1: 4, 2: 1, 3: 1}
_JOINT_NV = {0: 6, 1: 3, 2: 1, 3: 1}
_JOINT_TYPE = {0: "free", 1: "ball", 2: "slide", 3: "hinge"}


@dataclass(frozen=True)
class JointRow:
    """One generalized-coordinate block in MuJoCo joint order."""

    name: str
    joint_type: str
    qpos_index: int
    qpos_count: int
    velocity_index: int
    velocity_count: int
    axis: list[float] | None
    range_rad: list[float] | None
    actuator: str | None
    ctrl_range: list[float] | None


@dataclass(frozen=True)
class EqualityRow:
    """Closed-chain equality constraint declared in MJCF."""

    kind: str
    attributes: dict[str, str]


@dataclass(frozen=True)
class ModelMap:
    """Parsed DOF map for one vendored MJCF snapshot."""

    model_id: str
    title: str
    nq: int
    nv: int
    nu: int
    neq: int
    joints: tuple[JointRow, ...]
    equalities: tuple[EqualityRow, ...]
    upstream_path: str
    upstream_symbol: str
    snapshot_path: str
    content_sha256: str


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    """Load and return the golf-model manifest."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"{path}: manifest root must be an object"
        raise ValueError(msg)
    return data


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_equalities(xml_text: str) -> tuple[EqualityRow, ...]:
    root = ET.fromstring(xml_text)  # noqa: S314 — trusted vendored MJCF from manifest
    rows: list[EqualityRow] = []
    equality = root.find("equality")
    if equality is None:
        return tuple()
    for child in equality:
        tag = child.tag.split("}")[-1]
        attrs = {key: value for key, value in child.attrib.items()}
        rows.append(EqualityRow(kind=tag, attributes=attrs))
    return tuple(rows)


def _actuator_for_joint(model: Any, joint_id: int) -> tuple[str | None, list[float] | None]:
    import mujoco

    for act_id in range(model.nu):
        if int(model.actuator_trntype[act_id]) != int(mujoco.mjtTrn.mjTRN_JOINT):
            continue
        if int(model.actuator_trnid[act_id, 0]) != joint_id:
            continue
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, act_id)
        lo, hi = model.actuator_ctrlrange[act_id]
        if bool(model.actuator_ctrllimited[act_id]):
            return name, [float(lo), float(hi)]
        return name, None
    return None, None


def extract_model_map(
    *,
    repo_root: Path,
    entry: dict[str, Any],
) -> ModelMap:
    """Build a :class:`ModelMap` from one manifest entry using MuJoCo."""
    import mujoco

    snapshot = repo_root / str(entry["snapshot_path"])
    digest = _sha256_file(snapshot)
    expected = str(entry["content_sha256"])
    if digest != expected:
        msg = f"{snapshot}: sha256 mismatch (got {digest}, expected {expected})"
        raise ValueError(msg)

    model = mujoco.MjModel.from_xml_path(str(snapshot))
    xml_text = snapshot.read_text(encoding="utf-8")
    joints: list[JointRow] = []
    for joint_id in range(model.njnt):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, joint_id)
        jtype = int(model.jnt_type[joint_id])
        qadr = int(model.jnt_qposadr[joint_id])
        vadr = int(model.jnt_dofadr[joint_id])
        axis = None
        if jtype in (2, 3):
            axis = [float(v) for v in model.jnt_axis[joint_id]]
        jrange = None
        if bool(model.jnt_limited[joint_id]):
            lo, hi = model.jnt_range[joint_id]
            jrange = [float(lo), float(hi)]
        actuator, ctrl = _actuator_for_joint(model, joint_id)
        joints.append(
            JointRow(
                name=name or f"joint_{joint_id}",
                joint_type=_JOINT_TYPE.get(jtype, str(jtype)),
                qpos_index=qadr,
                qpos_count=_JOINT_NQ.get(jtype, 1),
                velocity_index=vadr,
                velocity_count=_JOINT_NV.get(jtype, 1),
                axis=axis,
                range_rad=jrange,
                actuator=actuator,
                ctrl_range=ctrl,
            )
        )

    return ModelMap(
        model_id=str(entry["id"]),
        title=str(entry["title"]),
        nq=int(model.nq),
        nv=int(model.nv),
        nu=int(model.nu),
        neq=int(model.neq),
        joints=tuple(joints),
        equalities=_parse_equalities(xml_text),
        upstream_path=str(entry["upstream_path"]),
        upstream_symbol=str(entry["upstream_symbol"]),
        snapshot_path=str(entry["snapshot_path"]),
        content_sha256=digest,
    )


def maps_to_document(manifest: dict[str, Any], maps: list[ModelMap]) -> dict[str, Any]:
    """Serialize maps plus manifest pin for machine-readable reference output."""
    return {
        "schema": manifest.get("schema"),
        "upstream_commit": manifest.get("upstream_commit"),
        "models": [asdict(item) for item in maps],
        "myosuite_assets": manifest.get("myosuite_assets"),
    }


def _fmt_axis(axis: list[float] | None) -> str:
    if axis is None:
        return "—"
    return f"({axis[0]:g}, {axis[1]:g}, {axis[2]:g})"


def _fmt_range(jrange: list[float] | None) -> str:
    if jrange is None:
        return "—"
    return f"[{jrange[0]:g}, {jrange[1]:g}] rad"


def render_qmd(manifest: dict[str, Any], maps: list[ModelMap]) -> str:
    """Render Quarto markdown tables for the MuJoCo golf model maps."""
    commit = manifest.get("upstream_commit", "")
    lines = [
        "<!-- Generated by scripts/generate_golf_model_maps.py; do not edit. -->",
        "",
        f"Pinned UpstreamDrift commit "
        f"[`{commit}`](https://github.com/D-sorganization/UpstreamDrift/tree/{commit}).",
        "",
        "MuJoCo reports configuration size `nq`, tangent velocity size `nv`, and motor "
        "count `nu`. Internal revolute/universal joints use radians. A `free` joint "
        "occupies seven `qpos` entries (translation plus unit quaternion) and six "
        "velocity components.",
        "",
    ]
    for model_map in maps:
        lines.extend(_render_model_section(model_map))
    lines.extend(_render_myosuite_section(manifest))
    lines.append("")
    return "\n".join(lines)


def _render_model_section(model_map: ModelMap) -> list[str]:
    header = (
        f"### {model_map.title} (`{model_map.model_id}`) " f"{{#{model_map.model_id}-mujoco-map}}"
    )
    cite = (
        f"Source: "
        f"`{model_map.upstream_path}` (`{model_map.upstream_symbol}`); "
        f"vendored snapshot `{model_map.snapshot_path}`."
    )
    summary = (
        f"| `nq` | `nv` | `nu` | equality constraints |\n"
        f"|---:|---:|---:|---:|\n"
        f"| {model_map.nq} | {model_map.nv} | {model_map.nu} | {model_map.neq} |"
    )
    rows = [
        "| `qpos` idx | `v` idx | Joint | Type | Axis | Range | Actuator | `ctrl` range |",
        "|---:|---:|---|---|---|---|---|---|",
    ]
    for joint in model_map.joints:
        ctrl = "—"
        if joint.ctrl_range is not None:
            ctrl = f"[{joint.ctrl_range[0]:g}, {joint.ctrl_range[1]:g}]"
        act = joint.actuator or "—"
        rows.append(
            "| "
            + " | ".join(
                [
                    str(joint.qpos_index),
                    str(joint.velocity_index),
                    f"`{joint.name}`",
                    joint.joint_type,
                    _fmt_axis(joint.axis),
                    _fmt_range(joint.range_rad),
                    f"`{act}`" if act != "—" else act,
                    ctrl,
                ]
            )
            + " |"
        )
    eq_lines = ["", "#### Grip and Hip Closure", ""]
    if not model_map.equalities:
        eq_lines.append("No `<equality>` constraints are declared in this MJCF.")
    else:
        eq_lines.append("| Kind | Attributes |")
        eq_lines.append("|---|---|")
        for eq in model_map.equalities:
            attrs = ", ".join(f'{key}="{value}"' for key, value in eq.attributes.items())
            eq_lines.append(f"| `{eq.kind}` | {attrs} |")
        eq_lines.append("")
        eq_lines.append(
            "MuJoCo `weld` and `connect` constraints are soft equalities whose violation "
            "and constraint forces depend on solver settings; they are not independent "
            "joint coordinates."
        )
    return [
        "",
        header,
        "",
        cite,
        "",
        summary,
        "",
        "#### Generalized-Coordinate Map",
        "",
        *rows,
        "",
        *eq_lines,
        "",
    ]


def _render_myosuite_section(manifest: dict[str, Any]) -> list[str]:
    assets = manifest.get("myosuite_assets")
    if not isinstance(assets, dict):
        return []
    entries = assets.get("entries")
    if not isinstance(entries, list):
        return []
    upstream = assets.get("upstream_path", "")
    lines = [
        "",
        "### MyoSuite Asset Paths (Declared Sizes Only)",
        "",
        f"Motor-driven MuJoCo humanoids above are distinct from MyoSuite musculoskeletal "
        f"assets referenced in `{upstream}`. AffineDrift does not vendor those MJCF files "
        f"in this slice; counts below are taken from upstream comments only.",
        "",
        "| Asset ID | Relative path | Declared `nq` | Declared `nu` | Note |",
        "|---|---|---:|---:|---|",
    ]
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        nu = entry.get("declared_nu")
        nu_cell = "—" if nu is None else str(nu)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{entry.get('id', '')}`",
                    f"`{entry.get('relative_path', '')}`",
                    str(entry.get("declared_nq", "")),
                    nu_cell,
                    str(entry.get("note", "")),
                ]
            )
            + " |"
        )
    return lines
