"""Universal Joint Model package - decomposed from 1710-LOC monolith (fixes #2359).

Import from sub-modules:
- physics: kinematic and torque calculations
- visualisation: mesh and animation helpers
"""
from .physics import compute_joint_angles, compute_joint_torque, wrist_euler_angles_to_rotation
from .visualisation import build_joint_mesh, joint_animation_frames

__all__ = [
    "compute_joint_angles",
    "compute_joint_torque",
    "wrist_euler_angles_to_rotation",
    "build_joint_mesh",
    "joint_animation_frames",
]
