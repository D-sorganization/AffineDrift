# Contraction Development Workspace Review — #4465

## Scope and Central Argument

Read the complete long LaTeX manuscript, consolidated Quarto manuscript, eight
companion chapters and development hub: eleven indexed sources under #4021/#4009.
The correction connects mechanical and actuator assumptions, feasible nominal
motion, perturbation dynamics, delivery objectives, feedback and robustness.
An optimized swing can be sensitive to disturbances; a contracting controller can
track an ineffective swing. Connecting these questions requires explicit bounds,
not shared geometric vocabulary or an interpretation of cost as physical energy.

This subtree is excluded from the production Quarto render list. Its historical
URLs redirect to the newer series. This is a complete source and local-preview
review of this workspace, not clearance of those destination articles, activation
of new routes, whole-volume certification or empirical evidence about golfers.

## Corrected Findings

1. **P1 — Regional Contraction.** State the common vector field/input, existence,
   invariant domain and bounded positive metric. Integrate the infinitesimal
   inequality along admissible curves. A Euclidean initial-distance bound needs
   an admissible straight segment; geodesic convexity alone does not supply it.
   Continuing mismatched disturbances generally leave a residual error.
2. **P1 — Linearization and Sampling.** Include derivatives of state-dependent
   input vector fields, feasible nominal dynamics and absolute start time in a
   nonautonomous held-input flow. Distinguish exact first variations from finite
   perturbations with a generally second-order remainder. Remove the unsupported
   five-percent validity threshold and separate stage index from physical time.
3. **P1 — Optimization and Error Decay.** Derive the Bellman correction including
   future value. Unconstrained finite-horizon LQR with semidefinite state/terminal
   costs and positive input cost does not require controllability. Its value
   matrix need not be a metric. Supply full DDP gradient, cross and dynamics-
   Hessian terms, feedforward correction, regularization and line-search limits.
   A Riccati identity alone establishes neither regional nonlinear contraction
   nor stability after the finite horizon.
4. **P1 — Coordinate Geometry.** A task pullback is positive definite exactly
   when its Jacobian has full column rank. A background completion changes the
   objective and must transform with the coordinates. An ordinary nonlinear
   value Hessian has an extra gradient term and is not generally a tensor or
   positive metric. Reusing an identity matrix in a new chart changes the penalty.
5. **P1 — Certification.** Derive the fixed-rate LTI LMI using inverse metric
   and transformed feedback, with the negative-feedback sign. Joint rate design
   is bilinear. Separate continuous and discrete residuals. Samples can miss an
   expanding interior; a regional coverage claim needs derivative/error bounds,
   metric definiteness and invariance. Retain the CCM integrability amendment.
6. **P1 — Mechanical and Biological Applicability.** Close actuator and contact
   dynamics before linearizing; include event-time sensitivity at impacts.
   Distinguish configuration, state, task output and their nullspaces. Muscle
   force is not categorically passive; zero excitation retains internal history.
   Remove unsupported human/robot rankings and universal dimension cutoffs.
   Optimization, a segment-speed sequence and a simulation fit do not identify
   neural control, energy transfer, tissue load or clinical safety.

All 32 original equation labels remain available in the LaTeX manuscript.
The companion chapters now develop the assumptions and examples rather than
repeat generic motivation. Long equations were split to remain readable on mobile.

## Independent Mathematical Checks

`tests/test_contraction_workspace_rigor.py` contains eight manufactured checks
and six specific source regressions. Before correction, all six source checks
failed and eight numerical checks passed. All fourteen now pass.

- A one-step LQR example has state 1 to 2 while value falls from 1 to 0: the
  unpenalized terminal quadratic form is not a metric.
- A valid two-step example gives Riccati values (1.6, 1.5, 1), gains (0.6, 0.5),
  states (1, 0.4, 0.2), and values (1.6, 0.24, 0.04). The uniform factor 0.21875
  is a conservative bound, not either exact step ratio.
- A nonlinear coordinate-Hessian calculation, checked by finite differences,
  changes sign relative to the pullback; transformed background penalties differ
  from a newly imposed coordinate identity.
- Endpoint derivatives of a polynomial are negative while the central derivative
  is positive, demonstrating the gap between sampling and regional certification.
- State-dependent actuation, nonautonomous held-input integration and LMI
  congruence independently check three easily omitted terms/sign conventions.

These are mathematical checks, not measured swing data or physiological validation.

## Primary-Source Review

- [Lohmiller and Slotine](https://web.mit.edu/nsl/www/preprints/contraction.pdf):
  differential contraction and finite-separation integration.
- [Forni and Sepulchre](https://arxiv.org/pdf/1208.2943): Theorem 1, connecting
  curves, invariant regions and coordinate-invariant differential analysis.
- [Manchester and Slotine](https://arxiv.org/pdf/1503.03144) and the
  [integrability amendment](https://arxiv.org/pdf/1711.08128): differential
  feedback construction and the rank-changing counterexample/additional condition.
- [Tassa, Mansard and Todorov](https://roboti.us/lab/papers/TassaICRA14.pdf):
  DDP derivatives, feedforward and feedback corrections, input limits and rollout.
- [Tedrake's LQR chapter](https://underactuated.mit.edu/lqr.html): finite-horizon
  Riccati equations and the need for a specified continuation beyond the horizon.
- [Boyd et al.](https://web.stanford.edu/~boyd/lmibook/lmibook.pdf): inverse-metric
  variables and state-feedback LMI congruence.

Only cited references were checked for this argument. The shared bibliography's
other unused entries have not received a comprehensive bibliographic audit.

## Delegation and Validation

Six supplied-text-only agy `gemini-3.8-flash-high` plan-mode calls ran in three
parallel pairs: claim inventory, fixture arithmetic and final consistency review.
The lead checked adopted suggestions against equations and primary sources.
Rejected suggestions included confusing a conservative decay bound with an exact
ratio and incorrectly dismissing the CCM amendment's rank-changing example.
No permission bypass or unattended file/tool access was used; fleet dispatcher
issue Repository_Management#1800 still blocks that broader execution mode.

The full Python suite recorded 5,519 passed, two failed, 29 skipped and 132
deselected, with 92.88% src coverage. Both failures were root-hygiene checks on
Playwright's temporary log directory. After moving those logs into development
QA, all six hygiene checks passed. Root Ruff, Black (727 files), title audit (638
publishable sources) and mypy (91 sources) pass. Content-lint results and exact
source/render digests are retained in the companion verification receipt.

Ten explicit Quarto renders succeeded. Twenty light-theme browser cases (390px
and 1440px) have one visible H1, no document or display-math overflow, no MathJax
errors and no unresolved citation markers. Mobile captures were visually read;
the consolidated long capture also received mathematical DOM checks. The standalone
main/hub previews request a missing listing index; this excluded subtree has no
production listing context. No axe or dark-theme clearance is asserted here.

The native MiKTeX build succeeds in three passes: 15 pages, all visually checked,
without overfull boxes or undefined-reference warnings. The built-in editor
compiler was unavailable (platform standard-directory error); native compilation
is the evidence. PDF, screenshots and raw logs remain local QA, not a new public
download. Production render exclusions and redirects remain unchanged.

The first CI static gate could not resolve five uses of local inline-bibliography
keys. Aligned all seven LaTeX reference keys with the shared BibTeX entries and
added the checked LQR entry. Native compilation and the baseline-aware
structural gate pass with the old untracked proximal-distal generated LaTeX
preview excluded; the argument and displayed references are unchanged.
