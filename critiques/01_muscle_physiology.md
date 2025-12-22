# Critique: The Fallacy of Passive Drift and the "Skeletal Baseline"

## Summary of Concern
The AffineDrift theory separates dynamics into "passive drift" ($f(x)$) and "active input" ($g(x)u$), assuming drift is input-invariant.
However, muscle activation ($u$) fundamentally alters joint impedance (stiffness/damping). The "Skeletal Drift" defense (Assumption 5) argues that $f(x)$ represents the "skeletal baseline".
**The Weakness:** This "Skeletal Baseline" corresponds to a flaccid/cadaveric state, which is mechanically irrelevant to the high-stiffness regime of a power swing. Using a "cadaver baseline" to quantify "passive contributions" during a 115 mph swing provides a mathematically rigorous but biologically meaningless counterfactual.

## Location
- **Page:** `articles/affine-nature-golf-swing.qmd`
- **Section:** `Assumption 5` and `Defense Strategy`
- **Claim:** "The term $f(x)$ represents the **skeletal drift**... serving as a 'skeletal baseline' rather than a representation of a flaccid... golfer."

## Nature of the Issue
- **Conceptual Vacuity**: The baseline exists mathematically but has no functional relevance.
- **Overestimation of Passive Stability**: If the model uses "active-like" stiffness parameters in $f(x)$ (as per `parameter_causality_leakage`), it violates the "Skeletal" claim. If it uses true "flaccid" parameters, the ZTCF trajectory will be a chaotic collapse, making it a useless comparison for the actual swing.

## Why This Is a Problem
- **The "Floppy Doll" Dilemma**:
    - Case A: ZTCF uses stiffness identified from active motion. -> Drift depends on Input. (Violates Affine Assumption).
    - Case B: ZTCF uses passive (cadaver) stiffness. -> ZTCF trajectory diverges instantly into a heap. (Violates Utility).
- The theory tries to have it both ways: keeping the stability of active stiffness while calling it "passive drift".

## Evidence / References
- **Hogan, N. (1984).** "Adaptive control of mechanical impedance..." (Stiffness scales with torque).
- **Franklin, D. W. et al. (2003)**. "Adaptation to stable and unstable dynamics..." (Reflex gains change with task).

## Severity
- **High**: It challenges the fundamental utility of the decomposition for biological systems.

## Suggested Remedies
1.  **Rebranding**: Stop calling it "Passive Drift". Call it **"Constant-Impedance Baseline"**.
2.  **Explicit Definition**: Define the baseline as "The motion of a robot with locked stiffness parameters identical to the golfer's instantaneous active stiffness, but with zero driving torque."
    - *Critique of Remedy*: This is still physically impossible (cannot have active stiffness without active torque).
3.  **Honest Limitation**: Admit that the decomposition attributes *structural support* (impedance) to the Plant, even when that support is metabolically expensive. Ideally, "Input" should capture *everything* the golfer pays for (Torque + Impedance). The current model gives the golfer a discount by putting Impedance in the free "Drift" column.
