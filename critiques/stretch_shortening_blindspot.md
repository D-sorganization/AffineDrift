# Critique: Conflation of Active and Passive Muscle-Tendon Dynamics

## Summary of Concern

The AffineDrift framework defines "Drift" ($f(x)$) as the *skeletal* baseline, including rigid-body inertia, gravity, and shaft elasticity. By exclusion, the "Input" term ($\tau_{input}$) absorbs all other forces, including the passive elastic energy stored and released by muscle-tendon units (the Series Elastic Component or SEC). This misclassifies the **Stretch-Shortening Cycle (SSC)**—a dominant power source in the golf swing—as "Active Input", confounding *metabolic effort* with *elastic recoil*.

## Location

- **Article:** `articles/theory-part1.qmd`
- **Section:** 2.1 Modeling Assumptions, Assumption 5 ("Torques treated as generalized inputs")
- **Article:** `articles/affine-nature-golf-swing.qmd`
- **Section:** Taxonomy / Input Forces

## Nature of the Issue

- **Biomechanical Validity:** Biological actuation is not purely force-generative (Contractile Element); it is viscoelastic (SEC/PEC).
- **Causal Misattribution:** The "Active" term $\tau_{input}$ captures the *release* of elastic energy in tendons, which is a passive dynamical event driven by state history, not instantaneous neural command.
- **Terminological Ambiguity:** "Active" implies volitional drive, but SSC recoil is physically closer to "Drift" (energy storage and release).

## Why This Is a Problem

A reviewer with a biomechanics background will immediately object that the framework overestimates the "Active" contribution at the transition and impact.
By lumping tendon recoil into $u$, the model suggests the golfer is "working" during the release phase, when they may actually be "riding" the elastic return.
This obscures the efficiency mechanism of the swing (using the body as a whip/spring) and treats it mathematically as if it were a motor driving a rigid linkage.
It invalidates the "Drift Invariance" defense in a subtle way: if $u$ includes passive recoil, then $u$ depends on state history $x(t-\tau)$, blurring the line between state-dependent drift and input.

## Evidence / References

- **Hill-Type Muscle Models:** Separately model CE (Contractile Element), SEC (Series Elastic), and PEC (Parallel Elastic).
- **Komi (2000):** *Stretch-shortening cycle of bone-muscle-tendon-complex.*
- **Roberts & Azizi (2011):** *Flexible mechanisms: the diverse roles of biological springs in vertebrate movement.* (Tendons act as power amplifiers, decoupling muscle shortening velocity from joint velocity).

## Severity

- **High** (Biomechanical fidelity).
- **Medium** (Control theoretic structure — the math holds, but the labels are wrong).

## Suggested Remedies

1.  **Refine Assumption 5:** Explicitly state that "Input" $\tau_{input}$ represents the *net neuromuscular moment*, comprising both contractile and series-elastic contributions.
2.  **Add a "Biological Drift" Category:** Ideally, $f(x)$ should include a "Passive Muscle Stiffness" term $K_{mus}(q)q$. If this is impossible due to the "Effective Plant" problem, add a **"Viscoelastic Caution"** to the Taxonomy.
3.  **Reframe "Active" as "Net Internal":** Change the label from "Active Input" to "Net Internal Torque" to avoid implying pure metabolic cost.
