"""Execute the published filtering example against physical and input contracts."""

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest

CHAPTER = (
    Path(__file__).resolve().parents[1]
    / "articles/The_Geometry_of_Motion/Volume_III/chapters/ch07_experimental_methods.tex"
)


@pytest.fixture(scope="module")
def processor() -> Callable[..., Any]:
    source = CHAPTER.read_text(encoding="utf-8")
    match = re.search(
        r"\\begin\{lstlisting\}\[language=Python,[^\n]*\]\n(.*?)\\end\{lstlisting\}",
        source,
        flags=re.DOTALL,
    )
    assert match is not None, "The published Python listing must remain executable"
    namespace: dict[str, Any] = {}
    exec(compile(match.group(1), str(CHAPTER), "exec"), namespace)
    return namespace["process_mocap_data"]


def test_integer_positions_keep_fractional_motion(processor: Callable[..., Any]) -> None:
    data = (np.arange(500) // 10).reshape(-1, 1, 1).repeat(3, axis=2)
    original = data.copy()
    position, velocity, acceleration = processor(data, 100.0, 6.0)
    assert position.shape == velocity.shape == acceleration.shape == data.shape
    assert np.issubdtype(position.dtype, np.floating)
    assert np.any(np.abs(position[100:-100] - np.round(position[100:-100])) > 0.01)
    np.testing.assert_array_equal(data, original)
    assert np.isnan(velocity[[0, -1]]).all()
    assert np.isnan(acceleration[[0, -1]]).all()
    assert np.isfinite(velocity[1:-1]).all()
    assert np.isfinite(acceleration[1:-1]).all()


def test_stationary_markers_have_zero_interior_derivatives(processor: Callable[..., Any]) -> None:
    data = np.full((500, 2, 3), 1.25)
    position, velocity, acceleration = processor(data, 200.0, 6.0)
    np.testing.assert_allclose(position, data, atol=1e-10)
    np.testing.assert_allclose(velocity[50:-50], 0.0, atol=1e-9)
    np.testing.assert_allclose(acceleration[50:-50], 0.0, atol=1e-8)


def test_declared_single_pass_cutoff_is_half_amplitude_after_two_passes(
    processor: Callable[..., Any],
) -> None:
    sample_rate, frequency = 200.0, 6.0
    t = np.arange(2000) / sample_rate
    signal = np.sin(2 * np.pi * frequency * t)
    data = signal[:, None, None].repeat(3, axis=2)
    position, velocity, acceleration = processor(data, sample_rate, frequency)
    interior = slice(300, -300)
    np.testing.assert_allclose(position[interior, 0, 0], 0.5 * signal[interior], atol=1e-5)
    expected_v = np.pi * frequency * np.cos(2 * np.pi * frequency * t[interior])
    expected_a = -0.5 * (2 * np.pi * frequency) ** 2 * signal[interior]
    np.testing.assert_allclose(velocity[interior, 0, 0], expected_v, atol=0.12)
    np.testing.assert_allclose(acceleration[interior, 0, 0], expected_a, atol=2.2)


@pytest.mark.parametrize(
    "data",
    [
        np.zeros((50, 3)),
        np.zeros((50, 0, 3)),
        np.zeros((50, 1, 2)),
        np.zeros((3, 1, 3)),
        np.full((50, 1, 3), np.nan),
        np.full((50, 1, 3), np.inf),
    ],
)
def test_invalid_marker_data_is_rejected(processor: Callable[..., Any], data: np.ndarray) -> None:
    with pytest.raises(ValueError):
        processor(data, 100.0, 6.0)


@pytest.mark.parametrize(
    "sample_rate,cutoff,order",
    [
        (0.0, 6.0, 4),
        (np.inf, 6.0, 4),
        (100.0, np.nan, 4),
        (100.0, 50.0, 4),
        (100.0, 0.0, 4),
        (100.0, 6.0, 0),
        (100.0, 6.0, True),
        (100.0, 6.0, 2.5),
    ],
)
def test_invalid_filter_design_is_rejected(
    processor: Callable[..., Any], sample_rate: float, cutoff: float, order: int
) -> None:
    with pytest.raises(ValueError):
        processor(np.zeros((100, 1, 3)), sample_rate, cutoff, order)
