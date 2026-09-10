# DCR Article: Complete Technical Review

## Scope and Status

Issue #4338, native child of epic #4009, corpus #4021. Branch
`fix/4338-dcr-complete-rigor`, parent `06c7742b741e9a79d2856c9b8de51e98e73f9716`.
The complete 5,940-word original article, governed reachability and event
protocols, and related critique records were inspected. The article's complete replacement is implemented and locally validated. No calibrated golfer result is available.
Preserve the canonical DCR definition, six bounded cases, negative/null
results, claim-authority pins, peer impact work and immutable publication.

## Findings and Correction Decisions

- Withdraw the unsupported downswing growth factor. The abstract called it
  DCR, the body DIR, and neither had reproducible parameters or histories.
- Derive fixed-configuration quadratic homogeneity without assuming monotone
  growth. Include zero quadratic drift and potential/velocity cancellation.
- Keep acceleration-space DCR distinct from the full state derivative; add
  Cartesian curvature and nonlinear-coordinate Hessian terms. Ordinary
  coordinate acceleration is not a tangent vector under nonlinear charts.
- Transport acceleration metrics through the inverse mass matrix before
  comparing force ratios. Inertia weighting is neither unique nor energy.
- Declare regularizer units, zero capacity, capacity versus realized input,
  directional omissions and the exact interpretation of numeric thresholds.
- Distinguish three acceleration channels from six state coordinates. Show
  the double-integrator controllability matrix, horizon bounds and Gramian.
- State compact-convex-input/local unconstrained assumptions for the
  short-time set limit. Switching among nonconvex inputs convexifies the
  leading endpoint set; bounded sets are not generally cones.
- Derive event-time and output sensitivities with transversality and reset
  limits. A fixed-time perturbation is not an impact-event perturbation.
- Replace the arbitrary misleading graph with a table of exact manufactured
  mechanical states. A table exposes every input and result without implying
  a measured downswing curve. All rows hold configuration fixed and therefore
  are not a time history. No new production plotting utility is needed.
- Replace invented critics and unverified video descriptions/timestamps with
  authored questions and bounded primary sources. Preserve accessible prose,
  historical heading destinations, authorship and relevant internal links.

## Independent Derivations

For normalized T=e^(2q)*v^2/2 and U=-e^(2q)/2, Euler-Lagrange yields
qdd=1-v^2+e^(-2q)*u. At q=0 and |u|<=1, DCR=|1-v^2| gives 1,0,3,8 for
speeds 0,1,2,3. Realized u=0.2 makes DIR five times DCR. This is a constructed
potential and a state family, not gravity in a calibrated golf model.

For qdd=u and z=q^2 on q>0, zdd=2*v^2+2*q*u. At q=v=1 the zero original
acceleration drift becomes 2 in z, with capacity 2. A metric alone cannot
remove the Hessian term. For constant linear z=Lq, transport H as
L^(-T)*H*L^(-1). For a=M^(-1)*tau, transport H to M^(-T)*H*M^(-1).

Drift (3,4) and input effects (u,0), |u|<=2 yield ratios 2.5, 2 and
sqrt(153)/2 in Euclidean, infinity and diag(1,9) metrics. For M=diag(1,10),
drift force (1,1) and input force (u,0), |u|<=1, unweighted force and
acceleration ratios are sqrt(2) and sqrt(1.01). Regularized 11/(1+0.1)=10
differs from the unregularized 11; epsilon must scale with units.

For the double integrator, rank(B)=1 but rank([B,AB])=2. Wc has entries
T^3/3,T^2/2,T and determinant T^4/12. Pointwise bounded inputs instead give
marginal endpoint bounds umax*T and umax*T^2/2, not an arbitrary rectangle
of simultaneously attainable pairs. Fast switching between -1 and 1 gives
zero leading displacement, outside the nonconvex instantaneous input set.

For y0=1,v0=-1,a=-8, downward event speed is -sqrt(17), with derivative
1/sqrt(17) versus fixed-time derivative t*=0.3904. The event-map expansion
uses delta_t=-(g_x*delta_x)/(g_t+g_x\*fminus); grazing or missing events need
explicit failure handling. Covariance propagation requires that event map
and a declared joint covariance, neither of which is supplied by DCR.

