"""Check the published muscle mapping and single-frame IK examples."""

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

CHAPTERS = (
    Path(__file__).resolve().parents[1] / "articles/The_Geometry_of_Motion/Volume_III/chapters"
)


def listing_namespace(filename: str) -> dict[str, Any]:
    source = (CHAPTERS / filename).read_text(encoding="utf-8")
    match = re.search(
        r"\\begin\{lstlisting\}\[language=Python,[^\n]*\]\n(.*?)\\end\{lstlisting\}",
        source,
        flags=re.DOTALL,
    )
    assert match is not None
    namespace: dict[str, Any] = {}
    # Only repository-owned chapters selected by literal filenames in these tests are executed.
    # nosemgrep: python.lang.security.audit.exec-detected.exec-detected
    exec(compile(match.group(1), filename, "exec"), namespace)
    return namespace


@pytest.fixture
def ik() -> dict[str, Any]:
    return listing_namespace("ch06_inverse_problems.tex")


def test_ik_recovers_identifiable_synthetic_translation(ik: dict[str, Any]) -> None:
    offsets = np.array([[0.0, 0.0, 0.0], [1.0, 0.5, -0.5]])
    expected = np.array([0.1, -0.2, 0.3])
    measured = offsets + expected
    result = ik["inverse_kinematics_frame"](measured, lambda q: offsets + q, np.zeros(3))
    np.testing.assert_allclose(result, expected, atol=1e-6)


@pytest.mark.parametrize(
    "weights",
    [np.array([-1.0, 1.0]), np.zeros(2), np.array([1.0]), np.array([np.nan, 1.0])],
)
def test_ik_rejects_invalid_weights(ik: dict[str, Any], weights: np.ndarray) -> None:
    with pytest.raises(ValueError):
        ik["inverse_kinematics_frame"](
            np.zeros((2, 3)), lambda q: np.zeros((2, 3)) + q, np.zeros(3), weights
        )


@pytest.mark.parametrize("measured", [np.zeros((0, 3)), np.zeros((2, 2)), np.full((2, 3), np.nan)])
def test_ik_rejects_invalid_observations(ik: dict[str, Any], measured: np.ndarray) -> None:
    with pytest.raises(ValueError):
        ik["inverse_kinematics_frame"](measured, lambda q: measured, np.zeros(3))


def test_ik_rejects_model_broadcasting(ik: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        ik["inverse_kinematics_frame"](np.zeros((2, 3)), lambda q: np.zeros((1, 3)), np.zeros(3))


def test_ik_does_not_return_failed_optimizer_as_solution(ik: dict[str, Any]) -> None:
    ik["minimize"] = lambda *args, **kwargs: SimpleNamespace(
        success=False, x=np.zeros(3), fun=0.0, message="iteration limit"
    )
    with pytest.raises(RuntimeError, match="iteration limit"):
        ik["inverse_kinematics_frame"](np.zeros((2, 3)), lambda q: np.zeros((2, 3)), np.zeros(3))


def test_muscle_mapping_preserves_signed_power() -> None:
    mapping = listing_namespace("ch05_multibody_bio.tex")["compute_joint_torques"]
    r = np.array([[0.05, -0.03], [0.04, 0.02]])
    force, velocity = np.array([200.0, 100.0]), np.array([-1.0, 2.0])
    torque = mapping(r, force)
    np.testing.assert_allclose(torque, [7.0, 10.0])
    np.testing.assert_allclose(torque @ velocity, -force @ (-r.T @ velocity))


@pytest.mark.parametrize("force", [np.array([-1.0, 1.0]), np.array([np.inf, 1.0]), np.ones((2, 1))])
def test_muscle_mapping_rejects_invalid_tensions(force: np.ndarray) -> None:
    mapping = listing_namespace("ch05_multibody_bio.tex")["compute_joint_torques"]
    with pytest.raises(ValueError):
        mapping(np.eye(2), force)
