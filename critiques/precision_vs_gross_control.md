---
title: 'Critique: Precision vs. Gross Control (The "locked-in" Fallacy)'
description: 'Critique and response context for Precision vs. Gross Control (The "locked-in" Fallacy) in AffineDrift''s control-affine golf-swing framework.'
---

## Critique: Precision vs. Gross Control (The "locked-in" Fallacy)

## Summary of Concern

The article `articles/controllability-drift-ratio.qmd` argues that because the Drift-Control Ratio (DCR) exceeds 100 in the late downswing, the system becomes effectively uncontrollable ("locked in a drift tube"). It implies that "No meaningful correction is possible." This conflates **Gross Trajectory Control** (reversing or reshaping the swing) with **Fine Outcome Control** (adjusting impact parameters by millimeters or degrees). A 1% control authority on a high-energy system is insufficient to stop the swing, but potentially sufficient to alter the impact location or face angle by the small margins required for error.

## Location

- **Article:** `articles/controllability-drift-ratio.qmd`
- **Section:** 5 (Control Authority Collapse), 6.5 (Application to the Golf Swing)
- **Claim:** "Late Downswing — Cone Collapse... Only the ballistic trajectory remains reachable. No meaningful correction is possible."

## Nature of the Issue

- **Logical Gap:** The magnitude of the _total_ state vector (dominated by drift) is compared to the _control_ vector to infer uncontrollability. However, the _tolerance_ for success in golf is extremely small (degrees, millimeters).
- **Scaling Error:** If Drift Acceleration $\approx 1000 \text{ rad/s}^2$ and Control Acceleration $\approx 10 \text{ rad/s}^2$ (DCR=100), the integrated control effect over 50ms ($\Delta t = 0.05$) is $\Delta \theta \approx 0.5 \cdot 10 \cdot (0.05)^2 = 0.0125$ rad $\approx 0.7^\circ$.
- $0.7^\circ$ of face angle change results in lateral errors of ~3-5 yards at 250 yards. This is a "meaningful correction."
- The text implies that because you cannot _stop_ the train, you cannot _switch tracks_. But switching tracks only requires small lateral forces.

## Why This Is a Problem

- **Control Theorists** will object that "Controllability" is usually binary (Kalman rank condition). If the author means "Reachability Sets are small," they must quantify "small" relative to the _target set_, not the _state space_.
- **Biomechanists** know that fine motor control operates at the margins of max force. "Steering" is exactly what happens in the last 50ms (e.g. wrist maneuvers).
- It undermines the "Dominant Attractor" claim. If the golfer can still steer the ball into the rough vs the fairway, the ZTCF is not a strong enough attractor to dictate the _outcome_, only the _energetics_.

## Evidence / References

- **Todorov (2004):** _Optimality principles in sensorimotor control_. Emphasizes "minimum intervention" principle—control is used only in task-relevant dimensions. The task-relevant manifold is narrow.
- **Loftin et al. (2004):** _Precision of the golf swing_. Variability at impact is small, implying active regulation or repeatable initial conditions.
- **Scaling Analysis:** $1\%$ authority on $45 \text{ m/s}$ is $0.45 \text{ m/s}$. That's enough to miss the ball entirely.

## Severity

**High**.
The claim "No meaningful correction is possible" is empirically false (golfers do manipulate shots late) and mathematically unsupported by the DCR magnitude alone. It risks discrediting the valid insight about "Gross" ballistic dominance.

## Suggested Remedies

### 1. Distinguish Macro vs. Micro Control

**Location:** Section 5 or 6.
**Suggestion:**
Explicitly state that DCR prohibits **Macro-Correction** (e.g., fixing a slice into a draw, stopping the swing) but may permit **Micro-Correction** (steering impact location).

> **Refinement:** "While the golfer cannot strictly _reshape_ the trajectory (Macro-Control), the residual control authority ($\approx 1\%$) may still be sufficient to alter face angle or path by the small margins (degrees, millimeters) that define success (Micro-Control). However, this micro-control operates under extreme signal-to-noise constraints."

### 2. Quantify the "Drift Tube" Diameter

**Location:** Section 6.5.
**Suggestion:**
Calculate the radius of the reachable set at impact. If it's $\pm 2^\circ$, admit that this covers the entire range of "Fairway vs. Out of Bounds."

### 3. Reframe "Locked In"

**Location:** Abstract and Intro.
**Suggestion:**
Change "Practical Controllability collapses" to "Gross Trajectory Authority collapses."

## Editorial Adjudication and Evidence Boundaries

1. **Historical Versus Corrected State:**
   The historical article asserted that late in the downswing "no meaningful correction is possible" and claimed that the golfer becomes "locked into a ballistic trajectory". In the corrected article (`articles/controllability-drift-ratio.qmd`, audited in `reports/technical-review/dcr-complete-review.md`), these claims were removed. The article explicitly specifies that instantaneous acceleration ratios do not quantify finite-horizon reachability sets, task-space clubhead delivery tolerances, or terminal impact sensitivity.

2. **Critique Boundary and Counterexamples:**
   While the critique properly distinguishes gross kinetic deflection from fine terminal adjustments, the critique itself oversteps its evidence boundaries:
   - **Simplistic kinematic integration:** The critique posits a constant acceleration integration over 50 ms ($\Delta \theta \approx 0.5 \cdot a \cdot \Delta t^2$) yielding $0.7^\circ$ of face angle change. In a coupled multibody system, control torques pass through configuration-dependent inertia and Coriolis matrices; single-channel acceleration cannot be directly integrated into face orientation without accounting for dynamic coupling and neuromuscular force development rate limits.
   - **Velocity percentage fallacy:** The critique claims that "1% authority on 45 m/s is 0.45 m/s". DCR is a ratio of acceleration vectors, not velocity magnitudes; control authority cannot be interpreted as a percentage scalar of clubhead linear speed.
   - **Impact sensitivity:** As derived in `tests/test_dcr_article_rigor.py::test_task_event_time_response_matches_an_exact_contact_solution`, terminal impact outcomes require exact event-time sensitivity analysis with transversality conditions ($\frac{\partial t^*}{\partial x}$), which are entirely absent from both the original DCR text and the critique's back-of-the-envelope calculations.
