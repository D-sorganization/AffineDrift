# Anatomy and Joint Modeling Review

## Scope and Current Acceptance

Issue [#4412](https://github.com/D-sorganization/AffineDrift/issues/4412) continues
the Physics review #4054 under corpus #4021 and epic #4009. Both Chapter 22
sources were inspected, including their differing injury language, taxonomy,
anatomical sections, summary and seven exercises. Both sources now have a complete
technical revision, including all seven worked exercises. Local numerical,
source, print and public-route checks are recorded below. Protected merge and
exact-main deployment acceptance remain outstanding. This review qualifies this
chapter, not the entire textbook or a clinical application.

## Why the Review Was Reopened

At base `bc22952d`, the route was marked reviewed with no findings and only
the QMD source as evidence, bound to `4f372cd4326fc94c82500334af22b407b098febd`.
That source still equated a scalar with a vector in the hinge constraints,
misstated the universal-joint constraint, and claimed its perpendicular axes
could align and lock. The body-count explanation also disagreed between print
and web. These are direct counterexamples to complete scientific acceptance.
Issues #4054, #4021 and #4009 were reopened; #4412 is a native child of #4054.
The chapter route returns to deferred while its substantive review is incomplete.
Other routes are not reclassified without inspection.

## Joint Geometry and Mechanical Interpretation

- Define frames at joint origins and distinguish their coincidence from the
  movement of segment centers of mass. A revolute joint aligns two body-fixed
  unit axes: three written alignment components have differential rank two.
- A prismatic joint must suppress two transverse translations. One unspecified
  perpendicular dot product is insufficient.
- Unit quaternion component count is not rotational mobility. An Euler chart
  singularity does not remove a spherical joint's physical rotational freedom.
- The universal joint imposes orthogonality of one axis fixed in each body.
  Its angular-velocity columns stay orthonormal in the explicit two-angle
  parameterization. A fixed-normal preservation equation rejects legitimate
  motion. Driveshaft transmission geometry, task Jacobians and local joint
  freedom must not be conflated.
- Derive generalized moment by virtual power, using the current rate map.
  Ideal reaction moments can carry load while doing no relative work.
- Count the fixed-base weld or merge the base with ground. A missing weld
  explains the extra six freedoms; planarity is not the error. For loops, use
  independent closure rank and distinguish infinitesimal mobility at a singular
  configuration from realizable finite motion.

The independent tests use finite rotation increments, differential constraint
rank, power pairing, Euler chart rank and an axial point-displacement example.
The initial regression run failed in both editions, with six mathematical
checks passing. After correction all eight checks pass. These checks support
the stated equations; they do not prove human joint fidelity or clinical risk.

## Anatomical Findings and Dispositions

1. **P1, corrected — Joint geometry and counting.** Replace dimensionally invalid
   constraints, a fixed universal-joint normal and false axis-alignment locking.
   Separate coordinate singularities, joint mobility, loop rank and task authority.
2. **P1, corrected — Anatomy and force inference.** Replace universal knee fidelity
   and optimizer claims with sensitivity and identification requirements. Distinguish
   hip rotation from pelvis turn, moving scapular centers from fixed humeral roots,
   anatomical angles from laboratory orientations, and forearm rotation from wrist
   deformation. Two coordinates can have coupled forces and energy.
3. **P1, corrected — Clinical interpretation.** Remove unsourced injury cutoffs,
   direct-measurement attribution for modeled spine loads, a universal wrist rate,
   compulsory trail-arm eccentric recruitment and DCR-based injury causation.
   Explain what kinematics, net moments, EMG, tissue-load models and clinical
   outcomes can identify at each stage.
4. **P2, corrected — Worked models and exercises.** Replace the erroneous per-arm
   count with a fully specified 35-velocity tree; the separate fixed-pelvis exercise
   has 18 freedoms before an assumed independent rank-six hand closure. Rework
   every exercise with sufficient data or an explicit non-identifiability answer.
5. **P2, corrected — Presentation and editions.** Align the scientific content,
   preserve section targets, split six wide displays, fix print title/paragraph
   overflow and avoid a duplicate exercise label. Remove the small print-only
   primitive sketch, whose spherical 3R shorthand obscured the chart distinction.

## Connections and Adversarial Checks

- A fitted segment orientation cannot recover a missing translating shoulder
  center. Differentiate the center-plus-orientation expression and check it against
  finite position increments.
- A common laboratory rotation changes pelvis and femur poses while preserving
  their relative hip rotation. A pelvis-turn target therefore does not prescribe
  a unique anatomical hip angle or spinal compensation.
- A prescribed scapular coupling changes generalized forces through the transpose
  of its derivative. Power conservation under that reduction does not validate its
  physiology. Existing muscle-work evidence is bounded to its observed task.
- A positive-definite two-coordinate stiffness matrix has distinct soft and stiff
  directions without adding a kinematic degree of freedom. The numerical matrix
  and its energies are constructed examples, not identified wrist parameters.
- A rigid grip retains a constant relative transform while the club has nonzero
  shaft-axis angular velocity in space. Club roll alone cannot identify slip.
- An omitted axial rotation moves an off-axis point, not a point on its axis;
  tibial length alone cannot resolve the exercise. Geometry uncertainty contributes
  separately from coordinate uncertainty to an output sensitivity.
- Ground wrench, contact-point power, COM power and arch energy are separate
  quantities. The passive spring-damper example explicitly balances storage and
  dissipation. A club momentum balance does not uniquely allocate two hand loads.
- A matching release trace does not uniquely identify wrist stiffness. Geometry,
  inputs, initial state, contact, shaft dynamics and measurement conventions offer
  competing explanations. More detail requires additional observations, not
  stronger clinical language.

These counterexamples support the chapter's investigative message: model choices
connect motion, load, work and control, while every inference needs its own
observable and validation boundary. The preface still contains a contradictory
muscles-going-limp/free-power explanation; that separate finding is tracked in
[#4413](https://github.com/D-sorganization/AffineDrift/issues/4413), also under #4054.

## Sources Read and Reading Limits

- Lynch and Park, [Modern Robotics, section 2.2 video transcript](https://modernrobotics.northwestern.edu/nu-gm-book-resource/2-2-degrees-of-freedom-of-a-robot/):
  joint freedom and independent constraints. The detailed frame/rate/power
  derivations above are independently reconstructed and numerically checked.
- Crisco et al. (2005), [publisher abstract via PubMed](https://pubmed.ncbi.nlm.nih.gov/16322624/):
  radial extension toward ulnar flexion and measured carpal kinematics; does
  not establish a universally strongest wrist motion or a golf coaching rule.
- McClure et al. (2001), [abstract](https://pubmed.ncbi.nlm.nih.gov/11408911/):
  eight volunteers, bone-pin scapular measurements and three-dimensional motion
  during arm elevation. This is not a golf-specific rhythm calibration.
- Seth et al. (2016), [publisher article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0141028):
  abstract plus selected methods/results/discussion inspected for the cited
  scapulothoracic formulation. No golf-specific numerical accuracy is claimed.
- Seth et al. (2019), [publisher article](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2019.00090/full):
  abstract, methods, results and discussion inspected, including model scaling and
  the single-subject limitation. Its work estimates are not direct force measurements.
- Griffin et al. (2016), [consensus abstract](https://pubmed.ncbi.nlm.nih.gov/27629403/):
  the FAI-syndrome definition requires symptoms, signs and imaging; it supplies no
  universal golf hip-angle limit.
- Lim et al. (2012), [study abstract](https://pubmed.ncbi.nlm.nih.gov/22900401/):
  five male collegiate golfers; modeled L4-L5 loading, not instrumented spinal
  measurements. Only abstract-supported details are retained.

Neumann/Nordin remain the chapter's existing general anatomy references; their
entire books were not retrieved or newly reviewed. Reference ROM values remain
qualified examples of assessment, not swing targets. The Cheetham citation retains
the earlier verified pelvis/torso distinction. Search snippets alone were not used
to support new quantitative or clinical statements.

## Validation and Remaining Publication Work

- Initial taxonomy checks: two edition regressions failed, six independent
  checks passed; corrected run eight passed. Extended revision: two further
  edition regressions failed; an initially overstrict floating-point zero check
  was corrected to a 1e-14 tolerance. Final mechanics/edition/label module has
  16 passing checks. Ruff and Black100 pass.
- Full Python run: 5,368 passed, 29 skipped, 132 deselected, 59 warnings;
  coverage 79.06% against a 75% floor. Two failures identified the shared
  bibliography's stale review digest. Regeneration fixed that dependency;
  the combined mechanics, inventory, deployment-boundary, citation and LaTeX
  focused rerun passed all 94 checks. This is not described as a clean full rerun.
- Added five bibliography entries; reused the existing Lim entry. Existing
  bibliography records were not changed. The Chapter 16 evidence dependency
  requires an explicit commit rebind after the new source checkpoint.
- Quarto 1.8.26, matching the repository pin, rendered the book view and the
  public route. The initial book phone view exposed six wide displays; these
  were split at natural boundaries. The public route has 109 MathJax containers,
  no MathJax errors and no document overflow at 390 pixels. A complete scroll
  pass in all four viewport/theme cases rendered all 109 expressions (zero
  remaining lazy placeholders), with no display-container overflow or broken
  local anchors. Initial immediate-scroll screenshots were premature; settled
  captures were inspected instead. The service-worker update notice was
  dismissed using its normal accessible button.
- The chapter-only print build uses the actual book preamble and the production
  print ordinal (24). All 18 pages, including the bibliography, were rasterized
  and visually inspected. Final compilation has no overfull boxes, undefined
  citations or reference warnings. This is not a complete-book PDF acceptance.
- The normal public-site verifier passes all four desktop/mobile light/dark
  cases, with zero serious/critical axe violations. The standard deployment
  polyfill sanitation was applied; no CSP relaxation or source workaround was
  introduced. A scoped manifest avoids treating old local excluded HTML as
  fresh deployment content.
- Local artifacts remain under `docs/development/technical-review/anatomy-*`.
  Exact committed evidence binding, protected PR checks, merge and post-merge
  deployment verification remain to be completed.

## Publication Checkpoint From the Previous Session

PR #4377 is merged at `32010d08d9980896c51f0c93ac875f23eb818556`.
Its exact Deploy Website run `34730740904` completed successfully. Live artifact
`10309497076` was downloaded and inspected on September 22. All 960 route cases
passed; the four companion-route records independently confirm HTTP 200, zero
overflow and passing desktop/mobile light/dark checks, with no serious/critical
axe findings. This closes the outstanding publication verification for
DL-#4375 and DL-#4376; it is not a new review of every companion chapter.