## Sources and Evidence Boundaries

- MIT's primary [multibody notes](https://underactuated.mit.edu/multibody.html):
  read the Lagrangian/manipulator derivation, double-pendulum geometry,
  velocity quadratic terms and C-matrix nonuniqueness. Supports the mechanical
  foundation; no golf DCR result is attributed to it.
- Harris and Wolpert (1998), [primary Nature abstract](https://www.nature.com/articles/29528):
  read the signal-dependent-noise/eye-and-arm planning hypothesis. Full
  primary lab PDF was located but not treated as fully read. The article
  makes no claim that this paper measured DCR, golfers or an optimal
  drift-maximizing golf policy.
- The new examples are independent analytic constructions, not inferred
  measurements. The protected APIs and all six existing synthetic cases
  remain unchanged. No trust claim is promoted to golf, causal or population
  authority by this editorial review.

## Companion Critique Follow-Up

Related critique records themselves contain unresolved technical problems:
`dimensional_inconsistency_dcr.md` proposes force/acceleration equivalence
and a misleading dynamic-fiber repair; `lie_bracket_formalism_overreach.md`
confuses acceleration actuation with full state input rank;
`planar_dcr_blindness.md` overstates isolated axial inertia and golfer precision;
`normative_ambiguity_drift.md` overstates sensitivity/free-energy inferences;
`precision_vs_gross_control.md` needs qualified time/face/shot projections.
These are queued for a separate complete critique review under #4009/#4021.
They are not accepted as factual merely because a critique ledger lists them.

## Provenance and Compatibility

The readiness factory had attributed every fresh evidence digest to a fixed
August review, even after the named route reviewer and review date changed.
An independent regression first failed on that stale attribution. The factory
now uses the actual route review metadata and places manufactured transition
and rejection events no earlier than that review. Existing lifecycle tests
now choose dates relative to the event being tested; they still reject missing
successors, stale revisions, revoked evidence and reversed chronology.

Regeneration follows the actual dependency chain: source and calculation
artifacts, route inventory, readiness library, the atlas readiness digest,
and finally all dependent route digests. Only the atlas's readiness dependency
is rebound. Its publication claims, source-manifest and critique-authority
pins are unchanged, as are scientific protocol specifications, all six
bounded cases, simulation-ready states and rejected promotion attempts.
No unavailable provider or golfer-validation evidence is manufactured.

The authored summary uses the site's native disclosure component. Its trust
test reads that component and retains the same claim-amplification validation.
A temporary legacy wrapper passed that old selector but caused pale text on a
light background in dark mode. Visual inspection found it; removing the wrapper
and adapting the selector restored contrast. All three wide tables use the
existing keyboard-focusable scrolling region. No CSS or JavaScript was added.

## Validation and Delivery

Initial independent suite: ten analytic checks passed and two publication
checks failed against the unsupported original wording (RED). Thirteen new
checks now cover mechanics, coordinates, metrics, regularization, finite-time
control, event sensitivity, publication bounds and actual review attribution.
The first complete run exposed stale readiness digests and legacy summary
bindings; a later run exposed the dependent atlas digest and calendar-fixed
lifecycle tests. These were corrected at their source, not waived.

- Full required run: `py -3.12 -X utf8 -m pytest tests/ --cov=src --cov-report=xml --timeout=60`:
  **5,124 passed, 29 skipped, 132 deselected, 50 warnings; 92.88% coverage**.
- After the final disclosure markup and trust-test selector correction:
  **84 affected tests passed** across article rigor, DCR reachability, scientific
  trust metadata, readiness, lifecycle and falsification-atlas suites.
- Final content lint: **131 passed**; all **34 static contracts**, **636 title
  checks**, internal site links, Ruff, Black100, quality and configured mypy pass.
  The final independent article/reachability suite also passes.
- Selected Quarto HTML render passes. All 31 historical heading destinations
  are retained, with no duplicate IDs or missing local fragments; 220 math
  items, including 31 displays, render without MathJax errors.
- Complete article read through 31 overlapping browser captures. Table clipping
  found during that reading was repaired and the tables inspected at both ends.
  Seven viewport widths in both themes pass without document overflow. The
  polished interaction run verifies 42 keyboard-scroll cases and both native
  disclosure controls. Representative final mobile equation endpoints were
  visually read; capture creation alone is not counted as visual inspection.
- Final canonical browser gate: **14/14 passed**, no serious/critical axe
  violations. Separate full-page axe scans with both disclosures expanded pass
  in both themes at that severity. A shared moderate `landmark-unique` finding
  remains. All four final expanded-panel captures were inspected and dark
  text/background contrast is restored. The persistent browser reports four
  console errors and two warnings; no zero-console claim is made.

Local logs and captures are scratch evidence. Canonical source, tests and this
review record carry the reproducible argument. No textbook PDF changed in this
article-only correction. Prior passive PR #4337 is now protected-merged and
published at a1ef3f22ce38d148064b0c0b5c29c6db30f46168; deploy 34441497877
succeeded, and all 956 records in exact artifact 10138837491 were independently
checked. Implementation 92e92d6577edc6ca501ba290645b67ecf767aa0f is on the protected
passive squash; its tree is identical to the validated pre-rebase tree
f7ee966d5c83bdf5310af9595718824e5e978c49. The initial rebase lacked that
locally fetched commit and was retried after fetching it. No remote branch
was created by the interrupted push. A later push correctly rejected the
article digest: Git normalized the editor's CRLF source to canonical LF at
commit. The canonical-byte digest and its readiness/atlas dependents were
regenerated before retrying. No mathematical or rendered content changed.
The standalone development-log checker still reports the preserved peer
#3903/#3902 metadata omissions; this feature's entry has its concrete SHA.
PR #4339 protected-squash-merged from head 7ba2db42 as
06ad67134fb08841281640d4373d9df1d7cc56ae. Normal commit/push hooks and protected
checks passed. Exact deployment 34447587020 failed before publication: docs/ output pruning removed the bound review document. Relocate durable evidence outside generated output and test that boundary before retrying publication.
The corpus and companion critiques remain unfinished.

## Deployment Source Boundary: #4342

Run 34447587020 for protected DCR merge 06ad67134fb08841281640d4373d9df1d7cc56ae
failed before publication at the scientific claim-audit coverage step. The
review path was under `docs/`, both a development-document location and Quarto's
configured output directory. The deployment's internal-Markdown pruning removed
it before the final evidence validator. The article and mathematical checks
were valid; the evidence storage boundary was not.

This canonical review now resides under `reports/technical-review/`, outside
rendered output. The ledger binds the same reviewed content at its durable
path with current digests. No authority pin, review disposition, publication
gate or pruning rule is relaxed. Development handoff/logs reference this source.
The new integration regression copies every reviewed route's bound evidence
into an isolated temporary root, validates it, runs the real output-pruning
function and validates again. It reproduced the exact missing-review failure
before relocation. It additionally excludes all durable evidence from the
configured output directory, covering full clean renders as well as pruning.
Never run the destructive output pruner against a development checkout merely
to reproduce this failure; the test's fixture is sufficient.

This delivery repair accompanies fascia #4341 in the same protected PR, with
separate issue #4342 and DL-#4342 tracking. The fascia implementation replay
preserved tree 140a424c7be130df564fd6a8b3ccabfc807e5786 when moved from the DCR
PR head onto its identical protected squash. Full publication verification
remains pending the corrected protected deployment.

The boundary test is GREEN after relocation; 35 combined boundary, trust,
presentation and fascia checks pass. Ruff and Black pass. The publication
coverage command (`generate_claim_audit_inventory --manifest ... --check
--enforce-publication`) passes for all 239 previously published routes using
current local HTML records. This is a scoped local check: a manifest of the
entire long-lived preview cache also included 14 stale or local-only HTML
files and correctly failed coverage. They were excluded by matching the
independently verified prior live-route set, not by weakening the validator.
The clean protected deployment remains authoritative for the new render.
