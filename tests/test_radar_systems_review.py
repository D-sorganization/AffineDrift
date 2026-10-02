"""Manufactured radar checks; no hardware or human-swing validation is implied."""

from pathlib import Path

import numpy as np
import pytest
from scipy.constants import c
from scipy.spatial.transform import Rotation

C_SI: float = c


def test_exact_si_monostatic_doppler() -> None:
    mph_to_mps: float = 1609.344 / 3600.0  # Exact statutory definition
    f_kband: float = 24.125e9
    f_xband: float = 10.5e9
    shift_k: float = 2.0 * f_kband * mph_to_mps / C_SI
    shift_x: float = 2.0 * f_xband * mph_to_mps / C_SI
    assert shift_k == pytest.approx(71.94870792913676, rel=1e-12)
    assert shift_x == pytest.approx(31.31446355465, rel=1e-12)


def test_phase_ambiguity_branch_reconstruction() -> None:
    d_over_lambda: float = 1.0
    u_true, u_alias = 0.2, -0.8
    phi_true: float = 2.0 * np.pi * d_over_lambda * u_true
    phi_alias: float = 2.0 * np.pi * d_over_lambda * u_alias
    np.testing.assert_allclose(np.exp(1j * phi_true), np.exp(1j * phi_alias), atol=1e-12)

    measured_phase: float = float(np.angle(np.exp(1j * phi_true)))
    k_branch: int = 0
    u_recovered: float = (measured_phase + 2.0 * np.pi * k_branch) / (2.0 * np.pi * d_over_lambda)
    assert u_recovered == pytest.approx(u_true, abs=1e-12)
    other_branch = (measured_phase - 2 * np.pi) / (2 * np.pi * d_over_lambda)
    assert other_branch == pytest.approx(u_alias, abs=1e-12)

    # Half-wavelength spacing wraps endpoint boundaries onto identical phasors
    d_half: float = 0.5
    np.testing.assert_allclose(
        np.exp(1j * 2.0 * np.pi * d_half * 1.0),
        np.exp(1j * 2.0 * np.pi * d_half * (-1.0)),
        atol=1e-12,
    )


def test_rotating_feature_los_projection() -> None:
    # Epistemic limit: Point kinematics neglect structural aspect occlusion and scattering-center migration.
    r0 = np.array([0.0, 0.015, -0.008], dtype=np.float64)
    omega = np.array([0.0, 120.0, 0.0], dtype=np.float64)
    v_kinematic = np.cross(omega, r0)
    assert float(np.dot(v_kinematic, [1.0, 0.0, 0.0])) == pytest.approx(-0.96, abs=1e-12)
    assert float(np.dot(v_kinematic, [0.0, 1.0, 0.0])) == pytest.approx(0.0, abs=1e-12)

    # Independent finite rotation checks the instantaneous cross-product formula.
    dt: float = 1e-7
    rotations = Rotation.from_rotvec(np.array([-dt, dt])[:, None] * omega)
    rotated = rotations.apply(r0)
    v_fd = (rotated[1] - rotated[0]) / (2 * dt)
    np.testing.assert_allclose(v_fd, v_kinematic, atol=1e-7)


def test_rotating_signal_half_period_harmonic_structure() -> None:
    # Epistemic limit: Half-period repetition eliminates odd harmonics; spectral lines admit dual base hypotheses.
    w0: float = 2.0 * np.pi * 100.0  # 100 Hz baseline
    t = np.linspace(0.0, 1.0, 20000, endpoint=False)
    # Signal satisfies s(t + T/2) = s(t) with T = 2*pi/w0; lacks odd harmonics of w0
    s = np.cos(2.0 * w0 * t) + 0.3 * np.cos(4.0 * w0 * t)
    dt: float = float(t[1] - t[0])
    fft_mag = np.abs(np.fft.rfft(s)) * (2.0 / len(t))
    freqs = np.fft.rfftfreq(len(t), d=dt)

    idx_100 = int(np.argmin(np.abs(freqs - 100.0)))
    idx_200 = int(np.argmin(np.abs(freqs - 200.0)))
    idx_300 = int(np.argmin(np.abs(freqs - 300.0)))
    idx_400 = int(np.argmin(np.abs(freqs - 400.0)))

    assert fft_mag[idx_100] < 1e-9 and fft_mag[idx_300] < 1e-9
    assert fft_mag[idx_200] == pytest.approx(1.0, abs=1e-3)
    assert fft_mag[idx_400] == pytest.approx(0.3, abs=1e-3)


