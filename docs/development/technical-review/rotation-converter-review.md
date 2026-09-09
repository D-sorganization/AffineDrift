# Rotation Converter and Reference Review — Issue #4322

## Scope and Reading Boundaries

Native child of epic #4009, corpus #4021. Both complete sources were read:
rotation-converter.qmd (1,067 lines, indexed 6,405 words including UI) and
rotation-representations-reference.qmd (352 lines, indexed 1,849 words), plus
the complete original JavaScript engine/UI, all 52 existing Jest cases and
the existing Python mixed-sign half-turn test. The existing Volume 0
quaternion_demo.py was also read in full for reuse. The companion screw and
book articles are linked, not claimed newly audited here. No immutable source
is changed. Claim was clear; codex lease technical-review-20260906 expires
2026-09-09T22:51:27Z. Branch fix/4322-rotation-converter-reference begins after
energy documentation f0a5b6c2; replay only this issue before first push if
parent PR #4321 merges.

## Findings and Independent Checks

The old UI accepts numeric prefixes and substitutes a z axis for a zero axis,
even with nonzero angle. Its matrix path returns purported rotations for
reflections, shear and zero matrices. The displayed infinity norm is actually
the maximum absolute entry of R.T R-I. Approximate input acceptance is a
rounding convention, not a fit or uncertainty estimate.

arccos loses tiny rotations when the trace rounds to three. The quaternion
extractor divides by an arbitrarily small scalar near pi; its half-turn branch
is too narrow to prevent this. The axis extractor snaps a neighborhood of pi.
The Euler extractor treats |sin(pitch)| within 1e-7 of one as exact lock and
drops roll, changing near-lock orientations. The printed dynamic formulas do
not identify their singular cases. The Python example has no half-turn axis
branch or gimbal-lock branch; claimed identical algorithms are not identical.

TDD first ran 29 new JavaScript cases. An initial parameterized-array fixture
passed rows as separate arguments; this was corrected before implementation.
The meaningful RED result is 19 failures/10 passes. New tests construct
matrices independently from normalized analytic quaternions, checking finite
outputs, unit norm and reconstruction at 1e-12, 1e-8, both sides of pi,
mixed-sign axes and near 2pi. Nonzero yaw and roll test both signs of pitch
lock and nearby rotations. Reflection, shear, zero, NaN, infinity, numeric
strings and 1e308 quaternion magnitudes exercise actual public boundaries.
After the mathematics correction, all 81 old/new JavaScript cases pass.

The Python RED cases expose five axis-boundary failures, one near-lock Euler
failure and three missing reflection rejections. Three other cases pass.
The replacement reuses the already-reviewed Volume 0 quaternion routines;
it does not reproduce that implementation in the reference article.

## Derivation Decisions

For an exact rotation, squared quaternion components are
(1+tr R, 1+2R11-tr R, 1+2R22-tr R, 1+2R33-tr R)/4.
Their sum is one, so the largest is at least 1/4 and its component is at
least 1/2. Select it, recover the others using symmetric/skew entries divided
by four times that component, normalize and choose nonnegative scalar w.
Then theta=2 atan2(norm(v),w) retains tiny angles and returns [0,pi]; the
identity axis and the sign at exactly pi remain conventions. Finite input
axis/quaternion normalization scales by the maximum component before norming.

ZYX extraction uses atan2(-R31,hypot(R11,R21)); generic yaw and roll are
retained until |cos(pitch)|<1e-12. At either exact lock choose roll=0 and
yaw=atan2(-R12,R22). This reproduces yaw-roll at +pi/2 and yaw+roll at
-pi/2. It does not erase physical angular freedom or cure measurement
ill-conditioning. ZYZ instead locks at middle angle 0 or pi.

Rotation vectors rho are elements of R^3; hat(rho) is in so(3). Their
derivative is generally not angular velocity. R alone gives orientation,
not a spatial axis line or motion history. The reference must connect
calibrated relative frames, time-resolved angular velocity, task direction
and uncertainty to the separately specified inertia/force/power problem.

## Primary Sources Consulted

