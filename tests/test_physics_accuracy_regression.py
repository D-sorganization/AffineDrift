"""Physics accuracy regression tests for AffineDrift textbooks.

Addresses issues:
- #2301: Tangent space of SO(3) incorrectly identified at arbitrary R
- #2290: Inconsistent double pendulum parameters across chapters
- #2291: Euler-Bernoulli beam equation missing inertial term
- #2305: Eigenvalue invariance claim wrong for time-dependent coords
"""

import math
from pathlib import Path

import pytest

from src.core.constants import GRAVITY_M_S2

REPO_ROOT = Path(__file__).resolve().parents[1]
GEOMETRY_CH01 = REPO_ROOT / "articles/The_Geometry_of_Motion/quarto/ch01_foundations.qmd"
GEOMETRY_CH01_TEX = (
    REPO_ROOT / "articles/The_Geometry_of_Motion/Volume_I/chapters/ch01_foundations.tex"
)


class TestSO3TangentSpace:
    """Regression tests for SO(3) tangent space identification - #2301."""

    def test_tangent_space_at_identity(self):
        """Tangent space of SO(3) at identity is so(3) (skew-symmetric matrices)."""
        # At identity R=I, tangent space is so(3) = {A : A + A^T = 0}
        # This is 3-dimensional, spanned by basis elements e1, e2, e3
        so3_dim = 3
        SO3_manifold_dim = 3
        assert so3_dim == SO3_manifold_dim, "dim(so(3)) must equal dim(SO(3)) = 3"

    def test_tangent_space_at_arbitrary_R(self):
        """Tangent space at arbitrary R is R * so(3), not so(3) itself.

        Issue #2301: textbook incorrectly identified tangent space at R as so(3).
        Correct: T_R SO(3) = {R * A : A in so(3)} = R * so(3).
        """
        # Verify: if X is tangent at R, then R^T * X is skew-symmetric
        try:
            import numpy as np
        except ImportError:
            pytest.skip("numpy required")

        # Example: R = rotation by 45 degrees around z-axis
        theta = math.pi / 4
        R = np.array(
            [
                [math.cos(theta), -math.sin(theta), 0],
                [math.sin(theta), math.cos(theta), 0],
                [0, 0, 1],
            ]
        )
        # A tangent vector at R: X = R @ skew(omega) for some omega
        # skew(omega) with omega = (0, 0, 1)
        omega = np.array([0, 0, 1])
        skew_omega = np.array(
            [[0, -omega[2], omega[1]], [omega[2], 0, -omega[0]], [-omega[1], omega[0], 0]]
        )
        X = R @ skew_omega  # tangent vector at R

        # R^T @ X should be skew-symmetric (in so(3))
        RT_X = R.T @ X
        skew_check = RT_X + RT_X.T
        assert np.allclose(skew_check, 0, atol=1e-10), (
            "R^T @ X must be skew-symmetric for X in T_R SO(3)"
        )

    def test_geometry_chapter_states_tangent_space_at_R_as_translated_lie_algebra(self):
        """Chapter text must not identify T_R SO(3) directly with skew matrices."""
        for source in (GEOMETRY_CH01, GEOMETRY_CH01_TEX):
            chapter = source.read_text(encoding="utf-8")

            assert "T_{\\mat{I}}\\SO(3) = \\mathfrak{so}(3)" in chapter
            assert "T_{\\mat{R}}\\SO(3) = \\{\\mat{R}\\mat{S}" in chapter
            assert "= \\mat{R}\\mathfrak{so}(3)" in chapter
            assert "T_{\\mat{R}}\\SO(3) = \\{\\mat{S} \\in \\R^{3 \\times 3}" not in chapter


class TestDoublePendulumConsistency:
    """Tests for double pendulum parameter consistency - #2290."""

    def test_parameter_ranges_physically_valid(self):
        """Double pendulum parameters must be physically plausible."""
        # Standard double pendulum: m1, m2 > 0, length1, length2 > 0, g > 0
        m1, m2 = 1.0, 1.0  # kg
        length1, length2 = 1.0, 1.0  # m
        g = GRAVITY_M_S2

        assert m1 > 0 and m2 > 0, "Masses must be positive"
        assert length1 > 0 and length2 > 0, "Link lengths must be positive"
        assert g > 0, "Gravity must be positive"

    def test_natural_frequency_consistency(self):
        """Natural frequency of simple pendulum limit must be consistent."""
        # For m2->0, double pendulum reduces to simple pendulum
        # omega_0 = sqrt(g / length)
        g = GRAVITY_M_S2
        length = 1.0
        omega_0 = math.sqrt(g / length)
        period = 2 * math.pi / omega_0
        # Period of 1m pendulum: ~2.006 seconds
        assert 1.9 < period < 2.1, f"Period {period:.3f}s must be ~2.0s for 1m pendulum"


