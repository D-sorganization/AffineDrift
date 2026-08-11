"""Scientific-boundary checks for the ground-reaction chapter."""

from pathlib import Path

CHAPTER = Path("articles/The_Physics_of_Golf/quarto/ch15_ground_reaction_forces.qmd")


def test_chapter_uses_conditional_contact_work_claim() -> None:
    text = CHAPTER.read_text(encoding="utf-8")

    assert "ideal rigid, stationary, no-slip contact" in text
    assert "does not imply zero muscular work" in text
    assert "ground reaction force does zero work and delivers zero power" not in text


def test_chapter_rejects_unique_torque_and_bilateral_inference() -> None:
    text = CHAPTER.read_text(encoding="utf-8")

    assert "cannot uniquely identify muscle torques" in text
    assert "cannot uniquely determine the bilateral allocation" in text
    assert "we can infer the muscle torques" not in text


def test_chapter_defines_pointwise_reaction_counterfactuals() -> None:
    text = CHAPTER.read_text(encoding="utf-8")

    assert "Pointwise Ground-Reaction ZTCF" in text
    assert "Pointwise Ground-Reaction ZVCF" in text
    assert "must not be added" in text
    assert "not forward simulations" in text


def test_chapter_has_falsification_and_measurement_requirements() -> None:
    text = CHAPTER.read_text(encoding="utf-8")

    for term in (
        "synchronized bilateral six-axis force plates",
        "held-out participants",
        "dynamic consistency",
        "free moment",
        "center of pressure",
    ):
        assert term in text


def test_chapter_does_not_prescribe_one_correct_grf_pattern() -> None:
    text = CHAPTER.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "one universal COP or GRF waveform" in normalized
    assert "template of optimal performance" not in text
    assert "correct swing" not in text
