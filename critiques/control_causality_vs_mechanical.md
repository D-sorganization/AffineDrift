# Critique: Control Causality vs. Mechanical Causality

## Summary of Concern

Assumption 5 defends the model against reflex-loop objections by distinguishing "Control Causality" (neural intent) from "Mechanical Causality" (force origin).
**The Weakness:** This distinction is technically valid but functionally useless for analyzing human movement. In biological systems, the "Mechanical Causality" is _downstream_ of the "Control Causality" in a way that makes separating them arbitrary. If a reflex loop ($u = -Kx$) is fast enough, the system _mechanically behaves_ like a spring. Insisting on calling it "Input" because it comes from a muscle, rather than "Drift" because it acts like a spring, misclassifies the functional behavior of the system.

## Location

- **Page:** `articles/affine-nature-golf-swing.qmd`
- **Section:** `Limitations` -> `Mechanical vs. Control Causality`
- **Claim:** "The ZTCF answers the question: 'Regardless of the complex sensory-motor loops... what would the system have done if that input were instantaneously removed?'"

## Nature of the Issue

- **The "So What?" Problem**: If the "input" ($u$) is effectively a feedback law ($u(x)$) determining the system's impedance, then removing it ($u=0$) creates a counterfactual that never happens and _cannot_ happen.
- **Arbitrary Boundary**: Why is the tendon (passive) part of Drift, but the short-latency reflex (active but automatic) part of Input? Both are "spring-like" to the conscious brain.
- **Identifiability**: We cannot measure $u$ separate from passive mechanics in vivo without invasive nerve blocks. The model assumes we can know $u$, but we only know $\tau_{net}$.

## Why This Is a Problem

- It makes the theory "physically true but biologically irrelevant."
- It ignores the concept of **synergy** and **impedance control** (Hogan, 1985), which are foundational in modern motor control.
- A control theorist would say: "You are analyzing the open-loop plant, but the human is a closed-loop system. Your 'Drift' is the plant, but the _effective_ plant includes the reflexes."

## Evidence / References

- **Todorov, E. (2004).** Optimality principles in sensorimotor control. (Feedback laws define the dynamics).
- **Latash, M. L.** (2008). Synergy. (Uncontrolled manifold hypothesis).

## Severity

- **High**: It threatens the applicability of the framework to real human data.

## Suggested Remedies

1.  **Impedance Term**: Ideally, split dynamics into $\dot{x} = f(x) + h(x, u_{stiffness}) + g(x)u_{torque}$.
2.  **Reflex Admission**: Explicitly state that "Drift" includes _only_ physics, not reflexes. "Input" includes _all_ neural activity, reflexive or voluntary.
3.  **Functional Grouping**: Acknowledge that for the _golfer_, high impedance feels like "Drift" (stability), even if the model labels it "Input" (cost). The taxonomy should perhaps distinguish **"Stabilizing Input"** vs **"Driving Input"**.
