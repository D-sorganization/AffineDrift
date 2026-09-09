# Wrist Constraints and Cardan Demonstration Guide

Author: Dieter Butz. Technical revision: 8 September 2026 (#4299).

The main [wrist article](https://affinedrift.com/articles/wrist-universal-joint.html)
investigates how measured grip geometry, constraints, actuation, club inertia
and uncertainty interact. This directory also contains a historical Cardan
demonstration. Its supported-driveshaft formula is not a calibrated wrist model.
The earlier claims of validated grip optimization and universal palm-grip
instability are withdrawn.

## What Each Resource Does

| Resource | Purpose | Evidence Boundary |
|---|---|---|
| Wrist_Universal_Claude.tex | Print edition of the corrected mechanics argument | Idealized derivations and a testable hypothesis |
| Wrist_Universal_Claude.html | Guide to the current article | Avoids retaining a conflicting older narrative |
| MATHEMATICAL_DERIVATION.md | Cardan phase, speed, acceleration and power derivation | Fixed supported shafts; not anatomical identification |
| VALIDATION_AND_TESTING.md | Independent checks and remaining qualification | Software verification is distinct from experiments |
| TECHNICAL_REVIEW.md | Correction record and consequences | Explains why earlier validation claims failed |
| Universal_Joint_Model_Enhanced.py | Compatibility launcher for the Qt demonstration | Formula/axis-response illustration; no swing integration |
| Wrist_Universal_FBPost.sty | Original exploratory discussion | Historical hypothesis, not corrected technical authority |

The implementation lives in `src/tools/wrist_universal_joint` at the repository
root. The launcher retains its filename so existing links remain usable. It
imports that package and is not a self-contained downloadable application.
Use the repository's Python 3.12 environment and declared GUI dependencies;
run from the repository root with the root on PYTHONPATH:

```bash
PYTHONPATH=. python content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py
```

On PowerShell, set `$env:PYTHONPATH = (Get-Location).Path` before the Python
command. The Streamlit and standalone browser interfaces use the same
demonstration interpretation. Their installation and embedding files describe
deployment mechanics, not experimental qualification.

## Reading the Controls and Plots

The legacy argument named `grip_angle` supplies both the Cardan bend and a
subsequent vector-projection angle. `wrist_angle` supplies the input shaft
phase. These are synthetic demonstration coordinates; no measured mapping to
finger position, wrist deviation or flexion has been supplied. The anatomical
sketch is a historical illustration, not the geometry from which the Cardan
formula was derived.

At a selected phase, a time trace is multiplied by a fixed transmission gain.
The graph does not solve the evolving phase of a rotating shaft, let alone a
golf swing. Its phase sweep evaluates that gain at other phases. Torque and
velocity ratios are dimensionless; scalar acceleration-per-torque has inverse
inertia units and should not be interpreted on the same scale without its label.

The alpha inertia is a transverse grip-point rod/point-head estimate. Gamma
uses a demonstration ratio, default 0.5, and is not a measured shaft-axis
inertia. Dividing a torque component by these scalar inertias is an isolated
axis-response illustration. It omits support acceleration, the full tensor,
gyroscopic terms, muscles, contacts and the face-orientation map.

Angles above the numerical 89-degree bend limit are clipped. A plotted
90-degree input therefore does not represent a 90-degree Cardan assembly or
an extreme human grip. The full derivation explains the phase convention and
domain; use those definitions when comparing tables and plots.

## What the Demonstration Cannot Establish

It cannot identify wrist constraint reactions, rank grip styles, recommend a
20–40-degree optimum, prescribe impact wrist posture, infer muscle effort or
predict ball flight. Torque multiplication is not increased energy efficiency;
inertia is not damping; and a mean-zero signal can still have large variance.
Those distinctions let the illustration remain useful without asking it to
answer a different mechanical problem.

For the golf hypothesis, follow the main article's reaction equations,
hand–club transform, inertia transport, face sensitivity and temporal covariance.
Measure geometry and loads, qualify the contact/compliance model, and test
predictions on held-out trials. Preserve the original question while making
each claimed implication conditional on the evidence actually available.
