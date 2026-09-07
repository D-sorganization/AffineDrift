"""Small, explicitly idealized rigid-body examples for the Physics textbook."""

from dataclasses import dataclass
from xml.etree.ElementTree import Element, SubElement, indent, tostring

import numpy as np
from numpy.typing import NDArray

type Array = NDArray[np.float64]
STANDARD_GRAVITY = 9.81  # Example value, in metres per second squared.


def _configuration(q: Array) -> Array:
    """Require two finite relative joint angles, measured in radians."""
    values = np.asarray(q, dtype=float)
    if values.shape != (2,) or not np.isfinite(values).all():
        raise ValueError("configuration must contain two finite joint angles")
    return values


@dataclass(frozen=True)
class TwoLinkArm:
    """Two uniform cylinders along local x, rotating about parallel z axes.

    Positive SI dimensions define a teaching mechanism, not measured anatomy.
    The first joint is fixed in space; each angle is relative to its parent.
    """

    lengths: tuple[float, float] = (0.3, 0.25)
    masses: tuple[float, float] = (2.0, 1.0)
    radius: float = 0.02

    def __post_init__(self) -> None:
        """Reject nonphysical or dimensionally incompatible segment inputs."""
        for values in (self.lengths, self.masses):
            array = np.asarray(values)
            if array.shape != (2,) or not np.isfinite(array).all() or np.any(array <= 0):
                raise ValueError("lengths and masses must each contain two positive finite values")
        if not np.isfinite(self.radius) or self.radius <= 0:
            raise ValueError("radius must be positive and finite")

    def centroidal_inertias(self) -> Array:
        """Return principal moments [Ixx, Iyy, Izz] about each cylinder's COM."""
        mass = np.asarray(self.masses)
        length = np.asarray(self.lengths)
        longitudinal = mass * self.radius**2 / 2
        transverse = mass * (3 * self.radius**2 + length**2) / 12
        return np.column_stack((longitudinal, transverse, transverse))

    def mass_matrix(self, q: Array) -> Array:
        """Compute the two-revolute generalized inertia in kg m^2."""
        angle = _configuration(q)
        length1, length2 = self.lengths
        mass1, mass2 = self.masses
        inertia1, inertia2 = self.centroidal_inertias()[:, 2]
        coupling = mass2 * length1 * length2 / 2 * np.cos(angle[1])
        diagonal2 = inertia2 + mass2 * (length2 / 2) ** 2
        diagonal1 = inertia1 + mass1 * (length1 / 2) ** 2
        diagonal1 += diagonal2 + mass2 * length1**2 + 2 * coupling
        return np.array([[diagonal1, diagonal2 + coupling], [diagonal2 + coupling, diagonal2]])

    def potential(self, q: Array) -> float:
        """Gravitational potential for downward global y, zero at q=(0,0)."""
        angle = _configuration(q)
        length1, length2 = self.lengths
        mass1, mass2 = self.masses
        height1 = length1 / 2 * np.sin(angle[0])
        height2 = length1 * np.sin(angle[0]) + length2 / 2 * np.sin(sum(angle))
        return float(STANDARD_GRAVITY * (mass1 * height1 + mass2 * height2))

    def gravity(self, q: Array) -> Array:
        """Return dV/dq on the left side of M qddot + h = tau."""
        angle = _configuration(q)
        length1, length2 = self.lengths
        mass1, mass2 = self.masses
        distal = mass2 * length2 / 2 * np.cos(sum(angle))
        proximal = (mass1 * length1 / 2 + mass2 * length1) * np.cos(angle[0])
        return STANDARD_GRAVITY * np.array([proximal + distal, distal])

    def urdf(self) -> str:
        """Generate a complete URDF tree with explicit COM inertias and geometry.

        Importers determine whether the root is fixed or floating. The chapter
        verifies MuJoCo 3.4.0's fixed-root interpretation, separately from XML.
        Continuous joints avoid implying physiological limits or torque limits.
        """
        robot = Element("robot", name="teaching_arm")
        SubElement(robot, "link", name="base")
        for index in range(2):
            self._add_link(robot, index)
            joint = SubElement(robot, "joint", name=f"joint{index + 1}", type="continuous")
            SubElement(joint, "parent", link="base" if index == 0 else "link1")
            SubElement(joint, "child", link=f"link{index + 1}")
            offset = 0.0 if index == 0 else self.lengths[0]
            SubElement(joint, "origin", xyz=f"{offset:.12g} 0 0", rpy="0 0 0")
            SubElement(joint, "axis", xyz="0 0 1")
        indent(robot, space="  ")
        return tostring(robot, encoding="unicode") + "\n"

    def _add_link(self, robot: Element, index: int) -> None:
        """Attach one physical cylinder and its correctly oriented inertia."""
        link = SubElement(robot, "link", name=f"link{index + 1}")
        length = self.lengths[index]
        centroid = f"{length / 2:.12g} 0 0"
        inertial = SubElement(link, "inertial")
        SubElement(inertial, "origin", xyz=centroid, rpy="0 0 0")
        SubElement(inertial, "mass", value=f"{self.masses[index]:.12g}")
        moments = self.centroidal_inertias()[index]
        attributes = {
            key: f"{value:.12g}" for key, value in zip(("ixx", "iyy", "izz"), moments, strict=True)
        }
        SubElement(inertial, "inertia", attributes, ixy="0", ixz="0", iyz="0")
        for tag in ("visual", "collision"):
            shape = SubElement(link, tag)
            SubElement(shape, "origin", xyz=centroid, rpy=f"0 {np.pi / 2:.12g} 0")
            geometry = SubElement(shape, "geometry")
            SubElement(geometry, "cylinder", radius=f"{self.radius:.12g}", length=f"{length:.12g}")


def dynamic_inverse(mass: Array, jacobian: Array) -> Array:
    """Return M^-1 J^T (J M^-1 J^T)^-1 for SPD M and full-row-rank J.

    Inputs must use consistent coordinates, units and task scaling. This
    teaching calculation rejects rank loss; it does not regularize a task.
    """
    mass = np.asarray(mass, dtype=float)
    jacobian = np.asarray(jacobian, dtype=float)
    if mass.ndim != 2 or mass.shape[0] != mass.shape[1] or mass.shape[0] == 0:
        raise ValueError("mass must be a nonempty square matrix")
    if jacobian.ndim != 2 or jacobian.shape[1] != mass.shape[0] or jacobian.shape[0] == 0:
        raise ValueError("task Jacobian has incompatible dimensions")
    if not np.isfinite(mass).all() or not np.isfinite(jacobian).all():
        raise ValueError("matrices must be finite")
    if not np.allclose(mass, mass.T) or np.linalg.eigvalsh(mass).min() <= 0:
        raise ValueError("mass must be symmetric positive definite")
    if np.linalg.matrix_rank(jacobian) != jacobian.shape[0]:
        raise ValueError("task Jacobian must have full row rank")
    weighted = np.linalg.solve(mass, jacobian.T)
    return np.linalg.solve(jacobian @ weighted, weighted.T).T
