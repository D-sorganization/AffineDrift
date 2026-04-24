import pytest

from src.core.constants import (
    POG_BALL_COR_DRIVER,
    POG_BALL_DIAMETER_M,
    POG_BALL_MASS_KG,
    POG_DOWNSWING_DURATION_MAX_S,
    POG_DOWNSWING_DURATION_MIN_S,
    POG_DOWNSWING_DURATION_S,
    POG_DRIVER_CLUBHEAD_MASS_KG,
    POG_DRIVER_GRIP_MASS_KG,
    POG_DRIVER_SHAFT_DAMPING_NS_M,
    POG_DRIVER_SHAFT_LENGTH_M,
    POG_DRIVER_SHAFT_MASS_KG,
    POG_DRIVER_SHAFT_STIFFNESS_N_M,
    POG_I0,
    POG_I1,
    POG_I2,
    POG_L0,
    POG_L0_CM,
    POG_L1,
    POG_L1_CM,
    POG_L2,
    POG_L2_CM,
    POG_M0,
    POG_M1,
    POG_M2,
    _env_float,
    _env_int,
)
from src.tools.utils import constants


def test_imports():
    assert constants


def test_exclude_dirs():
    assert constants.EXCLUDE_DIRS
    assert ".git" in constants.EXCLUDE_DIRS_PYTHON
    assert "docs" in constants.EXCLUDE_DIRS_CONTENT


# ── PoG canonical double-pendulum parameters (Table 3.1) ────────────────────


class TestPogDoublePendulumParams:
    """Verify PoG canonical double-pendulum parameters have physically reasonable values.

    These are the source of truth for Ch02-Ch16 numerical examples (Issue #2792).
    """

    def test_l1_arm_length_reasonable(self):
        """Arm length should be 0.4-0.8 m (adult male range)."""
        assert 0.40 <= POG_L1 <= 0.80, f"POG_L1={POG_L1} outside adult arm length range"

    def test_l1_cm_less_than_l1(self):
        """CoM distance must be strictly less than total link length."""
        assert POG_L1_CM < POG_L1, "CoM must be within the segment"

    def test_l1_cm_positive(self):
        assert POG_L1_CM > 0

    def test_m1_arm_mass_reasonable(self):
        """Combined arm mass should be 2-6 kg (adults, De Leva range)."""
        assert 2.0 <= POG_M1 <= 6.0, f"POG_M1={POG_M1} outside plausible arm mass range"

    def test_i1_rotational_inertia_positive(self):
        """Rotational inertia must be positive."""
        assert POG_I1 > 0

    def test_l2_driver_length_usga_limit(self):
        """Driver shaft length must not exceed 48 in (1.219 m) USGA limit."""
        assert 0.90 <= POG_L2 <= 1.22, f"POG_L2={POG_L2} outside USGA driver length range"

    def test_l2_cm_less_than_l2(self):
        """Club CoM must be within the club length."""
        assert POG_L2_CM < POG_L2

    def test_l2_cm_positive(self):
        assert POG_L2_CM > 0

    def test_m2_driver_mass_reasonable(self):
        """Total driver mass should be 0.28-0.38 kg (typical tour range)."""
        assert 0.28 <= POG_M2 <= 0.38, f"POG_M2={POG_M2} outside expected driver mass range"

    def test_i2_rotational_inertia_positive(self):
        assert POG_I2 > 0

    def test_mass_matrix_m11(self):
        """Spot-check M_11 of the mass matrix using canonical params.

        M_11 = I1 + M1*L1_cm^2 + I2 + M2*(L1^2 + L2_cm^2 + 2*L1*L2_cm*cos(0))
        evaluated at theta_2=0 (straight configuration) to 3 decimal places.
        """
        import math

        theta2 = 0.0
        M11 = (
            POG_I1
            + POG_M1 * POG_L1_CM**2
            + POG_I2
            + POG_M2 * (POG_L1**2 + POG_L2_CM**2 + 2 * POG_L1 * POG_L2_CM * math.cos(theta2))
        )
        # Expected value computed from canonical values
        expected = 0.075 + 3.5 * 0.28**2 + 0.058 + 0.310 * (0.60**2 + 0.85**2 + 2 * 0.60 * 0.85)
        assert abs(M11 - expected) < 1e-9, f"M11 mismatch: {M11} vs {expected}"
        # Sanity range: should be O(1) kg*m^2 for a person+driver
        assert 0.5 <= M11 <= 5.0, f"M11={M11:.3f} outside plausible range"


# ── PoG canonical triple-pendulum parameters ─────────────────────────────────


class TestPogTriplePendulumParams:
    """Verify PoG canonical triple-pendulum (torso) parameters."""

    def test_l0_torso_length_reasonable(self):
        """Torso length hip-to-shoulder: 0.45-0.65 m for adult males."""
        assert 0.45 <= POG_L0 <= 0.65

    def test_l0_cm_less_than_l0(self):
        assert POG_L0_CM < POG_L0

    def test_m0_torso_mass_reasonable(self):
        """Torso mass: 25-50 kg for adult males (pelvis + trunk)."""
        assert 25.0 <= POG_M0 <= 55.0

    def test_i0_positive(self):
        assert POG_I0 > 0


# ── PoG canonical equipment parameters ───────────────────────────────────────


