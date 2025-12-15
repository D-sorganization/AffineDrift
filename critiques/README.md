# Critique of AffineDrift Scientific Claims

This directory contains a catalog of scientific critiques identifying weaknesses, unjustified assumptions, and potential errors in the theoretical frameworks presented on the AffineDrift website.

## List of Critiques

1.  **[Affine Control Assumptions](affine-control-limitations.md)**
    *   **Topic:** The modeling of the golfer as a control-affine system $\dot{x} = f(x) + g(x)u$.
    *   **Weakness:** Ignores force-velocity/force-length properties of muscle (Hill-type models), treating torque as an independent input. Omission of aerodynamic drag leads to false attribution of "Input" forces.
    *   **Status:** Fundamental modeling oversight.

2.  **[Strokes Gained Limitations](strokes-gained-limitations.md)**
    *   **Topic:** The argument that population-based Strokes Gained metrics fail for individuals.
    *   **Weakness:** While theoretically true that $J_{ref} \neq J_i$, the critique ignores the statistical impossibility of estimating $J_i$ for individuals (variance vs bias trade-off). The proposed "divergence" of gradients is unproven empirically.

3.  **[Counterfactual Validity](counterfactual-validity.md)**
    *   **Topic:** The Zero Torque (ZTCF) and Zero Velocity (ZVCF) counterfactuals.
    *   **Weakness:** "Zero Torque" is biologically impossible (ignoring passive muscle stiffness/damping). "Zero Velocity" provides static analysis for a dominated-by-dynamics system.

4.  **[Secondary Axis Instability](secondary-axis-instability.md)**
    *   **Topic:** Application of the Intermediate Axis Theorem to putting.
    *   **Weakness:** The instability scales with $\omega^2$. At putting speeds (< 2 rad/s), the effect is negligible compared to grip stiffness. The trade-off (50% MOI reduction) is likely detrimental.

5.  **[Wrist Universal Joint Model](wrist-model-anatomy.md)**
    *   **Topic:** Modeling the wrist as a 2-DOF Universal Joint with "uncontrollable" constraint torques.
    *   **Weakness:** Anatomically incorrect. The "constrained" axis (forearm rotation) is fully actuated by pronator/supinator muscles. The "constraint torque" is actually a dynamic coupling term that can be actively managed.
