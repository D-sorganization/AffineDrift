# Textbook Editorial Review - 2026-04-22

Automation: Textbook Reviews
Reviewer stance: senior commissioning editor for rigor, source quality, notation, structure, and tone.
Scope: Drifter Manifesto, Dynamics / Geometry Is Motion, and Golf Biomechanics and Modeling.

## Executive Assessment

This pass focused on source traceability and model-bounded inference. The manuscripts are materially stronger than they were at the start of this review series, but the main publication risk remains the same: mathematically useful diagnostics can sound like direct measurements or universal swing laws when they leave the technical chapters and appear in orientation text, examples, summaries, or coaching-adjacent prose.

The commissioning judgment is that AffineDrift should keep its strongest claims tied to explicit source contracts: coordinates, actuator convention, contact model, torque bound, parameter values, disturbance set, and validation data. Drift/control diagnostics, Lie-bracket reachability arguments, funnel certificates, muscle force estimates, and energy-transfer statements are valuable when stated as model-conditioned tools. They become vulnerable when presented as direct evidence about hidden muscle recruitment, individual coaching cues, or real-grip losslessness.

## Source Edits Made

### Drifter Manifesto

- Added a structured claim-to-source matrix under the existing manifesto source map.
- Separated four claim families: control-affine notation, DCR and phase labels, counterfactual diagnostics, and inverse-dynamics hidden-load claims.
- Added a publication burden for each family so public-facing claims must point back to model assumptions and evidence categories before stronger wording is used.

Edited file:

- `pages/drifter-manifesto.qmd`

### Dynamics / Geometry Is Motion

- Rewrote the Volume II configuration-manifold remark on Lie algebras so it describes local accessibility under smoothness, rank, and constraint assumptions rather than universal reachability.
- Reframed the trajectory-optimization chapter opener so an optimizer returns a model-conditioned candidate trajectory, not a "perfect" human swing.
- Softened the Pontryagin/singular-arc discussion: a simplified golf-release model may resemble a singular arc, but that does not directly predict measured wrist activation.
- Updated the Volume II aggregate Quarto aphorism to avoid unsupported "perfect motion" language.

Edited files:

- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch03_configuration_manifolds.tex`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch06_trajectory_optimization.tex`
- `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`

### Golf Biomechanics and Modeling

- Corrected the Physics of Golf energy decomposition: muscular power can be positive or negative; eccentric braking absorbs energy.
- Scoped zero constraint power to ideal, time-independent, holonomic, lossless bilateral constraints in the declared generalized-coordinate model.
- Removed "lossless energy transfer" language from TeX and Quarto summaries and replaced it with a model-conditioned redistribution statement.
- Brought the TeX muscle-force chapter into alignment with the safer Quarto wording on activation delay, force-velocity limits, and late-downswing correction claims.
- Added an explicit caveat that the wrist control-gain numbers are illustrative model parameters, not subject-independent measurements.
- Replaced the "accelerate to impact" myth/reality passage with model-bounded interpretation and cue language that does not prescribe a universal coaching rule.

Edited files:

- `articles/The_Physics_of_Golf/chapters/ch10_energy_transfer.tex`
- `articles/The_Physics_of_Golf/quarto/ch10_energy_transfer.qmd`
- `articles/The_Physics_of_Golf/chapters/ch17_muscle_force_generation.tex`
- `articles/The_Physics_of_Golf/quarto/ch17_muscle_force_generation.qmd`

## Publication Assessment

The Drifter Manifesto is now closer to a durable front door because it gives an editor or reviewer a claim-routing table rather than only prose provenance. That matters for publication because it prevents the manifesto from becoming a citation substitute.

The Geometry of Motion material is more defensible because reachability and optimal-control language now reflects the actual theorem burden. Lie brackets support local accessibility statements under assumptions; they do not override torque limits, time horizons, contact constraints, or biological variability. Likewise, a singular-arc analogy for wrist release is useful as a modeling hypothesis but should not be treated as a measured neuromuscular finding.

The Golf Biomechanics material now has a cleaner energy and muscle-control contract. Ideal constraints can redistribute energy without net work in the declared model, but real grips, tissues, damping, and impact must be estimated. Muscles can also absorb energy, so the old "muscles do positive work" line was mechanically wrong. The muscle-force chapter now avoids deriving exact coaching prescriptions from generic force-velocity reasoning.

## Validation

Runtime access was green after the GitHub automation setup helper ran successfully. `gh auth status`, representative `git ls-remote`, and representative `fetch --dry-run` checks passed before source work.

Validation commands run in this worktree:

- `git diff --check` - passed.
- `python scripts/scan_quarto_syntax.py` - passed; no issues found across 241 scanned files.
- `python -m scripts.validate_frontmatter` - passed; 135 files checked.
- Source-link existence check for the manifesto matrix links - passed.
- New-citation sweep over added diff lines - passed.
- Scoped rejected-pattern check over changed textbook sources - passed.
- `quarto --version` - blocked because Quarto is not installed or not in PATH (`The term 'quarto' is not recognized as a name of a cmdlet, function, script file, or executable program.`), so local Quarto/PDF renders were not run.

## Residual Risks

- The manifesto source matrix is still HTML embedded in a Quarto page; future work should decide whether this should become a reusable data-driven component.
- Volume II still has canonical TeX plus aggregate Quarto content. This run edited the affected aggregate aphorism, but the project still needs a documented canonical-source rule.
- Several golf chapters still include high-level coaching or physiology summaries that should be reviewed with the same evidence-category standard, especially Chapters 13, 24, 27, and 30.
- Full local render remains unverified until Quarto is available in this runtime or CI renders the branch.

## Recommended Next Pass

1. Audit Physics of Golf Chapters 13, 24, 27, and 30 for claims that infer neural planning, passive control, or kinetic-chain coaching directly from model structure.
2. Add a concise canonical-source note for Volume II TeX versus aggregate Quarto maintenance.
3. Convert the manifesto claim-to-source matrix into a reusable table component if the site has an established component pattern.
4. Add one worked example that reports DCR with norm, weighting matrix, torque bound, parameter set, and sensitivity check in one place.
