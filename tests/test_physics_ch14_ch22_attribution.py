"""Regression tests verifying citation, work-efficiency, and anatomical attribution in Physics ch14 and ch22."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PHYSICS_DIR = ROOT / "articles" / "The_Physics_of_Golf"

CH14_TEX = PHYSICS_DIR / "chapters" / "ch14_complete_swing.tex"
CH14_QMD = PHYSICS_DIR / "quarto" / "ch14_complete_swing.qmd"
CH22_TEX = PHYSICS_DIR / "chapters" / "ch22_anatomy_joint_modeling.tex"
CH22_QMD = PHYSICS_DIR / "quarto" / "ch22_anatomy_joint_modeling.qmd"


@pytest.mark.parametrize("path", [CH14_TEX, CH14_QMD])
def test_ch14_nesbit_work_efficiency_attribution(path: Path) -> None:
    """Ensure Nesbit2005b is attributed to mechanical joint-work ratio, not metabolic efficiency."""
    text = path.read_text(encoding="utf-8")

    # Nesbit2005b must NOT be cited as evidence of muscle metabolic efficiency
    assert "metabolic energy input) is approximately 20--25% \\citep{Nesbit2005b}" not in text
    assert "Muscles are only about 20--25% efficient [@Nesbit2005b]" not in text
    assert "muscle input to ball kinetic energy is relatively low \\citep{Nesbit2005b}" not in text

    # Must accurately describe mechanical swing efficiency as club work / total joint work
    assert "Nesbit2005b" in text
    assert "total body joint work" in text or "total work done across all body joints" in text


@pytest.mark.parametrize("path", [CH22_TEX, CH22_QMD])
def test_ch22_hip_internal_rotation_and_cheetham_attribution(path: Path) -> None:
    """Ensure Cheetham2001 is not attributed to 35-50 deg hip internal rotation ROM."""
    text = path.read_text(encoding="utf-8")

    # Old erroneous assertion conflated pelvic turn/X-factor with hip IR ROM
    assert "reporting approximately 35--50" not in text
    assert "reporting approximately $35" not in text

    # Must distinguish pelvic rotation from anatomical hip internal rotation
    assert "Cheetham2001" in text
    assert "pelvis" in text
    assert "internal rotation" in text