class TestPogEquipmentParams:
    """Verify PoG canonical equipment parameters (driver, ball)."""

    def test_driver_clubhead_mass_usga_range(self):
        """Clubhead mass should be 180-215 g (typical tour drivers)."""
        assert 0.180 <= POG_DRIVER_CLUBHEAD_MASS_KG <= 0.215

    def test_driver_shaft_mass_reasonable(self):
        """Shaft mass: 40-80 g for lightweight graphite drivers."""
        assert 0.040 <= POG_DRIVER_SHAFT_MASS_KG <= 0.080

    def test_driver_shaft_length_usga_limit(self):
        """Shaft length must not exceed USGA 48 in (1.219 m) limit."""
        assert 0.90 <= POG_DRIVER_SHAFT_LENGTH_M <= 1.22

    def test_driver_shaft_stiffness_positive(self):
        assert POG_DRIVER_SHAFT_STIFFNESS_N_M > 0

    def test_driver_shaft_damping_positive(self):
        assert POG_DRIVER_SHAFT_DAMPING_NS_M > 0

    def test_driver_grip_mass_reasonable(self):
        """Grip mass: 40-90 g for typical rubber grips."""
        assert 0.040 <= POG_DRIVER_GRIP_MASS_KG <= 0.090

    def test_ball_mass_usga_rule(self):
        """Ball mass must be <= USGA maximum of 1.620 oz = 45.93 g."""
        assert POG_BALL_MASS_KG <= 0.04593 + 1e-9
        assert POG_BALL_MASS_KG > 0.040, "Ball mass below physically plausible minimum"

    def test_ball_diameter_usga_rule(self):
        """Ball diameter must be >= USGA minimum of 1.680 in = 42.67 mm."""
        assert POG_BALL_DIAMETER_M >= 0.04267 - 1e-9
        assert POG_BALL_DIAMETER_M < 0.050, "Ball diameter unreasonably large"

    def test_ball_cor_driver_below_usga_limit(self):
        """Driver COR must not exceed USGA limit of 0.830."""
        assert POG_BALL_COR_DRIVER <= 0.830
        assert POG_BALL_COR_DRIVER >= 0.700, "COR below plausible minimum for modern drivers"

    def test_total_driver_mass_consistency(self):
        """Sum of clubhead + shaft + grip should be close to POG_M2 (total club mass)."""
        total = POG_DRIVER_CLUBHEAD_MASS_KG + POG_DRIVER_SHAFT_MASS_KG + POG_DRIVER_GRIP_MASS_KG
        # POG_M2 = 0.310 kg; component sum = 0.200 + 0.055 + 0.055 = 0.310
        assert (
            abs(total - POG_M2) < 0.005
        ), f"Component masses sum to {total:.3f} kg but POG_M2={POG_M2:.3f} kg"


# ── PoG canonical swing timing ────────────────────────────────────────────────


class TestPogSwingTiming:
    """Verify PoG canonical downswing timing parameters."""

    def test_downswing_duration_central_value(self):
        """Central downswing duration must be 250 ms (literature consensus)."""
        assert abs(POG_DOWNSWING_DURATION_S - 0.250) < 1e-9

    def test_downswing_duration_within_literature_range(self):
        """Central value must lie within [min, max] literature range."""
        assert POG_DOWNSWING_DURATION_MIN_S <= POG_DOWNSWING_DURATION_S
        assert POG_DOWNSWING_DURATION_S <= POG_DOWNSWING_DURATION_MAX_S

    def test_downswing_duration_min_reasonable(self):
        """Minimum downswing duration: 150 ms is an absolute lower bound."""
        assert POG_DOWNSWING_DURATION_MIN_S >= 0.150

    def test_downswing_duration_max_reasonable(self):
        """Maximum downswing duration: 500 ms is an absolute upper bound."""
        assert POG_DOWNSWING_DURATION_MAX_S <= 0.500

    def test_downswing_duration_range_ordered(self):
        """Min must be strictly less than max."""
        assert POG_DOWNSWING_DURATION_MIN_S < POG_DOWNSWING_DURATION_MAX_S


# ── Core constants env-var helpers ──────────────────────────────────────────


@pytest.mark.parametrize(
    ("env_var", "env_val", "default", "expected"),
    [
        ("__NONEXISTENT_AD_VAR__", None, 3.14, 3.14),
        ("__TEST_AD_FLOAT__", "2.5", 0.0, 2.5),
        ("__TEST_AD_BAD__", "not-a-number", 7.7, 7.7),
    ],
    ids=["unset-default", "valid-value", "bad-value-fallback"],
)
def test_env_float(monkeypatch, env_var, env_val, default, expected):
    """_env_float handles missing, valid, and invalid environment values."""
    if env_val is not None:
        monkeypatch.setenv(env_var, env_val)
    else:
        monkeypatch.delenv(env_var, raising=False)
    assert _env_float(env_var, default) == expected


@pytest.mark.parametrize(
    ("env_var", "env_val", "default", "expected"),
    [
        ("__NONEXISTENT_AD_INT__", None, 42, 42),
        ("__TEST_AD_INT__", "99", 0, 99),
        ("__TEST_AD_INT_BAD__", "xyz", 10, 10),
    ],
    ids=["unset-default", "valid-value", "bad-value-fallback"],
)
def test_env_int(monkeypatch, env_var, env_val, default, expected):
    """_env_int handles missing, valid, and invalid environment values."""
    if env_val is not None:
        monkeypatch.setenv(env_var, env_val)
    else:
        monkeypatch.delenv(env_var, raising=False)
    assert _env_int(env_var, default) == expected
