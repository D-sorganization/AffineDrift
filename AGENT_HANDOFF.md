# Agent Handoff — AffineDrift

> Update this file with every PR and every push to main.

Last updated: 2026-08-13

## Current Work

Follow-up PR [#3846](https://github.com/D-sorganization/AffineDrift/pull/3846)
repaired the one post-merge publication failure from the definitional-integrity migration: The Physics of
Golf used an undefined uppercase `\ZTCF` command instead of its declared
`\ztcf` macro. The same pass removes residual no-muscle interpretations,
recasts ground-reaction residuals as non-identifying model diagnostics, and
qualifies shaft/control-authority statements in the paired LaTeX and Quarto
sources. The terminology gate now rejects direct physiological
reinterpretations. The focused contracts, terminology scan, title-case audit,
and a 617-page local `pdflatex` build pass.

Epic [#3834](https://github.com/D-sorganization/AffineDrift/issues/3834)
tracks the repository-wide definitional-integrity migration. Protected PR
[#3845](https://github.com/D-sorganization/AffineDrift/pull/3845) merged as
`ee3766be`. Preserve protected checks; do not close #3834 until the conforming
UpstreamDrift migration also merges, this publication follow-up is merged, and
both remote-main states are verified.

### Ratified Contract

- `NOTATION.md` is the normative public semantic authority.
- Drift is the complete autonomous vector field of the declared effective
  plant, including every retained state-dependent, shaft, passive, contact,
  and constraint term.
- The ZTCF family contains pointwise samples, stitched pointwise traces,
  forward trajectories, and achieved-state branched trajectories. First use
  must state the construction.
- Zero declared generalized control does not mean zero activation, EMG,
  co-contraction, reflex activity, or effort.
- ZVCF is an instantaneous zero-velocity, zero-control acceleration. A
  control-preserved zero-velocity calculation uses a different name.
- DCR compares drift with bounded control capacity in the same declared
  acceleration or task-projected space and reports `W`, `U(x)`, and epsilon.
- Use `f(x)` for drift, `G(x)` for the input map, `g(q)` for gravity, and `u`
  for declared control.

The reasoning and rejected alternatives are in
`docs/development/terminology-decision-record.md`.

### Implemented on This Branch

- Added a machine-readable terminology contract to `NOTATION.md`.
- Extended `scripts/check_terminology.py` to fail closed when authority rows
  are absent, reject previously unseen expansions, and require a ZTCF
  construction qualifier on first use.
- Added RED/GREEN regression coverage in `tests/test_check_terminology.py`.
- Reconciled the Quarto and LaTeX article trees for ZTCF, ZVCF, DCR, DgCR, and
  input-map/gravity notation.
- Rewrote the Physics of Golf counterfactual chapter and glossaries to remove
  zero-muscle claims and compare drift/control in a common acceleration space.
- Corrected the Geometry of Motion chapter to distinguish canonical ZVCF from
  a zero-velocity control-preserved evaluation.
- Replaced invalid convergence and counterfactual identities in the manifesto
  with falsifiable reconstruction, held-out prediction, and sensitivity tests.
- Updated `SPEC.md` to 1.0.190.

### Verified Locally

- Terminology gate: pass, zero baseline exceptions.
- Focused content tests: 28 pass.
- Title-case gate: 474 sources pass.
- Tree parity: no new divergence; three main-baseline findings remain under
  #3499.
- Black and Ruff on changed Python: pass.
- `git diff --check`: pass.
- Full Python suite: pass at 93.36% coverage, with only declared skips and
  existing mock warnings.
- Selected Quarto notation, overview, DCR, counterfactual, and glossary pages:
  render successfully. A single-file Physics of Golf render emits the expected
  unresolved sibling-chapter warning; the repository cross-reference gate
  resolves the reference in full-project context.

### Remaining Before AffineDrift Publication

1. Run the full repository quality gate and relevant Quarto/LaTeX renders.
2. Inspect rendered counterfactual, glossary, DCR, and notation pages at phone
   and desktop widths.
3. Commit, push, open a ready PR linked to #3834, and preserve protected merge
   requirements.
4. After merge, verify the merge commit on remote main before closing the
   AffineDrift child issues.

## Cross-Repository Follow-Up

UpstreamDrift work is isolated in
`UpstreamDrift-worktrees/terminology-3834` on
`docs/3834-cross-repo-terminology`, based on remote main `ad71c1fbe`.

The current implementation uses “ZVCF” for a calculation that preserves
applied control. Migrate it as follows after the AffineDrift authority merges:

1. Add failing tests for zero-control canonical ZVCF and a separately named
   zero-velocity control-preserved acceleration.
2. Change shared helpers and engine adapters without silently deleting the old
   diagnostic.
3. Relabel or regenerate proximal–distal data fields, figures, and prose so
   existing control-preserved evidence is not misrepresented as canonical
   ZVCF.
4. Add an UpstreamDrift conformance profile linking the exact AffineDrift main
   commit and declaring coordinates, units, loads, contact mode, and tolerance.
5. Run focused numerical tests, full gates, publication render/inspection, and
   protected merge verification.

## Safety Boundaries

- Do not infer muscle activation or a coaching prescription from a mechanical
  counterfactual alone.
- Do not compare vectors with different units or spaces under DCR.
- Do not call stitched pointwise samples an integrated trajectory.
- Do not rewrite existing evidence labels until the underlying diagnostic has
  been identified and, where necessary, regenerated.
