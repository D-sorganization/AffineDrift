# Critique: Geometric Stiffness and Centrifugal Stiffening Omission

## Summary of Concern
The modeling assumption of a "Finite-dimensional modal approximation" (Assumption 2) with constant modal stiffness matrix $K_s$ (Section A.1) likely omits **Geometric Stiffness** (Centrifugal Stiffening). In high-speed rotation, tension significantly increases the transverse stiffness of the shaft. By using a linear beam model with constant stiffness, the "Drift" field $f(x)$ underestimates the passive restoring forces at high swing speeds.

## Location
- **Page:** `articles/affine-nature-golf-swing.qmd`
- **Section:** `Assumption 2`, `Appendix B (Modal Approximation)`
- **Equation:** $F_s(\eta, \dot{\eta}) = K_s \eta + C_s \dot{\eta}$ (where $K_s$ is constant).

## Nature of the Issue
- **Modeling Deficit**: Physics omission.
- **Validity**: The passive baseline ($f(x)$) is physically inaccurate for high-speed dynamics.

## Why This Is a Problem
1.  **Underestimated Drift**: At high angular velocities ($\dot{q}$), the real shaft is stiffer than the model. The model predicts a "softer" passive response.
2.  **Misattribution**: Since Input is calculated as a residual ($\tau_{input} = \tau_{total} - \tau_{drift}$), the forces arising from centrifugal stiffening (which are passive) are not captured in $\tau_{drift}$. Consequently, they leak into $\tau_{input}$.
3.  **Artifacts**: The golfer may be credited with "active stiffening" or "active recoil control" that is actually purely passive geometric mechanics.

## Evidence / References
- **Sim, H. et al. (1991)**. "Dynamic stiffening of rotating beams." (Centrifugal force increases natural frequencies).
- **Mayo, J. et al. (2000)**. "The effect of centrifugal stiffening on the deflection of a golf club shaft." (Demonstrates significant effect at swing speeds).

## Severity
- **Medium/High**: It affects the core claim of "exact" decomposition in the most critical phase of the swing (late downswing/impact).

## Suggested Remedies
1.  **Explicit Modeling**: Include a velocity-dependent stiffness term $K_{geo}(\dot{q})$ in the Drift field.
    - Note: This preserves Affine Structure (since it depends on $\dot{q}$, not $u$).
2.  **Disclaimer**: If explicit modeling is out of scope, add a limitation stating that "Linear modal analysis neglects geometric stiffness, potentially underestimating passive restoring forces at high speeds."
3.  **Refine ZVCF**: Note that ZVCF (Zero Velocity) inherently removes geometric stiffness (which scales with $\dot{q}^2$). Thus, ZVCF represents the "static" stiffness, not the "dynamic" stiffness experienced during the swing.
