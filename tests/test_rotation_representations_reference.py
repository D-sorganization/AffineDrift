import re
from pathlib import Path

import numpy as np
import pytest

REFERENCE_ARTICLE = Path("articles/rotation-representations-reference.qmd")


def _load_reference_namespace() -> dict[str, object]:
    article_text = REFERENCE_ARTICLE.read_text(encoding="utf-8")
    match = re.search(r"```python\n(.*?)\n```", article_text, flags=re.DOTALL)
    assert match is not None
    implementation = match.group(1).split("# --- Verification", maxsplit=1)[0]
    namespace: dict[str, object] = {}
    exec(compile(implementation, str(REFERENCE_ARTICLE), "exec"), namespace)  # nosec B102
    return namespace


def _quaternions_match(actual: np.ndarray, expected: np.ndarray) -> bool:
    return bool(np.allclose(actual, expected) or np.allclose(actual, -expected))


def test_r_to_quaternion_preserves_mixed_sign_axis_for_180_degree_rotation() -> None:
    namespace = _load_reference_namespace()
    axis_angle_to_R = namespace["axis_angle_to_R"]
    R_to_quaternion = namespace["R_to_quaternion"]
    axis = np.array([-1.0, 2.0, -3.0])
    axis = axis / np.linalg.norm(axis)

    rotation_matrix = axis_angle_to_R(axis, np.pi)
    quaternion = R_to_quaternion(rotation_matrix)

    assert _quaternions_match(quaternion, np.concatenate(([0.0], axis)))


@pytest.mark.parametrize("angle", [1e-12, 1e-8, np.pi - 1e-8, np.pi, np.pi + 1e-8])
def test_reference_axis_angle_reconstructs_boundary_rotations(angle: float) -> None:
    namespace = _load_reference_namespace()
    axis = np.array([-1.0, 2.0, -3.0]) / np.sqrt(14)
    original = namespace["axis_angle_to_R"](axis, angle)
    recovered_axis, recovered_angle = namespace["R_to_axis_angle"](original)
    reconstructed = namespace["axis_angle_to_R"](recovered_axis, recovered_angle)
    np.testing.assert_allclose(reconstructed, original, atol=2e-14, rtol=0)
    assert 0 <= recovered_angle <= np.pi


@pytest.mark.parametrize("pitch", [np.pi / 2, -np.pi / 2, np.pi / 2 - 1e-8])
def test_reference_euler_reconstructs_at_and_near_gimbal_lock(pitch: float) -> None:
    namespace = _load_reference_namespace()
    original = namespace["euler_zyx_to_R"](0.7, pitch, -0.9)
    angles = namespace["R_to_euler_zyx"](original)
    np.testing.assert_allclose(namespace["euler_zyx_to_R"](*angles), original, atol=2e-14)


@pytest.mark.parametrize("function", ["R_to_axis_angle", "R_to_quaternion", "R_to_euler_zyx"])
def test_reference_rejects_reflections(function: str) -> None:
    with pytest.raises(ValueError):
        _load_reference_namespace()[function](np.diag([1, 1, -1]))
