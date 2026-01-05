# Critique: The Effective Plant Fallacy (Task-Dependent Impedance)

## Summary of Concern
The AffineDrift framework relies on "Drift Invariance" ($\nabla_u f(x) \equiv 0$) to justify the separation of passive dynamics ($f(x)$) from active input ($g(x)u$). However, the defense against "Input-Dependent Boundary Conditions" invokes the concept of the **"Effective Plant"**—a model where passive stiffness/damping parameters ($K, D$) are tuned to represent the "structural impedance" required for the task.

**This is a fundamental contradiction.** If the "passive" parameters ($K, D$) are determined by the task (which is defined by the input strategy), then $f(x)$ is implicitly a function of $u$. The "Zero Torque Counterfactual" ($u=0$) then simulates a physical impossibility: a system with the high stiffness of maximal activation but zero drive. This "Zombie Golfer" baseline violates the physiology of recruitment (Henneman's Size Principle) and renders the causal decomposition circular.

## Location
- **Page:** `articles/theory-part3.qmd` (Drift Invariance) and `articles/affine-nature-golf-swing.qmd` (Limitations)
- **Claim:** "Drift invariance... guarantees that the 'passive' dynamics identified by the model are structurally unpolluted by the 'active' control inputs." vs "The ZTCF acts as a **'frozen strategy' baseline**: it asks how the system would evolve if the golfer... maintained the *structural impedance* required for the task."

## Nature of the Issue
- **Logical Circularity**: The "Passive" baseline is defined by the "Active" strategy it is meant to be compared against.
- **Hidden Parameter Dependency**: The "Constant Impedance Assumption" hides the functional dependence $K = K(u)$ and $D = D(u)$ inside fixed parameters $K_{eff}, D_{eff}$.
- **Physiological Violation**: Skeletal muscle cannot maintain high impedance without metabolic activity and force generation. A high-impedance, zero-force state is biologically invalid.

## Why This Is a Problem
1.  **Tautological Stability**: By freezing the "Effective Plant" at the high-impedance values required for the swing, the ZTCF artificially stabilizes the passive trajectory. A true "passive" baseline (relaxed muscle) would likely diverge or collapse. The framework thus attributes the stabilizing effect of *impedance control* (an active neural strategy) to *passive drift*.
2.  **Underestimation of Control Cost**: The "cost" of maintaining high impedance (metabolic, neural) is hidden. The framework makes the swing look "more passive" than it is by granting the ZTCF free stiffness.
3.  **Invalid Counterfactual**: A counterfactual must be a *possible* world. The "Zombie Golfer" is not a possible world in a biological system.

## Evidence / References
- **Hogan, N. (1984)**. "An organizing principle for a class of voluntary movements." (Impedance control requires activation).
- **Todorov, E. (2004)**. "Optimality principles in sensorimotor control." (Gains are task-dependent).
- **Latash, M. L. (2008)**. *Synergy*. (Critique of separating "parameters" from "variables" in biological control).
- **Henneman, E. (1957)**. (Size Principle: recruitment leads to force and stiffness simultaneously).

## Severity
- **High**: It threatens the core claim that the decomposition isolates "Mechanical Causality" from "Neural Strategy". In reality, the "Mechanical" layer is pre-conditioned by the "Neural" layer via impedance.

## Suggested Remedies
1.  **Explicit Bifurcation of Baselines**: Define two distinct baselines:
    *   **$\text{ZTCF}_{skeletal}$**: The "Cadaveric" baseline ($u=0, K \to 0$). True passive mechanics.
    *   **$\text{ZTCF}_{frozen}$**: The "Effective" baseline ($u=0, K = K_{task}$). The current definition.
    *   The difference between them is the **"Stabilization Drift"**—passive dynamics enabled by active impedance.
2.  **Rename "Passive Drift"**: Use **"Impedance-Conditioned Dynamics"** to acknowledge the dependency.
3.  **Admit "Virtual" Nature**: Explicitly state that the ZTCF is a *virtual* reference frame (like a rotating frame of reference), not a physical experimental condition.
