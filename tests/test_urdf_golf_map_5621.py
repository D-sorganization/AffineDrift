"""Contracts for the pinned on-disk golfer URDF reference."""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import Mock

import pytest
from defusedxml.common import DefusedXmlException

from scripts import generate_urdf_golf_map as generator
from scripts.generate_urdf_golf_map import parse_joints, render_table, verify_source

ROOT = Path(__file__).resolve().parents[1]
XML = b"""<robot name="golfer">
<joint name="shoulder" type="revolute"><parent link="torso"/>
<child link="arm"/><axis xyz="0 1 0"/>
<limit lower="-0.7" upper="0.52"/></joint>
<joint name="grip" type="fixed"><parent link="arm"/><child link="club"/></joint>
</robot>"""


def test_table_preserves_declared_axis_limits_and_fixed_attachment() -> None:
    rows = parse_joints(XML)
    table = render_table(rows)
    assert len(rows) == 2
    assert "| 0 | `shoulder` | revolute | `torso` → `arm` | `0 1 0` | [-0.7, 0.52] |" in table
    assert "| 1 | `grip` | fixed | `arm` → `club` | — | — |" in table
    assert "XML Row" in table


def test_verification_rejects_changed_source_bytes() -> None:
    digest = hashlib.sha256(XML).hexdigest()
    verify_source(XML, digest)
    with pytest.raises(ValueError, match="SHA-256"):
        verify_source(XML + b"\n", digest)


@pytest.mark.parametrize(
    "old,new",
    [
        (b"revolute", b"continuous"),
        (b'upper="0.52"', b'upper="-1"'),
        (b"0 1 0", b"0 0 0"),
        (b"-0.7", b"nan"),
        (b'<axis xyz="0 1 0"/>', b""),
        (b'name="grip"', b'name="shoulder"'),
    ],
)
def test_invalid_or_unsupported_joint_data_fails_closed(old: bytes, new: bytes) -> None:
    with pytest.raises(ValueError):
        parse_joints(XML.replace(old, new))


def test_entity_expansion_is_rejected() -> None:
    xml = b'<!DOCTYPE robot [<!ENTITY x "expanded">]><robot name="&x;"/>'
    with pytest.raises(DefusedXmlException):
        parse_joints(xml)


@pytest.mark.parametrize("check", [False, True])
@pytest.mark.integration
def test_cli_uses_pinned_objects_and_detects_stale_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, check: bool
) -> None:
    output = tmp_path / "table.qmd"
    output.write_text(render_table(parse_joints(XML)), encoding="utf-8")
    monkeypatch.setattr(generator, "OUTPUT", output)
    monkeypatch.setattr(generator, "SOURCE_SHA256", hashlib.sha256(XML).hexdigest())
    run = Mock(return_value=Mock(stdout=XML))
    monkeypatch.setattr("scripts.generate_urdf_golf_map.subprocess.run", run)
    monkeypatch.setattr(
        "sys.argv", ["generator", "--upstream", str(tmp_path)] + (["--check"] if check else [])
    )
    assert generator.main() == 0
    assert run.call_count == 2
    for call, path in zip(run.call_args_list, generator.SOURCES, strict=True):
        assert call.args[0][-1] == f"{generator.PIN}:{path}"
    if check:
        output.write_text("stale", encoding="utf-8")
        with pytest.raises(ValueError, match="stale"):
            generator.main()


@pytest.mark.integration
def test_published_reference_states_order_and_loader_boundaries() -> None:
    page = (ROOT / "models/golf-urdf-joint-map.qmd").read_text(encoding="utf-8")
    table = (ROOT / "models/_generated/golf-urdf-joints.qmd").read_text(encoding="utf-8")
    assert "include _generated/golf-urdf-joints.qmd" in page
    assert "43 revolute" in page and "four fixed" in page
    assert "not native" in page and "idx_q" in page and "idx_v" in page
    assert "thorax3_to_mid_hands" in table
    assert "mid_hands_to_club_shaft" in table
    assert sum("| revolute |" in line for line in table.splitlines()) == 43
    assert sum("| fixed |" in line for line in table.splitlines()) == 4
