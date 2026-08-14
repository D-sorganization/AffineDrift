# Agent Handoff — AffineDrift

> Update this file with every PR and every push to main.

Last updated: 2026-08-14

## Subject-Scaled Closed-Contact Feasibility Pin

- Branch `docs/8557-closed-contact` pins UpstreamDrift PR #8642, merged as
  `1ab8d755fcf242631c0b64b9f82a8b2f1caabd5f`.
- Six deterministic de Leva engineering profiles, three grip spans, and 61
  states per case miss the declared grip contacts by 0.171--0.616 m (median
  0.405 m); no case meets the registered 5 mm closure tolerance.
- Every local bilateral contact Jacobian still has rank six. This is an adverse
  result: local correction rank does not establish geometric contact closure.
- The bounded follow-up closes 234/234 reduced-tree profile--span--phase samples
  to at most 1.16e-10 m while holding club coordinates fixed. All achieved
  contact Jacobians retain rank six; the minimum broad engineering joint-limit
  margin is 0.103 rad and the minimum coarse collision clearance is 0.0309 m.
  An unreachable 2.0 m grip span fails as the registered negative control.
- The result is a necessary-condition screen, not anatomical, force, passivity,
  timing, slack, delivery, or human-strategy evidence. Subject-specific anatomy
  and calibrated compliant forward contact remain the next gates.
- The companion snapshot pins 987/987 reviewed candidates, 263 claims, and 455
  qualified artifacts from the 217-page upstream publication.

## Bilateral-Wrench Sensor Qualification Pin

- Branch `research/8557-sensor-qualification` pins UpstreamDrift PR #8635,
  merged as `8e6fa91243f373be322624e894987fc63c9c0feb`.
- The ideal two-point-force map has rank five and a one-dimensional invisible
  equal-and-opposite axial mode. One independent internal axial scalar restores
  full point-force rank.
- The full 12-component bilateral-wrench map has rank six and nullity six, so
  one net club wrench cannot recover individual six-axis hand allocation.
- The trajectory-level synthetic qualification shows why numerical net-wrench
  closure is insufficient: net-only allocation has 11.86 N RMSE and 29.05 N
  axial-mode RMSE. It separately quantifies noise, cross-talk correction,
  residual calibration error, contact migration, and a combined registered case.
- These are seeded synthetic point-force results, not device or human evidence.
  Full bilateral wrenches, distributed contact, anatomy, intentionality, and
  human validation remain open; #8556 remains the governed data gate.
- The companion snapshot pins 975/975 reviewed candidates, 258 claims, and 440
  qualified artifacts from the 215-page upstream publication.

## Typed-Slack Dynamics and Identifiability Pin

- Branch `research/typed-slack-evidence` pins UpstreamDrift PR #8626, merged as
  `92100115ea0be0d6744dcf7a4504ec8453fae6fa`.
- Five declared slack classes are exercised separately under two synthetic
  excitations. Four mechanical surrogates close their work-energy ledgers to
  `5.13e-10 J`; the control deadband remains a nonmechanical signal map.
- Full local sensitivity rank does not identify a class. Contact and biological
  surrogate outputs differ by only 1.96% normalized RMSE, so global benefit,
  necessity, intentionality, delivery, anatomical, and human claims remain open.
- The companion snapshot now pins 962/962 reviewed candidates, 252 claims,
  428 qualified artifacts, and an 8/9 source-agenda readiness result. #8556
  remains the governed bilateral-wrench data gate.

## Common-Phase Timing Viability and Recovery Pin

- Branch `research/timing-viability-8557` advances the public companion to
  UpstreamDrift PR #8625, merged at
  `8ccbbcc598b168905591508fe35bc58b4924ccea`.
- The pinned study contains 60 paired policy/load/phase cases and 120
  trajectories. Clock timing has the larger task-viability region under every
  registered guard set; neither policy shows sustained half-error recovery.
  This is a reduced planar model result, not a human timing or coaching result.
- The complete audit now contains 959/959 reviewed candidates, 251 claims,
  zero unadjudicated entries, and 423 qualified artifacts. Seven of the nine
  handwritten-agenda points have bounded/partial/negative model answers; two
  remain unresolved or definition-gated.
- UpstreamDrift #8556 remains open at the governed bilateral-wrench data gate.
  NotebookLM collection review still requires manual Google reauthentication.

## Complete Proximal-to-Distal Claim Audit and Agenda Pin

- Branch `research/momentum-readiness-8557` pins the canonical complete audit
  and nine-point source-agenda readiness result at UpstreamDrift merge
  `0a0c44168194bc953990aac662d44eb1ffd0c3ff`.
- The public article and machine snapshot expose 956/956 reviewed candidates,
  250 bounded claims, zero unadjudicated entries, nine source questions,
  release hashes, and the main adverse scientific boundaries. Five questions
  have bounded/partial/negative-rule answers and four remain unresolved or
  definition-gated. The site does not promote audit completion as human
  validation or coaching authority.
- #8556 remains an external governed bilateral-wrench data gate. NotebookLM
  collection mining remains blocked on manual interactive reauthentication.
- PR #3849 merged the prior audit pin as `745168a8`; this branch supersedes its
  counts and exact upstream evidence pin without changing the authority split.

## Current Work

Follow-up PR [#3846](https://github.com/D-sorganization/AffineDrift/pull/3846)
merged as `4542b55f` and repaired the one post-merge publication failure from
the definitional-integrity migration: The Physics of Golf used an undefined uppercase `\ZTCF` command instead of its declared
`\ztcf` macro. The same pass removes residual no-muscle interpretations,
recasts ground-reaction residuals as non-identifying model diagnostics, and
qualifies shaft/control-authority statements in the paired LaTeX and Quarto
sources. The terminology gate now rejects direct physiological
reinterpretations. The focused contracts, terminology scan, title-case audit,
and a 637-page local `pdflatex` build pass. PR
[#3847](https://github.com/D-sorganization/AffineDrift/pull/3847) records the
final content-architecture and decision-marker acceptance evidence.

Epic [#3834](https://github.com/D-sorganization/AffineDrift/issues/3834)
tracks the repository-wide definitional-integrity migration. Protected PR
[#3845](https://github.com/D-sorganization/AffineDrift/pull/3845) merged as
`ee3766be`. The conforming UpstreamDrift PR
[#8588](https://github.com/D-sorganization/UpstreamDrift/pull/8588) merged as
`1d6af73d`; close #3834 only after #3847 and both remote-main ancestry checks
are verified.

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
- Updated `SPEC.md` through 1.0.192.

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

### Remaining Before Epic Closure

1. Preserve PR #3847's squash auto-merge and required checks.
2. Verify #3845, #3846, #3847, and UpstreamDrift #8588 as ancestors of their
   respective remote `main` branches.
3. Attach acceptance evidence to and close the eight AffineDrift child issues,
   then close #3834.

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
