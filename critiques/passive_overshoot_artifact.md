# Critique: Passive Overshoot Artifact (Simulink "Proof")

## Summary of Concern

The Simulink "Proof of Concept" claims that "Passive momentum contributions can exceed total forces temporarily."
**The Weakness:** This "overshoot" (where passive force > total force, implying negative/braking input) might be an artifact of the "Skeletal Baseline" having insufficient damping.
A real arm/wrist complex has significant viscoelasticity. If the model uses low-friction joints to represent the "Skeleton," it will swing more wildly (overshoot) than a real passive arm would.
Thus, the "negative input" identified might just be the golfer "paying" to emulate the damping that the model forgot to include.

## Location

- **Page:** `articles/affine-nature-golf-swing.qmd`
- **Section:** `Simulink Forward Dynamics Modeling`
- **Claim:** "Passive momentum contributions can exceed total forces temporarily, indicating competing active and passive effects."

## Nature of the Issue

- **Model Mismatch**: Under-damped model $\rightarrow$ Exaggerated Drift $\rightarrow$ False "Braking" Input.
- **Interpretation Error**: The golfer isn't "braking" the club; they are just having normal joint viscosity. The model _thinks_ they are braking because the model's joints are frictionless.

## Why This Is a Problem

- It creates a "Ghost Force". The taxonomy labels "Viscosity" as "Input" (braking torque).
- It leads to incorrect coaching advice ("Stop braking the club!").
- It invalidates the claim that the Simulink model "validates" the theory. It only validates the _math_, not the _physics_.

## Evidence / References

- **Winters, J. M. (1990).** Hill-based muscle models: A systems engineering perspective. (Passive viscosity is significant).
- **Damping Ratios**: Human joint damping ratios are often $\zeta \approx 0.1 - 0.5$ depending on activation. Steel pin joints are $\zeta \approx 0.001$.

## Severity

- **Medium/High**: It biases the numerical results significantly.

## Suggested Remedies

1.  **Damping Sensitivity Analysis**: Run the Simulink model with variable joint damping coefficients ($b = 0.1, 0.5, 1.0$ Nms/rad).
2.  **Conservative Claim**: Change "Passive momentum exceeds total" to "Passive momentum _component_ is significant."
3.  **Viscosity Term**: Add a specific $-\Gamma \dot{q}$ term to the Drift field $f(x)$ to model passive tissue viscosity, separate from the "Skeletal" structure.
