# Textbook Editorial Review - 2026-04-24

Automation: Textbook Reviews
Reviewer stance: senior commissioning editor for rigor, citation quality, notation, structure, and tone.
Scope: Drifter Manifesto, Dynamics / Geometry Is Motion, and Golf Biomechanics and Modeling.

## Executive Assessment

This pass focused on a narrower but still publication-relevant failure mode: places where the manuscripts correctly introduce a mathematical or biomechanical tool, then slide too quickly into language that sounds stronger than the model actually supports. The main vulnerabilities were still in three areas. First, public-facing pages did not yet say clearly enough how readers should cite the manifesto versus the technical sources behind it. Second, the Geometry / Control material still contained a few sentences that could let a reader confuse local underactuated-model behavior with universal self-correction or guaranteed funnel behavior. Third, the biomechanics volume still blurred the boundary between net joint loads, model-based force inference, and direct measurement.

Editorially, the repository is stronger after this pass because those boundaries are now stated more explicitly at the page, chapter, and method levels. The manifesto now distinguishes editorial orientation from evidentiary citation. Volume II now keeps local zero-dynamics behavior, funnel verification, and reachable-set language on a tighter mathematical leash. Volume III now states more plainly that inverse dynamics ends at net generalized loads and that muscle-force estimates require additional assumptions rather than falling out of the measurements automatically.

## Source Edits Made

### Drifter Manifesto

- Added a citation-practice note clarifying that the manifesto is an orientation page, not the endpoint citation for scientific claims.
- Expanded the claim-to-source matrix with a dedicated row for trajectory, funnel, and accessibility language so those claims route back to `Control Is Motion` instead of floating as manifesto-level assertions.

Edited file:

- `pages/drifter-manifesto.qmd`

### Dynamics / Geometry Is Motion

- Strengthened the Volume II landing-page publication guardrail so Chapter 5 and Chapter 7 claims must distinguish open-loop underactuated behavior, closed-loop correction, and certified invariance.
- Rewrote the remaining zero-dynamics passages in the underactuation chapter and Quarto aggregate so they now describe a specified reduced model and phase interval rather than "the golf swing" in general.
- Reframed the abnormal-extremal section to use a more defensible Pontryagin-based description and removed the implication that real swings literally instantiate bang-bang or singular control.
- Tightened the funnel-synthesis chapter by replacing "exact boundary" rhetoric with verified-boundary language and by clarifying that a computed funnel is a conservative verified subset, not the full reachable set.
- Cleaned up one leftover orbital-stability sentence in both TeX and Quarto so phase drift is described as still satisfying orbital stability, not as being "perfectly stable."

Edited files:

- `books/control-is-motion.qmd`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch04_orbital_stability_and_transver.tex`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch05_underactuation_and_passive_dyn.tex`
- `articles/The_Geometry_of_Motion/Volume_II/chapters/ch07_funnel_synthesis.tex`
- `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`

### Golf Biomechanics and Modeling

- Strengthened the Volume III landing page so it now states plainly that muscle, tendon, and tissue loads are not directly measured unless the instrumentation and identification pipeline are given.
- Rewrote the multibody-biomechanics chapter to reduce grandiose framing, add citations for moment-arm and energy-transfer claims, and keep the control-theory analogy subordinate to anatomy and model structure.
- Reworked the inverse-problems chapter so inverse dynamics is framed as a central tool rather than a uniquely decisive one, the pipeline diagram now labels muscle-force inference as model-based, and the text separates net-joint-moment calculation from redundancy-resolution choices such as static optimization or CMC.

Edited files:

- `books/biomechanics-biology-to-systems.qmd`
- `articles/The_Geometry_of_Motion/Volume_III/chapters/ch05_multibody_bio.tex`
- `articles/The_Geometry_of_Motion/Volume_III/chapters/ch06_inverse_problems.tex`

## Publication Assessment

The manifesto is now a better commissioning surface because it tells editors what it is for: orientation, scope control, and routing. That matters because the most common publication mistake at this stage is not a wrong equation; it is citing the high-level page as if it carried the derivation, measurement, or experiment.

Volume II is more credible because it now keeps three categories distinct that readers often collapse together: local accessibility statements, verified closed-loop invariance claims, and intuitive coaching descriptions of release or self-correction. Those categories can inform one another, but they are not interchangeable.

Volume III is materially stronger because the inverse-problem chapter now names the real identifiability break: moving from net torques to individual muscle-force histories requires extra assumptions. That is the point at which many biomechanics texts become rhetorically overconfident, and the revised chapter now avoids that trap.

## Validation

Runtime access was green after the GitHub automation setup helper ran successfully. `gh auth status`, representative `git ls-remote`, and representative `fetch --dry-run` checks passed before source work.

Validation commands run in this worktree:

- `git diff --check` - passed.
- `python scripts/scan_quarto_syntax.py` - passed; no issues found across 238 scanned files.
- `python -m scripts.validate_frontmatter` - passed; 135 files checked.
- `python scripts/check_textbook_claims.py` - passed.
- Scoped citation-key sweep over the changed TeX chapter files - passed after removing one legacy citation key that was not present in the current bibliography.
- Scoped rejected-pattern sweep over the edited textbook sources - passed after rephrasing one guardrail sentence that had quoted a flagged overclaim verbatim.
- `python --version` - `Python 3.14.3`.

Local Quarto/PDF rendering remains unavailable in this runtime because `quarto --version` is not on PATH.

## Residual Risks

- Volume II still contains broader rhetorical drift outside this slice, especially in the later Quarto aggregate sections where stability and funnel language become more aphoristic.
- Volume III still needs a future pass on experimental-methods and inference chapters if the repo wants a tighter chain from observables to tissue-level claims.
- The manifesto claim-to-source matrix is stronger, but the underlying linked technical articles still need to stay aligned with these newer editorial guardrails.
- Full local render remains unverified until Quarto is available in this runtime or CI renders the branch.

## Recommended Next Pass

1. Audit the remaining Volume II Quarto aggregate sections that still use aspirational or aphoristic control language, especially later funnel and trajectory-library passages.
2. Review Volume III Chapters 7 and 8 so the experimental-methods and inference material matches the stronger identifiability framing now used in Chapter 6.
3. Decide whether the manifesto should eventually link to a dedicated editorial style guide for claim classes, so this routing logic is not carried only in page prose.
