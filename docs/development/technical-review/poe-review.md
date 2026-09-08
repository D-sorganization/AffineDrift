# Product-of-Exponentials Review

Date: 2026-09-08. Issue [#4297](https://github.com/D-sorganization/AffineDrift/issues/4297),
native child of epic #4009; corpus #4021, geometry batch #4055.
Worktree: `AffineDrift-technical-review`; branch: `fix/4297-product-exponentials`.
The issue was unclaimed before the codex lease, which expires at
2026-09-09T00:11:53.245934UTC. The immutable proximal-distal monograph is untouched.

## Reading Scope and Sources

Read the complete original Volume 0 chapter, its short Quarto edition, figures,
program and all exercises. The corpus estimate was 7,200 words for the TeX
chapter; a separate whitespace count was 5,682. These are different counting
methods, not evidence that sections were skipped. Reconciled the full subjects
and preserved every original explicit TeX label and index term. The web edition
now carries the same substantive treatment and executable example.

Checked the authors' official Modern Robotics transcripts for
[space PoE](https://modernrobotics.northwestern.edu/nu-gm-book-resource/4-1-1-product-of-exponentials-formula-in-the-space-frame/),
[body PoE](https://modernrobotics.northwestern.edu/nu-gm-book-resource/4-1-2-product-of-exponentials-formula-in-the-end-effector-frame/),
[space Jacobians](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-1-space-jacobian/),
[singularities](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-3-singularities/),
[manipulability](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-4-manipulability/),
and [numerical pose IK](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-2-of-2/).
These source sections support convention checks; the numerical examples and
derivations below were computed independently. Existing Murray/Li/Sastry and
Lynch/Park book references are retained as further reading; this is not a claim
to have reread both entire books during this batch.

Replaced the D-H bibliography's Google Scholar search URL with the registered
DOI, 10.1115/1.4011045. Crossref's publisher-deposited record confirms the title,
authors, ASME journal, volume 22, issue 2, pages 215–221 and 1 June 1955 date.
The DOI page could not be retrieved through the web tool; no claim of reading
the full 1955 paper follows from the verified metadata.

## Findings and Derivation Decisions

1. **Order and Moving Axes.** The old space formula was correct but its figure,
   prose derivation and Python loop reversed the factors. Current downstream
   axes are transported, although stored home axes are constant. Deriving
   `exp(E1 [S2] E1^-1 q2) E1 M = E1 E2 M` exposes the error. The body product
   retains joint order, with `Bi = Ad(M^-1) Si`; using the current pose for
   this home-axis conversion changes the model. D-H remains a valid alternative.
2. **Twist Types and Differentiation.** A six-vector differs from its 4×4 Lie
   algebra generator; only the angular block is skew. Differentiate each
   exponential with its constant generator and one joint-rate factor. Product
   cancellation gives `Js,i = Ad(Prefix) Si`, a 6×6 adjoint operation. Angular
   components precede linear components throughout the revised code. Spatial
   `vs = pdot - omega × p`; endpoint velocity requires the point map.
3. **Geometry and Numerical Values.** The standard D-H example now includes
   every link. Its independent planar endpoint is (1.635139, 1.493718) m at
   (45, −30, 60) degrees, with 75-degree yaw. The spatial 3R example uses
   exactly its stated z/y/x home axes. At (pi/4, pi/6, −pi/3), its origin is
   (0.659740, 0.659740, −0.25) m. The original second rotation used inconsistent
   angles; its translation and the third factor's invented translation were
   wrong. The third x axis contains the home tool origin, so that joint changes
   orientation without changing the origin's position.
4. **Task-Dependent Rank.** `rank(J) < n` falsely marks redundant mechanisms as
   singular everywhere. Rank loss is relative to the mechanism/task's attainable
   maximum. A positive-length planar 2R arm loses position rank at a straight
   or folded elbow, while its full pose map retains rank two. Neither condition
   alone decides nonlinear controllability, finite reachability or joint loading.
5. **Metrics and Loads.** Determinant is not condition number. Choose task/rate
   metrics before singular values; `sqrt(det(J J^T))` is the full-dimensional
   volume scale, not the actual ellipsoid volume. The unit-ball constant matters.
   At 45 degrees the unit-link 2R position ellipse has semiaxes 2.07313218 and
   0.34108138, ratio about 6.08, contradicting the old nearly circular drawing.
   The new plot uses equal scales and independently evaluated Jacobians.
   Reciprocal force axes require the dual metric and static torque bounds.
   An ideal unbounded force direction represents a constraint reaction, not
   unlimited strength, actuator authority or a dynamic swing-force prediction.
6. **Null Motion and IK.** The SVD pseudoinverse handles ranks that invalidate
   the full-row-rank shortcut. Damped inverses leak secondary commands. Null
   velocity is instantaneous; a finite Euler step generally drifts quadratically.
   The positive gradient contribution need not overcome the primary task's
   negative contribution. A body-log pose error matches `Jb`, unlike the former
   position-first residual. Its exact derivative is `-L(e) Jb`, where `L` is
   explicitly defined by the derivative of `log(exp(delta) exp(e))`. A local
   iteration is not a global feasibility proof. The planar IK exercise is
   independently solvable, with one branch (−0.230011, 1.230959) radians.
7. **Golf and Humanoid Inference.** Added the floating-base velocity term, the
   constrained map `J Z`, acceleration bias `Jdot qdot`, power duality and
   conditional uncertainty propagation. A fast available clubface direction can
   also amplify coordinate uncertainty and coexist with limited face-angle
   correction or excessive reaction loads. Pose, velocity, force and biological
   recruitment remain distinct inference steps. The chapter proposes an explicit
   validation sequence rather than treating kinematics as a complete swing model.

## Verification and Adverse Evidence

The first four tests of the actual embedded program failed against the original
chapter. The corrected program passes those tests and thirteen additional
checks, including independent pose derivatives, body-product order, reported
numbers, task ranks, reciprocal force bounds, finite-step drift and the pose-log
residual derivative. The seventeenth test checks edition code equality and
unbroken display-math blocks. No production Python module was added.

The first PDF command failed before launching because its relative log path
had one extra parent segment; subsequent commands use an absolute log directory.
The first actual compile exposed `\\[p]` being parsed as an optional line-break
length; bracing the following matrix cell repairs it. Print review then caught
a hyphenated chapter title, an overwide axis equation, a hyphenated section
heading and low-contrast inherited listing colors. Explicit title breaks,
aligned axes and local listing colors correct those defects.

The 239-page volume builds with pdflatex, BibTeX, makeindex and repeated
pdflatex. Initial full visual coverage includes PDF 4–13, chapter 158–173,
and index/bibliography 232–239: 34 selected pages. Final changed pages require
the last contrast/title pass. Existing warnings in other chapters are not
claimed corrected.

The first browser pass covered 77 full-scroll captures: 19 desktop-light,
29 phone-light and 29 phone-dark. Fourteen responsive checks passed and axe
reported no serious/critical violations. Existing moderate duplicate landmark
labels remain. Visual review nevertheless found one raw equation: removing a
mid-equation anchor left a blank line that broke Pandoc's math parsing. The
converter now removes blank equation lines, and the regression covers it.
Final render, visual rechecks and root quality gates remain pending.

All failed attempts and outstanding checks are retained here. A local render
is not a claim that protected CI, merge or public deployment has succeeded.


## Final Local Verification

Final root CI command (`pytest tests/ --cov=src --cov-report=xml --timeout=120`)
passes 4,813 tests, with 29 skips, 131 deselections and 50 warnings in 553.41
seconds. Coverage for that explicit `src` scope is 92.78%; this is not the
broader configured `src` plus `scripts` measurement quoted in some earlier
batches. Content checks pass 130 with four skips; all 34 static contracts,
631 title checks, Ruff, Black100 (670 files) and mypy (86 files) pass.

All 34 selected PDF pages were visually inspected. Final code/heading pages
169–171 and bibliography page 236 were inspected again after the last changes.
All 77 initial web scroll captures were inspected; the final fixes pass 16
target views and 24 right-edge views, all visually inspected. Both figures
respond to keyboard scrolling. All 42 display equations render, the actual
HTML program matches the tested TeX program, and all four historical section
anchors occur exactly once. Final responsive checks pass 14/14; both themes
have zero serious/critical axe findings. Moderate duplicate landmark labels
remain; the browser logs also record blocked external-font probes from axe
under the existing CSP and unused-preload warnings.

The first final-browser locator timed out because Quarto's anchor link adds
an accessible name to the heading. After inspecting the actual heading DOM,
the verifier selects its text through the heading element. This is a verifier
repair, not a change to the article. A second contact-sheet helper run included
its own prior sheets in a broad glob; the verified count remains the 77 original
scroll captures, not the helper's later inflated count of 90.

Test-generated presentation metadata differed only by date, JSON layout or
line endings. Compared those six known files against HEAD before restoring
their original bytes. No other user or agent work was discarded. All local
tests, builds, renders and browser QA ended before staging and delivery.

Biology #4294 / PR #4296 has protected-merged as
c02463f0e0b51dccf7aece0bb9b3dcd156c97657. Its main CI 34287893078 and deployment
34287893043 remain in progress; textbook compilation has passed. No live
publication success is claimed yet. The next long source, wrist-universal-joint.qmd,
has now been read completely, but its companion sources and corrections remain.

## Delivery Checkpoint

All ten critical-module coverage gates pass under Python 3.12.10. The first
invocation also passed but the script's bare `pytest` subprocess selected
Python 3.13.5 from PATH. Repeated with the Python 3.12 installation and Scripts
directories prefixed to the child PATH; the log confirms 3.12 for every gate.
This dispatch correction did not change source or weaken coverage thresholds.

Biology's main CI 34287893078 passed. Deployment 34287893043 was cancelled
during pre-deployment page verification after newer protected main d7e51655
superseded it. Replacement deployment 34289532320 remains pending; no exact
biology-only live artifact is claimed. Wrist findings are filed and claimed
as #4299, a native child of #4009. Its original long web article and TeX
manuscript have been read completely; its companion audit is still in progress.

The staged whitespace check caught trailing spaces emitted by Matplotlib in
SVG path lines. Removed only trailing line whitespace; verified identical
whitespace-separated SVG tokens. No coordinates, labels or visual styling changed.