Modern Robotics official Chapter 3.2.3 video transcript, complete short text:
https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-3-exponential-coordinates-of-rotation-part-2-of-2/
The exponential maps skew matrices to rotations; its constant-axis construction
does not identify an arbitrary measured motion history. Authors are Kevin M.
Lynch and Frank C. Park (not the reversed order in the old article).

Official Chapter 3.2.2 angular-velocity transcript:
https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-2-angular-velocities/
The complete relevant transcript was subsequently read (official page lines
29–39): basis-vector derivatives give Rdot=[omega_s]R and omega_s=R omega_b.
The article independently derives the Euler map, Jacobian and covariance;
those additions are not represented as quotations from the transcript.

SciPy official Rotation.from_matrix and as_euler descriptions/parameters read:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_matrix.html
https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.as_euler.html
These document matrix fitting and Euler sequence/lock conventions. Our browser
does not promise SciPy's projection algorithm; its principal extraction and
independent checks are specified directly. No complete-book reading is claimed.

## Implemented Correction and Compatibility

Both complete articles are reconciled. The reference connects noncommuting
frame composition, intrinsic/extrinsic Euler conventions, both ZYX locks,
rotation-vector Jacobians, Hamilton composition and quaternion derivatives to
calibrated relative motion, face-normal sensitivity, correlated uncertainty
and physical power. An orientation is not a trajectory, joint-axis location,
angular velocity or evidence of energy transfer. The original 23 heading
anchors remain reachable. All four book links point to verified published
chapter routes. No complete reading of those companion chapters is claimed
as part of this issue.

The converter separates the engine, UI and optional Three.js illustration.
Finite decimal/scientific parsing rejects prefixes, nonfinite entries, zero
axes/quaternions and improper matrices. Invalid edits retain explicitly stale
results; editing does not rewrite the active field. Unit changes update
labels, output and illustration while rotation-vector components stay radians.
Identity and half-turn branches are explicit. The reported matrix residual is
the maximum absolute entry, not an induced infinity norm. Large finite input
normalization scales first. Formulas describe the actual extraction branch.

Canonical changes: articles/rotation-converter.qmd,
articles/rotation-representations-reference.qmd, js/rotation-converter.js,
js/rotation-converter-ui.js, js/rotation-converter-viz.js,
css/rotation-converter.css, scripts/sync_frontend_assets.py,
src/tools/rotation_reference_examples.py and four rotation test files.
Generated frontend mirrors are synchronized but are not committed artifacts.
The original checkout and articles/proximal_distal_energy_transfer/ are untouched.
No PDF target changes in this issue.

## Local Validation

- JavaScript numerical RED: 19 fail, 10 pass; corrected engine plus existing
  cases: 81 pass. UI RED: ten missing-module failures; GREEN: ten pass. Two
  subsequent fallback cases bring the final UI run to 12 passes. Full Jest
  before those two additions: 24 suites, 395 pass, 19 skip; final UI 12 pass.
  Commands use node node_modules/jest/bin/jest.js with --runInBand.
- Python reference RED: nine fail, three pass; GREEN: 12 pass. Six independent
  kinematics cases compare finite differences/SciPy, frame cancellation,
  Hamilton derivatives and face sensitivity. One initial theoretical-zero
  comparison needed an explicit 1e-14 absolute tolerance; all final 18 pass.
- py -3.12 -X utf8 -m pytest --cov --cov-report=xml --timeout=60:
  **5,078 pass, 29 skip, 131 deselected; 79.19% coverage**, 342.26 seconds.
  This includes configured tests and benchmarks and src/scripts coverage.
  An earlier narrower tests/ --cov=src run passed 5,033 with 92.68% coverage;
  it is not the comparable configured coverage figure.
- Content lane: pytest --override-ini addopts= tests/ -m content_lint
  --timeout=120: 130 pass, four skip. CI static contracts: all 34 pass.
- Ruff check . passes; Black --check --line-length 100 . passes (686 files).
  Configured strict mypy command checks 91 sources. Full tracked Python
  code-quality check, including both newly created Python files, passes.
