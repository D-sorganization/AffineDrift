# Critique: Misattribution of Stability (Gravity vs. Inertia) in Putter Design

## Summary of Concern
The article attributes the stability benefits of "Central Spine" putter designs to **Inertial Alignment** (Tensor Diagonalization) and the mitigation of **Secondary Axis Instability** (a dynamic, velocity-dependent phenomenon). This attribution is physically unsound for the putting regime. At putting speeds ($\omega \approx 1-3$ rad/s), the dynamic torques ($\tau_{dyn} \approx \omega \times I \omega$ and $I \dot{\omega}_{parasitic}$) are orders of magnitude smaller than the static gravitational torques ($\tau_{grav} = r \times mg$) caused by off-axis mass distribution. The observed performance benefits likely stem from **Gravitational Balancing** (Zero Torque), not inertial dynamics.

## Location
- **Page:** `articles/secondary-axis-stability.qmd`
- **Section:** "Background: Principal Axes and Rotational Stability" & "Synthesis: The AffineDrift Context"
- **Claim:** That "Inertial Coupling... is a linear effect... where a pure rotation torque applied by the golfer creates parasitic accelerations... dominant in putting."

## Nature of the Issue
- **False Cause Fallacy:** Attributing an effect (stability) to a minor cause (inertia) while ignoring a major cause (gravity).
- **Order-of-Magnitude Failure:** The article fails to compare the magnitudes of competing forces.
- **Physics Blind Spot:** The analysis treats the putter as a generic rigid body but ignores the constant external field (gravity) which is the primary source of instability in handheld pendular motion.

## Why This Is a Problem
A biomechanist or engineer will reject the premise that "Inertial Coupling" is the dominant disturbance in putting.
Comparing torques for a typical putter ($m=0.35$ kg, offset $r=0.02$ m):
1.  **Gravitational Torque (Static):** $\tau_g \approx mgr \sin\theta \approx 0.35 \cdot 9.8 \cdot 0.02 \approx 0.07$ Nm.
2.  **Inertial Coupling Torque (Dynamic):** Assuming aggressive acceleration $\alpha \approx 5$ rad/s$^2$ and significant off-diagonal inertia $I_{xy} \approx 10^{-4}$ kg m$^2$: $\tau_{dyn} \approx I_{xy} \alpha \approx 0.0005$ Nm.

**Result:** Gravity is $\approx 140\times$ stronger than the inertial effect.
By focusing on "Tensor Diagonalization," the article constructs a sophisticated theoretical edifice to explain a phenomenon that is simply "Face Balancing" or "Zero Torque Balance" (placing the CM on the rotation axis). This undermines the credibility of the AffineDrift framework by applying high-speed dynamic theory to a low-speed static problem.

## Evidence / References
- **L.A.B. Golf (Lie Angle Balance):** Explicitly markets "Zero Torque" (gravitational balance) as the mechanism for stability, not inertial alignment.
- **Euler's Equations with Gravity:** $\tau_{net} = I \dot{\omega} + \omega \times I \omega - \tau_{grav}$. In the limit $\omega \to 0$, $\tau_{net} \to -\tau_{grav}$.
- **Standard Putter Design:** "Toe Hang" is quantified by the angle of the face under *gravity*, acknowledging it as the primary force.

## Severity
- **High** (The theoretical justification for the article is physically misplaced).

## Suggested Remedies
1.  **Acknowledge Gravity Explicitly:** The article must admit that for putting, $\tau_{grav} \gg \tau_{inertial}$.
2.  **Reframe the Mechanism:** Argue that "Central Spine" designs likely achieve **both** Gravitational Balancing (placing CM on shaft axis) and Inertial Alignment.
3.  **Preserve the AffineDrift Link:** The argument can be saved by noting that Gravitational Torque is *also* part of the Drift Field $f(x)$ (specifically the potential term $G(q)$).
    - *Correction:* "The Central Spine design stabilizes the drift field $f(x)$ primarily by nullifying the gravitational gradient $\nabla V(q)$ (Face Balancing) and secondarily by diagonalizing the mass matrix $M(q)$ (Inertial Alignment)."
4.  **Retract "Dominant in Putting":** Remove the claim that Inertial Coupling is "dominant" in putting. State it is "present but secondary to gravity," or argue that while gravity is constant, inertial coupling adds *variable* noise during acceleration transients.
