# Critique: Coulomb Friction Violation of Drift Invariance

## Summary of Concern
The central proof of **Drift Invariance** (Proposition 1) asserts that the drift vector field $f(x)$ is independent of the input $u$ ($\nabla_u f(x) \equiv 0$). This proof relies on the assumption that all passive forces (included in $h(x)$) depend only on state $(q, \dot{q})$.

However, real mechanical systems contain **Coulomb friction** at joints, where $\tau_{fric} = \mu F_N \operatorname{sgn}(\dot{q})$. The normal force $F_N$ is a component of the constraint force vector, which depends explicitly on the applied acceleration and thus the input torque $u$ (via the Constraint Jacobian).
Therefore, in the presence of realistic dry friction, the passive resistance $f(x)$ becomes a function of $u$, violating the affine structure $\dot{x} = f(x) + g(x)u$.

## Location
- **Page:** `articles/theory-part3.qmd`
- **Section:** `Drift Invariance and Input Constraints` (Proposition 1)
- **Claim:** "The drift vector field $f(x)$ is invariant with respect to the control input $u$... friction terms are linear in velocity (viscous)."

## Nature of the Issue
- **Modeling Assumption Failure**: The proof assumes only viscous damping ($D\dot{q}$). It ignores dry friction, which is significant in loaded biological joints and mechanical linkages.
- **Mathematical Inconsistency**: If Coulomb friction is present, the system is no longer control-affine. The decomposition $\tau_{input} = \tau_{total} - \tau_{drift}$ fails because $\tau_{drift}$ cannot be calculated without knowing $\tau_{input}$.

## Why This Is a Problem
1.  **Exactness Claim**: The paper claims the decomposition is "analytically exact" for the model. This is only true for a specific, friction-simplified model.
2.  **Magnitude**: In high-load scenarios (like the golf downswing where joint reaction forces are huge), the friction variation due to input-induced normal force loading could be non-negligible. The "passive" resistance increases as the player pushes harder.
3.  **Causal Leakage**: A portion of the "Input" (effort) is instantly consumed by the "Drift" (friction increase) it creates. The ZTCF (where $u=0$) would underestimate the friction present in the actual swing, making the "Drift" look more efficient than it is.

## Evidence / References
- **Featherstone, R. (2008).** *Rigid Body Dynamics Algorithms*. (Constraint forces depend on applied forces).
- **Pain, M. T. G., & Challis, J. H. (2006).** "The influence of soft tissue movement on ground reaction forces..." (Joint reaction forces in biomechanics).

## Severity
- **Medium**: It limits the "Exactness" claim but likely doesn't destroy the macro-level utility of the framework for swinging motions (where inertial forces dominate friction).

## Suggested Remedies
1.  **Explicit Exclusion**: Add "Coulomb Friction" to the list of "Limitations" (alongside Aerodynamics).
2.  **Justification**: Argue that for high-speed ballistic motions, inertial terms ($M\ddot{q} \sim \omega^2$) dominate frictional terms, making the viscous approximation acceptable.
3.  **Refined Claim**: Change "Structurally Independent" to "Structurally Independent (under the assumption of viscous-only damping)".
