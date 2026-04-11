"""Tests for universal joint physics module (fixes #2359)."""


class TestUniversalJointPhysics:
    """Validate extracted physics functions against known values."""

    def test_zero_bend_angle_gives_unity_velocity_ratio(self):
        """At zero joint angle, velocity ratio should equal cos(0)=1."""
        from docs.content.Wrist_as_Universal_Joint.universal_joint_model.physics import (
            compute_joint_angles,
        )

        _, vr = compute_joint_angles(0.0, 0.0, 0.5)
        assert abs(vr - 1.0) < 1e-9, f"Expected VR=1 at zero bend, got {vr}"

    def test_rotation_matrix_orthogonality(self):
        """Rotation matrix must satisfy R @ R.T = I."""
        import numpy as np

        from docs.content.Wrist_as_Universal_Joint.universal_joint_model.physics import (
            wrist_euler_angles_to_rotation,
        )

        R = wrist_euler_angles_to_rotation(0.3, 0.2, 0.1)
        I_approx = R @ R.T
        assert np.allclose(I_approx, np.eye(3), atol=1e-12), "R must be orthogonal"

    def test_torque_power_conservation(self):
        """Output torque * output omega = input torque * input omega."""
        from docs.content.Wrist_as_Universal_Joint.universal_joint_model.physics import (
            compute_joint_angles,
            compute_joint_torque,
        )

        _, vr = compute_joint_angles(0.1, 0.1, 0.4)
        T_in = 10.0
        T_out = compute_joint_torque(T_in, vr)
        # Power conservation: T_in * 1 = T_out * vr
        assert abs(T_in - T_out * vr) < 1e-9
