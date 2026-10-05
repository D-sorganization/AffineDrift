"""Check the published URDF topology, inertial frames and optional engine import."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest
from defusedxml import ElementTree as ET

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/The_Geometry_of_Motion/Volume_V/chapters/ch03_building_models.tex"
)


def _xml_listing() -> str:
    """Extract a fixed, repository-owned XML listing."""
    match = re.search(
        r"\\begin\{lstlisting\}\[language=XML[^\n]*\]\n(.*?)\\end\{lstlisting\}",
        CHAPTER.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    assert match is not None, "The chapter must contain the complete URDF example"
    return match.group(1)


def test_connected_tree_and_joint_contract() -> None:
    """Every moving link is connected with explicit frame, axis and limits."""
    root = ET.fromstring(_xml_listing())
    assert root.tag == "robot"
    assert {link.attrib["name"] for link in root.findall("link")} == {"base", "rod"}
    joints = root.findall("joint")
    assert len(joints) == 1
    joint = joints[0]
    assert joint.attrib["type"] == "revolute"
    assert joint.find("parent").attrib["link"] == "base"
    assert joint.find("child").attrib["link"] == "rod"
    assert joint.find("axis").attrib["xyz"] == "0 1 0"
    assert joint.find("origin").attrib["xyz"] == "0 0 0"
    assert float(joint.find("dynamics").attrib["damping"]) == 0.05
    limits = {key: float(value) for key, value in joint.find("limit").attrib.items()}
    assert limits == {"lower": -3.14, "upper": 3.14, "effort": 20.0, "velocity": 30.0}


def test_cylinder_inertia_and_geometry() -> None:
    """Inertia is about the declared COM, not accidentally about the hinge."""
    rod = ET.fromstring(_xml_listing()).find("link[@name='rod']")
    inertial = rod.find("inertial")
    assert float(inertial.find("mass").attrib["value"]) == 1.0
    assert inertial.find("origin").attrib["xyz"] == "0 0 -0.5"
    values = {key: float(value) for key, value in inertial.find("inertia").attrib.items()}
    transverse = (1 + 3 * 0.02**2) / 12
    assert values == pytest.approx(
        {"ixx": transverse, "iyy": transverse, "izz": 0.02**2 / 2, "ixy": 0, "ixz": 0, "iyz": 0}
    )
    for tag in ("visual", "collision"):
        geometry = rod.find(tag)
        assert geometry.find("origin").attrib["xyz"] == "0 0 -0.5"
        cylinder = geometry.find("geometry/cylinder")
        assert float(cylinder.attrib["length"]) == 1.0
        assert float(cylinder.attrib["radius"]) == 0.02


@pytest.mark.requires_mujoco
def test_mujoco_import_matches_analytic_mechanics() -> None:
    """One installed engine checks loaded mass, gravity, damping and kinematics."""
    mujoco = pytest.importorskip("mujoco")
    model = mujoco.MjModel.from_xml_string(_xml_listing())
    data = mujoco.MjData(model)
    assert (model.nq, model.nv) == (1, 1)
    assert np.sum(model.body_mass) == pytest.approx(1.0)
    data.qpos[0], data.qvel[0] = 0.3, 2.0
    mujoco.mj_forward(model, data)
    # One DOF has a single packed inertia entry, avoiding version-specific fullM signatures.
    assert data.qM[0] == pytest.approx(1 / 3 + 0.02**2 / 4)
    assert data.qfrc_bias[0] == pytest.approx(4.905 * np.sin(0.3))
    assert data.qfrc_passive[0] == pytest.approx(-0.1)
    body = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "rod")
    assert body >= 0
    np.testing.assert_allclose(data.xipos[body], [-0.5 * np.sin(0.3), 0, -0.5 * np.cos(0.3)])
