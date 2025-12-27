# Critique: Teleological Blindness (Mechanics $\neq$ Intent)

## Summary of Concern

The Drift/Input decomposition ($\tau = \tau_{drift} + \tau_{input}$) is purely mechanical. It identifies *that* a torque was applied, but is structurally blind to *why*.
Specifically, it cannot distinguish between:
1.  **Trajectory Drive:** Torque applied to accelerate the clubhead (Work).
2.  **Impedance Modulation:** Torque applied to stiffen a joint in anticipation of impact (Stability/Stiffness).

In the late downswing, golfers often "brace" for impact. This involves co-contraction and stiffening. In the AffineDrift model, this stiffening torque appears simply as $\tau_{input}$.
If this input opposes the motion (to stiffen), the decomposition labels it as "braking" or "fighting drift". The narrative then becomes "The golfer is inefficiently fighting the club," when in reality, the golfer is "intelligently stabilizing the face."
The framework risks misdiagnosing **Robustness** (good) as **Inefficiency** (bad).

## Location

- **Page:** `articles/affine-nature-golf-swing.qmd`
- **Section:** `sec-drift_input` and `sec-taxonomy`
- **Claim:** "Input forces arising solely from actively applied joint torques." / "Comparing $\tau_{input}$ to $\tau_{ZTCF}$ reveals torque effectiveness."

## Nature of the Issue

- **Interpretational Ambiguity**: The scalar value of $\tau_{input}$ maps to multiple conflicting intents (Move vs. Stiffen).
- **Metric Failure**: "Torque Effectiveness" is defined implicitly as "Does it help speed/path?". It ignores "Does it help robustness?".

## Why This Is a Problem

- **Coaching Risk**: A coach might see a "Braking Input" at impact and instruct the player to "relax and release". If that braking input was actually stabilizing the face against off-center hits, the player gains speed but loses accuracy.
- **Dimensionality Reduction**: The decomposition collapses the $(u_{agonist}, u_{antagonist})$ space into a single net $\tau_{input}$, destroying the information about stiffness.

## Evidence / References

- **Hogan, N. (1985)**. "Impedance control: An approach to manipulation." (Distinction between motion control and interaction control).
- **Burdet, E., et al. (2001)**. "The central nervous system stabilizes unstable dynamics by learning optimal impedance." (Humans stiffen in specific directions).

## Severity

- **Medium**: It limits the *tactical* utility of the theory for coaching, though the *mechanical* decomposition remains valid (Net Torque is Net Torque).

## Suggested Remedies

1.  **Explicit Warning**: "Net Input Torque $\tau_{input}$ aggregates both motion-driving torque and impedance-creating torque (if asymmetrical). A 'braking' torque may be a stability mechanism, not an error."
2.  **Terminology Update**: Avoid terms like "fighting the drift" which imply error. Use neutral terms like "modulating the drift".
3.  **Future Work**: Suggest electromyography (EMG) or detailed muscle modeling to separate Co-contraction (Stiffness) from Net Torque (Drive).
