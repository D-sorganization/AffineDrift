---
title: "Critique: The Validation Dimensionality Gap"
description: "Match each verification or validation claim to the motion, contact and output quantities actually represented by its model."
---

## Summary of Concern

A planar simulation cannot validate a prediction about an omitted spatial
degree of freedom. The wrist grip hypothesis concerns hand–club orientation,
spatial reactions and face delivery, so planar examples elsewhere in the
project do not establish it. Each claim needs evidence from a model and
measurement process that represent its relevant variables.

The earlier critique also made excessive claims. It dismissed planar
verification as trivial, assumed spatial gyroscopic coupling implied chaos,
and said a planar model cannot contain constraint reactions. Those conclusions
do not follow. A planar model can test substantial dynamics and numerical
implementation within its declared scope.

## Distinguish the Questions

| Question | Appropriate Evidence | Insufficient Substitute |
|---|---|---|
| Are the stated equations implemented correctly? | Independent identities, solver/convergence checks and limiting cases | An attractive simulation alone |
| Does a planar intervention reproduce a specified planar response? | Matched model/input/boundary conditions and residuals | Mere cancellation of quantities defined to cancel |
| Does grip change spatial face sensitivity? | Spatial orientation, contact and inertia model with defined output | A planar clubhead-speed example |
| Does the model predict human grip performance? | Measured geometry, repeated trials, uncertainty and held-out validation | Software checks or qualitative agreement with instruction |

If angular velocity lies along a principal normal to an ideal planar body,
the body's gyroscopic cross product vanishes. That does not remove planar
multibody Coriolis/centrifugal coupling or reactions enforcing joints and
contacts. A spatial tensor can also imply out-of-plane reaction moments when
planar motion is imposed. State the actual model rather than making a blanket
zero-torque claim from the word “planar.”

## Consequences for the Site

The [wrist article](../articles/wrist-universal-joint.qmd) must distinguish
its spatial two-axis model, supported Cardan demonstration and empirical
hypothesis. Two rotational coordinates do not make a mechanism a planar swing.
The [Part5 model](../articles/theory-part5.qmd) should report only the
interventions, degrees of freedom and outputs its actual artifacts support.
Neither a successful algebraic decomposition nor a passing planar test is
automatically a robustness result for a different spatial model.

Spatial gyroscopic terms can introduce coupling without chaos. Conversely,
planar systems can be nonlinear and sensitive. Whether a trajectory is stable,
chaotic, controllable or robust requires the corresponding analysis and
definitions; none is determined by spatial dimension alone.

## Suggested Remedies

Bind every result to its model revision, coordinates, constraints, external
loads, intervention and measured output. Report equation and constraint
residuals, time-step convergence and uncertainty. Use a spatial model when
testing out-of-plane face behavior; include contact and compliance when those
mechanisms affect the claim. Test resulting predictions on independent data.

The original MacKenzie–Sprigings forward-dynamics paper is a useful example
of why model dimension and observation dimension must be reported separately:
its 3D model was compared with a single-camera 2D measurement process from one
golfer. That is bounded evidence, not either blanket validation or no useful
evidence at all. The available author-hosted methods excerpt documents that
scope. [MacKenzie and Sprigings, 2009](https://doi.org/10.1007/s12283-009-0020-9).

## Evidence Status

Planar verification remains useful within its declared domain. Spatial grip
and human-performance qualification remain outstanding. The critique's earlier
claims about absent reactions and necessarily chaotic spatial coupling are
withdrawn; the central demand to match evidence to the prediction remains.
