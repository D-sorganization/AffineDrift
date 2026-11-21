# Option A Comparison Results — 2026-11-10

Simulation only. One MuJoCo swing-and-recovery fixture, eight preregistered perturbation
trials, rad-space state (`recovery_threshold_rad` = 0.40, tracking baseline 0.28 rad). No
participant data, no cross-engine check, and no contact-rich skills.

## Summary

Correction-authority detection uses the offline LTV Gramian evaluator on measured one-step
residuals with a declared joint-angle task direction; the tracking-error baseline times are
vendored with the trace. On the two labelled **unrecoverable** trials, correction authority
flags earlier than the tracking baseline (median lead-time advantage about 0.033 s before
horizon-end failure). On all six **recovered** trials, correction authority also flags
(`false_positive_rate` = 1.0), so preregistered prediction **H-CA-LEAD** is recorded as **null**,
not supported. Rad-space versus planar distal-tip pass/fail labels agree on every trial
(disagreement rate 0.0); metre-space readout is not guaranteed by the rad-space bound.

## Limits

Coordinates, horizon (0.35 s), torque cap, and perturbation grid are fixed. Assessment Board
sign-off remains required before any public correction-authority claim.

Evidence: `data/humanoid_robotics/option_a/comparison_result_v1.json`,
`src/affine_control/option_a_comparison.py`, `tests/test_option_a_comparison.py`.
