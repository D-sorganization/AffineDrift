# Mathematical Notation Reference

**Unified notation conventions for AffineDrift documentation**

This document serves as the authoritative reference for all mathematical symbols, notation conventions, and sign conventions used across Physics of Golf, Geometry of Motion, and all articles.

---

## Table of Contents

1. [Canonical Control-Affine Terminology](#canonical-control-affine-terminology)
2. [Coordinate Systems & Rotation](#coordinate-systems--rotation)
3. [Group Theory Notation](#group-theory-notation)
4. [Vectors & Tensors](#vectors--tensors)
5. [Physical Quantities](#physical-quantities)
6. [Sign Conventions](#sign-conventions)
7. [Symbol Overloading Reference](#symbol-overloading-reference)
8. [Component Notation](#component-notation)

---

## Canonical Control-Affine Terminology

These definitions govern the site, textbooks, and terminology gate. A local
model may use a reduced inventory only when it states the omitted terms. A
counterfactual label never identifies muscle activation, biological effort, or
intent by itself.

<!-- TERMINOLOGY-CONTRACT:START -->

| Acronym  | Canonical Expansion          | First-Use Qualifiers                           |
| -------- | ---------------------------- | ---------------------------------------------- |
| **ZTCF** | Zero-Torque Counterfactual   | pointwise, stitched, forward, branched, family |
| **ZVCF** | Zero-Velocity Counterfactual | instantaneous                                  |
| **DCR**  | Drift-Control Ratio          | ratio                                          |
| **DgCR** | Drag-Curve Ratio             | ratio                                          |

<!-- TERMINOLOGY-CONTRACT:END -->

### Drift and Control

For a declared control-affine effective plant,

$$
\dot{x}=f_p(x)+G_p(x)u,
$$

$p$ collects declared model parameters, contact mode, prescribed motion, and
any frozen impedance or strategy variables. The **drift** $f_p$ is the complete
autonomous evolution of that declared plant when the declared control $u$ is
zero. It therefore includes every retained state-dependent term: inertia,
gravity, Coriolis and centrifugal effects, passive elasticity and damping,
shaft dynamics, and compatible constraint or contact reactions. A rigid,
frictionless gravity-plus-Coriolis drift is a special model, not the general
definition.

The **control** $u$ is the input channel explicitly removed by the
counterfactual. If activation changes impedance, then the analyst must either
model that change as control or declare the impedance frozen in $p$; it must not
silently move between drift and control. Exogenous disturbances that are not
zeroed belong in a separately declared disturbance channel rather than being
called control.

### ZTCF Construction Family

The **Zero-Torque Counterfactual (ZTCF) family** sets the declared applied
generalized-control channel to zero while preserving the declared effective
plant. The family has four distinct constructions:

1. A **pointwise ZTCF sample** evaluates $f_p(x(t))$ at one achieved state.
2. A **stitched pointwise ZTCF trace** collects pointwise samples along achieved
   states; it is not a dynamically integrated trajectory.
3. A **forward ZTCF trajectory** integrates $\dot{x}=f_p(x)$ from one declared
   initial state.
4. A **branched ZTCF trajectory** is a forward trajectory initialized at an
   achieved state and compared with the achieved future.

The construction must be qualified on first use. ZTCF does not mean “no
muscle,” “no EMG,” or “flaccid body.” It means zero value in the declared
applied-control channel under the stated frozen-plant assumptions.

### Instantaneous ZVCF

For second-order dynamics

$$
M(q)\ddot q+h(q,\dot q,z;p)=B(q)u,
$$

the **instantaneous Zero-Velocity Counterfactual (ZVCF) acceleration** is

$$
a_{\mathrm{ZVCF}}(q,z;p)
=-M(q)^{-1}h(q,0,z_0;p),
\qquad u=0.
$$

All generalized velocities and declared velocity-like internal states are
zeroed; configuration, contact mode, non-velocity internal state, and frozen
parameters are held fixed. The ZVCF is an instantaneous acceleration, not a
state or a releasable trajectory. It includes retained configuration-dependent
autonomous loads and excludes both velocity-dependent terms and the direct
control contribution. A generalized-force image may be reported as a **ZVCF
generalized-force representation**, but that representation is not the ZVCF
itself.

### DCR and DgCR

The **Drift-Control Ratio (DCR)** compares drift acceleration with the maximum
available control acceleration in the same declared space:

$$
\operatorname{DCR}_{W,\mathcal U}(x)
=\frac{\lVert W a_d(x)\rVert_2}
{\sup_{u\in\mathcal U(x)}\lVert W B_a(x)u\rVert_2+\varepsilon}.
$$

$a_d$ and $B_a u$ are the drift and control blocks in one acceleration or
task-projected space; $W$ supplies the declared scaling or metric;
$\mathcal U(x)$ is the admissible control set; and $\varepsilon$ is a reported
regularizer. A full-state norm that mixes position and velocity units is not a
DCR. A ratio using the realized input rather than bounded authority must be
called a **realized drift-to-input ratio**, not DCR.

The aerodynamic **Drag-Curve Ratio (DgCR)** remains
$(1-\mathrm{COR})/(1+\mathrm{COR})$ and must never use the bare DCR acronym.

---

## Coordinate Systems & Rotation

### SO(3) vs so(3)

| Notation   | Meaning                              | Context                                          | Example                                                                                                                       |
| ---------- | ------------------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| **SO(3)**  | Special Orthogonal Group (Lie Group) | Rotation matrices, group elements                | $R \in SO(3)$                                                                                                                 |
| **so(3)**  | Lie algebra of SO(3)                 | Skew-symmetric matrices, infinitesimal rotations | $[\omega]_\times \in so(3)$                                                                                                   |
| **R**      | Rotation matrix                      | 3×3 orthogonal matrix                            | $\mathbf{R} = \begin{pmatrix} r_{11} & r_{12} & r_{13} \\ r_{21} & r_{22} & r_{23} \\ r_{31} & r_{32} & r_{33} \end{pmatrix}$ |
| **[·]\_×** | Skew-symmetric matrix operator       | Cross-product matrix form                        | $[\mathbf{v}]_\times = \begin{pmatrix} 0 & -v_3 & v_2 \\ v_3 & 0 & -v_1 \\ -v_2 & v_1 & 0 \end{pmatrix}$                      |

### Quaternions

| Notation             | Meaning               | Convention                    |
| -------------------- | --------------------- | ----------------------------- | --- | ------- | -------------------------- | --------------------- |
| **q**                | Unit quaternion       | Hamilton convention (default) |
| **q = (w, x, y, z)** | Quaternion components | Scalar-first format           |
| \*\*                 |                       | q                             |     | = 1\*\* | Unit quaternion constraint | Normalized quaternion |
| **q^{-1} = q^\***    | Quaternion inverse    | Conjugate of unit quaternion  |

**Hamilton vs JPL Conventions:**

- **Hamilton (default):** q = (w, x, y, z), quaternion multiplication q₁q₂
- **JPL (aerospace):** q = (x, y, z, w), quaternion multiplication q₁ ⊗ q₂
- **Current project:** Hamilton convention throughout unless otherwise noted

### Euler Angles

| Notation        | Meaning                     | Convention                     |
| --------------- | --------------------------- | ------------------------------ |
| **φ (phi)**     | Roll angle                  | Rotation about X-axis (first)  |
| **θ (theta)**   | Pitch angle                 | Rotation about Y-axis (second) |
| **ψ (psi)**     | Yaw angle                   | Rotation about Z-axis (third)  |
| **Intrinsic**   | Rotations about moving axes | Default for body-fixed frames  |
| **Extrinsic**   | Rotations about fixed axes  | For inertial frame rotations   |
| **Z-Y-X order** | Rotation sequence           | Most common in golf mechanics  |

**Order Convention:** Z-Y-X (Yaw-Pitch-Roll)

- Applied in extrinsic (fixed-frame) order
- Equivalent to intrinsic X-Y-Z on moving frame
- $R(\psi, \theta, \phi) = R_Z(\psi) R_Y(\theta) R_X(\phi)$

---

## Group Theory Notation

### Adjoint Representations

| Notation  | Meaning                              | Definition                                 |
| --------- | ------------------------------------ | ------------------------------------------ |
| **Ad**    | Adjoint map                          | $\text{Ad}_g(v) = g v g^{-1}$              |
| **ad**    | Adjoint representation (Lie algebra) | $\text{ad}_v(u) = [v, u]$                  |
| **[·,·]** | Lie bracket                          | Commutator for matrices: $[A,B] = AB - BA$ |

### Screw/Twist Notation

| Notation   | Meaning             | Type       | Components                                                                  |
| ---------- | ------------------- | ---------- | --------------------------------------------------------------------------- |
| **ξ**      | Screw/twist element | 6-D vector | $\xi = (\omega_x, \omega_y, \omega_z, v_x, v_y, v_z)^T$                     |
| **[ξ]\_×** | Screw matrix form   | 4×4 matrix | $[\xi]_\times = \begin{pmatrix} [\omega]_\times & v \\ 0 & 0 \end{pmatrix}$ |
| **V**      | Spatial velocity    | 6-D twist  | Linear + angular velocity                                                   |
| **F**      | Spatial force       | 6-D wrench | Torque + linear force                                                       |

---

## Vectors & Tensors

### Vector Notation

| Notation              | Meaning              | Example                                                                               |
| --------------------- | -------------------- | ------------------------------------------------------------------------------------- | -------------- | ----------------------------------------------- |
| **v** or **v̄**        | Vector (bold or bar) | Velocity: $\mathbf{v}$ or $\bar{v}$                                                   |
| **v_i** or **[v]\_i** | Component notation   | $v_1, v_2, v_3$ for (x, y, z)                                                         |
| \*\*\\                | v\\                  | \*\*                                                                                  | Magnitude/norm | $\|\mathbf{v}\| = \sqrt{v_1^2 + v_2^2 + v_3^2}$ |
| **v^T** or **v^†**    | Transpose/conjugate  | Row vector form                                                                       |
| **u · v**             | Dot product          | $u_1v_1 + u_2v_2 + u_3v_3$                                                            |
| **u × v**             | Cross product        | $\begin{pmatrix} u_2v_3 - u_3v_2 \\ u_3v_1 - u_1v_3 \\ u_1v_2 - u_2v_1 \end{pmatrix}$ |

### Tensor Notation

| Notation       | Meaning                 | Rank                   |
| -------------- | ----------------------- | ---------------------- |
| **I**          | Identity tensor/matrix  | 2 (3×3)                |
| **ω** or **Ω** | Angular velocity tensor | 2 (skew-symmetric)     |
| **I_body**     | Inertia tensor          | 2 (symmetric)          |
| **ε\_{ijk}**   | Levi-Civita symbol      | 3 (pseudotensor)       |
| **δ\_{ij}**    | Kronecker delta         | 2 (identity indicator) |

---

## Physical Quantities

### Kinematics

| Symbol   | Quantity             | Units         | Sign Convention           |
| -------- | -------------------- | ------------- | ------------------------- |
| **r, x** | Position             | meters (m)    | Distance from origin      |
| **v**    | Velocity             | m/s           | Direction of motion       |
| **a**    | Acceleration         | m/s²          | Direction of force        |
| **ω**    | Angular velocity     | rad/s         | Right-hand rule           |
| **α**    | Angular acceleration | rad/s²        | Right-hand rule           |
| **θ**    | Angle                | radians (rad) | Counterclockwise positive |

### Dynamics

| Symbol | Quantity          | Units          | Notes                            |
| ------ | ----------------- | -------------- | -------------------------------- |
| **m**  | Mass              | kilograms (kg) | Always positive                  |
| **F**  | Force             | newtons (N)    | Vector quantity                  |
| **τ**  | Torque            | N⋅m            | Vector quantity, right-hand rule |
| **I**  | Moment of inertia | kg⋅m²          | Tensor, always positive-definite |
| **p**  | Linear momentum   | kg⋅m/s         | = m**v**                         |
| **L**  | Angular momentum  | kg⋅m²/s        | = **I** **ω**                    |

### Golf-Specific Quantities

| Symbol   | Quantity                       | Definition                                                                                                                    | Units                     |
| -------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| **CoG**  | Center of gravity              | Center of mass                                                                                                                | m (relative to reference) |
| **COR**  | Coefficient of restitution     | (v_out - v_contact) / (v_in - v_contact)                                                                                      | Dimensionless, 0-1        |
| **DCR**  | Drift-Control Ratio            | $\lVert W a_d(x)\rVert_2 /(\sup_{u\in\mathcal U(x)}\lVert W B_a(x)u\rVert_2+\varepsilon)$; see the canonical definition above | Dimensionless             |
| **DgCR** | Drag–curve ratio (aerodynamic) | (1 - COR) / (1 + COR)                                                                                                         | Dimensionless, 0-1        |
| **e**    | Coefficient of restitution     | Same as COR                                                                                                                   | Dimensionless             |
| **v_0**  | Ball velocity (impact)         | Velocity immediately after impact                                                                                             | m/s                       |
| **α**    | Launch angle                   | Angle above horizontal                                                                                                        | degrees (°) or radians    |
| **β**    | Spin rate                      | Revolutions per minute (RPM) or rad/s                                                                                         | RPM or rad/s              |

**Acronym note (DCR):** The bare acronym **DCR** is reserved site-wide for the **Drift–Control Ratio**, the load-bearing controllability quantity defined in [Controllability & the Drift-Control Ratio](../articles/controllability-drift-ratio.html). The aerodynamic drag–curve ratio (formerly also abbreviated "DCR") is written **DgCR** to avoid the collision.

**DgCR (Drag–curve ratio) Sign Convention:** Always positive

- DgCR = (1 - COR) / (1 + COR)
- COR = 0 (perfectly inelastic) → DgCR = 1
- COR = 1 (perfectly elastic) → DgCR = 0

---

## Sign Conventions

### Cross Product (Right-Hand Rule)

**Convention:** Right-hand rule for all cross products

- Curl fingers of right hand in direction of first vector
- Extend thumb in direction of second vector
- Result points in direction of thumb

**Example:** Torque = **r** × **F**

- **r**: Position vector from origin to force application point
- **F**: Force vector
- **τ**: Torque (points along axis of rotation by right-hand rule)

### Angular Velocity

**Convention:** Right-hand rule for axis of rotation

- Thumb points in direction of **ω**
- Fingers curl in direction of rotation
- Positive angular velocity = counterclockwise when viewed from tip of **ω** vector

**Sign in Equations:**

- Clockwise (viewed from above): ω < 0
- Counterclockwise (viewed from above): ω > 0

### Quaternion Convention

**Hamilton Convention (default):**

- q = (w, x, y, z) = scalar-first
- Unit quaternion: w² + x² + y² + z² = 1
- Rotation: **v'** = q **v** q⁻¹ (sandwich product)

### Euler Angle Rotation

**Convention:** Extrinsic Z-Y-X (Yaw-Pitch-Roll)

- First: Rotate ψ about fixed Z-axis (yaw/heading)
- Second: Rotate θ about fixed Y-axis (pitch)
- Third: Rotate φ about fixed X-axis (roll)

**Matrix multiplication (right-to-left):**
$$R = R_Z(\psi) R_Y(\theta) R_X(\phi)$$

### Coordinate Frame Conventions

| Axis             | Direction            | Notation            |
| ---------------- | -------------------- | ------------------- |
| **X**            | Forward/Longitudinal | Roll axis           |
| **Y**            | Lateral/Side         | Pitch axis          |
| **Z**            | Vertical/Up          | Yaw axis            |
| **Right-handed** | z = x × y            | Standard convention |

**Frame Types:**

- **Inertial frame**: Fixed in space, non-rotating
- **Body frame**: Fixed to moving object, rotates with it
- **Local frame**: Centered at local point of interest

---

## Symbol Overloading Reference

Some symbols are used for multiple meanings depending on context. Use surrounding context to disambiguate.

### f, G, g, and u (Control-Affine Dynamics)

| Symbol     | Meaning                                                   | Type                                          | Rule                                                                        |
| ---------- | --------------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------- |
| **$f(x)$** | Complete autonomous drift of the declared effective plant | State vector field                            | State and declared frozen parameters only; no direct $u$ contribution       |
| **$G(x)$** | Input map                                                 | Matrix or collection of control vector fields | Uppercase $G$ throughout control-affine equations                           |
| **$g(q)$** | Gravity generalized-force vector                          | Generalized force                             | Lowercase $g$ is reserved for gravity in mechanics equations                |
| **$u$**    | Declared control input                                    | Input vector                                  | State its physical level, admissible set, and what the counterfactual zeros |

**Disambiguation rule:** Do not use lowercase $g(x)$ for the input map. Do not
use uppercase $G(q)$ for gravity. When a source convention must be quoted,
identify it as source notation and translate immediately to the canonical
symbols.

### F (Force, Frame, Frequency)

| Context            | Meaning          | Units       | Example                          |
| ------------------ | ---------------- | ----------- | -------------------------------- |
| Dynamics chapter   | Force vector     | N (newtons) | **F** = m**a**                   |
| Coordinate systems | Reference frame  | (none)      | "In frame F, the velocity is..." |
| Signal processing  | Frequency        | Hz (hertz)  | F = ω/(2π)                       |
| Trajectory         | Frequency domain | Hz          | Fourier transform                |

**Disambiguation rule:** Check chapter/section context. Dynamics chapters use **F** for force. Coordinate chapters use F for frames. Signal articles use F for frequency.

### R (Rotation, Resistance, Radius)

| Context           | Meaning                | Type          | Example                    |
| ----------------- | ---------------------- | ------------- | -------------------------- |
| Rotation matrices | Rotation matrix        | SO(3) element | **R** ∈ SO(3)              |
| Electrical        | Resistance             | Scalar        | R = V/I                    |
| Geometry          | Radius                 | Length        | r = 0.5 m                  |
| Drag force        | Aerodynamic resistance | Force         | **R**\_drag = ½ ρ A C_d v² |

**Disambiguation rule:** Matrices use bold **R**. Scalars use italic R.

### m (Mass, Meter)

| Context | Meaning           | Type   | Example      |
| ------- | ----------------- | ------ | ------------ |
| Physics | Mass              | Scalar | m = 0.046 kg |
| Units   | Meter (SI length) | Unit   | x = 2 m      |

**Disambiguation rule:** Usually clear from context. Mass in equations. Meters in dimension statements.

### ω (Angular velocity, Frequency)

| Context     | Meaning           | Units | Type                  |
| ----------- | ----------------- | ----- | --------------------- |
| Rotation    | Angular velocity  | rad/s | Vector **ω**          |
| Oscillation | Angular frequency | rad/s | Scalar ω = 2πf        |
| Signals     | Angular frequency | rad/s | ω = 2πf where f in Hz |

**Disambiguation rule:** Rotation chapters use bold vector **ω**. Signal/oscillation chapters use scalar ω.

### v (Velocity, Volt)

| Context    | Meaning  | Units     | Type         |
| ---------- | -------- | --------- | ------------ |
| Kinematics | Velocity | m/s       | Vector **v** |
| Electrical | Voltage  | V (volts) | Scalar v     |

**Disambiguation rule:** Bold **v** = velocity. Plain v = voltage (context dependent).

---

## Component Notation

### Index Notation (Einstein Convention)

| Notation          | Meaning                            | Example                            |
| ----------------- | ---------------------------------- | ---------------------------------- |
| **v_i**           | i-th component                     | v₁, v₂, v₃ for x, y, z             |
| **v_i u_i**       | Summation (repeated index)         | = v₁u₁ + v₂u₂ + v₃u₃ (dot product) |
| **v_i w_i**       | Implicit sum over i                | Matrix/tensor contraction          |
| **A_ij v_j**      | Matrix-vector product              | = Σ_j A_ij v_j                     |
| **ε_ijk v_i w_j** | Cross product via Levi-Civita      | (v × w)\_k = ε_ijk v_i w_j         |
| **δ_ij**          | Kronecker delta (1 if i=j, 0 else) | **I** = δ_ij (identity matrix)     |
| **ε_ijk**         | Levi-Civita symbol                 | ±1 or 0 depending on i,j,k order   |

### Matrix Component Notation

| Notation          | Meaning                    | Dimension                     |
| ----------------- | -------------------------- | ----------------------------- |
| **A**             | Matrix (bold capital)      | m × n                         |
| **A_ij**          | Element in row i, column j | Single value                  |
| **A**\_·j         | j-th column                | Column vector                 |
| **A**\_i·         | i-th row                   | Row vector                    |
| **A^T** or **A'** | Transpose                  | Swap rows/columns             |
| **A^{-1}**        | Inverse                    | If A is square and invertible |
| **det(A)**        | Determinant                | Single value                  |
| **tr(A)**         | Trace                      | Sum of diagonal elements      |

---

## Glossary by Symbol

Quick lookup table for symbols used in the project:

### Lowercase Greek

| Symbol | Name    | Uses                             | Context                      |
| ------ | ------- | -------------------------------- | ---------------------------- |
| α      | alpha   | Roll angle, angular acceleration | Kinematics, Euler angles     |
| β      | beta    | Spin rate, side-slip angle       | Golf, aerodynamics           |
| γ      | gamma   | Shear rate, gyration tensor      | Dynamics, materials          |
| δ      | delta   | Kronecker delta, variation       | Tensor notation, calculus    |
| ε      | epsilon | Strain, Levi-Civita symbol       | Materials, tensor            |
| ζ      | zeta    | Damping ratio, vorticity         | Dynamics, fluids             |
| η      | eta     | Viscosity, efficiency            | Fluids, energy               |
| θ      | theta   | Pitch angle, generic angle       | Euler angles, geometry       |
| ι      | iota    | (rarely used)                    | —                            |
| κ      | kappa   | Curvature, torsion               | Differential geometry        |
| λ      | lambda  | Eigenvalue, Lagrange multiplier  | Linear algebra, optimization |
| μ      | mu      | Friction coefficient, mean       | Materials, statistics        |
| ν      | nu      | Poisson's ratio, frequency       | Materials, waves             |
| ξ      | xi      | Screw/twist, damping ratio       | Mechanics, dynamics          |
| ο      | omicron | (rarely used)                    | —                            |
| π      | pi      | 3.14159..., projection           | Constants, geometry          |
| ρ      | rho     | Density, radius                  | Materials, coordinates       |
| σ      | sigma   | Stress, standard deviation       | Materials, statistics        |
| τ      | tau     | Torque, shear stress, time       | Dynamics, materials, time    |
| υ      | upsilon | (rarely used)                    | —                            |
| φ      | phi     | Roll angle, phase angle          | Euler angles, signals        |
| χ      | chi     | (rarely used)                    | —                            |
| ψ      | psi     | Yaw angle, potential             | Euler angles, physics        |
| ω      | omega   | Angular velocity, frequency      | Rotation, signals            |

### Uppercase Greek

| Symbol | Name   | Uses                                     |
| ------ | ------ | ---------------------------------------- |
| Γ      | Gamma  | Surface tension, Christoffel symbols     |
| Δ      | Delta  | Change/difference operator               |
| Θ      | Theta  | Moment of inertia tensor, potential      |
| Λ      | Lambda | Eigenvalue matrix, cosmological constant |
| Ξ      | Xi     | (rarely used in project)                 |
| Π      | Pi     | Product operator, Poincaré map           |
| Σ      | Sigma  | Summation operator, covariance           |
| Φ      | Phi    | Potential energy, flux                   |
| Ψ      | Psi    | Wave function, potential                 |
| Ω      | Omega  | Solid angle, frequency, domain           |

---

## References & Authoritative Sources

**For external validation:**

- [ISO 80000-2:2019](https://www.iso.org/standard/64973.html) — Mathematical notation and symbols
- [NIST Special Publication 330](https://physics.nist.gov/cuu/pdf/sp330.pdf) — SI Units
- [NIST Special Publication 811](https://physics.nist.gov/cuu/pdf/sp811.pdf) — Guide for the Use of SI

**Project-specific:**

- Physics of Golf (Chapters 1-31) — Foundational reference
- Geometry of Motion (Volumes 0-1) — Advanced mechanics
- Articles on screw theory, Euler angles, quaternions

---

## How to Update This Document

1. **New notation discovered:** Add to relevant section with meaning, units, and context
2. **Ambiguity found:** Add to [Symbol Overloading Reference](#symbol-overloading-reference)
3. **Sign convention clarified:** Update [Sign Conventions](#sign-conventions)
4. **New chapter published:** Review for consistency with NOTATION.md

**Maintenance:** Review quarterly or when new content published. Update links in chapter preambles when notation changes.

---

## Examples: Using This Reference

### Example 1: Quaternion Rotation

"The rotation of point **v** by quaternion q is: **v'** = q **v** q⁻¹"

From NOTATION.md:

- q = (w, x, y, z) [Quaternions section] — Hamilton convention
- **v** = vector [Vectors section]
- q⁻¹ = q\* [Quaternions section] — inverse of unit quaternion

### Example 2: Torque Equation

"Torque **τ** = **r** × **F** follows the right-hand rule"

From NOTATION.md:

- **τ** = torque [Physical Quantities] in N⋅m
- **r** = position vector [Physical Quantities]
- **F** = force vector [Physical Quantities] in N
- × = cross product [Cross Product section] — right-hand rule applies

### Example 3: Euler Angle Convention

"Rotate by Euler angles (ψ, θ, φ) in Z-Y-X order"

From NOTATION.md:

- ψ (psi) = yaw [Euler Angles section]
- θ (theta) = pitch [Euler Angles section]
- φ (phi) = roll [Euler Angles section]
- Z-Y-X = extrinsic rotation order [Euler Angle Rotation section]
- R = R_Z(ψ) R_Y(θ) R_X(φ) [Matrix form]

---

**Last Updated:** April 2026  
**Version:** 1.0  
**Maintained By:** AffineDrift Documentation Team  
**Status:** Authoritative Reference ✓
