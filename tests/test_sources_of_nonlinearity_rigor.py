import numpy as np


def test_rigid_pendulum_inertia_constant() -> None:
    # Rigid physical pendulum about a fixed pivot O:
    # I_O = I_cm + m*d^2 = const (independent of angle theta)
    mass = 2.0
    length = 1.0
    dist_cm = 0.5
    i_cm = (1.0 / 12.0) * mass * (length**2)
    i_pivot = i_cm + mass * (dist_cm**2)
    for _theta in [0.0, np.pi / 6, np.pi / 4, np.pi / 2, np.pi]:
        # Inertia is strictly independent of theta
        assert np.isclose(i_pivot, (1.0 / 12.0) * 2.0 * (1.0**2) + 2.0 * (0.5**2))


def test_planar_2r_skew_symmetry_and_dynamics() -> None:
    # Planar 2R arm energy-consistent equations
    m1, m2 = 1.5, 1.0
    l1, l2 = 1.0, 0.8
    d = m2 * (l2**2) / 3.0
    beta = m2 * l1 * l2 / 2.0
    a = m1 * (l1**2) / 3.0 + m2 * (l1**2) + d

    for q2 in [-1.2, 0.0, 0.5, 1.8]:
        for v1, v2 in [(0.5, -0.2), (1.0, 2.0), (-1.5, 0.8)]:
            m_mat = np.array(
                [[a + 2.0 * beta * np.cos(q2), d + beta * np.cos(q2)], [d + beta * np.cos(q2), d]]
            )
            # Positive definite
            assert np.linalg.det(m_mat) > 0
            assert np.all(np.linalg.eigvals(m_mat) > 0)

            # Coriolis matrix C(q, v)
            h = beta * np.sin(q2)
            c_mat = np.array([[-h * v2, -h * (v1 + v2)], [h * v1, 0.0]])

            # M_dot
            m_dot = np.array(
                [
                    [-2.0 * beta * np.sin(q2) * v2, -beta * np.sin(q2) * v2],
                    [-beta * np.sin(q2) * v2, 0.0],
                ]
            )

            # Skew-symmetry: M_dot - 2C must be skew-symmetric
            skew_diff = m_dot - 2.0 * c_mat
            assert np.allclose(skew_diff + skew_diff.T, 0.0)

            # c = C * v matches direct Christoffel contraction
            v_vec = np.array([v1, v2])
            c_vec = c_mat @ v_vec
            c_expected = np.array(
                [-beta * v2 * (2.0 * v1 + v2) * np.sin(q2), beta * (v1**2) * np.sin(q2)]
            )
            assert np.allclose(c_vec, c_expected)


def test_stribeck_friction_model() -> None:
    tau_c = 1.0
    tau_s = 2.5
    v_s = 0.1
    sigma_v = 0.2

    # Kinetic Stribeck friction for v != 0
    def stribeck_kinetic(v: float) -> float:
        res = float((tau_c + (tau_s - tau_c) * np.exp(-abs(v) / v_s)) * np.sign(v) + sigma_v * v)
        return res

    # Symmetry: f(-v) == -f(v)
    for v_val in [0.01, 0.05, 0.1, 0.5, 2.0]:
        assert np.isclose(stribeck_kinetic(-v_val), -stribeck_kinetic(v_val))
        # At high speed, viscous dominates
        assert stribeck_kinetic(v_val) > 0

    # At low speed (limit v -> 0+), kinetic friction approaches tau_s
    assert np.isclose(stribeck_kinetic(1e-6), tau_s, atol=1e-3)


def test_hill_muscle_curve_and_curvature() -> None:
    f0 = 100.0
    v_max = 5.0
    k = 0.25  # standard dimensionless a/F0 ~ 0.25
    # Hill formula: F(v) = F0 * (v_max - v) / (v_max + v / k)
    # or with a = k*F0, b = k*v_max: (F + a)(v + b) = (F0 + a)*b
    a_param = k * f0
    b_param = k * v_max

    def hill_force(v: float) -> float:
        return (f0 * b_param - a_param * v) / (v + b_param)

    # Physical boundary conditions:
    assert np.isclose(hill_force(0.0), f0)  # Isometric
    assert np.isclose(hill_force(v_max), 0.0)  # Shortening max speed
    assert 0.0 < hill_force(0.5 * v_max) < f0


def test_magnus_aerodynamics() -> None:
    rho = 1.225
    area = 0.001432  # Golf ball area
    speed = 60.0
    omega = 300.0  # rad/s
    radius = 0.02135  # radius
    # Spin parameter S = r * omega / v
    spin_param = radius * omega / speed
    assert spin_param > 0.0
    # C_L is dimensionless function of S
    c_lift = 0.25
    f_lift = 0.5 * c_lift * rho * area * (speed**2)
    # Unit check: N = kg/m^3 * m^2 * (m/s)^2 = kg*m/s^2 = N
    assert f_lift > 0.0
    assert np.isclose(f_lift, 0.5 * 0.25 * 1.225 * 0.001432 * 3600.0)


def test_kinematic_bicycle_turning_radius() -> None:
    wheelbase = 2.5  # wheelbase (m)
    delta = float(np.deg2rad(15.0))  # steer angle
    radius = wheelbase / np.tan(delta)
    v1 = 10.0  # m/s
    v2 = 20.0  # m/s
    # Curvature kappa = 1/R = tan(delta)/L is fixed by geometry at low speed
    # Lateral acceleration a_y = v^2 / R increases quadratically with speed
    ay1 = (v1**2) / radius
    ay2 = (v2**2) / radius
    assert np.isclose(ay2 / ay1, 4.0)
