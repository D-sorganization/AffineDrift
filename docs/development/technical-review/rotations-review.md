# Rotation Conventions and Quaternion Review

## Scope and Reading Record

Issue #4288 under epic #4009, corpus #4021 and Geometry batch #4055. The complete
899-line Volume 0 chapter (indexed 7,633 words), 131-line web companion, actual
120-line included quaternion program and all 16 original exercises were read.
The program's existing independent tests were also read in full. The revised
configuration and screw chapters' introductory frame/tangent conventions were
checked for consistency; this does not claim another full audit of those chapters.

The rotation chapter reverses intrinsic ZYX/ZXZ factors and pairs spatial
Jacobian columns with the wrong rate ordering. Its manifold proof lacks a rank
argument; its fixed-axis proof assumes the result. Gimbal lock is confused with
loss of physical freedom, and body/spatial angular velocities are mixed. The
quaternion domain omits -1, the inverse omits zero, and matrix conversion divides
by zero at half turns. SLERP changes the dot product without changing its endpoint.
Exercises repeat these errors and omit the Lie-bracket factor of two. The web
edition omits most derivations and every exercise while adding blanket numerical
stability and software-storage claims. The included program's rotate/to_matrix
contracts disagree for scaled quaternions and do not validate finite inputs.

## Direction and Derivation Boundaries

Use right-handed frames and column vectors with R=R_sb taking body components
to spatial components. Compose R_sc=R_sb R_bc. Intrinsic ZYX is Rz(psi) Ry(theta)
Rx(phi); the spatial rate columns, ordered roll/pitch/yaw, are Rz Ry e_x,
Rz e_y and e_z. Establish rank and inverse conditioning without claiming that
the rigid body loses freedom. Derive both Rdot R^T and R^T Rdot, their adjoint
relation and quaternion kinematics. Distinguish the finite rotation axis from
instantaneous angular velocity and retain the neighboring screw convention.

Prove the regular-level-set rank of R^T R and derive the fixed axis from odd
dimension, orthogonality and determinant. Explain S^3/{+1,-1}, local rotation
vectors, the principal-log cut at pi and exponential differential degeneracy
at nonzero 2pi multiples. Supply a largest-component quaternion conversion,
short-arc SLERP with sign alignment and an honest small-angle approximation.
Connect small orientation perturbations to clubface normals, point locations,
frame-transformed uncertainty and contact timing. Geometry alone establishes
neither torque feasibility nor measured swing performance.

## Primary-Source Reading Boundaries

- Lynch and Park's official Modern Robotics video transcripts 3.2.1 part 2 and
  3.2.2 were read completely: matrix composition, component change, active
  rotation and spatial/body angular velocity. The algebra here is independently
  derived rather than copied from the transcripts.
- Shoemake (1985), author paper hosted at Carnegie Mellon: abstract and
  introduction, section 3.3, section 3.4's sign choice, and inspected passages
  in sections 4.3 and 5.2–5.4. This is not a full ten-page-paper reading or
  replication of its spline experiments. DOI10.1145/325165.325242 is the journal
  version; conference DOI10.1145/325334.325242 is a separate presentation record.
- MuJoCo's official simulation documentation: quaternion order (w,x,y,z) and
  position/velocity dimensionality passages read. This supports a precise
  interface example, not claims about every engine or comparative speed.
- Hamilton's original letter dated17 October1843, published in1844: first
  letter page and editorial metadata read, including its account of the prior
  day's discovery. Do not imply the full seven-page algebra was audited.
- Numdam's Rodrigues1840 record verifies the full title, journal, volume5 and
  pages380–440. Its full historical proof has not been read. The modern matrix
  proof is provided independently. Euler Archive E478 retrieval failed; do not
  retain the unsupported1775 publication-date claim.

