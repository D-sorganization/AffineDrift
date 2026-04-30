# Mathematical Notation Reference — AffineDrift

This document serves as the authoritative reference for all mathematical notation used across AffineDrift textbooks, articles, and research content. It resolves symbol ambiguities and explicitly declares sign conventions.

**Status:** Phase 1 — Core symbol reference and sign conventions  
**Last Updated:** 2026-04-30  
**Scope:** Physics of Golf (Ch 1-31), Geometry of Motion (Vol 0-1), all articles

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Lie Groups & Algebras (SO(3), so(3))](#lie-groups--algebras)
3. [Quaternions](#quaternions)
4. [Euler Angles](#euler-angles)
5. [Twists & Screws](#twists--screws)
6. [Coordinate Frames](#coordinate-frames)
7. [Sign Conventions](#sign-conventions)
8. [Symbol Overloading Matrix](#symbol-overloading-matrix)
9. [Parameters & Physical Quantities](#parameters--physical-quantities)

---

## Quick Reference

| Symbol | Meaning | Type | Context | First Use |
|--------|---------|------|---------|-----------|
| **R** | Rotation matrix | Matrix (3×3) | SO(3), rigid body rotation | Physics of Golf Ch 1 |
| **ω** | Angular velocity | Vector (3D) | so(3), body-fixed rate | Physics of Golf Ch 2 |
| **q** | Quaternion | Vector (4D) | Unit quaternion (Hamilton) | Geometry of Motion Vol 0 |
| **θ** | Rotation angle | Scalar | Axis-angle representation | Physics of Golf Ch 3 |
| **v** | Linear velocity | Vector (3D) | Cartesian space | Physics of Golf Ch 1 |
| **M** | Mass | Scalar | kg | Physics of Golf Ch 4 |
| **I** | Moment of inertia | Matrix (3×3) | kg⋅m² | Physics of Golf Ch 4 |
| **F** | Force | Vector (3D) | Newtons (N) | Physics of Golf Ch 1 |
| **τ** | Torque | Vector (3D) | Newton-meters (N⋅m) | Physics of Golf Ch 2 |
| **g** | Gravitational acceleration | Vector (3D) | m/s² (typically [0,0,-9.81]) | Physics of Golf Ch 5 |
| **V** | Adjoint matrix / Twist | Matrix (6×6) / Vector (6D) | Lies, screw motion | Geometry of Motion Vol 1 |
| **J** | Jacobian | Matrix | Linearization of kinematics | Geometry of Motion Vol 1 |

---

## Lie Groups & Algebras

### SO(3): Special Orthogonal Group (3D Rotations)

**Definition:** SO(3) is the group of 3×3 orthogonal matrices with determinant +1.

```
R ∈ SO(3) ⟺ R^T R = I, det(R) = +1
```

**Representation:** Rotation matrices representing orientation in 3D space

**Key Property:** R^{-1} = R^T (inverse = transpose)

**Symbol usage across content:**
- **R** — Standard rotation matrix notation (Physics of Golf, Geometry of Motion)
- **C** — Alternative notation in some aerodynamics literature (use R for consistency)

**Examples:**
- Rotation from world frame to body frame: R_wb
- Rotation from body frame to world frame: R_bw (= R_wb^T)

---

### so(3): Skew-Symmetric Lie Algebra (Angular Velocities)

**Definition:** so(3) is the vector space of 3×3 skew-symmetric matrices.

```
[ω]_× = [  0   -ω_z   ω_y ]
        [ ω_z   0   -ω_x ]
        [-ω_y  ω_x   0  ]
```

**Representation:** Angular velocity vectors ω ∈ ℝ³

**Relationship to SO(3):**
```
dR/dt = [ω]_× R    (body-fixed rate)
dR/dt = R [ω]_×    (world-fixed rate)
```

**Symbol usage:**
- **ω** — Angular velocity vector (standard across all content)
- **[ω]_×** — Skew-symmetric matrix form of ω

**NOTE:** In Physics of Golf, we consistently use **body-fixed rates** (left multiplication):
```
dR/dt = [ω]_× R
```

---

## Quaternions

### Hamilton Convention (Standard in AffineDrift)

**Definition:** Unit quaternion q = [q_x, q_y, q_z, q_w] = [q_v, q_w] where:
- q_v = [q_x, q_y, q_z] (vector part)
- q_w (scalar part, w = w for "scalar" or s for "scalar" component)
- ||q|| = 1 (unit quaternion constraint)

**⚠️ CRITICAL: Hamilton Convention Declaration**

AffineDrift uses the **Hamilton convention** (scalar last):
```
q = [x, y, z, w]  where w is the scalar component
```

**NOT** the JPL (Jet Propulsion Laboratory) convention:
```
q_JPL = [w, x, y, z]  (w first — NOT used here)
```

**Reason for Declaration:** Quaternion conventions are common sources of sign errors. This explicit declaration prevents bugs in rotation compositions.

### Quaternion-to-Rotation Matrix

From quaternion q = [q_x, q_y, q_z, q_w] to rotation matrix R:

```
R = [1-2(q_y²+q_z²)    2(q_x q_y-q_z q_w)    2(q_x q_z+q_y q_w) ]
    [2(q_x q_y+q_z q_w)  1-2(q_x²+q_z²)    2(q_y q_z-q_x q_w) ]
    [2(q_x q_z-q_y q_w)  2(q_y q_z+q_x q_w)  1-2(q_x²+q_y²)   ]
```

**Symbol usage:**
- **q** — Quaternion (typically q = [q_x, q_y, q_z, q_w] = [q_v, q_w])
- **q̄** — Quaternion conjugate (q̄ = [-q_x, -q_y, -q_z, q_w] = [-q_v, q_w])
- **q^{-1}** — Quaternion inverse (for unit quaternions: q^{-1} = q̄)
- **q₁ * q₂** — Quaternion multiplication (composition of rotations)

---

## Euler Angles

### Intrinsic vs. Extrinsic Rotations

**Intrinsic (ZYX - Yaw-Pitch-Roll):** Rotations about moving axes  
**Extrinsic (XYZ):** Rotations about fixed axes

**AffineDrift Standard: Intrinsic ZYX (Yaw-Pitch-Roll)**

```
R = R_z(yaw) R_y(pitch) R_x(roll)   [Intrinsic ZYX order]
  = R_x(roll) R_y(pitch) R_z(yaw)   [Extrinsic XYZ order — mathematically equivalent]
```

**Symbol usage:**
- **ψ (psi)** — Yaw (rotation about z-axis)
- **θ (theta)** — Pitch (rotation about y-axis)
- **φ (phi)** — Roll (rotation about x-axis)

**Angles array:** [ψ, θ, φ] or [yaw, pitch, roll]

**⚠️ Gimbal lock occurs when θ = ±90°**

---

## Twists & Screws

### Twist (Infinitesimal Screw Motion)

A twist V ∈ se(3) represents an infinitesimal rigid motion (rotation + translation).

**6D vector representation:**
```
V = [ω; v] = [ω_x, ω_y, ω_z, v_x, v_y, v_z]^T
  = [angular velocity; linear velocity]
```

**Matrix form (4×4 homogeneous):**
```
[V]_× = [  [ω]_×   v  ]
        [   0      0  ]
```

**Symbol usage:**
- **V** — Twist (6D vector or 4×4 matrix form)
- **ω** — Angular velocity component (3D)
- **v** — Linear velocity component (3D)
- **[V]_×** — Skew-symmetric matrix form

**Key relationship:**
```
dT/dt = [V]_× T    (body-fixed twist)
dT/dt = T [V]_×    (world-fixed twist)
```

### Screw Axis

A screw axis is a normalized twist representing a line and rotation direction in space.

**Symbol usage:**
- **S** — Screw axis (unit twist, ||S|| = 1)
- **θ** — Screw parameter (angle of rotation about the axis)

---

## Coordinate Frames

### Frame Notation

**Subscript notation for transformations:**
```
R_ab  = Rotation from frame b to frame a
p_a   = Position of point p expressed in frame a
T_ab  = Homogeneous transformation (4×4) from frame b to frame a
```

**Common frames in Physics of Golf:**
- **W** — World frame (fixed, typically ground)
- **B** — Body frame (clubhead-fixed or golf ball-fixed)
- **C** — Club frame (specific to club geometry)
- **G** — Grip frame (at club handle)

**Example (Golf ball rotations):**
```
R_wb = Rotation from ball body frame to world frame
ω_b  = Angular velocity of ball, expressed in body frame
p_w  = Position expressed in world frame
```

---

## Sign Conventions

### Cross Product Sign Convention

**Right-hand rule:** Standard right-hand rule applies throughout.

```
a × b = [a_y b_z - a_z b_y, a_z b_x - a_x b_z, a_x b_y - a_y b_x]^T
```

**Skew-symmetric representation:**
```
[a]_× b = a × b
```

---

### Drag-Curve Ratio (DCR) Sign Convention

**Definition:** DCR measures the curve magnitude relative to drag magnitude.

```
DCR = curve_magnitude / drag_magnitude
```

**Sign convention:**
- **Positive DCR** — Draw (leftward curve for right-handed golfer)
- **Negative DCR** — Fade (rightward curve for right-handed golfer)
- **DCR = 0** — Straight shot (no curve)

**Physical basis:** Based on Magnus effect direction relative to drag force.

---

### Angular Momentum Sign Convention

**Definition:**
```
L = I ω    (angular momentum = inertia tensor × angular velocity)
```

**Sign follows ω:** If ω points up (right-hand rule), L points up.

---

## Symbol Overloading Matrix

Some symbols have multiple meanings depending on context. This matrix disambiguates:

| Symbol | Meaning 1 | Meaning 2 | Meaning 3 | Context Selection |
|--------|-----------|-----------|-----------|------------------|
| **F** | Force (vector) | Frame (reference frame) | Frequency (scalar) | Usually context-clear; disambiguate if ambiguous |
| **R** | Rotation matrix | Real numbers ℝ | Radius (scalar) | SO(3) context = rotation; uppercase ℝ = reals |
| **S** | Screw axis | Spin axis (golf ball) | Spatial frame | Usually clear from context (twists vs. aerodynamics) |
| **T** | Transformation matrix | Time interval | Torque (alternate) | Matrix notation clarifies; use τ for torque |
| **ω** | Angular velocity | Angular frequency | — | Typically angular velocity in this context |
| **V** | Twist (screw) | Velocity (linear) | Volume | Twist context = 6D; velocity = 3D; volume = scalar |

**Recommendation:** When ambiguous, use explicit notation:
- **F_ext** for external force
- **F_ref** for reference frame
- **f_impact** for impact frequency (lowercase for scalar quantities)

---

## Parameters & Physical Quantities

### Standard Symbols for Golf Physics

| Parameter | Symbol | Unit | Definition | Chapter(s) |
|-----------|--------|------|-----------|-----------|
| Club mass | M_c | kg | Total club head mass | Ch 4 |
| Ball mass | M_b | kg | Golf ball mass (standard = 0.04593 kg) | Ch 4 |
| Club length | L_c | m | Effective club length | Ch 6 |
| Impact time | Δt | s | Duration of club-ball contact (≈0.0005 s) | Ch 7 |
| Coefficient of restitution | e | (dimensionless) | Bounce coefficient (0 < e < 1) | Ch 8 |
| Spin rate | Ω | RPM or rad/s | Ball rotational rate | Ch 9 |
| Carry distance | d_c | m | Horizontal distance in air | Ch 12 |
| Ball velocity | v_b | m/s | Speed after impact | Ch 7 |
| Launch angle | α | degrees | Initial elevation angle | Ch 10 |
| Spin axis angle | β | degrees | Tilt of spin axis from vertical | Ch 9 |

**⚠️ Unit consistency:** Always specify units when introducing parameters.

---

## Cross-References to Content

### Physics of Golf
- **Chapter 1:** Vectors, matrices, coordinate systems
- **Chapter 2:** SO(3) and angular velocity
- **Chapter 3:** Quaternions (Hamilton convention)
- **Chapter 4:** Rigid body dynamics (inertia tensors, I)
- **Chapter 5:** Gravity and forces
- **Chapters 9-10:** Golf ball aerodynamics and spin (DCR sign)

### Geometry of Motion
- **Vol 0:** SO(3), so(3), Lie groups and algebras
- **Vol 1:** Twists, screws, and adjoint representations
- **Vol 2:** Control theory and optimization

### Key Articles
- **Shaft BC Theory:** Uses quaternions for shaft bending
- **Control Theory:** Twists and Jacobians for trajectory planning
- **Aerodynamics:** DCR, Magnus effect (sign convention critical)

---

## Validation Checklist

Use this checklist when writing new content:

- [ ] Quaternion convention declared (Hamilton, scalar last)
- [ ] Euler angle order declared (intrinsic ZYX)
- [ ] Frame notation consistent (R_ab, p_a)
- [ ] Sign conventions explicit (cross product, DCR, angular momentum)
- [ ] Units specified for all physical quantities
- [ ] Ambiguous symbols disambiguated on first use
- [ ] References to this notation guide provided
- [ ] Mathematical symbols consistent with rest of document

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-04-30 | 1.0 | Initial notation reference | Claude Haiku 4.5 |

---

## Future Sections (Phase 2)

- [ ] Complete symbol reference (all Ch 1-31, Vol 0-1)
- [ ] Adjoint operator notation (Ad, ad)
- [ ] Numerical examples validating each convention
- [ ] Glossary entries linking to notation.md
- [ ] References from all chapter preambles
