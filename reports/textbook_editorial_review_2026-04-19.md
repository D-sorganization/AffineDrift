# Textbook Editorial Review - 2026-04-19

Automation: Textbook Reviews
Reviewer stance: senior commissioning editor for rigor, source quality, notation, structure, and tone.
Scope: Drifter Manifesto, Dynamics / Geometry Is Motion, and Golf Biomechanics and Modeling in the AffineDrift repository.

## Executive Assessment

This pass tightened the books at the point where ambitious interpretive claims were beginning to outrun stated assumptions. The main editorial risk was not lack of conceptual coherence; it was insufficient boundary-setting around ratios, phase variables, muscle-to-joint mappings, and impact estimates. The edits therefore focus on making the manuscripts more publication-safe: modeling claims are now marked as model-bound, numerical ratios require explicit reporting standards, and notation has been made more defensible where it maps muscle forces into joint torques.

The strongest remaining issue is reproducibility. Chapter 6 now states a minimum reporting standard for the Drift-Control Ratio (DCR), but a full sensitivity appendix with numerical parameter sweeps still needs to be built. That should be the next substantial pass before stronger language about drift dominance is allowed to stand.

## Source Edits Made

### Drifter Manifesto

- Added an evidence-standard callout to distinguish research-program language from established clinical, coaching, or universal mechanical claims.
- Clarified that ratios, phase labels, and counterfactuals require a stated model, parameter set, sensitivity check, and data source before being treated as evidence.

Edited file:

- `pages/drifter-manifesto.qmd`

### Dynamics / Geometry Is Motion

- Replaced overconfident phase-variable language with a model-bound account of clock time, progress coordinates, saturation, and failure cases.
- Added a guardrail that phase coordinates require a domain, monotonicity condition, reset behavior, and explicit failure modes.
- Corrected a control-affine notation inconsistency from `g(x)u` to `G(x)u`.
- Mirrored the phase-variable edits in both the current Geometry of Motion source and the older motion-control copies so the same overclaims are not preserved in sibling source files.

Edited files:

- `books/control-is-motion.qmd`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch08_phase_variable_control.tex`
- `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`
- `articles/motion-control/chapter8.tex`
- `articles/motion-control/Control_Is_Motion_Complete.tex`

### Golf Biomechanics and Modeling

- Added a DCR minimum reporting standard requiring state vector, coordinate convention, drift/control weighting `W`, norm, epsilon, actuator bound `u_max`, model parameters, and a sensitivity check.
- Revised the DCR summary and exercise language so students are asked to report weighting, bounds, parameters, and perturbation sensitivity instead of treating a single number as self-validating.
- Corrected the muscle-length Jacobian convention in Chapter 16:
  - `R(q) in R^{n_m x n_j}`
  - `R_{ji} = partial ell_j / partial q_i`
  - `tau = R(q)^T F^M`
- Replaced a missing `Murray2000` citation with existing musculoskeletal-model citations and added missing bibliography entries for `Neumann2017`, `Nordin2012`, and `cross2014impact`.
- Fixed `HumeKeogh2005` to the existing `Hume2005` key.
- Removed universal phrasing around wrist muscle velocity and wrist moment-arm ranges; those values now have to come from the selected model or measurement source.

Edited files:

- `books/biomechanics-biology-to-systems.qmd`
- `articles/The_Physics_of_Golf/chapters/ch06_zero_torque_counterfactual.tex`
- `articles/The_Physics_of_Golf/quarto/ch06_zero_torque_counterfactual.qmd`
- `articles/The_Physics_of_Golf/chapters/ch16_muscle_to_joint_torques.tex`
- `articles/The_Physics_of_Golf/quarto/ch16_muscle_to_joint_torques.qmd`
- `articles/The_Physics_of_Golf/chapters/ch17_muscle_force_generation.tex`
- `articles/The_Physics_of_Golf/chapters/ch22_anatomy_joint_modeling.tex`
- `articles/The_Physics_of_Golf/golf_physics.bib`

## Validation

Runtime access was green after the GitHub automation setup helper ran successfully. `gh auth status`, representative `git ls-remote`, and representative `fetch --dry-run` checks passed before source work.

Validation commands run in the worktree:

- `git diff --check` - passed.
- Scoped bibliography key sweep over changed TeX/QMD files - passed; all bibliography-style citation keys resolved in the checked project bibliographies after this pass.
- Guardrail grep for known rejected patterns (`Murray2000`, `HumeKeogh2005`, `perfectly encapsulates`, `impervious`, `perfectly timed passive impact dynamics`, `most glaring flaw`, and related terms) - no matches.
- `python --version` - Python 3.14.3.
- `quarto --version` - blocked because `quarto` is not installed in this runtime.

## Residual Risks

- The DCR standard is now explicit, but the book still needs a numerical appendix or table showing sensitivity of DCR values to `W`, `u_max`, inertial parameters, damping assumptions, and initial conditions.
- The Geometry of Motion Quarto aggregate and legacy motion-control copies are edited in this pass, but the repository still needs a clear generated-vs-canonical ownership rule so future edits do not drift between source copies.
- Golf chapters outside this pass still contain many numerical claims about drag, impact force, joint range of motion, and kinetic-chain timing. They should be reviewed under the same "model, parameter, sensitivity, citation" rule.
- Some rhetorical claims in the old `articles/motion-control/Control_Is_Motion_Complete.tex` synthesis remain more grandiose than the newer book standard. This pass removed the most direct phase-variable overclaims but did not rewrite the entire legacy synthesis.

## Recommended Next Pass

1. Build the DCR sensitivity appendix: choose a minimal double-pendulum model, define `W`, `epsilon`, and `u_max`, then show perturbation results rather than single-point ratios.
2. Audit Golf chapters 8, 11, 17, 19, 21, and 30 for numerical claims that need source tables or model-bound wording.
3. Establish a canonical-source rule for Quarto aggregate files, chapter TeX files, and legacy complete manuscripts.
4. Replace remaining "perfect swing" or "mathematical secret" rhetoric in legacy Dynamics / Geometry sources with hypothesis-driven language.
