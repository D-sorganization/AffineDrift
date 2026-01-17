# Critique: The Passive-Active Boundary Ambiguity (The "Effective Plant" Tautology)

## Summary of Concern
The framework asserts a clean causal separation between "Drift" (passive physics) and "Input" (active torque). However, this separation relies on the **"Effective Plant"** assumption: that the stiffness and damping parameters in the drift field $f(x)$ are fixed properties of the system. In a biological system, these parameters are actively modulated by the golfer via co-contraction.
Consequently, the "Drift" is not an objective, immutable baseline (like gravity) but a **strategy-dependent** construct. By classifying impedance-generated forces as "passive," the framework effectively attributes a significant portion of the golfer's agency (stiffness control) to the environment. This leads to an underestimation of the "Active" contribution, as the metabolic cost of maintaining high stiffness is hidden inside the "Passive" drift term.

## Location
- **Article:** `articles/affine-nature-golf-swing.qmd`
- **Section:** Limitations -> Parameter identification and causality
- **Claim:** "The 'Effective Plant' baseline is the only relevant counterfactual for analyzing control *around* the intended trajectory."

## Nature of the Issue
- **Arbitrary Classification:** The framework draws the boundary between "Active" and "Passive" at the level of *net torque production*, ignoring *impedance generation*. Both require neural drive and metabolic energy.
- **Tautological Baseline:** The ZTCF is defined using parameters ($K, D$) identified from the swing itself. Thus, the baseline is not independent of the behavior it is analyzing. The "plant" is defined by what the golfer does.
- **Hidden Cost:** A stiff, highly controlled swing will appear to have large "Passive Restoring Forces" in this framework. The analysis will conclude the golfer is "riding the drift," while in reality, they are burning energy to create that drift.

## Why This Is a Problem
- **Biomechanists** will reject the classification of co-contraction forces as "drift". In motor control, stiffness *is* a control variable.
- **Metabolic Inconsistency:** The term "Passive" implies "Free". But "Effective Plant" stiffness is not free.
- **Ambiguous Agency:** If the golfer chooses the impedance, they choose the drift. Therefore, the "Drift" is not truly "Input-Invariant" in the broad sense (invariant to strategy), only in the narrow sense (invariant to instantaneous torque).

## Evidence / References
- **Hogan, N. (1984).** "Adaptive control of mechanical impedance by coactivation of antagonist muscles." (Establishes impedance as an active control variable).
- **Franklin, D. W., et al. (2003).** "Stability of the human arm system in the presence of forces." (Shows humans tune stiffness to the environment).

## Severity
- **Medium/High.**
  It does not break the math ($\nabla_u f = 0$ still holds for fixed parameters), but it severely compromises the **interpretation** of the results. "Drift" is a misleading label for "Active Stiffness + Passive Inertia".

## Suggested Remedies
1.  **Refine Terminology:** Replace "Passive Drift" with **"Impedance-Conditioned Drift"** or **"Structural Drift"** to acknowledge its dependence on the system's *state* of stiffness.
2.  **Explicit Disclaimer:** Add a specific limitation stating: *"The decomposition separates Torque Generation (work) from Impedance Maintenance (stability). It classifies the forces resulting from active stiffness as 'drift' because they are state-dependent, not because they are metabolically passive."*
3.  **Counter-Argument in Defense:** Argue that from the perspective of the *actuator* (the muscle), the stiffness of the *joint* effectively acts as a spring against which it must work. Thus, mechanically, it *is* a passive load to the torque generator, even if it is metabolically active to the organism.
