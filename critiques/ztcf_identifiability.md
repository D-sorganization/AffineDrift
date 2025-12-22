# Critique: Identifiability and "Input" as a Residual

## Summary of Concern

The framework defines Input Force via subtraction: $\tau_{\text{input}} = \tau_{\text{total}} - \tau_{\text{drift}}$.
Here, $\tau_{\text{total}}$ is derived from Inverse Dynamics (ID) on measured motion, and $\tau_{\text{drift}}$ is computed from the model.

This structure forces **all unmodeled dynamics** and **measurement noise** into the $\tau_{\text{input}}$ term.
specifically:

1.  **Unmodeled Physics**: Aerodynamic drag, tissue compliance, and marker wobble are not in $f(x)$ (Drift). ID sees their effects in the motion. Thus, the residual $\tau_{\text{input}}$ absorbs them.
    - Example: Drag opposes motion. ID calculates a higher "Net Torque" to explain the motion? No, ID calculates the torque required to _produce_ the observed (damped) motion. Wait.
    - _Correction_: If drag slows the club, $\ddot{q}$ is smaller. ID calculates $\tau_{total} = M \ddot{q} + \dots$. So $\tau_{total}$ is _smaller_. The model drift (without drag) predicts a certain $\tau_{drift}$.
    - If $\tau_{total}$ (measured) < $\tau_{drift}$ (model), then $\tau_{\text{input}}$ becomes negative (braking).
    - So the golfer is "credited" with braking the club, when actually the air did it.
2.  **Noise**: $\ddot{q}$ is noisy. $f(x)$ (Drift) depends on $q, \dot{q}$ (less noisy). $\tau_{\text{input}}$ depends on $\ddot{q}$. So $\tau_{\text{input}}$ inherits all the noise.

The claim that $\tau_{\text{input}}$ isolates "Active Muscular Effort" is false. It isolates "Active Effort + Unmodeled Forces + Noise".

## Location

- **Page:** `articles/affine-nature-golf-swing.qmd`
- **Section:** `sec-ztcf` (Using ZTCF with inverse dynamics)
- **Claim:** "Input forces arising solely from actively applied joint torques."

## Nature of the Issue

- **Empirical Insufficiency**: Sensitivity to model mismatch.
- **Overgeneralization**: Claiming "Exactness" of decomposition when it is structurally sensitive to unmodeled terms.

## Why This Is a Problem

- **False Negatives/Positives**: As shown above, aerodynamic drag could be misinterpreted as "Active Braking" by the golfer.
- **Noise Interpretation**: High-frequency noise in $\tau_{\text{input}}$ might be over-interpreted as "twitchy" control or high-frequency muscle inputs, when it is just differentiation noise.

## Evidence / References

- **Southgate, D. F., et al. (2009).** Sensitivity of inverse dynamics to errors in input data.
- **Hatze, H. (2002).** The fundamental problem of myoskeletal inverse dynamics.

## Severity

- **High**: It compromises the physical interpretation of the results, specifically the "Soleness" of the attribution.

## Suggested Remedies

1.  **Relax "Solely" Claim**: Change "arising solely from active torques" to "**containing** the active torque contribution (plus unmodeled residuals)".
2.  **Explicit Noise Model**: Discuss how noise propagates.
3.  **Aerodynamic Correction**: Explicitly recommend including aerodynamics in the Drift model if outdoor swings are analyzed, to prevent "Active Braking" artifacts.
4.  **Inline Edit**: In Section `sec-limitations` (Data and parameter limitations), add:
    > "Because $\tau_{\text{input}}$ is calculated as a residual ($\tau_{\text{total}} - \tau_{\text{drift}}$), it absorbs all unmodeled external forces (e.g., aerodynamics) and measurement errors. For example, unmodeled aerodynamic drag will reduce the observed acceleration, causing Inverse Dynamics to compute a lower total torque; the decomposition will attribute this deceleration to a negative 'braking' input by the golfer. Thus, $\tau_{\text{input}}$ should be interpreted as the 'Net Non-Conservative Forcing' rather than pure muscular torque in the presence of modeling errors."
