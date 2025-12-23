# Critique: Parameter Causality Leakage

## Summary of Concern

The claim that the decomposition isolates "Active" from "Passive" forces rests on the assumption that the passive parameters ($M, K, C$) are known exactly (Assumption 8) and represent the purely passive system.
However, in practice, these parameters are often identified or tuned using swing data (where the golfer is active).
If parameters are fit to minimize residual error on active motion, the "Passive" model will inevitably absorb some "Active" effects.

## Location

- **Page:** `articles/affine-nature-golf-swing.qmd`
- **Section:** `sec-drift_input` (Drift vs Input Decomposition)
- **Claim:** "The decomposition is analytically exact... in practice it is limited by parameter accuracy."

## Nature of the Issue

- **Methodological Circularity**: The "Nature" baseline is contaminated by the "Golfer" data used to define it.
- **Hidden Assumption**: That parameters identified from active motion separate cleanly into passive mechanical constants.

## Why This Is a Problem

1.  **Co-contraction Masquerading as Stiffness**: If a golfer co-contracts muscles to stiffen joints/shaft coupling, and the model is fit to this data, the identified "Passive Stiffness" ($K$) will be artificially high.
2.  **Causal Leakage**: The "Drift" term (using high $K$) effectively includes the active stiffening. The "Input" term (residual) will show _less_ input than actual.
3.  **Result**: The golfer's active impedance control is reclassified as "Passive Drift", exaggerating the "swinging itself" narrative.

## Evidence / References

- **Gomi & Kawato (1997)**. "Human arm stiffness during discrete point-to-point movements." (Shows stiffness varies with command).
- **Ljung, L. (1999)**. "System Identification." (Parameter bias when closed-loop dynamics are identified).

## Severity

- **Medium**: It weakens the empirical claims (Part II/III) more than the theory (Part I), but the theory must acknowledge this vulnerability.

## Suggested Remedies

1.  **Strict Identification Protocol**: Mandate that passive parameters (especially stiffness/damping) be identified from **passive experiments** (e.g., static deflection tests, pendulum drop tests) or physics-based estimation, _never_ from the active swing data itself.
2.  **Variable Impedance Acknowledgement**: Explicitly state that if parameters are constant, they cannot capture time-varying impedance control, so "Drift" represents the "Constant-Parameter Skeletal Baseline" only.
