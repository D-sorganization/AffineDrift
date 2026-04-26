# Textbook Editorial Review - 2026-04-21

Automation: Textbook Reviews
Reviewer stance: senior commissioning editor for rigor, source quality, notation, structure, and tone.
Scope: Drifter Manifesto, Dynamics / Geometry Is Motion, and Golf Biomechanics and Modeling.

## Executive Assessment

This pass focused on traceability and evidence ladders. The manuscripts have become more careful over the last several runs, but the remaining publication risk is that public-facing orientation pages and chapter summaries can still sound stronger than the technical record supports. A reader should be able to tell whether a statement is a measured kinematic fact, a model-conditioned load estimate, an inferred muscle/tissue quantity, or a coaching/clinical interpretation.

The commissioning judgment is that the AffineDrift books are strongest when the ambition remains mathematical but the claims stay explicitly conditional. Funnels, passive wrist release, ZTCF, DCR, and inverse dynamics are useful technical tools; they should not be presented as universal swing laws or as direct measurements of hidden muscle forces.

## Source Edits Made

### Drifter Manifesto

- Added a source map that routes manifesto claims to the core theory articles, DCR treatment, inverse-dynamics articles, zero-torque counterfactual material, and critique pages.
- Preserved the manifesto as an orientation page while making the burden of proof more explicit for public reuse.

Edited file:

- `pages/drifter-manifesto.qmd`

### Dynamics / Geometry Is Motion

- Added a publication guardrail to the Volume II landing page for passive wrist release, funnel narrowing, face orientation, and repeatability claims.
- Rewrote Volume II Chapter 1 and aggregate Quarto text so passive coupling and funnel profiles are framed as model-dependent hypotheses rather than automatic swing outcomes.
- Rewrote Volume II Chapter 5 and aggregate Quarto text to remove coaching-adjacent claims that passive physics alone pulls the clubhead into the ball, maximizes consistency, or eliminates wrist torque.
- Tightened Chapter 6 and Chapter 7 language around underactuated optimization and funnel certification. A computed funnel is now described as a certificate for a stated closed-loop model, not as a guarantee of human performance.

Edited files:

- `books/control-is-motion.qmd`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch01_throwing_away_the_target.tex`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch05_underactuation_and_passive_dyn.tex`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch06_trajectory_optimization.tex`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch07_funnel_synthesis.tex`
- `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`

### Golf Biomechanics and Modeling

- Added an evidence ladder to the Volume III landing page that separates observed kinematics, model-conditioned net loads, inferred muscle/tissue quantities, and clinical or coaching interpretation.
- Added an identifiability table to Golf Chapter 18 in both TeX and Quarto forms.
- Softened claims around dual null spaces, pelvis ground-reaction moments, ZTCF robustness, and constraint multipliers so they require instrumentation, declared contact models, or auxiliary assumptions.
- Repaired the exercise prompt that implied constraint forces are usually uniquely determined from kinematics alone.

Edited files:

- `books/biomechanics-biology-to-systems.qmd`
- `articles/The_Physics_of_Golf/chapters/ch18_inverse_dynamics_parallel.tex`
- `articles/The_Physics_of_Golf/quarto/ch18_inverse_dynamics_parallel.qmd`

## Publication Assessment

The Drifter Manifesto is now a safer front door because it tells readers where to verify each major class of claim. It still needs a more durable source-map table in a future pass, but the page no longer asks readers to infer the provenance of the central ideas.

The Dynamics / Geometry Is Motion material is more publication-safe because it now distinguishes three things that were previously blended: a useful underactuated double-pendulum model, a funnel certificate for a stated closed-loop system, and a real human golf swing. This makes the mathematical program easier to defend.

The Golf Biomechanics material now gives readers a practical identifiability ladder. This is important because inverse dynamics is often rhetorically misused: net joint loads, individual muscles, tissue stresses, and coaching implications are not the same evidentiary category.

## Validation

Runtime access was green after the GitHub automation setup helper ran successfully. `gh auth status`, representative `git ls-remote`, and representative `fetch --dry-run` checks passed before source work.

Validation commands run in this worktree:

- `git diff --check` - passed.
- `python scripts/scan_quarto_syntax.py` - passed; no issues found across 241 scanned files.
- `python -m scripts.validate_frontmatter` - passed; 135 files checked.
- Scoped source-map link existence check for the new manifesto links - passed.
- Scoped rejected-pattern grep over changed sources - passed after replacing targeted overclaim language.
- Citation token scan over changed TeX/QMD sources completed; no new bibliography keys were introduced.
- `python --version` - Python 3.14.3.
- `quarto --version` - blocked because Quarto is not installed or not in PATH (`The term 'quarto' is not recognized as a name of a cmdlet, function, script file, or executable program.`), so local Quarto/PDF renders were not run.

## Residual Risks

- The source-map addition is currently compact prose; a future pass should turn it into a structured claim-to-source table.
- Several other Physics of Golf chapters still use "automatic" or coaching-adjacent language; the next risk-based audit should focus on Chapters 10, 16, 24, 27, and 30.
- Volume II still carries duplicate canonical TeX and Quarto aggregate surfaces. This run edited both for the touched sections, but the repository still needs a clear canonical-source rule.
- Local full rendering remains unverified until Quarto is available in this runtime or CI renders the branch.

## Recommended Next Pass

1. Build a manifesto claim-to-source matrix with one row per public-facing claim family.
2. Audit Physics of Golf Chapters 10, 16, 24, 27, and 30 for automaticity, coaching, and neuromuscular inference overclaims.
3. Add a minimal executable proxy notebook for the Volume II underactuated golf example so funnel and passive-release claims can point to a reproducible artifact.
4. Decide whether `volume2_content.qmd` is generated or canonical, then document the editing rule to avoid drift between TeX chapters and aggregate Quarto output.