Sources: [Lynch–Park Frames](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-1-rotation-matrices-part-2-of-2/),
[Lynch–Park Rates](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-2-angular-velocities/),
[Shoemake](https://www.cs.cmu.edu/~kiranb/animation/p245-shoemake.pdf),
[MuJoCo](https://mujoco.readthedocs.io/en/latest/programming/simulation.html),
[Hamilton](https://www.maths.tcd.ie/pub/HistMath/People/Hamilton/QLetter/QLetter.pdf),
[Rodrigues](https://www.numdam.org/item/JMPA_1840_1_5__380_0/).

## Coordination and Publication

The issue-filing exemption list has no AffineDrift entry; scoped duplicate search
found no existing correction covering this chapter. Claim checked free, then
leased to codex/session technical-review-20260906 until18:34:23UTC. This branch
starts at residual PR #4287 head5f9008e6, whose protected squash auto-merge is
enabled. Replay only rotation commits after that base onto protected main before
first push. Residual publication is still pending; retain its exact validation
and check publication while this correction proceeds. No subagents, no immutable
monograph changes, and no commit/push/switch during local QA. Corpus unfinished.

## Initial Implementation and Numerical Verification

TDD RED:44 failures,75 passes and12 warnings on the original teaching program.
The corrected program validates finite shapes and domains, normalizes quaternions
after scaling to avoid intermediate norm overflow/underflow, uses the same
normalized rotation contract at both entry points, and adds largest-component
matrix conversion. Initial GREEN:119 tests pass. Eight further independent
derivation checks bring the focused lane to127 passes in1.63s; Ruff/Black pass.
These checks differentiate SciPy rotation constructions to verify Euler-rate
columns, body/spatial rates and the exponential differential at pi and2pi,
and verify point/normal sensitivity, conditioning and timestamp examples.

Both complete editions now share the substantive argument and18 exercises with
answer checks: all16 original topics retained and two task/timing exercises added.
The web edition typesets the actual checked program. The print frame figure is
replaced by an explicitly specified35-degree rotation, paired with a web SVG.
All explicit historical print labels and index terms are retained; the original
live page's11 content IDs have been captured for final retention verification.
Title audit631 passes. Full-root, content/static, PDF and browser QA are pending.

The initial conversion script attempted to add missing prose spaces but also
changed digits inside LaTeX labels. Its label-set assertion stopped before any
canonical write. The repaired conversion protects math and command arguments;
all original label checks then pass. This diagnostic was a conversion failure,
not a claim that the chapter had rendered successfully.

## Residual Protected Merge

PR #4287 passed protected checks and merged at16:50:25UTC as
10d4e7cb9de4633022e5cd93885cb54aca8a34ba. Deployment34253504940, protected-main
CI34253504820 and textbook run34253504790 are active. Verify their completion and
the exact live artifact before claiming publication. The rotation branch still
starts at5f9008e6; replay only its own commits onto protected main before pushing.

## Root Tests and Print Iteration

The complete root run passes4,828 tests with29 skips,131 deselections and59
warnings in304.58s. This invocation did not request coverage; the required
coverage gate remains a separate check. All127 focused tests pass again after
the strict-mypy correction wrapping the SLERP result in a typed NumPy array.
The initial combined typing/style command returned its final style exit code,
masking one mypy no-any-return diagnostic; the diagnostic was inspected and
repaired, and a separate strict-mypy run now passes. Do not describe the initial
typing run as successful.

The first latexmk invocation failed before compilation because MiKTeX could not
find Perl. Direct pdflatex, bibtex, makeindex and repeated pdflatex built the
241-page volume. Print inspection then identified cramped inline equations,
overlong headings and missing prose spacing around inline mathematics. These
are being corrected in the paired canonical sources before final visual QA.
Full-book duplicate-label warnings predate this slice; retain and distinguish
them from chapter-local overflow rather than claiming a warning-free volume.

## Publication and Validation Checkpoint

Residual #4286 is now published: protected-main CI34253504820, textbook
run34253504790 attempt2 and deployment34253504940 succeed. Exact live
artifact10068131804 passes956/956 across239 routes with zero serious/critical
axe findings, retries or transient responses. The first textbook run compiled
every book; Physics artifact finalization failed with an intermediary403.
Only the failed job was rerun, and it passed. No source repair was needed.

The rotation coverage run passes4,828 tests,29 skips and131 deselections in
365.91s, with79.04% across the configured coverage scope (75% required). This
differs from earlier src-only percentages; do not compare them as the same scope.
Ruff, Black668 files and root mypy86 files pass. The default quality invocation
also scanned untracked review scratch and reported139 findings; the same checker
passes on all677 tracked Python files and on all three changed/new Python files.
No scratch scripts are part of the proposed commit. Static34 passes after fixing
two LaTeX quote pairs; content130 passes with four skips.

Complete print pages76–96 were inspected. The final numbering is local to this
chapter and makes18 exercises correspond to18 answers. Web inspection caught
collapsed answer numbering after a display block, repeated figure captions,
and long inline equations spilling out of narrow text columns. The converter
now nests the display inside its list item; the figure uses an explicit alt
attribute; scoped CSS exposes horizontal inline-math scrolling at full type size.
The final browser sweep, equation edges and responsive checks are in progress.

## Final Local Review

Final browser QA covers the complete chapter in desktop light, phone light and
phone dark views: 202 overlapping views, 83 equation-edge views, and 113 extra
views of all code/table horizontal positions, figure, answers and bibliography.
All 45 contact sheets were inspected. Long mathematics retains context font
size and reachable horizontal scrolling; the document itself does not overflow.
The seven-width, two-theme automated check passes all 14 cases, with zero
serious/critical axe findings. All 11 historical anchors occur exactly once,
there are no duplicate IDs, all 18 answers are numbered, and the rendered code
matches the actual tested program. Local stylesheet and image requests succeed.

The final PDF has 241 pages. Chapter physical pages 76–96 and bibliography
pages 239–241 were visually inspected; final code spreads were rechecked after
the last docstring changes. Chapter-local overflow is limited to a visually
negligible 0.24196-point prose box; pre-existing book-wide duplicate-label
warnings remain distinguished from this chapter's corrected content.

The final static lane passes 34 checks, content passes 130 with four skips,
title case passes 631 sources, and the new CSS passes Stylelint, the stylesheet
budget and architecture checks. Runtime checks remain 127 focused and 4,828
root passes (29 skips, 131 deselections); the coverage run passes the configured
75% gate at 79.04%. Strict mypy passes the included program and the separate
root mypy lane passes 86 sources. Ruff and Black pass, as does the quality
checker on all 677 tracked Python files and all three changed/new Python files.

Review also exposed a duplicate title anchor and stale browser CSS retained by
a service worker. The duplicate was removed. Unregistering the local worker,
clearing its caches and reloading verified the canonical stylesheet. The final
inline rule constrains the parent math span; the first child-only rule did not
contain long expressions. The browser harness now verifies scroll reachability
and resets horizontal positions at each viewport/theme transition. Initial
failures are retained in scratch logs and are not counted as successful checks.

All local builds, tests and browser QA have ended. Protected PR submission and
exact-revision publication verification remain pending; the corpus is unfinished.
