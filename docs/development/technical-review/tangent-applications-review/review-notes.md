# Tangent Series and Applications Review

## Scope and Coordination

Epic #4009, corpus #4021, issue #4939. The review scope comprises canonical parts 1–6 of the
tangent-hyperplanes series plus appendix-applications.qmd. Part7 and advanced
companion manuscripts have their own prior review scopes; this batch does not
claim a new complete review of them. Parent putting PR4940 at582920964 is
integrated, with49 pending-prefix scopes of407 before this seven-row review.
Source review is complete; acceptance still requires the final rendered checks and frozen regression.

Lease receipt5989082122, session technical-review-20261005-tangent-applications.
Presence receipt5989326194 through08:30:53UTC on5October2026. The first presence
request rejected a trailing slash; the corrected normalized path succeeded.
Other agent #4883 completed Related Articles markup. Its current-main callout
titles and added previous/next links are preserved verbatim in all seven pages.
Shared SPEC/HANDOFF/DEVELOPMENT_LOG and the primary checkout .commit_msg remain
untouched. The old CLAUDE suggestion to work on main conflicts with direct user
and active fleet policy; work stays on an isolated topic branch and regular PR.

## Mathematical Decisions

Part1: tangent vectors are derivatives of curves. Use a full-row-rank Jacobian
and dimension n-p; only codimension one gives an affine hyperplane. C1 supports
little-o geometric error and C2 gives a local quadratic upper bound with
conditioning. Radial normalization is the closest-point map for the circle;
the same-height intersection is not. Rank failure of h=y^3 does not make its
zero set singular. Geometry alone neither stabilizes a controller nor defines
a physiological objective.

Part2: distinguish parameter derivative xi from finite difference Delta x.
The first variation is exactly linear without requiring control affinity.
For an embedded d-dimensional tangent basis E in R^n, use a left inverse and
retain E-dot; the ambient derivative of a tangent field need not be tangent.
Do not confuse fixed-time sensitivity with event-time observations. State
transition growth, not just instantaneous eigenvalues, controls amplification.

Part3: declare a half-quadratic cost so S is its Hessian. Include the affine
feedforward correction in the DDP/iLQR rollout. Derive Hessian blocks from the
discrete dynamics map; full DDP retains value-gradient contractions with the
dynamics Hessians, iLQR drops them. The one-step control example halves cost.
Finite-horizon effort-only LQR on an unstable scalar plant is a counterexample
to automatic contraction. Numerical solution is not machine-precision proof.

Part4: define actual, nominal and predicted trajectories separately. The full
Taylor bilinear remainder includes mixed state-input products. Propagate it
through Phi to derive a finite-horizon bound. Quadratic upper order does not
mean an exact factor-of-four error ratio; the scalar x-dot=x-squared example
makes this explicit. Coordinate Hessians are not intrinsic Riemannian curvature.
Model/measurement discrepancy and optimization convergence need separate tests.

Part5: distinguish squared differential length from length. Include the total
metric derivative, uniform bounds and forward-invariant connecting paths.
Use intrinsic region distance without falsely requiring geodesic convexity.
The Riccati decay identity needs additional positivity and rate conditions.
A rank-deficient task pullback cannot certify full-joint-state contraction.
Contraction-aware optimization is labeled a proposal, not a demonstrated human
motor-control mechanism.

Part6: derive saltation from event-time variation including time-dependent guard
and reset terms. Fields include the declared policy. Different mode orders,
grazing and Zeno require additional treatment. Small denominator alone does not
prove divergence when a numerator cancels. A bouncing point mass with positive
restitution supplies an independent example; zero restitution needs a resting
contact mode. Rigid reset and compliant finite-duration collision models are
different valid modeling choices, subject to their assumptions and validation.

Applications: distinguish same-state derivative/output algebra from forward
zero-input trajectories. A force output needs its own compatible map and
identifiability analysis. State-dependent gain and input limits do not destroy
affinity in actual input; nonlinear command composition can. Internal activation
and stored energy persist when the declared input is zero. Remove unsupported
runtime thresholds and transfer-learning guarantees; specify benchmarks and
player/session-separated validation instead.

## Primary Sources and Reading Scope

Tedrake, Underactuated Robotics, LQR chapter finite-horizon and tracking sections:
https://underactuated.mit.edu/lqr.html. Read the cost convention, Riccati
derivation and numerical integration caveat. The chapter's unqualified
infinite-horizon positivity wording is not adopted; this batch derives and
checks its own finite-horizon counterexample.

Tedrake trajectory optimization, lines272–279, iLQR/DDP subsection:
https://underactuated.mit.edu/trajopt.html. Supports the first- versus
second-order dynamics distinction. The article's local chain-rule expansion,
feedforward example and manufactured numerical checks are independently derived.

Lohmiller and Slotine, On Contraction Analysis for Nonlinear Systems, author
preprint: https://www.mit.edu/~nsl/preprints/contraction.pdf. Read physical
pages 3–8 on differential lengths, path integration, region retention and metric
generalization; not a claim to have reviewed all 27 pages. Initial alternate MIT
URL failed retrieval; the author-site URL succeeded. The regional intrinsic
distance statement follows by evolving each connecting curve and taking its
infimum, with explicit forward invariance.