def test_trajectory_constant_axis_nullspace_conditioning() -> None:
    # Exact nullspaces do not imply stable inference from noisy trajectories.
    rows_rank1 = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 2.0]], dtype=np.float64)
    rows_rank1 /= np.linalg.norm(rows_rank1, axis=1, keepdims=True)
    _, s1, vh1 = np.linalg.svd(rows_rank1)
    assert int((s1 > 1e-12).sum()) == 1
    assert vh1[1:].shape[0] == 2  # 2D nullspace permits an infinite continuum of unit normal axes

    rows_rank2 = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float64)
    _, s2, vh2 = np.linalg.svd(rows_rank2)
    assert int((s2 > 1e-12).sum()) == 2
    assert np.abs(np.dot(vh2[-1], [0.0, 0.0, 1.0])) == pytest.approx(1.0, abs=1e-12)

    # Nearly parallel lift rows can leave an algebraically unique axis poorly conditioned.
    rows_ill = np.array([[1.0, 0.0, 0.0], [1.0, 1e-5, 0.0]], dtype=np.float64)
    rows_ill /= np.linalg.norm(rows_ill, axis=1, keepdims=True)
    _, s_ill, _ = np.linalg.svd(rows_ill)
    assert (s_ill[0] / s_ill[1]) > 1e4


def test_unequal_baseline_delay_recovery() -> None:
    # Manufactured normalized quantities test the printed algebra, not real delay physics.
    sv, sh, d = 0.1, 0.2, 3.0
    for deg in [30.0, 120.0, -150.0, -60.0]:
        phi: float = float(np.deg2rad(deg))
        tv: float = (sv / d) * np.cos(phi)
        th: float = (sh / d) * np.sin(phi)
        assert np.arctan2(th / sh, tv / sv) == pytest.approx(phi, abs=1e-12)

    phi30: float = float(np.deg2rad(30.0))
    tv30: float = (sv / d) * np.cos(phi30)
    th30: float = (sh / d) * np.sin(phi30)
    bad_atan_deg: float = float(np.rad2deg(np.arctan((sh * th30) / (sv * tv30))))
    assert bad_atan_deg == pytest.approx(66.5867755536, abs=1e-10)


def test_reference_direction_common_rotation_invariance() -> None:
    # Epistemic limit: Rigid yaw invariance is kinematic; 1/wf sensitivity is specific to weighting formulas.
    face, path, wf = 0.04, 0.01, 0.8
    rel_expected: float = face - path
    for delta_ref in [-0.15, 0.0, 0.2]:
        launch = wf * face + (1 - wf) * path
        inferred = (launch + delta_ref - (1 - wf) * (path + delta_ref)) / wf
        assert inferred - (path + delta_ref) == pytest.approx(rel_expected, abs=1e-12)
    assert (1.0 / wf) == pytest.approx(1.25, abs=1e-12)


@pytest.mark.integration
def test_latex_source_radar_literature_and_branch_tokens() -> None:
    # This source contract guards the distinctions that failed on the original chapter.
    tex_path = Path("articles/Launch_Monitor_Technology_Review/sections/04-radar-systems.tex")
    text = tex_path.read_text(encoding="utf-8")
    assert "garminr10rct" in text
    assert "rapsodomlm2prorpt" in text
    assert r"\Delta\varphi+2\pi k" in text
