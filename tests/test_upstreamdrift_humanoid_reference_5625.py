"""Content contracts for humanoid balance and whole-body reference pages (#5625)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = "3afe09c1ed0247a459d16bf75cf0b28bb64f584a"
BALANCE = ROOT / "articles/upstreamdrift-humanoid-balance.qmd"
WBC = ROOT / "articles/upstreamdrift-whole-body-control.qmd"
UD = f"https://github.com/D-sorganization/UpstreamDrift/blob/{PIN}"


def test_humanoid_balance_links_zmp_module_and_capture_point() -> None:
    text = BALANCE.read_text(encoding="utf-8")
    assert "zmp_computer.py" in text
    assert f"{UD}/src/robotics/locomotion/zmp_computer.py#L143-L151" in text
    assert r"\dot{L}_{c,y}" in text
    assert "0.151" in text
    assert "_DEFAULT_CENTROIDAL_MASS_KG = 50" in text


def test_whole_body_control_documents_hierarchy_maturity() -> None:
    text = WBC.read_text(encoding="utf-8")
    assert "WholeBodyController" in text
    assert "PR #15025" in text
    assert "sorted(priority_groups.items(), reverse=True)" in text
    assert "mu = 0.5" in text