Kong, Payne, Zhu and Johnson, Saltation Matrices: The Essential Tool for
Linearizing Hybrid Dynamical Systems, https://arxiv.org/html/2306.06862v2.
Read Sections III-A and III-B defining the time-dependent system, guard/reset,
saltation construction and transversality assumptions. No fixed impact-duration
number or unreviewed collision experiment is imported. Existing book citations
in Part2 are retained as background, not represented as newly read full books.

## Flash Adjudication

Three original audits, two proposed drafts, three final audits and one turnover
audit ran through agy Gemini 3.8 Flash. Their output is advisory and their exit files are retained.
Rejected initial claims that velocity-dependent gains or state-dependent bounds
break affinity, and that geodesic convexity is always necessary. A sum-of-squares
bound can control mixed terms; omitting their explicit appearance is not alone
an invalid bound. Changing the half-cost convention changes the Hessian's
normalization, not the Riccati gain equation.

The proposed drafts were not copied wholesale: one miscomputed the circle
distance, demanded a Riemannian cost, and asserted universal finite-region
failure. The other inverted a rectangular tangent basis, invented a dimensionally
wrong lift law and a launch-angle threshold, and omitted landing-time sensitivity.
Final review falsely objected to a valid O(epsilon^6) remainder and to the
admissible moving-basis equation. Its claimed saltation sign errors were retracted
within its own calculation. Lead derivation and independent event integration
confirm the published signs. Adopted explicit epsilon-neighborhood wording and
column-gradient convention; event timing is derived in Part6 rather than
duplicated as an inaccurately named projection in Part2.

## Checks and Delivery

Independent script executes eight groups of100 seeded cases: closest-circle
projection by scalar minimization, moving-circle transport, nonlinear ODE
remainder, DDP Hessians by finite differences, Riccati identity, task null space,
saltation versus event-detecting ODE integration, and forward/same-state response.
All pass their predeclared tolerances; maximum saltation derivative error is
2.421e-9 against2e-7. These are manufactured mathematical checks, not empirical
golf or whole-body validation. No tolerance was widened.

The inherited moving-tangent SVG had horizontal segments that were not tangent
to its curve. A reproducible Matplotlib figure now uses exact circle positions
and tangent vectors with orthogonality assertions. Mobile pages and desktop excerpts have been inspected; final mobile equation line breaks are being rechecked. Quarto output modified tracked docs/styles.css; restore only that
known generated artifact from HEAD after rendering. Keep generated HTML,
screenshots and browser caches untracked under this scoped QA directory.

Putting PR4940 is regular and based on workbench PR4938. Its app attachment and
Repository_Management PR1998 attachment hit the100-item cap; do not remove other
attachments. Central title repair PR1998 has protected auto-merge armed. H PR4902
is third in the merge queue, with successful head checks but no merge-group head
yet; preceding unrelated PRs await checks. Do not alter other sessions' PR state.
After actual parent main delivery, retarget each owned stacked PR, arm through
the central guard, then verify accepted hashes on fetched main. Topic-base
merges are not main delivery. The full goal remains active.


## Final Presentation Repairs

The first complete mobile inspection found four scrolling display equations.
Their source now uses shorter aligned lines; this changes layout only. Expanding
the applications plain-language section exposed indented HTML rendered as code.
An explicit raw HTML block preserves the existing accessible toggle and prose
while rendering the section as intended. Recheck the expanded section after
rendering; document width alone did not detect either problem.

The turnover Flash audit's useful wording observations were adopted. Its claim
that “putting” was version-control jargon was rejected: it names the golf topic.
Its proposed conflict between branch isolation and tracking dependent PRs is
also false. Mathematical assumptions are stated in the canonical articles; the
turnover summary does not substitute for those derivations.


Final browser measurements pass for all seven pages at 390 and 1440 pixels:
294 MathJax containers per viewport, no math errors, lazy containers, broken
images, document overflow or internally scrolling display math. The expanded
appendix contains three real HTML explanation cards and no code block; its
content height is 2387 pixels when expanded and zero when collapsed, with the
matching hidden and ARIA states. The heading wrapper prevents the inherited
adjacent-sibling CSS rule from applying, so this one panel removes the obsolete
max-height cap inline; the existing JavaScript hidden attribute controls visibility.
All mobile pages, desktop geometry/control excerpts and the expanded panel were
visually inspected. Inherited narrow mobile title wrapping and the preview's
new-content toast are recorded; the toast was dismissed through its button.
The local preview still reports the known external polyfill CSP rejection and
missing public-site-manifest.json; no claim of a globally clean console.

Nine successful Flash jobs for this batch, including the turnover audit. A tenth
read-only job on the worked-example generator belongs to the next batch and is
not scientific acceptance evidence here. All 800 manufactured checks pass and
103 focused tests pass. Final source will now be committed and frozen for the
required complete regression; the corpus ledger is not advanced before that run.
