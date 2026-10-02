"""Manufactured review tests for Chapter 27 reproducibility and verification contracts."""

import hashlib
import json
import math
import random
import re
from pathlib import Path

import pytest


def test_artifact_identity_vs_result_comparison() -> None:
    """Artifact identity differs by serialization while numerical payload matches.

    Demonstrates artifact identity versus result comparison, not cryptographic
    attack detection.
    """
    payload_base = {"run_id": "sim_01", "velocity_mps": 12.5}
    raw_a = json.dumps(payload_base, indent=2).encode("utf-8")
    raw_b = json.dumps(payload_base, separators=(",", ":")).encode("utf-8")

    assert json.loads(raw_a) == json.loads(raw_b)
    assert hashlib.sha256(raw_a).hexdigest() != hashlib.sha256(raw_b).hexdigest()

    # Changed velocity fails numeric equality even if its checksum is recomputed and valid.
    changed_payload = {"run_id": "sim_01", "velocity_mps": 13.0}
    raw_c = json.dumps(changed_payload, separators=(",", ":")).encode("utf-8")
    c_hash = hashlib.sha256(raw_c).hexdigest()

    assert hashlib.sha256(raw_c).hexdigest() == c_hash
    assert json.loads(raw_c)["velocity_mps"] != json.loads(raw_a)["velocity_mps"]


def test_unit_conversion_and_frame_contrast() -> None:
    """Scalars match only after conversion; distinct frames are not matched observables.

    Manufactured metadata contrast, not a production validator.
    """
    speed_ms = 43.0
    speed_kmh = 154.8
    assert speed_ms != speed_kmh
    assert pytest.approx(speed_ms * 3.6, rel=1e-9) == speed_kmh

    # Matching scalar with a different event/frame is not a matched observable.
    frame_alpha = {"frame": "laboratory", "event": "impact", "speed_ms": speed_ms}
    frame_beta = {"frame": "moving_hand", "event": "release", "speed_ms": speed_ms}
    assert frame_alpha["speed_ms"] == frame_beta["speed_ms"]
    assert frame_alpha != frame_beta


def test_floating_point_summation_order() -> None:
    """Illustrate pairwise addition order sensitivity without claiming universal nondeterminism."""
    terms = [1e16, 1.0, -1e16]
    naive_forward = (terms[0] + terms[1]) + terms[2]
    naive_reordered = (terms[0] + terms[2]) + terms[1]

    assert naive_forward == 0.0
    assert naive_reordered == 1.0
    assert math.fsum(terms) == 1.0


def test_prng_call_order_control() -> None:
    """Demonstrate call-order control and identical replay, not cross-version guarantees."""
    rng_baseline = random.Random(2026)  # noqa: S311 -- numerical replay example, not cryptography.
    rng_perturbed = random.Random(2026)  # noqa: S311 -- numerical replay example, not cryptography.
    rng_replay = random.Random(2026)  # noqa: S311 -- numerical replay example, not cryptography.

    # Extra draw perturbs sequence; identical call sequence replays deterministically.
    _ = rng_perturbed.random()
    param_baseline = [rng_baseline.random() for _ in range(3)]
    param_perturbed = [rng_perturbed.random() for _ in range(3)]
    param_replay = [rng_replay.random() for _ in range(3)]

    assert param_baseline != param_perturbed
    assert param_baseline == param_replay


def _rk2_midpoint_step(q: float, v: float, omega: float, dt: float) -> tuple[float, float]:
    """Single step of explicit-midpoint RK2 for q'' + omega^2 q = 0."""
    q_mid = q + 0.5 * dt * v
    v_mid = v - 0.5 * dt * (omega**2) * q
    return q + dt * v_mid, v - dt * (omega**2) * q_mid


def _rk2_midpoint_integrate(omega: float, steps: int, t_end: float = 1.0) -> tuple[float, float]:
    """Integrate unit-inertia oscillator from q(0)=1 rad, v(0)=0 to t_end."""
    dt = t_end / steps
    q, v = 1.0, 0.0
    for _ in range(steps):
        q, v = _rk2_midpoint_step(q, v, omega, dt)
    return q, v


def test_oscillator_convergence_and_model_specification() -> None:
    """Verify RK2 convergence rate and contrast target physics against alternate model."""
    omega_target, omega_wrong, t_eval = 2.0, 1.0, 1.0

    # Exact solutions: q(t) = cos(omega*t), v(t) = -omega*sin(omega*t)
    q_exact = math.cos(omega_target * t_eval)
    v_exact = -omega_target * math.sin(omega_target * t_eval)
    e_target = 0.5 * (v_exact**2 + (omega_target**2) * (q_exact**2))
    assert pytest.approx(e_target, rel=1e-9) == 0.5 * (omega_target**2)

    # omega1 exact conserves its own energy but differs at 1s.
    q_wrong_exact = math.cos(omega_wrong * t_eval)
    v_wrong_exact = -omega_wrong * math.sin(omega_wrong * t_eval)
    e_wrong = 0.5 * (v_wrong_exact**2 + (omega_wrong**2) * (q_wrong_exact**2))
    assert pytest.approx(e_wrong, rel=1e-9) == 0.5 * (omega_wrong**2)
    assert q_exact != q_wrong_exact

    # Step halving (dt 1/20, 1/40, 1/80) approximately quarters error (ratio ~ 4).
    errors: list[float] = []
    for steps in (20, 40, 80):
        q_num, _ = _rk2_midpoint_integrate(omega_target, steps, t_eval)
        errors.append(abs(q_num - q_exact))

    ratio_1 = errors[0] / errors[1]
    ratio_2 = errors[1] / errors[2]
    assert 3.8 < ratio_1 < 4.2
    assert 3.8 < ratio_2 < 4.2

    # Numerical convergence of wrong omega1 model does not validate omega2 physics.
    wrong_errors = [
        abs(_rk2_midpoint_integrate(omega_wrong, steps, t_eval)[0] - q_wrong_exact)
        for steps in (20, 40, 80)
    ]
    assert 3.8 < wrong_errors[0] / wrong_errors[1] < 4.2
    assert 3.8 < wrong_errors[1] / wrong_errors[2] < 4.2
    q_wrong_num, _ = _rk2_midpoint_integrate(omega_wrong, 80, t_eval)
    assert abs(q_wrong_num - q_exact) > 0.8


def test_provider_links_pin_the_reviewed_source_revision() -> None:
    """Prevent the reviewed provider references from silently following mutable main."""
    root = Path(__file__).resolve().parents[1]
    chapter = root / "articles/proximal_distal_companion/chapters/ch27_open_evidence.qmd"
    text = chapter.read_text(encoding="utf-8")
    links = re.findall(r"https://github.com/D-sorganization/UpstreamDrift/[^)\s]+", text)
    assert len(links) >= 3
    revision = "85cce4d3307bb7ad3953d9fc6e583e370803515c"
    assert all(re.search(rf"/(?:blob|tree)/{revision}(?:/|$)", link) for link in links)
