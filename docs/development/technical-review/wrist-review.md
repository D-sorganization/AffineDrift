# Wrist Constraints, Grip Geometry and Cardan Models

Issue #4299, native child of #4009; corpus #4021/core #4058. Active branch
`fix/4299-wrist-constraint-mechanics` starts at PoE PR4300 head dda485aa.
After PoE squash merge, replay only commits after dda485aa onto protected main.
Never change commits/checkouts during local tests, builds or browser QA.

## Scope and Original Question

Read the complete long article `articles/wrist-universal-joint.qmd`, the full
older `Wrist_Universal_Claude.tex`, the original discussion in
`Wrist_Universal_FBPost.sty`, the mathematical derivation, technical review,
validation document, README and bibliography companion. Some bundled tool
outputs were truncated: validation was read again in full and the beginning
of the README was read separately. The HTML companion has only been sampled;
remaining UI modules and images still require inspection. Do not mark these
fully audited yet.

The original note explicitly proposes a hypothesis and reports difficulty
replaying sensed inverse-dynamics loads as forward inputs. Preserve that
research motivation. The note's response to Mike Duffey is the author's
response, not a quotation authored by Duffey. Keep historical discussion
distinct from the corrected derivation and preserve author attribution.

## Confirmed Defects and Decisions

1. Perpendicular cross pins are not perpendicular shafts. An ideal two-axis
   relative-orientation joint differs from a one-DOF Cardan driveshaft with
   externally fixed shaft axes. A forbidden rotation is not a third DOF.
2. For `R = Rx(phi) Ry(psi)`, permitted angular velocities span
   `a = ex` and `b = Rx(phi) ey`; reciprocal direction `n = a cross b` equals
   `Rx(phi) ez`. In hand coordinates it is `Ry(-psi) ez`. Neither is generally
   a fixed forearm/hand long axis. A local holonomic equation is `ex.T R ey=0`.
   The first fundamental form remains rank two: these orthogonal instantaneous
   axes do not lose rank when shaft axes align. Generic fixed-z zero-spin
   constraints and Euler-angle zero conditions must not be substituted.
3. For `M qdd + h = B u + f + A.T lambda`, `A qdot=0`, full row rank A and
   positive definite M give
   `lambda = (A M^-1 A.T)^-1[-Adot qdot - A M^-1(Bu+f-h)]`.
   Its input derivative is generally nonzero. With A=[0,0,1], B=[ex,ey] and
   M=[[2,0,.5],[0,2,0],[.5,0,2]], zero state bias, input u on x yields
   qddx=u/2 and lambda=u/4. Reactions are not automatically uncontrollable
   drift or vectors in ker(B). Constraint annihilation concerns velocities.
4. Pairwise ideal power is `F.(vH-vF)+tau.(omegaH-omegaF)=0` at the common
   joint point. Individual body powers need not vanish. A prescribed moving
   base contributes energy; finite spring/damper energy needs separate terms.
5. Axis names change inside both editions. A transverse moment about the grip
   is not clubhead inertia or shaft-axis inertia. Include `I_P=I_C +
   m[(r.r)Id-r r.T]` in one frame; use full tensor and `m r cross aP` for a
   moving body-fixed reference point P. Scalar tau/I requires its own model.
6. Face yaw is atan2(ny,nx) for a defined ground-frame face normal n, with
   derivative `(nx dny-ny dnx)/(nx^2+ny^2)`. Shaft twist, plane-normal rotation,
   loft and lie therefore cannot be universally ranked from inertia alone.
7. Frozen random torque, zero initial errors: sigma_theta = T^2 sigma_tau/(2I).
   The web example (.15Nm,.01s,I=.005/.00015) gives .08594 and2.86479 degrees,
   not .17/5.7. Old TeX additionally mislabeled angular velocity and converted
   about83rad to4.8degrees. Its assumptions fail well before such large angles.
   General covariance needs the double integral of temporal cross covariance;
   white-noise intensity yields T^3/3, not the frozen-error T^4/4 variance.
8. Coplanarity does not imply collinearity. Fixed full kinematics, fixed input
   torques and changed constraints cannot all be freely prescribed. Separate
   fixed-input, fixed-motion inverse, and reoptimized-policy comparisons.
