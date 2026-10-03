"""Manufactured checks separating metric decay from coordinate error growth."""

from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "articles/motion-control/chapter5.tex",
    "articles/motion-control/Control_Is_Motion_Complete.tex",
    "articles/The_Geometry_of_Motion/Volume_II/chapters/ch05_underactuation_and_passive_dyn.tex",
    "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd",
)


@pytest.mark.parametrize("rate", [0.0, 1.0])
@pytest.mark.parametrize("initial", [(1.0, 0.0), (0.0, 1.0)])
def test_metric_certificate_and_finite_window_bound(
    rate: float, initial: tuple[float, float]
) -> None:
    """Exact diagonal flows test zero/positive rates in a changing metric."""
    initial_error = np.asarray(initial)
    generator = np.diag([-rate - 2.0, -rate + 2.0])
    final_time = 1.0
    lower_metric_bound = np.exp(-4.0 * final_time)
    for time in (0.0, 0.25, 0.5, final_time):
        error = np.exp(np.diag(generator) * time) * initial_error
        metric = np.diag(np.exp(np.array([4.0, -4.0]) * time))
        metric_rate = np.diag([4.0, -4.0]) @ metric
        quadratic_error = error @ metric @ error
        derivative = error @ (metric_rate + generator.T @ metric + metric @ generator) @ error
        assert derivative == pytest.approx(-2.0 * rate * quadratic_error, abs=1e-12)
        assert quadratic_error == pytest.approx(np.exp(-2.0 * rate * time))
        coordinate_bound = np.exp(-rate * time) / np.sqrt(lower_metric_bound)
        assert np.linalg.norm(error) <= coordinate_bound + 1e-12


def test_metric_decay_does_not_imply_coordinate_norm_decreases() -> None:
    """A shrinking metric can hide coordinate growth without a lower bound."""
    final_error = np.array([0.0, np.e])
    final_metric = np.diag([np.exp(4.0), np.exp(-4.0)])
    assert np.linalg.norm(final_error) > 1.0
    assert final_error @ final_metric @ final_error == pytest.approx(np.exp(-2.0))
    assert np.linalg.eigvalsh(final_metric)[0] == pytest.approx(np.exp(-4.0))


@pytest.mark.content_lint
@pytest.mark.parametrize("relative", SOURCES)
def test_chapter_states_decay_certificate_assumptions(relative: str) -> None:
    """All maintained chapter copies must expose the certificate's scope."""
    text = (ROOT / relative).read_text(encoding="utf-8")
    for fragment in (r"\lambda>0", r"V_\delta", r"w_-", "nominal trajectory", "Lohmiller"):
        assert fragment in text, f"Missing certificate disclosure {fragment!r} in {relative}"
