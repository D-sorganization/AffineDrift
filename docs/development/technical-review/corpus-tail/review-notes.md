# Corpus Tail Review

## Scope and Ownership

Epic #4009, corpus #4021, issue #4950. Exact 26-row scope in scope.json:
four generated worked examples, eleven generated trust fragments, and eleven
publication wrappers. Every scoped source and the relevant generator/model
contracts were read. Control Is Motion was excluded while #4878/PR4880 was
live-owned; that independent PR subsequently merged to main at 3b97042e2.
Its source and acceptance will be integrated without duplicating its edits.
Base source 4160ed572 contains the consolidated H–V scientific work; merge its
final acceptance and metadata repairs before this branch's frozen validation.

## Scientific Decisions

Launch-monitor introduction: remove universal identical-algorithm, perfect-camera,
full-outdoor-radar-flight and universal hybrid-sensor claims. Distinguish radial
velocity observations, calibrated angular information, orientation estimation,
finite capture volume, model fits, extrapolation and normalization. Measurement
event definitions are vendor/parameter specific: TrackMan club speed refers to
the geometric clubhead center immediately before contact, not universal maximum
compression. Existing primary citations are retained. The right-handed x-downrange,
y-up, z-right convention does not impose a universal spin-component sign rule.
The abstract describes architecture families instead of misclassifying SkyTrak.

Geometry wrappers: first variations obey exact linear variational equations at
a declared nominal solution; finite changes carry higher-order remainders, and
moving bases require transport terms. Common-operator additivity does not imply
superposition of finite nonlinear interventions. Zero-input drift depends on
the chosen model/input definition and is not necessarily passive momentum.
Remove the false contrast that conventional nonlinear control generally relies
on global linearization. State prerequisites and limits without promising a
self-contained universal toolkit. Volume V's preface was read and needs no
additional scientific edit after the accepted Q/R corrections.

Publication counts: six manuscript volumes 0–V; 40 notebook scaffolds map to
I–IV. Canonical chapter inputs give counts 12/10/11/10/12/10. Volume I's HTML
listing has ten chapters. Volumes 0/I have separate HTML chapters; II uses the
combined monograph; III–V retain PDF/LaTeX availability. The proximal-to-distal
PDF is 252 pages. Availability and counts do not establish instructional or
empirical completeness.

DCR trust panel: adjudication applies only to its declared reachability claim,
not all separate critiques. Its explicit counterexample uses x-dot=d+u with
constant drift, fixed horizon, fixed input bound and no state constraints:
the reachable width is 2UT and drift changes the center. Existing critique
states and the 2026-08-28 review date remain. Provenance at commit
524c28926f364631ed06b15be9c6fdf440acce64 was independently checked against
src/affine_control/reachability.py. Canonical registry edits were regenerated
with generate_trust_panels and generate_evidence_presentation.

## Independent Checks and Helper Adjudication

Six successful agy Gemini 3.8 Flash jobs: three wrapper reviews, one generated
example review, one trust review, and one final corrected-source review. Logs
are retained. Lead rejected claims that point-mass inertia should use uniform-rod
coefficients, that angular-only norms necessarily mix dimensions, that the
rigid/flexible Schur inverse was wrong, and that constant additive drift changes
reachable width for a fixed linear operator and input set. Helper opinions
are not scientific evidence. Missing separate Volume II HTML chapters are an
edition choice, not missing canonical manuscript content.

independent-checks.py.txt and its JSON compare independent analytic point-mass
double-pendulum equations integrated with DOP853 against printed RK4 values:
maximum state error 4.691155e-5 and separation error 3.659421e-5, both below the
four-decimal printing half-unit 5e-5. Independent discrete Riccati verification
gives matrix identity error 1.2079e-13, 100 seeded directional value checks with
maximum error 1.0232e-12 below 1e-10, and closed-loop spectral radius 0.729805.
No tolerance was widened. These are manufactured checks, not human experiments.

115 focused RNEA, golf-model, LQR, critique-ledger and worked-example tests pass.
28 trust tests pass after regenerating the initially stale evidence presentation
registry. Generator checks pass. Initial failures remain alongside successful
results. No new production behavior or implementation-mirroring tests were added.

## Rendering and Evidence Limits

Launch PDF: 105 pages, pdflatex/biber/repeated-pdflatex success; corrected
introduction pages visually inspected. Volume 0 PDF: 234 pages, repeated
pdflatex/bibtex success; corrected preface inspected. Existing out-of-scope
overfull boxes and Volume 0 duplicate labels remain; scoped pages are readable.
Six Quarto builds pass: Books index/roadmap, Geometry index/Volume 0/Volume I,
and the DCR article containing its generated panel. At 390 and 1440 pixels,
no document overflow or MathJax error was observed. Root previews retain the
known polyfill CSP rejection, absent site manifest and update notification.
The roadmap table can scroll within its container; a clipped rightmost column
in a viewport capture does not establish missing source text.

Initial desktop captures contained lazy blank content and an overly broad
panel crop; later scroll-through captures and scoped viewport captures expose
the corrected prose. Fixed navigation and transient preview notification can
overlap full-element screenshots; do not claim global UI or accessibility
certification. Browser/PDF pixels and build caches remain untracked. Quarto's
incidental docs/styles.css overwrite was restored to its original tracked bytes.

Book-audit source mismatches were expected after edits to index/roadmap. Prior
complete route records are preserved in prior-book-route-records.json. Only
these two source reviews are renewed; other route dates and scientific findings
remain historical. Record the final source/render commit after the source
checkpoint rather than manufacturing a revision for uncommitted bytes.

## Delivery and Continuation

Freeze the complete source, integrate the accepted consolidation, and run full
regression plus the central and relevant source gates. Advance 26 corpus rows
only after actual acceptance. Retain all earlier batch receipts and separate
local acceptance from protected remote-main and public deployment verification.
Never merge into a topic parent, create a draft, bypass hooks, close another
session's PR, or renew historical scientific claims merely to fix hashes.
