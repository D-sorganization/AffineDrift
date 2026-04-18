# Textbook Editorial Review - 2026-04-18

Automation: Textbook Reviews
Reviewer role: senior commissioning editor
Scope: Drifter Manifesto, Dynamics / Geometry Is Motion, and Golf Biomechanics and Modeling material in AffineDrift.

## Publication-Level Assessment

The series is closer to a defensible technical-publication posture after the prior review pass, but it still needed a consistency pass around three recurring editorial risks:

1. **DCR was being treated as a universal phase label.** The golf chapters sometimes implied that DCR approaches a fixed 0--1 scale or that a specific late-downswing threshold makes muscular control negligible. This is not publication-safe unless the norm, weighting, torque bound, and model parameters are stated.
2. **Configuration-path claims were being conflated with full state-space claims.** A slow and a fast swing may share a configuration path, but they are not the same state-space curve because velocity coordinates differ.
3. **Tone occasionally overreached.** Phrases such as "autopilot," "ballistic commitment," "passenger," and "trust the drift" made the intended modeling insight sound like a claim that muscle activation vanishes. That is stronger than the model and citations support.

The direct edits in this run move the manuscript toward publication quality by making the DCR diagnostic explicitly model-dependent, replacing absolute coaching rhetoric with bounded-control language, repairing malformed citations, and clarifying geometry/metric notation.

## Source Edits Made

### Drifter Manifesto

- Updated `pages/drifter-manifesto.qmd` to separate established nonlinear-control foundations from AffineDrift's proposed diagnostic layer.
- Added Isidori and Bullo-Lewis provenance language for the smooth control-affine form and drift vector fields.
- Changed the notation baseline so `DCR_W` is introduced only after the norm, weighting matrix, torque bound, and model parameters are stated.

### Dynamics / Geometry Is Motion

- Updated `articles/The_Geometry_of_Motion/Volume_II/chapters/ch02_curves_in_state_space.tex`.
- Mirrored the edits in `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`.
- Clarified that two swings may share a configuration path while differing as full state-space curves.
- Added `doCarmo1992` and `BulloLewis2004` citations to the arc-length and kinetic-energy metric discussion.
- Reframed the mass matrix as a kinetic-energy metric on configuration velocities, not as a generic metric for arbitrary state-space coordinates.

### Golf Biomechanics and Modeling / Physics of Golf

- Updated `articles/The_Physics_of_Golf/chapters/ch06_zero_torque_counterfactual.tex` and `articles/The_Physics_of_Golf/quarto/ch06_zero_torque_counterfactual.qmd`.
- Replaced DCR "blow-up" and "ballistic commitment" claims with a late-correction-window framing.
- Rewrote the DCR definition as a weighted, bounded-control diagnostic:
  `DCR_W(x; u_max) = ||W f(x)|| / (max ||W G(x) u|| + epsilon)`.
- Softened late-downswing claims so muscle activation remains present as impedance, grip stability, release timing, and bounded steering.
- Reworked the impact-control-margin example to present illustrative ranges rather than absolute loss of control.
- Updated chapter takeaways and exercises to require weighting, torque bounds, and sensitivity reasoning.

- Updated `articles/The_Physics_of_Golf/chapters/ch14_complete_swing.tex` and `articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd`.
- Replaced "Point of No Return," "Ballistic Phase," and "Autopilot Swing" language with "Shrinking Late-Correction Window," "Drift-Dominated Phase," and "Feedforward-Dominated Swing."
- Repaired malformed LaTeX citation commands that appeared as tab-plus-`te{...}` in chapter 14.
- Changed late-downswing DCR text from a universal near-1.0 label to a selected-weighting, model-dependent statement.
- Reframed final synthesis around managed drift under constraints, bounded steering, and state preparation.

## Citation And Notation Quality

The added and repaired citations resolve to existing bibliography keys in the repository:

- `doCarmo1992`
- `BulloLewis2004`
- `Nesbit2005`
- `MacKenzie2009`
- `Jorgensen1994`
- `Penner2001`
- `Nesbit2005b`

The manuscript still needs a later bibliography-level pass for prose-only references on the manifesto page. Those are currently used as public-facing provenance notes rather than formal citation commands.

## Validation

- `git diff --check` passed.
- Scanned edited textbook files for malformed tab-plus-`te{...}` citation fragments; none remain in the edited scope.
- Confirmed Python availability with `python --version`: `Python 3.14.3`.
- Quarto render was not run because `quarto --version` failed: `The term 'quarto' is not recognized as a name of a cmdlet, function, script file, or executable program.`
- `rg` could not be used in this Windows automation runtime because the packaged executable at `C:\Program Files\WindowsApps\OpenAI.Codex_26.415.3242.0_x64__2p2nqsd0c76g0\app\resources\rg.exe` returned Access denied. File searches used Git and PowerShell fallbacks.

## Residual Publication Risks

- The golf text still uses illustrative numerical DCR examples. They are now framed as model-dependent, but publication-quality treatment needs a parameter table, weighting declaration, and sensitivity sweep.
- The Quarto volume file for Geometry of Motion is a large aggregate source; future edits should verify whether it is generated or canonical before broader restructuring.
- The manifesto page now states the right guardrails, but a public reference list or tooltip-style bibliography would make the provenance stronger for readers outside the repo.

## Recommended Next Pass

1. Build a compact DCR sensitivity appendix for the golf text with explicit `W`, `u_max`, and model parameters.
2. Continue the golf review into chapter 8 and any remaining impact/shaft passages that make numerical claims without sensitivity framing.
3. Audit generated-vs-canonical source ownership for `volume2_content.qmd` before larger Geometry of Motion rewrites.
