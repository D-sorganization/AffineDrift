# Critique: Causal Masking in Drift Superposition

## Summary of Concern
The framework relies on the "Superposition of Drift and Input" ($\dot{x} = f(x) + g(x)u$) to attribute causality. It labels $f(x)$ as "Passive Drift" and $g(x)u$ as "Input". While this is algebraically true *at an instant*, it is causally misleading *over time*.

A significant portion of $f(x)$ (specifically the velocity-dependent terms: Coriolis, Centrifugal, Damping) is directly "induced" by the magnitude of previous inputs. For example, a high centrifugal force (Drift) exists only because the golfer previously applied torque (Input) to accelerate the system. By categorizing these forces as "Drift" (and implying they are "Passive" or "Free"), the framework obscures the fact that the golfer *paid* for them energetically in the past.

This creates a "Causal Masking" effect where the *consequence* of effort (velocity-dependent drift) is dissociated from the *source* of effort (input).

## Location
- **Page:** `articles/affine-nature-golf-swing.qmd`
- **Section:** `sec-drift_invariance` and `sec-taxonomy`
- **Claim:** "Drift represents what the system would do 'on its own'... Input forces arising solely from actively applied joint torques."

## Nature of the Issue
- **Logical Gap**: Confusing "Instantaneous Affine Independence" with "Causal Independence".
- **Interpretational Risk**: Risk of interpreting "Drift" as "Exogenous Assistance" rather than "System Response".

## Why This Is a Problem
- **Coaching Misinterpretation**: A coach might see high "Drift Force" and conclude the swing is efficient ("letting the club do the work"). In reality, high Drift Force (e.g., centrifugal) requires high Input energy to establish.
- **Optimization**: Maximizing "Drift" share of total force might essentially just mean "Maximizing Velocity", which requires Maximizing Input. It doesn't necessarily imply mechanical advantage, just high energy states.

## Evidence / References
- **Lynch, K. M., & Park, F. C. (2017).** *Modern Robotics*. (Definition of Coriolis forces as quadratic in velocity).
- **Spong, M. W. (2005).** *Robot Control Systems*. (Passivity vs. Zero Dynamics).

## Severity
- **Medium**: It affects the *narrative* and *interpretation*, not the equation correctness.

## Suggested Remedies
1.  **Refine Taxonomy**: Distinctly separate **"Base Drift"** (Gravity, Stiffness - truly passive/potential) from **"Induced Drift"** (Coriolis, Centrifugal, Inertial - kinetic/history-dependent). The ZVCF already helps this, but the text should be explicit.
2.  **Causal Warning**: Add a warning that "Velocity-dependent drift forces are passive in mechanism but active in origin (historically induced by input)."
3.  **Inline Edit**: In Section `sec-taxonomy` (Category 2):
    > "Note: While classified as 'Drift' because they do not depend on *instantaneous* torque, these velocity-dependent forces are causally linked to *prior* torque inputs that established the system's velocity. They represent the 'kinetic momentum' of the swing, not an exogenous source of energy."
