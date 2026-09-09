# Cardan Kinematics and the Wrist Modeling Boundary

Author: Dieter Butz. Technical revision: 8 September 2026, issue #4299.

This companion derives the supported-driveshaft calculation used by the
legacy demonstration. The [main wrist article](https://affinedrift.com/articles/wrist-universal-joint.html)
derives the separate two-coordinate wrist model, its reactions, power balance,
moving-point inertia and face-angle sensitivity. These mechanisms share a
joint analogy, but they do not share an automatically interchangeable set of
coordinates or constraints.

## 1. Specify the Mechanism Before the Formula

A Cardan assembly contains two shafts, a cross with perpendicular pins, and
supports that fix the shaft axes. The shaft bend is delta. Shaft spin angles
are phi and chi. For fixed bend, the supported assembly has one independent
spin coordinate. A free relative joint between forearm and hand instead has
two bending coordinates; changing hand–club attachment is another geometric
choice. An anatomical wrist flexion angle is not automatically shaft phase,
and a grip angle is not automatically the shaft bend.

The former derivation conflated these variables and then described the result
as a complete wrist model. Correcting the Cardan equation does not validate
that identification. To use a driveshaft analogy quantitatively, provide a
mapping from the anatomical model to its shafts, pins, supports, coordinates
and power ports, and verify that it preserves the relevant motions and loads.

## 2. Derive the Phase Relation

Take fixed bend |delta| < pi/2 and choose a phase origin satisfying

```text
tan(chi) = cos(delta) tan(phi)
chi = atan2(cos(delta) sin(phi), cos(phi)), continued through full turns.
```

The second expression handles quadrants. Ordinary atan(tan(...)) loses branch
information and can produce discontinuous output motion. Differentiate atan2:

```text
x = cos(phi), y = cos(delta) sin(phi)
dchi/dphi = (x dy/dphi - y dx/dphi)/(x² + y²)
          = cos(delta)/(cos²(phi) + cos²(delta) sin²(phi))
          = cos(delta)/(1 - sin²(delta) sin²(phi)) = r(phi, delta).
```

There is **no square root** in this derivative. A factor with a square root
can arise in other geometric quantities, but it is not this shaft speed ratio.
The independent full-turn condition is integral(r dphi) = 2 pi: one input
revolution produces one output revolution. The old formula fails this check
despite its reciprocal torque formula multiplying it to one.

The [MathWorks Driveline reference](https://www.mathworks.com/help/sdl/ref/universaljoint.html)
uses a cosine-squared phase convention. Set its base phase to phi - pi/2 to
compare speed ratios with this convention. The alternative relation
tan(chi) = tan(phi)/cos(delta) gives cos(delta)/[1-sin²(delta)cos²(phi)];
do not take the phase relation from one convention and the extrema from another.

## 3. Velocity and Acceleration

For a fixed bend,

```text
omega_out = r omega_in
alpha_out = r alpha_in + r_phi omega_in²
r_phi = cos(delta) sin²(delta) sin(2 phi)
        / [1 - sin²(delta) sin²(phi)]².
```

Thus constant input speed does not imply constant output speed or zero output
acceleration. Output shaft inertia demands torque for that acceleration. It
cannot be added to a massless transmission formula and ignored in power balance.
If delta varies, chi_dot also includes chi_delta delta_dot, where

```text
chi_delta = -sin(delta) sin(phi) cos(phi)
            / [cos²(phi) + cos²(delta) sin²(phi)].
```

A changing bend requires additional motion and force accounting at its
supports. The fixed-bend formula alone does not describe it.

For fixed nonzero bend, r ranges from cos(delta) at phi = 0 modulo pi to
sec(delta) at phi = pi/2 modulo pi. It has period pi. Its average over input
phase is one. At delta = 0 the speed ratio is one for every phase: alignment
is regular. As the bend approaches a right angle, the limiting mechanism
degenerates and this operating model ceases to apply. This is not proof of a
human wrist singularity at some grip label.

## 4. Torque Ratio and Power

For a coupling with negligible energy storage and loss and stationary
supports, choose a positive driving torque into the input and a positive
delivered torque out of the output:

```text
tau_in omega_in = tau_out omega_out
tau_out/tau_in = 1/r = [1-sin²(delta)sin²(phi)]/cos(delta).
```

At zero speed, the same quasistatic ratio follows from virtual work, not
division of two zero powers. If both torques are defined positive into the
coupling, their power sum is zero and their ratio carries the corresponding
minus sign. Torque multiplication trades against speed; it is not efficiency
above 100 percent. A realistic assembly obeys

```text
P_in - P_out + P_support = dE_stored/dt + P_loss.
```

Declare what components are inside the boundary and avoid counting energy
storage twice. Bearings can supply reaction moments even if their ideal
stationary reaction power vanishes. Conservation of angular momentum applies
to a system including all external moments; a supported pair of shafts is not
automatically torque-free.

## 5. Numerical Reference Table

For a 30-degree bend in the phase convention above:

| Input Phase | Speed Ratio | Ideal Delivered-Torque Ratio |
|---|---:|---:|
| 0 degrees | 0.866025 | 1.154701 |
| 30 degrees | 0.923760 | 1.082532 |
| 45 degrees | 0.989743 | 1.010363 |
| 60 degrees | 1.065877 | 0.938194 |
| 90 degrees | 1.154701 | 0.866025 |

At 45 degrees the ratios are not exactly one. At phi = 20 degrees,
delta = 30 degrees, the torque ratio is approximately 1.12093; recompute it
from the equation at full precision when using it in another calculation.
None of these rows represents wrist flexion or a measured golf grip.

## 6. The Legacy Projection Demonstration

The program retains historical argument names `grip_angle_deg` and
`wrist_angle_deg` for compatibility. In its Cardan calculation they mean
**demonstration bend/projection angle theta** and **input shaft phase phi**.
Its additional projection is

```text
tau_alpha = tau_out sin(theta)
tau_gamma = tau_out cos(theta).
```

This defines two components of one vector in an orthogonal basis. The squares
sum to tau_out²; the absolute component percentages need not sum to 100.
That identity is not an energy or angular-momentum proof. Setting projection
theta equal to shaft bend delta is a synthetic one-parameter choice, not an
anatomical relation established by the model.

The time plots multiply an arbitrary torque trace by the gain at a selected
fixed phase. They do not integrate a rotating Cardan assembly or a golf swing.
The phase sweep evaluates this gain at other phases. It must use the same
phase/bend argument order as the current-value plot; the older Streamlit
sweep accidentally reversed those arguments.

The inertia helper estimates a transverse grip-point inertia for a thin shaft
and point head:

```text
I_alpha = m_head d² + m_shaft L²/3.
I_gamma = chosen_ratio I_alpha.
```

The default chosen_ratio = 0.5 is a legacy illustration. It is not a measured
shaft-axis inertia ratio or a value validated by Jorgensen. Actual axial inertia
requires transverse offsets and intrinsic head/shaft inertia. The main article
shows the tensor parallel-axis formula and gives I_alpha = 0.177833 kg m²
for m_head=.2kg, d=.85m, m_shaft=.1kg and L=1m.

Scalar `alpha = tau/I` outputs are isolated axis-response illustrations with
the selected inertias. They omit gyroscopic, moving-support, contact and
control effects. The code neither maps them to clubface yaw nor solves a
constraint reaction. A mean-zero input trace can also have a zero mean output
while containing large fluctuations; the mean panel is not a variability metric.

## 7. Parameter Limits and Validation

The helper rejects nonfinite angles. It preserves a historical numerical
clip of finite bends above 89 degrees in magnitude. An output for a requested
90- or 95-degree bend therefore describes an 89-degree calculation, not the
requested geometry. The interface must disclose this boundary. A robust
anatomical model must use its own measured range and constraints.

Check the independent angle derivative, full-turn integral, extrema, phase
convention, both port signs, nonfinite inputs, and agreement among Python,
browser and plotted values. These are software and analytic verification.
They do not establish agreement with a real driveshaft or a biological wrist.

For wrist reactions use the full constrained dynamics in the main article.
For a compliant wrist add identified tissue states and constitutive laws.
For golf performance validate a complete output/uncertainty model with actual
measurements. The old claims of a universal 20–40-degree optimum, massive
palm-grip torque multiplication, and demonstrated control benefits are
withdrawn: they did not follow from the implemented mechanism.

## Sources and Scope

- MathWorks' Driveline Universal Joint documentation supplies a supported
  driveshaft reference with explicit phase conventions. The derivation here
  states its own angle relation and differentiates it independently.
- MathWorks' [Multibody joint reference](https://www.mathworks.com/help/sm/ref/universaljoint.html)
  describes a two-primitive relative joint and its sensing. It is a different
  modeling interface from the one-coordinate supported driveline assembly.
- The main wrist article links the anatomical and motor-control studies and
  qualifies what each supports. No human grip-performance dataset has been
  produced by this demonstration.
