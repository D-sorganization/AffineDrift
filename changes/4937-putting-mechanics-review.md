---
issue: 4937
summary: "Correct putting contact, slope, calibration and pendulum mechanics"
dl_state: "in_progress"
next_step: "Finish rendered inspection and frozen regression, then open a regular PR after workbench review"
owner: "codex"
branch: "fix/putting-mechanics-review"
---

Review the complete putting chapter in LaTeX and Quarto, and the golf book nomenclature. Separate stroke mechanics, impact transfer and surface contact. Replace zero-spin and fixed-skid claims with a signed slip model; include rolling inertia on slopes; distinguish an effective resistance moment from sliding friction; correct period/half-period comparisons and the unsupported passive-pendulum explanation of a universal tempo. Correct the putting citations against primary sources.

The existing chapter was absent from both book contents lists. A failing publication test reproduced that omission; both lists now include it. Nomenclature now distinguishes coordinates from speeds, actuator maps from selection matrices, multipliers from Cartesian forces, and virtual work from actual power of moving constraints.

Detailed reasoning, primary-source scope, rejected Flash findings, independent calculations and delivery instructions are in docs/development/technical-review/putting-mechanics-review/review-notes.md. This review does not certify a coaching prescription, human experiment or all pages of the rebuilt book. No corpus acceptance until the frozen regression and scoped visual review pass.
