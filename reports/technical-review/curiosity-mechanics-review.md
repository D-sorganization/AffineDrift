# Curious Golfer Chapter: Mechanics and Evidence Review

## Scope and Status

Issue [#4375](https://github.com/D-sorganization/AffineDrift/issues/4375) is a
native child of scientific-trust epic #4009, within corpus review #4021 and
mechanics foundations #4058. Source:
`articles/proximal_distal_companion/chapters/ch30_curiosity_and_review.qmd`.
The original source at `7b7ef6a15857d66497c61c78a2ccdf9f92f3a1f2` was read
completely, followed by the complete revised source. This is an included
chapter of `articles/proximal-distal-a-journey-through-the-swing.qmd`, not a
separate production route. The entire companion is not thereby reviewed.

The revision preserves the sustained golfer/reviewer dialogue and both long
worked conversations. Scientific source corrections and independent numerical
checks are complete at this checkpoint. Final visual review and hosted delivery
are separate requirements; consult the canonical `AGENT_HANDOFF.md` for status.

## Decisions and Independent Derivations

1. **Momentum and Acceleration.** Removed momentum as a cause of acceleration.
   A fixed planar rotor with inertia 0.1 kg m², angular speed 4 rad/s and
   moments -2/+5 N m has acceleration 30 rad/s². The individual powers are
   -8/+20 W and net power is 12 W. This establishes coexistence of an opposing
   contribution and acceleration, not optimality of the opposing command.
2. **Power Boundaries.** A rigid-body hand wrench at A supplies
   `F·v_A + M_A·omega`. Moment arms are included once. Joint power uses relative
   angular velocity or a conjugate generalized speed. Elastic storage is part
   of the club's energy ledger; its return is not an extra external supply.
   A flexible shaft needs the individual contact/deformation velocities.
3. **Reporting Point and Observer.** For r=B-A, substitute
   `v_B=v_A+omega×r` and `M_B=M_A-r×F`. The added triple products cancel.
   With r=(1,0,0), F=(0,2,0), v_A=(0,3,0), omega=(0,0,4), M_A=(0,0,5),
   both evaluations give 26 W (6+20 versus 14+12). This transports one
   physical velocity field; changing observer is a different operation.
4. **Instantaneous Attribution and Forward Work.** A 1 kg mass acted on by
   two 1 N forces for one second from rest ends with 2 J. Each force supplies
   1 J along the baseline. Removing one force produces a different trajectory
   and final energy 0.5 J; the surviving force supplies 0.5 J. Thus a 1 J
   baseline attribution is not the 1.5 J forward energy difference. Independent
   `solve_ivp` trajectories and `quad` work integrals reproduce these values.
5. **Grip Separation.** Around the midpoint, the force moment is
   `d×(F_R-F_L)/2`; the triangle inequality gives the stated bound. Equal
   opposite 10 N forces separated by 0.1, 0.01 and 0 m give 1, 0.1 and 0 N m.
   A direct free moment survives collapse. So can the resultant moment about
   a different point. A geometry intervention must resolve compatible states.
6. **Inference.** Coordinate invariance, numerical convergence, and physical
   interventions have distinct acceptance conditions. A component sign can
   flip legitimately with its oriented axis. Equal-fitting mechanisms show
   nonidentification; a failed scoped prediction challenges that prediction.
   An unsuccessful manipulation or imprecise null result is not equivalence.
7. **Matched Tasks.** The archived allocation sweep matches an instantaneous
   club control moment. It does not demonstrate matching a complete club path
   through dynamic activation/contact states. The chapter now states that
   extra forward-test requirement.
8. **Figure and Provenance.** The shared reviewer-path generator labels its
   boxes Claim, Figure, Data, Script, Test, Manifest. The chapter's former
   caption described a different diagram. Corrected caption/alt text preserve
   the shared asset and Chapter 27. Final research links now use the declared
   upstream evidence revision rather than a moving branch.

## Archived Primary Model Evidence

All three JSON records below were read completely from the existing local
UpstreamDrift Git object at
`a1a613999eb0c744da96caa040941955eb210a21`. Their corresponding NPZ arrays were
read independently to verify the specific numerical claims. No upstream
rollout was rerun. The six exact SHA-256 identities and checked values are in
`reports/technical-review/curiosity-checked-examples.json`.

- **Forward Two-Arm Study:** `data/forward_two_arm_study.json` and NPZ under
  `docs/research/proximal_distal_energy_transfer/`. Verified that the branch
  begins with exactly baseline q/qdot at index 800, covers 0.20-0.25 s, has
  zero applied control power and a negative force-generated moment at every
  stored sample, minimum -7.432451660254221 N m. The three declared source-file
  hashes also match their pinned Git bytes. Read the provider chapter's first
  170 lines, the full `branch_zero_command` function, persistence definition,
  and study excerpts constructing the intervention/control records. These
  support an archived forward-branch result, not a fresh execution, human
  contact qualification, or full solver-code audit. Fixed shoulders and ideal
  bilateral grip remain model assumptions. The 0.18 s cut's zero immediate
  persistence is not absence of later negative samples.
- **Allocation and Preload:** `data/torque_allocation_preload_study.json` and
  NPZ. Independently subtracting the archived metric arrays reproduces all
  twelve sensitivity differences. Three zero-width cases differ by at most
  2.78e-16 N m s, below the declared 1e-10 tolerance; all nine positive-width
  cases favor persistent direction by that metric. Read the channel dead-zone
  mapping and study initialization/sweep code. Equivalence is metric-specific,
  not equality of every channel trajectory or evidence of a human dead zone.
- **Biological Bridge:** `data/advanced_biological_bridge.json` and NPZ.
  Independently subtracting the two timestep-audit arrays reproduces all five
  differences: 0.0027696574, 0.0015530456, 0.0008566297, 0.0006280699 and
  0.0005143996 N m s. All are positive and decreasing under refinement. The
  provider explicitly withholds convergence of the magnitude. The chapter
  previously omitted that caveat. No physiological effect size is established.
  The adapter round trips in the same record are coordinate checks, not engine
  executions; none are promoted to runtime or human validation here.

These are the revision already identified by the site's complete-claim-audit
snapshot. The immutable monograph projection at revision 85cce4d3 and all
publication/authority pins remain unchanged. A newer snapshot is not a license
to rewrite an older immutable projection.

## External Primary Reading

- [Lynch and Park, Wrenches](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/):
  description and full short transcript read (lines 29-37 in retrieval),
  covering moment construction and wrench/twist duality. The chapter's
  observer qualification and numerical example were independently derived.
- [Höppner et al., 2017](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2017.00017/full):
  abstract, participant/protocol passages, and relevant discussion read.
  Ten seated participants maintained posture during grip perturbation tasks;
  co-contraction permitted different stiffness at similar force. This supports
  separate measurement, not golf transfer or a universal tension prescription.
  Full paper/appendix and figures are not claimed as reviewed. PMC returned a
  browser challenge; the publisher supplied the inspected passages.
- The Ludvig/Perreault knee-stiffness paper was only a search lead; its PMC
  content was unavailable in the attempted open. It is not cited as inspected
  evidence in the chapter.

## Validation Recipe and Limits

The local read-only QA script is
`docs/development/technical-review/check_curiosity_examples.py`. Run with
`py -3.12 -X utf8` from the worktree. It reads provider files using
`git -C ../UpstreamDrift show <revision>:<path>`, verifies source/array
consistency, integrates the independent mass example, checks the rotor and
point-transport arithmetic, and writes the checked-example report. The
mathematical specifications above allow independent reproduction without
depending on that local scratch script.

The revised chapter requires final web/PDF visual verification, link checks,
PDF synchronization, and a regular PR before publication. It must not
mark the entire book route reviewed. Open shared TOC #4370 and keyboard #4374,
peer Chapter 29, and impact/acoustics #4253/#4255 remain outside this edit.

## Checkpoint Results and Newly Identified Limits

- Final full root: `py -3.12 -X utf8 -m pytest --cov`, 5,335 passed,
  29 skipped, 132 deselected, 59 warnings, 193.66 s, coverage 79.29%.
  Log `curiosity-checkpoint-root.log`, process25465 completed exit0.
  Companion/pin tests27 and metadata/inventory tests22 pass; changed test
  Ruff and Black100 pass; all638 publication-source titles pass.
- The initial root70725 failed four checks. Two found that the direct Quarto
  PDF command had moved the tracked PDF away from its source path; its exact
  HEAD bytes were restored. One required adding the wrapper's route to the
  already-recorded provider revision. One misclassified a valid `@eq-`
  cross-reference as a citation. The citation check now subtracts only IDs
  actually declared in the manuscript; unresolved references still fail.
- Regenerated pin routes and the freshness dashboard were inspected. Only one
  route is added to the existing a1a61399 pin. All14 commits, states, dates,
  notes and active authority are unchanged; the pin remains unqualified.
  The dashboard generator and its tests were read fully; generated source
  changes only its route count/list. The mandatory evidence refresh changes
  only two digests in the dashboard's historical review, and the corresponding
  generated report. This is an additive route-metadata review, not renewed
  scientific qualification of the entire provider. A current-commit binding
  should follow the checkpoint's dashboard/source verification before release.
- Initial selected web/PDF renders and final paired render87026 succeeded.
  The direct 286-page Quarto PDF exposes a hierarchy mismatch: internal
  sections are promoted to chapters. Its pages265-272 were visually read,
  including the corrected figure and first two display equations. Remaining
  pages273-281 are not yet visually reviewed. The stored 202-page PDF has the
  correct Chapter30 hierarchy but old prose. Issue4376 explicitly distinguishes
  the rebuild/web defect from the stored PDF. Neither artifact is a finished
  replacement publication for this revision.
- Browser job79590 completed and its returned eight cases were parsed. All
  report no page overflow or MathJax errors; 47 chapter math containers are
  present. Early light-theme measurements counted zero settled displays;
  later measurements counted four. Wide mobile containers and visibly tiny
  point-transport math require a scoped readability/scroll verification pass.
  Only full-width capture00 and light/dark mobile point-transport captures were
  visually read. The other20 reading captures and remaining mobile images are
  pending. A service-worker update toast obscures the lower page and should be
  dismissed before definitive captures. Browser closed; no blanket visual pass
  is claimed. Local console records the known legacy-polyfill CSP rejection;
  production normalization and an actual route gate still need verification.
- Six unrelated test-generated registries/summaries were restored only after
  proving exact text equivalence modulo newlines or parsed JSON equivalence
  excluding `generated_on`. No user or peer content was discarded.

## Subsequent Hierarchy and Publication Checkpoint

The earlier render limitations above are historical. The corrected 205-page
PDF and all revised Chapter 30 pages have now been read, and both tracked PDF
copies are synchronized. All 29 final web captures were read; eight settled
width/theme cases confirm readable, keyboard-scrollable equations. See
`companion-hierarchy-review.md` and `companion-hierarchy-verification.json` for
the exact scope, artifact hashes, remaining presentation limits and root-test
hygiene repair. The full-book scientific review remains incomplete.
