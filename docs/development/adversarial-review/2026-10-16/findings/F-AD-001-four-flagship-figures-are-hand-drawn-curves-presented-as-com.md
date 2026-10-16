# F-AD-001

**Four flagship figures are hand-drawn curves presented as computed results**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟥 Critical | docs | high | M | proposed |

**Locations:** `scripts/core_theory_figures/ztcf.py:43`, `scripts/core_theory_figures/ztcf.py:178`, `scripts/core_theory_figures/ztcf.py:199`, `scripts/core_theory_figures/ztcf.py:290`, `scripts/core_theory_figures/superposition.py:303`, `articles/zero-torque-counterfactual.qmd:18`

## Finding

- Severity: Critical  - Category: docs / correctness
- Confidence: high
- Location: scripts/core_theory_figures/ztcf.py:41-46, 57-61, 177-178, 191-192, 286-297; scripts/core_theory_figures/superposition.py:296-303; articles/zero-torque-counterfactual.qmd:18, 22, 210, 214, 233, 286, 289; articles/superposition.qmd:199
- Evidence:
  ```python
  # ztcf.py:43-46  "Active baseline planar trajectory"
  theta_active = np.linspace(2.2, 0.0, 100)
  r_active = 1.6 - 0.2 * np.cos(theta_active)
  # ztcf.py:178   v_active = 48.2 / (1.0 + np.exp(-25.0 * (t - 0.19)))
  # ztcf.py:199   label="ZTCF at 100 ms (-62% speed)"
  # ztcf.py:290   acc_active = 350.0 * np.sin(np.pi * t / 0.25) * np.exp(-4.0 * (t - 0.12) ** 2)
  # superposition.py:303  traj_exact = traj_superposed + 18.0 * t**3 + 120.0 * t**4   # labelled "Exact Nonlinear"
  ```
  The article captions: "Decomposition of Distal Club Acceleration Into Active Muscular Torque $M^{-1}\tau$, Passive
  Interaction/Coriolis Coupling $-M^{-1}C\dot{q}$, and Gravitational Acceleration $-M^{-1}g$" (qmd:233); long
  description "quantitatively proving that late muscular forcing contributes minimally" (qmd:289); front-matter
  `evidence-level: "Simulation (Qualified Multi-Body)"` (qmd:22). No "schematic" or "illustrative" label anywhere.
- Failure scenario: a referee reproduces Fig. "clubhead speed loss" from the linked model and gets different
  numbers; or notices `M^{-1}\tau` was never computed. In a paper whose product is credibility this is the finding
  that ends the review. Internally, the trust ledgers pin these SVGs' SHA-256 as "evidence", so the apparatus
  certifies invented data.
- Why a newer engineer misses this: an LLM asked for "a figure showing X" will cheerfully draw X; nothing in the
  pipeline distinguishes a diagram from a plot of model output, and the caption generator is the same agent.
- Proposed change: regenerate all four from `GolfModel`/`double_pendulum_affine` (`ztcf_explorer.explore` already
  produces actual-vs-branch trajectories and speeds; `SwingAnalysis.joint_acceleration_components` produces the
  M⁻¹τ / −M⁻¹Cq̇ / −M⁻¹g split; `simulate` gives the superposition comparison). If a figure must stay schematic, add
  "Schematic, not model output" to title, caption, alt text and the long description, and drop every number from
  the legends.
- Verification: a test that imports the figure builder, extracts the plotted arrays, and asserts they equal
  (atol 1e-12) arrays recomputed from the model; grep that no `np.exp(-k*(t - t0))` logistic appears in
  `scripts/core_theory_figures/`.
- Effort: M

## Draft Pull Request

**Title:** `fix(figures): generate ZTCF and superposition figures from GolfModel`

### Why This Matters (The Pitch)

A referee who reruns the model and cannot reproduce the clubhead-speed figure ends the review, and this finding says that is exactly what is on offer today. Four flagship figures in the ZTCF and Superposition articles are logistic, sine and power-law curves drawn by hand, yet they are captioned as computed trajectories and decompositions, carry legends like "-62% speed" and "48.2 m/s", and one series is literally labelled "Exact Nonlinear". The front matter claims "Simulation (Qualified Multi-Body)" and no page says schematic. Worse, the trust ledgers pin these SVGs by SHA-256 as evidence, so the apparatus certifies invented data. The fix is cheap relative to the exposure: a working GolfModel, ztcf_explorer and SwingAnalysis already produce the real arrays, and the finding sizes the work at M. Do this before anything else in the manuscript queue, because every other correct thing in the kernel is overshadowed if the figures are not model output. The authors, and the journal reviewers who decide the paper's fate, benefit first.

### Proposed PR Body

## Problem
The figure builders in `scripts/core_theory_figures/ztcf.py:43-46, 178, 199, 290` and `scripts/core_theory_figures/superposition.py:303` plot hand-written curves (e.g. `48.2 / (1.0 + np.exp(-25.0 * (t - 0.19)))`, and `traj_exact = traj_superposed + 18.0 * t**3 + 120.0 * t**4`). `articles/zero-torque-counterfactual.qmd:22, 233, 289` and `articles/superposition.qmd:199` present them as computed decompositions and model results with quantitative legends. No page labels them schematic.

## Change
- [ ] Regenerate all four figures from `GolfModel` / `double_pendulum_affine`, using `ztcf_explorer.explore`, `SwingAnalysis.joint_acceleration_components` and `simulate`
- [ ] If any figure must stay schematic, add "Schematic, not model output" to title, caption, alt text and long description, and remove every number from its legend

## Verification
Add a test that imports the figure builder, extracts the plotted arrays, and asserts they equal (atol 1e-12) arrays recomputed from the model. Grep that no `np.exp(-k*(t - t0))` logistic remains in `scripts/core_theory_figures/`.

## Risk and Rollback
Changes are confined to figure scripts, captions and the tests; reverting the commit restores the old figures. Expect visibly different curves and legend numbers, which is the point.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** Follow-ups: deploy cache staleness (F-AD-010) so returning readers see the new SVGs; ledger regenerate for changed SVG digests.

Refs: adversarial review 2026-10-16, F-AD-001


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
