# Critique: Double Pendulum Energy Blindness

## Summary of Concern

The "Energy Transfer Decomposition" in `articles/drift-components-wrench-double-pendulum.qmd` (Section 6) analyzes power flow in a **rigid** double pendulum. This analysis is structurally blind to the primary energy transfer mechanism in the AffineDrift framework: the storage of active work as **elastic potential energy** in the shaft and its subsequent passive release.
By presenting a rigid power analysis as a general "drift vs active" model, the article implicitly suggests that kinematic transfer (centripetal pull) is the only passive energy mechanism, ignoring the "Catapult Effect" of the flexible shaft.

## Location

- **Article:** `articles/drift-components-wrench-double-pendulum.qmd`
- **Section:** 6. Energy Transfer Decomposition

## Nature of the Issue

- **Overgeneralization**: Applying rigid body power analysis to a system whose core novelty is flexibility.
- **Omission of Key Physics**: The term $\dot{V}_{elastic}$ is missing.
- **Conceptual Conflict**: Contradicts Part 1, which emphasizes $V_{elastic}(\eta)$ and $M_{q\eta}$ as critical.

## Why This Is a Problem

1.  **Misleading Intuition**: A reader might conclude that "Active Power" is just torque $\times$ angular velocity, missing the fact that torque often does work _against the spring_ (increasing $V_{elastic}$) rather than increasing kinetic energy directly.
2.  **Incomplete Taxonomy**: The distinction between "Natural" and "Active" power is incomplete without an "Elastic" buffer.

## Severity

- **Medium**: It limits the explanatory power of the double pendulum example but doesn't invalidate the main theory.

## Suggested Remedies

1.  **Explicit Disclaimer**: Add a note that this rigid model ignores elastic storage.
2.  **Augmented Equation**: Show how the equation changes if a spring is added (even a torsional spring at the joint).
3.  **Link to Part 1**: Refer the reader to `theory-part1.qmd` for the full elastic energy formulation.