9. Simscape primitive actuator torque is not a Cartesian component of a total
   wrench. Composite total includes actuator, internal, limit and constraint
   contributions in a chosen frame/direction. Inertia/Coriolis are terms in
   dynamics, not extra torques to add to the sensed wrench by name.
10. Companion formula `cos(delta)/sqrt(1-sin(delta)^2 sin(phi)^2)` is wrong.
    Define output phase `atan2(cos(delta) sin(phi), cos(phi))`; differentiate
    to obtain the same denominator without sqrt. This phase convention differs
    from the older tan(output)=tan(input)/cos(delta) convention. Reciprocal
    multiplication alone cannot validate kinematics. Fixed support, negligible
    joint storage/losses and port powers condition the inverse torque ratio.
11. `plots._compute_transmission_sweep` reverses phase and bend arguments,
    disagreeing with the current-value graph and Qt helper. Correct with named
    arguments. The rod/point-head inertia formula is transverse; default .5
    ratio is a demonstration setting, not a Jorgensen measurement.
12. The hard-constraint critique wrongly rejects all rigid approximations,
    calls aligned shafts singular, and equates forearm pronation with carpal
    compliance. The dimensionality critique dismisses planar checks as trivial
    and assumes gyroscopic coupling implies chaos. Correct both arguments;
    retain their legitimate demand for task-specific empirical qualification.

## Evidence Read So Far

