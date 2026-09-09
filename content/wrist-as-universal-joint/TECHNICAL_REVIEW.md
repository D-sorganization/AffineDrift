# Technical Review: Wrist Constraints and the Cardan Analogy

Technical revision: 8 September 2026. Issue #4299 supersedes the earlier
25 November 2025 review's claims of corrected and validated wrist physics.
The original investigation asked a useful question about grip geometry;
the proposed “enhancement” introduced errors of its own.

## Findings and Corrections

| Earlier Claim | Technical Finding | Correct Treatment |
|---|---|---|
| Two cross-pin axes imply perpendicular shafts | Pin axes and shaft axes are different | Declare the supported assembly and bend angle |
| Wrist flexion is Cardan input spin; grip is bend | No anatomical mapping was derived | Separate two-DOF wrist geometry from one-DOF supported shaft motion |
| Speed ratio has a square-root denominator | It does not differentiate the stated phase relation | Differentiate an explicit quadrant-aware output angle |
| Reciprocal speed and torque prove validity | Any nonzero wrong function and its reciprocal pass | Check angle derivatives, full revolutions, extrema and independent implementations |
| A transverse rod/point-head formula gives shaft inertia | The axis was mislabeled | Use the transverse label; measure intrinsic/offset inertia for shaft rotation |
| Alpha/gamma projections conserve energy | Squared components conserve vector norm | Check power using the matching angular velocities |
| Constraint reactions cannot depend on control | Constrained dynamics generally makes them input-dependent | Solve reactions together with motion |
| Inertia damps variability | Inertia stores energy and changes response | Include damping, temporal correlations, dynamics and task output separately |
| A high Cardan bend explains unstable palm grips | The synthetic angle has no validated anatomical mapping | Withdraw performance conclusions pending qualification |

## Why the Original Tests Missed It

The former tables disagreed with both the implemented square-root formula and
their stated extrema. Several supposed validation items were recommendations
to run future experiments, while the conclusion nevertheless said validation
was complete. The speed/torque product was constructed to equal one, so it
could not reveal the kinematic error. The corrected verification differentiates
the independent angle relation and integrates the speed ratio over a revolution.

The Streamlit sweep also exchanged the two arguments relative to its
current-value calculation. Named phase and bend arguments repair that mismatch.
The scalar inertia default was cited as if a reference supplied the number;
it is now identified as a compatibility demonstration setting.

## Preserve the Research Question

Constraint loads can transmit energy between segments while their combined
ideal power vanishes. Grip geometry can change load expression, moment arms,
effective dynamics and face sensitivity. Those are legitimate mechanisms.
They do not establish that one grip always transmits less noise, generates
more speed or requires less control. Reactions, muscle action, compliance and
disturbance correlations change together.

The main article derives a local input-dependent reaction counterexample,
moving-point rotational balance and a face-yaw Jacobian. It distinguishes
fixed-input, fixed-motion and reoptimized comparisons. This provides a stronger
basis for experiments than assuming the preferred grip in advance.

## Documentary Corrections

The previous derivative switched phase conventions mid-proof, misplaced
extrema, and simplified a square root incorrectly at a limiting angle. Its
numerical “typical” inertias were inconsistent with its own mass/length
example. The older TeX manuscript also mislabeled angular-velocity variability
and converted approximately 83 radians into 4.8 degrees. The web version
removed that extreme example but retained a missing one-half integration factor.
All of these are mathematical defects, not matters of rhetorical emphasis.

The old bibliography mixed a 2005 in-vivo carpal study with a 2011 mechanical
axes study, assigned unsupported years/locations, and listed supposed citation
edges to works published later. A thematic reading relationship must not be
presented as a verified citation in an older paper.

## Evidence Status

The [mathematical companion](MATHEMATICAL_DERIVATION.md) defines the supported
Cardan convention and limitations. The [validation guide](VALIDATION_AND_TESTING.md)
separates analytical verification, numerical convergence, mechanical experiments
and human performance. The detailed development log records individual checks
and failures. Neither an attractive plot nor a checked algebraic identity is
an empirical golf validation result.