- scripts/link-checker.py --site-gate passes. A separate broad scan of the
  accumulated local docs HTML reports 35 broken links and 39 orphaned files:
  old scratch previews and partial-book render links, with neither revised
  rotation route among the broken sources. This is not a clean full-site
  deployment artifact and is not reported as a passing production scan.
- Both selected Quarto HTML renders pass with root configuration restored.
  The complete rendered Python program matches the source and executes all
  13 reconstruction assertions (five axis/quaternion cases and three Euler
  cases). It imports the shared tested adapter; no copied algorithm drifts.

## Browser and Visual Evidence

Full page inspection covers 20 overlapping body captures (seven converter,
13 reference), all 178 math expressions and 37 displays. Both themes pass at
320, 375, 390, 768, 1024, 1440 and 1920 px: 28 width/theme cases, zero page
horizontal overflow, MathJax errors, raw display delimiters, duplicate IDs or
broken in-page fragments. Existing 23 historical destinations are preserved.

Initial dark-theme contrast findings in tables, input/tool text and properties
were corrected in canonical CSS/source and rerendered. Final axe at 390 and
1440 px in both themes and both pages reports zero serious/critical findings.
The shared minor navbar role and moderate repeated-region landmark findings
remain outside the scoped correction. No claim of universal accessibility is
made from these bounded checks.

All 46 right-edge captures, 68 table/code left/middle/right captures and ten
illustration/formula captures were visually read in addition to the complete
body. Content is reachable and mathematical brackets, subscripts, signs and
columns are readable. Tables and code intentionally scroll on narrow screens.
All 22 overflowing table/code cases respond to ArrowRight; an initial focus
and animation timing failure was reproduced in the harness and resolved by
settling the viewport and using focus({preventScroll:true}) before the key.
A separate check focuses the actual MathJax scroll containers, not their
nonoverflowing parent spans: all 36 overflowing math/theme cases scroll.

The identity illustration hides its undefined axis; arbitrary, 180-degree and
gimbal-lock presets show the expected transformed basis and principal axis.
The numerical interface still returns a valid 90-degree rotation when the
optional Three.js CDN is blocked; its explanatory fallback is visible. Jest
also verifies missing-library and WebGL-construction failure paths.

QA scratch: converter-complete-qa.json, converter-keyboard-final.log,
converter-math-keyboard.log, converter-root-configured.log, converter-content-final.log,
converter-static.log and local image sheets under this review directory.
These logs/images/helpers are untracked evidence, not publication sources.
Six unrelated test-regenerated trust summaries were restored only after
checking their exact differences and unchanged source inputs against HEAD.

## Protected Delivery

Implementation 1b52b0fab997ae6c60ddea961d28d63486eb9365 was committed after
all local QA completed, then replayed alone after f0a5b6c2 onto protected
energy main 4aea9755 as 12169b9b8d0a36138d5b27bbdd493a58314d34ea. Parent trees were identical.
PR https://github.com/D-sorganization/AffineDrift/pull/4323 is open. All normal
commit and push hooks pass. SPEC has one actual-PR row; the development log
records the resolved implementation. Enable normal squash auto-merge and
verify final protected CI and exact production evidence after merge. No
force push, direct-main push, self-approval or protection bypass occurred.
The corpus remains unfinished: 405 rows, 215 statuses beginning Indexed after
these two complete technical reviews, plus partially reviewed sources.

The central communication CLI became available before commit. Inbox read returned no messages but warned about a rejected identity change for the unrelated capture-product-01a08427-reference session (exit 1). This is recorded as a coordination warning, not proof of vacant scope. Our existing #4322 lease remains valid; presence registration succeeded at Repository_Management#1576 comment 5609216406 through 23:49:18Z. No conflicting path or message was returned.

The portable development-log checker rejects SELF as a development-log SHA; the entry records the actual parent plus validated working tree until the implementation commit is resolved. Unchanged peer DL-#3903 lacks a usable SHA and DL-#3902 lacks PR/Last verified fields; those pre-existing entries are preserved.

Energy parent publication: Deployment 34406274993 passes. Exact live artifact 10126445934 was downloaded and all 956 records across 239 routes were read and checked: HTTP 200, zero failures, serious/critical axe findings, retries, transients or exhausted retries; axe ran on all 239 routes.
