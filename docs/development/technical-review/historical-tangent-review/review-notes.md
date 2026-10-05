# Historical Tangent and Integral Draft Review

## Scope and Coordination

Epic #4009, corpus #4021, issue #4945. All 15 indexed QMD sources under
articles/tangent-hyperplane-articles/Drafts_Original_Articles were read in full.
Lease 5989812707 and presence 5989812933 expire around 09:11 UTC on 5 October
2026. Session technical-review-20261005-historical-tangent. The isolated branch
fix/historical-tangent-review now includes parent acceptance f52517a9c, regular
PR #4946. Before this review, 42 of 407 indexed scopes remain pending.

The originals are audit artifacts, excluded from production rendering by
_quarto.yml. All 15 already have aliases on canonical series pages. Preserve
that routing. Twelve lacked consistent deprecated/canonical metadata; this is
now explicit on every draft. The three existing banners remain intact. Every
original body is retained verbatim inside a collapsed callout titled Historical
Draft: Superseded Wording; targeted corrections precede it. Preservation hashes
and canonical destinations are in source-preservation.json. This does not claim
a new review of the canonical articles beyond the accepted parent batch.

## Technical Decisions

Hamiltonian draft: distinguish mechanical action in configuration/velocity from
optimal-control running cost with a state constraint. State the normal,
smooth, fixed-final-time, free-terminal-state assumptions, terminal costate
condition, admissible-control minimization, and the limited interior gradient
condition. Necessary conditions are not sufficient; hybrid and endpoint
constraints need separate conditions. A control Hamiltonian is not generally
mechanical energy. Read the primary MIT trajectory-optimization chapter's
Pontryagin and adjoint sections, especially continuous conditions and endpoint
cost: https://underactuated.mit.edu/trajopt.html. No full-book reading claim.

Numerical drafts: local Euler error is second order in step size, global error
is first order under the required fixed-interval consistency/stability
assumptions. Reducing time step recovers a nonlinear equation, not a globally
linear model. Derivatives of the same discrete map still add exactly; finite
interventions do not inherit that property. The x-dot equals x-squared example
makes the distinction explicit without claiming every nonlinear model has the
same residual sign.

Integral drafts: identify common nominal trajectory, coordinates/transport,
initial variations and operator. The state transition is a fundamental matrix,
not trajectory curvature. A finite-response residual requires a shared baseline;
model-data residuals may include model, numerical and observation errors.
Derivative superposition itself has no intrinsic interaction residual.

Mechanical interpretation: impulse follows total external-force balance in an
inertial frame for a declared constant-mass system. Power must be evaluated on
the actual velocity; conservative potential and its power cannot be counted
twice. Virtual work is a fixed-time admissible displacement pairing, not actual
trajectory work. None of these ledgers uniquely identifies muscle or intent.

Control/geometric drafts: codimension one is required for the hyperplane name;
finite tangent approximation needs an error statement. Quadratic Taylor bounds
need stronger regularity than differentiability. LQR is exact for its declared
linear-quadratic problem, not every nonlinear optimum. DDP retains second
transition derivatives; iLQR omits them. MPC is receding-horizon optimization,
not a superposition theorem. Cost decrease is not a contraction certificate.

## Delegation and Verification

Three agy Gemini 3.8 Flash jobs completed successfully: inventory and two
parallel correction reviews. The inventory's suggested claim that any finite
time step prevents exact additivity was rejected: a discrete map has a linear
derivative at a common base point. Likewise, nonlinear MPC need not use a local
quadratic method. The two final reviewers found no concrete correction defect;
lead derivation and independent checks, rather than those opinions, are the
acceptance basis. Final prose was written and adjudicated by the lead.

Four independent groups of 100 manufactured checks pass, seed 4945: continuous
adjoint gradient versus central cost difference (maximum 3.08e-11 below 1e-7),
Euler global convergence ratio (deviation from two below 0.02), constant-force
impulse/work identities (maximum 2.67e-15 below 1e-11), and nonlinear finite-flow
nonadditivity with ODE/analytic comparison (maximum 2.39e-13 below 1e-9). No
predeclared tolerance was widened; these are not empirical golfer experiments.

All 15 standalone Quarto renders exit zero. Since these are excluded sources,
Quarto writes adjacent standalone HTML rather than the root docs output. The
first preview request incorrectly used docs and returned 404; corrected preview
uses only the archive directory on loopback port 8877. No production render
exclusion was relaxed. All 15 mobile pages have viewport-width documents,
zero MathJax errors/lazy containers, visible correction headings and clearly
labelled collapsed historical bodies. All correction text was visually inspected
in sequential page crops. Local canonical links are validated against source
files, not against the archive-only preview server. Screenshots, caches and
standalone generated HTML remain untracked.

Thirty focused link/trust/citation tests pass. Title-case audit passes all 665
publishable sources; archive exclusion means that count does not itself certify
these drafts. A separate script verifies all 15 original bodies, local links,
deprecated metadata, canonical targets and root render exclusion. Frozen full
regression remains required before advancing the corpus ledger.

## Delivery and Next Work

U PR #4946 is regular, accepted at source 821594bd5 with 7227 full tests passing,
93.25% coverage and unchanged tracked tree. It remains stacked on putting PR
#4940. Its app attachment failed because the thread has 100 attachments; do not
remove unrelated artifacts. H PR #4902 remains behind other active merge groups;
its own head checks are green. Do not merge this branch into a topic parent or
claim remote-main delivery from PR creation.

The central title-gate PR #1998 exposed missing pypdf in the clean CI dependency
manifest. A declared dependency/lock update is being tested in an isolated clean
Python environment; it does not remove or skip PDF tests. The generated-example
Flash audit in U's untracked QA directory is only a planning aid: it falsely
labels correct point-mass off-diagonal inertia as a defect, treats angular norms
as dimensionally mixed, and miswrites 9.81 times 0.1 once. Review generator and
canonical model declarations directly before accepting any of those claims.

After this batch, remaining scopes include publication wrappers, generated
worked examples/trust panels, and the Control Is Motion wrapper owned by another
live agent (#4878). Respect that claim. Corpus counts measure heterogeneous
indexed scopes, not scientific or empirical completion percentages.


## Consolidation Checkpoint

Runner capacity at 00:29:21 PDT / 07:29:21 UTC on 5 October: 14 busy of 15 online
runners, 93% utilization. Fleet policy triggers consolidation at 70%. New issue
#4947 consolidates this session's accepted H-through-U stack and this reviewed
historical-source change. Freeze serial pushes; no separate V PR will be opened
before the combined-delivery decision. Preserve all batch evidence and original
PRs until the combined tree is validated, protected-main merged and canonical
hashes verified. Other live sessions and workflow changes remain excluded.
The final frozen regression for this historical batch will run on that combined
tree, rather than opening another serial stack entry. Source commit here saves
the reviewed corrections and complete scoped evidence first.

## Accepted Combined Validation

The frozen combined source 4160ed5726aa6ba68587acfe1205e1f74f96dadd passes 7,278
full tests (29 skipped, 210 deselected), with 93.31% coverage and unchanged
tracked tree. All 19 extra gates and eight central pre-PR gates pass; the latter
includes the separately validated metadata repair at 26d60d2ea. The fifteen
historical corpus rows are now accepted, leaving 27 indexed-prefix scopes.
Exact hashes and limits are in reports/technical-review/historical-tangent-validation.json.
Protected main delivery remains pending via consolidation #4947. Earlier pending
statements above describe the historical sequence, not current acceptance.
