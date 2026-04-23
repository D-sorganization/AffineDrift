import re
from pathlib import Path

import numpy as np

REFERENCE_ARTICLE = Path("articles/rotation-representations-reference.qmd")


def _load_reference_namespace() -> dict[str, object]:
    article_text = REFERENCE_ARTICLE.read_text(encoding="utf-8")
    match = re.search(r"```python\n(.*?)\n```", article_text, flags=re.DOTALL)
    assert match is not None
    implementation = match.group(1).split("# --- Verification", maxsplit=1)[0]
    namespace: dict[str, object] = {}
    exec(compile(implementation, str(REFERENCE_ARTICLE), "exec"), namespace)
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