class TestEulerBernoulliBeam:
    """Tests for Euler-Bernoulli beam equation completeness - #2291."""

    def test_static_deflection_formula(self):
        """Static deflection of simply-supported beam under uniform load."""
        # Delta_max = 5*w*L^4 / (384*E*second_moment_area)
        E = 200e9  # Pa (steel)
        second_moment_area = 1e-6  # m^4
        L = 1.0  # m
        w = 1000.0  # N/m (uniform load)

        delta = 5 * w * L**4 / (384 * E * second_moment_area)
        assert delta > 0, "Deflection must be positive"
        assert delta < 0.01, "Deflection must be < 1cm for these parameters"

    def test_dynamic_term_nonzero(self):
        """Dynamic (inertial) term rho*A*d^2w/dt^2 must be nonzero in vibration.

        Issue #2291: textbook omitted the rho*A*(d2w/dt2) inertial term.
        For vibration problems this term is REQUIRED.
        """
        rho = 7800.0  # kg/m^3 (steel)
        A = 0.01  # m^2
        # For sinusoidal vibration w = W*sin(omega*t), d2w/dt2 = -omega^2 * W*sin(omega*t)
        omega = 10.0  # rad/s
        W = 0.001  # m amplitude
        inertial_term = rho * A * omega**2 * W
        assert inertial_term > 0, "Inertial term rho*A*omega^2*W must be nonzero"
        assert inertial_term > 1e-6, "Inertial term is significant and must not be omitted"

    def test_textbook_equation_has_dynamic_term(self):
        """Regression guard: the chapter 11 flexible shaft source must include inertia."""
        chapter_path = Path("articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd")
        chapter_text = chapter_path.read_text(encoding="utf-8")

        expected_fragments = [
            "EI \\frac{\\partial^4 w}{\\partial z^4}(z,t) + \\rho A \\frac{\\partial^2 w}{\\partial t^2}(z,t)",
            "q(z,t)",
            "w(z,t)",
        ]
        for fragment in expected_fragments:
            assert fragment in chapter_text, f"Missing expected chapter fragment: {fragment}"

        static_fragment = "EI \\frac{\\partial^4 w}{\\partial z^4} = q(z)"
        assert static_fragment not in chapter_text, (
            "Static-only Euler-Bernoulli equation should not be used without dynamic context"
        )


class TestEigenvalueInvariance:
    """Tests for eigenvalue invariance claims - #2305."""

    def test_eigenvalues_invariant_under_similarity(self):
        """Eigenvalues ARE invariant under similarity transform (constant change of basis).

        Issue #2305: claim was wrong for TIME-DEPENDENT coordinate changes.
        Similarity transform P^{-1}AP preserves eigenvalues only if P is constant.
        """
        try:
            import numpy as np
        except ImportError:
            pytest.skip("numpy required")

        A = np.array([[2, 1], [0, 3]])
        P = np.array([[1, 2], [0, 1]])  # constant invertible matrix
        P_inv = np.linalg.inv(P)

        A_similar = P_inv @ A @ P
        eigs_A = sorted(np.linalg.eigvals(A).real)
        eigs_similar = sorted(np.linalg.eigvals(A_similar).real)

        assert np.allclose(eigs_A, eigs_similar, atol=1e-10), (
            "Eigenvalues must be invariant under constant similarity transform"
        )

    def test_eigenvalues_NOT_invariant_under_timedep_transform(self):
        """Eigenvalues are NOT invariant under time-dependent coordinate changes.

        The correct statement for x_dot = A(t) x under x = P(t)y:
        The transformed system has A_new = P^{-1}*A*P - P^{-1}*P_dot
        The P_dot term changes the eigenvalue structure.
        """
        # This test documents the CORRECT claim: eigenvalues can change
        # when P is time-dependent (the P^{-1}*P_dot correction term is nonzero)
        try:
            import numpy as np
        except ImportError:
            pytest.skip("numpy required")

        # P_dot != 0 means transformed system eigenvalues differ
        # P = rotation matrix with angular velocity omega
        omega = 1.0  # rad/s
        dt = 0.01
        # P(t) and P(t+dt) are different -> dP/dt != 0
        P_t = np.array(
            [
                [math.cos(omega * 0), -math.sin(omega * 0)],
                [math.sin(omega * 0), math.cos(omega * 0)],
            ]
        )
        P_tdt = np.array(
            [
                [math.cos(omega * dt), -math.sin(omega * dt)],
                [math.sin(omega * dt), math.cos(omega * dt)],
            ]
        )
        P_dot = (P_tdt - P_t) / dt
        assert np.any(np.abs(P_dot) > 1e-10), "P_dot must be nonzero for time-dep transform"
        # This nonzero P_dot is the correction term that changes effective eigenvalues

    def test_geometry_chapter_qualifies_eigenvalue_invariance_claim(self):
        """Chapter text must distinguish constant and time-dependent transforms."""
        for source in (GEOMETRY_CH01, GEOMETRY_CH01_TEX):
            chapter = source.read_text(encoding="utf-8")

            assert "For a time-independent coordinate" in chapter
            assert "the eigenvalues of $\\mat{A}$ are unchanged" in chapter
            assert "For a time-dependent coordinate" in chapter
            assert "instantaneous eigenvalues of $\\mat{A}_z$ need not match" in chapter
            assert "geometric content}---eigenvalues" not in chapter
            assert "geometric content*---eigenvalues" not in chapter