- [MathWorks Universal Joint](https://www.mathworks.com/help/sm/ref/universaljoint.html):
  description, rotation sequence, actuator and composite sensing, frame and
  direction, internal mechanics and limits. Read relevant sections, not fault
  APIs as biomechanics evidence. These docs verify software semantics, not
  the author's actual historical model or a human grip advantage.
- [MathWorks Force and Torque Sensing](https://www.mathworks.com/help/sm/ug/force-and-torque-sensing.html):
  full technical content, distinguishes primitive/composite outputs and signs.
- [Modern Robotics 8.7](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-7-constrained-dynamics/):
  full transcript; workless constraints, multipliers, projected dynamics and
  force control. Original derivations above are independently checked below.
- Crisco's 2011 [mechanical axes study](https://pubmed.ncbi.nlm.nih.gov/21248214/):
  abstract read, six cadaver wrists; oblique mechanical axes. This is not the
  2005 [in-vivo dart-throwing study](https://pubmed.ncbi.nlm.nih.gov/16322624/),
  whose abstract was also read. Do not blend their dates/sample designs.
- Scholz and Schoner1999 [original UCM paper](https://pubmed.ncbi.nlm.nih.gov/10382616/):
  abstract/metadata read; operational variance analysis of sit-to-stand, not
  proof that golf disturbances lie in an output-null subspace.
- MacKenzie2009 original author-hosted paper located; initial methods excerpt
  shows a 3D model compared with single-camera 2D data from one golfer. Full
  paper reading and precise source map remain pending.

## Red/Green and Adverse Evidence

Seventeen new cases failed before production edits: twelve angle-derivative
cases, one full-turn integral, three nonfinite inputs, and one sweep/current
parity check. The first isolated test run also lacked optional Streamlit;
reran alongside the established wrist tests, whose test environment supplies
the existing Streamlit stub. All seventeen then fail for the intended defects.
After fixing the denominator, finite-input rejection, and reversed sweep
arguments, the new cases plus existing wrist/unit/property tests pass.

Remaining: make the new test independently runnable without relying on test
collection order; complete source review, long-form corrections, companion
UI/JS/docs and meaningful mechanics tests; run all required checks and inspect
print/web outputs before committing. No wrist publication success is claimed.


## Continuing Checkpoint

Biology #4294 / PR #4296 is published via descendant protected main d7e51655d47d37a092b1bcd29d25972ce373b244 (one commit ahead of biology squash c02463f0). Deployment34289532320 succeeds. Exact-head live artifact10081509020 passes956/956 across239 routes, zero failures, serious/critical axe findings, retries or transient responses. The original biology deployment34287893043 was superseded before publication; do not report it as successful.

PoE PR4300 head dda485aa has textbooks and preliminary checks passing; CI34290663271 remains in progress. Wrist canonical web and mathematical companion drafts are now written, with17 historical section aliases. All17 new tests pass in isolation after a localized optional Streamlit decorator stub. The full article/source/companion QA and remaining UI/print editions are not yet complete. The author-hosted MacKenzie2009 PDF request failed TLS certificate verification after the web open failed; verification was not disabled, and the full paper is not claimed read.


## Completed Substantive Review and Independent Verification

The complete legacy HTML was extracted and read before replacement. Both original
JPEG drawings were inspected; they are historical wrist/forearm sketches, not
validated Cardan geometry. They remain unchanged and are not used as evidence.
The main article, four technical guides, bibliography, both critiques, Python
and browser calculations, Qt/Streamlit presentations and embedding instructions
have now been reconciled. The original discussion body is preserved with a
prominent historical notice. The print companion preserves Dieter Butz's original
author credit; the web article retains Dieter Olson. Neither Mike Duffey nor a
software vendor is assigned authorship of the proposed hypothesis.

The bibliography now states evidence scope and review depth. Added primary
records for Crisco 2005 and 2011 (distinct studies), Scholz–Schöner 1999,
Coleman–Rankin 2005, MacKenzie 2012 and Nesbit–Serrano 2005. These empirical
records were reviewed at abstract/metadata level. The author-hosted
MacKenzie–Sprigings 2009 methods excerpt establishes a 3D forward model compared
with single-camera 2D observations from one golfer; full-paper access failed and
is not claimed. The technical MathWorks and Modern Robotics sections were read.
The annotated bibliography replaces unsupported citation chains, fabricated
future publication edges and unsourced numerical assurances.

Independent article checks now include finite rotation of the reciprocal wrist
direction, a full constrained KKT solve demonstrating actuator-dependent reaction,
a particle-force check of the moving-reference-point moment equation, finite
clubface-yaw sensitivities at three lofts, and numerical covariance integration.
Together with the Cardan angle derivative, full revolution integral, nonfinite
inputs, exact phase marker and sweep parity, the new Python file has 25 passing
cases. The point/rod inertia is transverse about the grip; the gamma ratio remains
an explicitly illustrative half of alpha. The 10 ms frozen-noise examples are
0.08594 and 2.86479 degrees, not the former inconsistent web/TeX numbers.

The critiques now retain useful demands for empirical qualification while
withdrawing invalid blanket objections to rigid models and planar verification.
Their governed dispositions remain open: corrected algebra does not establish
human grip performance. Regenerated all 15 governed ledger surfaces after title
changes; no resolution or adjudication was fabricated.

## Companion Defects Found During Actual UI Checks

- Python/Qt/browser graphs mixed dimensionless transmission ratios with angular
  acceleration gains. Added a separate dimensional axis and exact phase marker.
- Renaming the Qt selector exposed an old exact-string callback dependency.
  Repaired the callback and tested the real combo-box event. The broad focused
  run initially failed two tests: a legacy global Streamlit MagicMock decorator
  interfered with collection and an older label assertion was stale. The new
  plot test now loads the actual module independently with only a local optional
  cache-decorator shim. The corrected focused recheck passes all 60 tests.
- The browser polynomial fallback appended to partially computed samples.
  A failing test observed 650 samples for 500 time points; the replacement now
  clears the partial signal. Actual page interaction then found nonfinite math
  results were accepted by the expression evaluator. Three new tests failed for
  division by zero, invalid square root and exponential overflow; the evaluator
  now rejects all three, allowing a reported, correctly aligned fallback.
- The initial inertia display was zero although the calculations used nonzero
  inertia. A DOM-initialization test failed, then passed after the display was
  updated from the same computed inertias on every update.
- Quarto copied the linked HTML demo but omitted its local polynomial JavaScript
  dependency. Added that dependency and the static reading guide to project
  resources. Actual HTTP retrieval confirms the helper is served.
- The browser had unlabeled sliders/selects and low-contrast numerical labels.
  Corrected associations, contrast and heading/main landmarks. Plot legends now
  sit below curves, dimensional axes have room, and narrow layouts scroll within
  a keyboard-focusable plot region. All three modes pass seven widths (320–1920),
  with no page overflow. Final axe reports no violations on the standalone demo.
- A valid scalar signal can have zero mean and nonzero variation. The information
  panel reports mean torque and component amplitudes, not energy shares or a
  claim of zero variability. Browser controls verify bend 0/30/89/90 degrees;
  the disclosed 90-to-89 numerical clip is not an anatomical extreme-grip result.

All 22 JavaScript suites now pass: 351 tests, 19 skips. This includes 11 Cardan/UI
cases and seven polynomial-evaluator cases. The final polynomial page test has
500 time and signal samples, with fallback midpoint -0.25. Cached JavaScript
initially made the browser rerun appear unfixed; direct HTTP retrieval showed the
new source while the browser still executed the old helper. Disabling browser
HTTP caching for QA, unregistering local service workers and clearing their
caches resolved the discrepancy. Network responses were not mocked.

## Print and Presentation Review

The rebuilt companion has 14 pages. XeLaTeX passes without overfull boxes,
missing glyphs or unresolved references; all 14 pages were visually inspected.
The two-panel analytic figure distinguishes rotating reciprocal wrist directions
from supported-shaft Cardan ratios. Final web-only figure scrolling does not
change the print argument or image. TeX and bibliography use normalized LF text.

All 68 initial main-article scroll captures were inspected: 16 desktop/light,
26 mobile/light and 26 mobile/dark. The article initially passed all 14
width/theme checks and every MathJax expression. A final image-width check found
that its page-specific articulated-body stylesheet was not included; added that
explicit dependency. Final figure/edge/keyboard verification is still pending
at this checkpoint. Main/critique axe reports only the existing moderate
landmark-unique finding, with no serious or critical finding. Browser logs retain
existing blocked Quarto polyfill/font probes under CSP and preload warnings;
CSP was not widened to suppress them.

The Qt application was inspected offscreen in top/bottom/sweep/documentation
views. The first offscreen font database produced squares; loading the installed
Arial font for the QA process produced readable labels. This was a QA environment
fix, not a production font change. Four final Qt views were inspected. Optional
Streamlit is not installed, so no live Streamlit UI success is claimed; helper
and Qt checks do not substitute for it. The standalone guide deliberately has
one light appearance, even when visited from a dark site page.

## Regression Checkpoint and Remaining Delivery

The first full root run was deliberately interrupted after a Qt-selector issue
was found; it is not a passing result. The next complete run passed 4,848 tests
but failed two publication contracts: stale critique titles in generated ledger
surfaces and a test still requiring the former HTML article to load site JS.
The replacement static guide requires no JS; its revised contract verifies the
no-script page and usable article/PDF links. All 22 ledger/runtime tests pass
after those repairs. That complete run measured 92.98% coverage for explicit src.
A final full regression run is now in progress; do not report it passed yet.

Black100 checks 672 files unchanged; Ruff and mypy (86 files) pass. All 34 final
static CI contracts pass. Source title case passes for 631 files. Earlier content
checks pass 130 with four skips; the final content gate and protected PR delivery
remain. No commit/checkout mutation occurred while tests, builds or QA were active.

## Prior Batch Publication Confirmed

PoE #4297 / PR #4300 protected-squash merged as
f07bf036a9e2d8a8fb8f20953c756efd7b53f2e1 at 2026-09-08 23:51:21 UTC.
Main CI 34292478876, textbooks 34292478858 and deployment 34292478895 succeed.
Exact live artifact 10082702228 passes 956/956 checks across 239 routes, with
zero axe violations at the configured serious/critical policy, retries,
transient responses or failures. Biology's successful descendant publication
is recorded above. The 405-source corpus remains unfinished.


## Final Local Completion

The final full root run passes 4,850 tests, with 29 skips, 131 deselections and
50 warnings in 633.37 seconds; explicit src coverage is 92.98%. All ten critical
module coverage gates pass under Python 3.12.10. Content lint passes 130 with
four skips and 4,876 deselections. An initial final content command used the
wrong marker `content`, selected zero tests and exited 5; that run is not counted
as validation. The correct repository marker is `content_lint`.

After the page-specific CSS repair, all 14 article width/theme combinations pass.
Its nine overflowing figure/equation regions were inspected at both edges in
both themes (36 final views); the figure moves 40 px using ArrowRight. Both
article tables and the dimensionality-critique table also move 40 px with the
keyboard; their 12 edge views were inspected. MathJax's inner equation containers
are programmatically scrollable; the separate outer-span keyboard probe selected
zero overflowing spans, so it does not establish keyboard behavior for all math.
All 17 historical article aliases occur exactly once. The five internal article
links respond successfully after browser-style backslash normalization; Python's
raw URL join initially produced false 404s for Windows-rendered relative links.
The excluded inverse article remains a .qmd link in this selected render; the
full site render rewrites it to HTML. Served PDF and polynomial-helper bytes
match the canonical files.

All 16 critique body captures and both static-guide captures were inspected.
Both critique themes pass their 14 width checks and serious/critical axe gates;
the guide's single light appearance passes all width checks and has no axe
violations. Nine final simulator views were inspected after allowing Plotly's
resize callback to finish: earlier immediate screenshots captured an intermediate
plot width after viewport changes. This was a QA timing correction, not a graph
calculation change. Initial full-article views (68), final edges (36), table
edges (12), critiques/guide (18) and simulator views (9) total 143 inspected web
captures. Four Qt and all 14 PDF pages were also inspected.

All local testing, rendering and visual checks have completed before staging.
Six known test-generated metadata files differed only by generation date, JSON
layout or line endings and were compared semantically before restoring HEAD
bytes. The two claim-audit projections retain the new project-resource hash.
Protected delivery is next; local verification is not yet live publication.

Next long chapter: #4303 is filed and linked under epic #4009. Both complete
computational-brain editions and all 14 exercises have been read. Arithmetic,
feedback, impedance, neural-evidence and AI-comparison defects are recorded in
the issue; correction and deep source review remain. Do not treat the whole
corpus as completed.


## Protected Delivery Checkpoint

The wrist commit was replayed from 284c33fb onto protected main a37f5cae as
be5612c6. Git range-diff reports an identical patch. No tracked source changed
during the replay and no local test/build/QA process was active.

The first push did not publish: Prettier normalized one inherited handoff line,
and the isolated pre-push mypy environment lacked the optional PyQt6, Matplotlib
and Streamlit dependencies. Its nine errors were Any-base classes and untyped
decorators. Installing those actual dependencies in that local hook environment
resolved the errors: the unchanged pre-push mypy hook passes. No type-check
configuration, ignores or hooks were weakened or bypassed. The first push's
Bandit and unit-test hooks also passed. This environment repair is distinct
from the completed Python 3.12 project validation recorded above.

All hooks passed on the retry and the branch was pushed. Ready PR #4304 is open
with Fixes #4299 and agent:codex. Its actual PR-keyed SPEC row is now recorded.
Protected review, CI and deployment remain; this is not a publication claim.


## PR Website Lint Repair

PR CI34300841286 job102307300320 found three HTML-validity errors that the
earlier local static-contract checks did not cover. The embed used percentage
width in a numeric HTML attribute, and the simulator used div role=main/region
where the repository requires native elements. The iframe now uses CSS width,
including the documented snippet; the simulator uses main and a named section.
No numerical behavior changed. The exact HTML lint command now passes.

The full CSS glob encountered 12,740 findings in untracked generated textbook
assets left by earlier QA. It is not a passing clean-checkout test. Running the
same Stylelint engine over all62 git-tracked CSS/SCSS files passes with zero
warnings. No generated third-party stylesheet was changed or deleted.

Fresh browser checks confirm one main, one named plot section, zero axe
violations, no viewport overflow at320/390/768/1440px, and40px keyboard plot
scroll. Desktop and mobile screenshots were inspected. These two new views
supplement the earlier143; protected CI must still validate the updated head.


## Protected-Main Replay and Wrist Publication, 2026-09-09

The saved brain checkpoint 2a5ec6fb was pushed with every hook passing. Remote
inspection then showed that PR #4304 had already merged as a11abdbf, after another
task changed the auxiliary HTML publication policy. That task removed the old
HTML guide from deployment and excluded content/src HTML from the Quarto page
manifest. The simulator remains linked as an auxiliary resource. This supersedes
the earlier instruction to repair an open wrist PR; no competing wrist repair
was made. The manifest no longer claims those auxiliary routes as Quarto pages.

Main deployment 34310520642 at descendant 19170f82 succeeded. Its exact live
artifact 10088805870 was downloaded and inspected: 956/956 checks, 239 routes,
zero failures, serious/critical axe findings, retries or transient responses.
Auxiliary simulator validation rests on the earlier direct browser checks,
not on the reduced page manifest. The wrist merge itself had a failed deploy;
the successful descendant contains the critique-link repair from PR #4305.

