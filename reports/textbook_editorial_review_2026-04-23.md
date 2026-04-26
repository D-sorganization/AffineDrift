# Textbook Editorial Review - 2026-04-23

Automation: Textbook Reviews
Reviewer stance: senior commissioning editor for rigor, source quality, notation, structure, and tone.
Scope: Drifter Manifesto, Dynamics / Geometry Is Motion, and Golf Biomechanics and Modeling.

## Executive Assessment

This pass targeted a narrower but still publication-relevant problem set: claims that quietly crossed from model structure into empirical or coaching language. The current AffineDrift manuscripts are strongest when they state the model class, the control assumptions, the measured quantities, and the boundary between a useful mathematical explanation and a claim about real golfers. They remain vulnerable when passive-release, self-organization, funnel contraction, or GRF language is allowed to sound like direct observation rather than model-conditioned interpretation.

The editorial judgment for this run is that the project is now more internally consistent on three fronts. First, the manifesto better routes passive-control and ground-reaction claims back to the correct technical sources. Second, Volume II now distinguishes local contraction and accessibility statements from universal self-correction or controllability claims. Third, the golf chapters now separate passive impedance, distributed feedback, and external moment balance more carefully from direct neural, coaching, or measurement claims.

## Source Edits Made

### Drifter Manifesto

- Tightened the manifesto publication-use note so it now requires editors to disclose whether a key quantity was directly measured or inferred from a model.
- Added a new claim-to-source row for passive-control, sequencing, and ground-reaction claims, routing those statements back to the passive-control article and the biomechanics volume.

Edited file:

- `pages/drifter-manifesto.qmd`

### Dynamics / Geometry Is Motion

- Added a landing-page guardrail clarifying that "self-correcting" release or contraction claims must specify whether they come from open-loop model contraction, closed-loop feedback, hybrid zero dynamics, or a numerical funnel on a declared disturbance set.
- Rewrote the Volume II underactuation chapter so wrist release is framed as a passive-release hypothesis for a simplified model, not proof that measured wrist torque vanishes in real swings.
- Replaced the overly strong controllability paragraph with a local-accessibility interpretation of Lie brackets and softened the singular-arc discussion so it no longer implies universal bang-bang control in real swings.
- Rewrote the orbital-stability example and its Quarto aggregate to describe a model-level admissible tube rather than a universal "natural funnel" that fixes errors without sensing or control.

Edited files:

- `books/control-is-motion.qmd`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch04_orbital_stability_and_transver.tex`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch05_underactuation_and_passive_dyn.tex`
- `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`

### Golf Biomechanics and Modeling

- Strengthened the Volume III landing page evidence ladder so passive-stability, sequencing, and GRF claims must declare which quantities are observed, inferred, or still interpretive.
- Reframed the passive-distributed-control chapter as a self-organizing swing model rather than an established fact, and aligned both TeX and Quarto versions on local stability, feedback burden, and passive-impedance limits.
- Rewrote the kinetic-chain GRF section so GRF is treated as the external torque channel during stance, while muscles are correctly described as shaping the reaction forces rather than being excluded from the mechanism.
- Softened the chapter's timing-sequence bullet list so it reads as a simplified timing hypothesis requiring EMG, force-plate, and kinematic validation instead of a universal activation script.

Edited files:

- `books/biomechanics-biology-to-systems.qmd`
- `articles/The_Physics_of_Golf/chapters/ch27_passive_distributed_control.tex`
- `articles/The_Physics_of_Golf/quarto/ch27_passive_distributed_control.qmd`
- `articles/The_Physics_of_Golf/chapters/ch30_kinetic_chain.tex`
- `articles/The_Physics_of_Golf/quarto/ch30_kinetic_chain.qmd`

## Publication Assessment

The manifesto is now a better commissioning tool because it explicitly captures a category that had been slipping through prior passes: claims about passive control, sequencing, and ground reaction were appearing in public-facing prose without a stable source contract. The added matrix row closes that gap.

Volume II is more defensible because it now keeps three statements distinct: local accessibility, local contraction, and real-swing self-correction. Those are not interchangeable. The revised text no longer lets a reader slide from "this simplified model contracts over a phase interval" to "the golf swing naturally fixes itself."

The golf biomechanics material is stronger because it now states a clearer hierarchy: passive impedance can reduce feedback burden, distributed feedback can contribute locally, and GRF supplies the external moment channel during stance, but none of those points alone settles a coaching rule or a measured neural-control story. That distinction is essential for publication credibility.

## Validation

Runtime access was green after the GitHub automation setup helper ran successfully. `gh auth status`, representative `git ls-remote`, and representative `fetch --dry-run` checks passed before source work.

Validation commands run in this worktree:

- `git diff --check` - passed after one trailing-whitespace cleanup in the new Volume II wrist-release paragraph.
- `python scripts/scan_quarto_syntax.py` - passed; no issues found across 238 scanned files.
- `python -m scripts.validate_frontmatter` - passed; 135 files checked.
- `python scripts/check_textbook_claims.py` - passed.
- Scoped rejected-pattern sweep over the edited textbook sources - passed; no remaining hits for the targeted overclaim phrases in the changed files.

Local Quarto/PDF rendering remains blocked until Quarto is available in PATH. `quarto --version` still fails in this runtime with `The term 'quarto' is not recognized as a name of a cmdlet, function, script file, or executable program.`

## Residual Risks

- `The Physics of Golf` still contains coaching-adjacent or mechanistic overreach outside this slice, especially in Chapters 13, 29, and 31.
- Volume II still mixes chapter TeX and aggregate Quarto maintenance; this run kept the shared passages aligned, but the repo still needs a clearer canonical-source rule.
- The passive-control chapter still contains quantitative neural-bandwidth framing that would benefit from a tighter source audit if it is intended for publication rather than internal exposition.
- Full local render remains unverified until Quarto is available in this runtime or CI renders the branch.

## Recommended Next Pass

1. Audit `The Physics of Golf` Chapters 13, 29, and 31 for remaining "automatic," "fully determined," or coaching-prescriptive language that outruns the cited evidence.
2. Review Volume II Chapter 1 for additional funnel and reachable-set rhetoric that still leans from model structure toward universal swing interpretation.
3. Decide whether the passive-control chapter should add explicit citations for its neural-bandwidth numbers or recast them as illustrative modeling motivation.
