# Textbook Editorial Review - 2026-04-20

Automation: Textbook Reviews
Reviewer stance: senior commissioning editor for rigor, source quality, notation, structure, and tone.
Scope: Drifter Manifesto, Dynamics / Geometry Is Motion, and Golf Biomechanics and Modeling.

## Executive Assessment

This pass focused on identifiability and model-conditioning. The strongest residual publication risk in the current manuscripts is not lack of mathematical ambition; it is the tendency to present model-conditioned conclusions as if they were direct measurements or universal swing laws. Yesterday's pass tightened DCR reporting and phase-variable guardrails. Today's pass extends the same standard to inverse dynamics, kinetic-chain claims, and the Volume II golf case study.

The main commissioning judgement is that the books are stronger when they separate four categories explicitly: measured kinematics, model-conditioned net loads, unobserved muscle recruitment, and forward counterfactual predictions. ZTCF remains a useful framing device, but it should be described as a forward simulation under stated model, contact, and parameter assumptions, not as a route around all modeling uncertainty.

## Source Edits Made

### Drifter Manifesto

- Added a publication-use guardrail distinguishing the manifesto as an editorial map from the technical sources.
- Required stronger public-facing claims to identify coordinate convention, actuator model, contact assumptions, validation data, and uncertainty or sensitivity analysis.

Edited file:

- `pages/drifter-manifesto.qmd`

### Dynamics / Geometry Is Motion

- Rewrote the Volume II golf case-study TeX source to match the more careful Quarto aggregate standard.
- Replaced "athletic perfection" and universal funnel language with a hypothetical 15-DOF model framed as a testable analysis.
- Added explicit citations around transverse linearization and SOS/funnel certification.
- Clarified that phase, contact, torque-limit, and signal-dependent-noise assumptions must be stated before claims about face squaring or athletic consistency.

Edited files:

- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch11_case_study_the_complete_golf_s.tex`
- `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`

### Golf Biomechanics and Modeling

- Reworked Chapter 18 inverse-dynamics language to distinguish net joint-load estimates from muscle-force inference.
- Replaced direct-measurement overclaims with model-conditioned language around RNEA, force plates, grip sensors, constraint multipliers, drift terms, and ZTCF.
- Removed the unsupported Feynman-style epigraph and the claim that motion capture "knows exactly" how the skeleton moved.
- Corrected the TeX source's dangling `eq:KKT_matrix` reference by pointing to the local constrained KKT equation.
- Reframed Chapter 30 kinetic-chain claims as model predictions, not automatic properties of every real swing.
- Softened training and DCR claims so they require measured kinematics, force data, and repeated-swing evidence.
- Corrected the stale `Zero-Time-Constraint Force` index entry to `Zero Torque Counterfactual`.

Edited files:

- `articles/The_Physics_of_Golf/chapters/ch18_inverse_dynamics_parallel.tex`
- `articles/The_Physics_of_Golf/quarto/ch18_inverse_dynamics_parallel.qmd`
- `articles/The_Physics_of_Golf/chapters/ch30_kinetic_chain.tex`
- `articles/The_Physics_of_Golf/quarto/ch30_kinetic_chain.qmd`

## Publication Assessment

The Drifter Manifesto is now safer as a public orientation page because it makes the burden of proof explicit. It still needs a durable source map linking each manifesto claim to a technical article, bibliography, or critique page; otherwise the manifesto risks becoming a polished index rather than a traceable scholarly front door.

The Dynamics / Geometry Is Motion case study is now publication-safer in the TeX source. Its remaining gap is implementation evidence: the hypothetical 15-DOF model, collocation problem, and SOS certificate need an executable notebook or appendix before the chapter can support stronger claims about specific golf-swing behavior.

The Golf Biomechanics chapters now draw a cleaner line between kinematic observability and causal inference. Chapter 18 no longer implies that motion capture alone uniquely determines constraint forces or muscle forces. Chapter 30 now treats proximal-to-distal sequencing as a coupled-model prediction that must be checked against measured kinematics and force data.

## Validation

Runtime access was green after the GitHub automation setup helper ran successfully. `gh auth status`, representative `git ls-remote`, and representative `fetch --dry-run` checks passed before source work.

Validation commands run in this worktree:

- `git diff --check` - passed.
- `git diff --cached --check` - passed after staging only the scoped textbook-review files.
- `python scripts/scan_quarto_syntax.py` - passed; no issues found across 241 scanned files.
- `python -m scripts.validate_frontmatter` - passed; 135 files checked.
- Scoped rejected-pattern grep over changed sources - passed; no matches for the targeted overclaim phrases.
- Citation-key sweep over changed TeX/QMD sources - passed after excluding `\citeneeded{...}` placeholders from bibliography-key resolution.
- `python --version` - Python 3.14.3.
- `quarto --version` - blocked because Quarto is not installed or not in PATH (`The term 'quarto' is not recognized...`), so local Quarto/PDF renders were not run.

## Residual Risks

- The inverse-dynamics chapter still needs a compact table mapping data sources to identifiable quantities: motion capture, force plates, grip sensors, EMG, optimization assumptions, and musculoskeletal model priors.
- The kinetic-chain chapter still contains many numerical examples that should eventually be tagged as illustrative, measured, or literature-sourced.
- The Geometry Volume II case study needs a reproducible model artifact before the text can claim that any particular funnel or passive-wrist result has actually been computed.
- The repository still carries duplicate TeX and Quarto surfaces; this pass edited both for the touched chapters, but long-term canonical-source rules are still needed.

## Recommended Next Pass

1. Build an identifiability table for Golf Chapter 18 and link it from the chapter summary.
2. Audit Golf Chapters 19, 21, 28, and 30 for numeric examples that need source tables, parameter declarations, or explicit "toy model" labels.
3. Create an executable minimal notebook for the Volume II golf case study, even if the first version is a low-dimensional proxy rather than the full 15-DOF model.
4. Add a source map from the Drifter Manifesto to the specific technical articles, reports, and critique pages that substantiate each public-facing claim.
