# Moving-Base Review — #4774

Full Chapter 17 source read and revised under epic #4009 and corpus #4021.
This is an implementation checkpoint, not a completed-audit or publication
claim. The corpus remains at 118 pending full-source audits plus whole-book
consistency. The final source and publication are verified; exact committed-source binding
and protected delivery remain required.

## Scientific Decisions

1. **Separate Fixed, Prescribed, and Dynamic Bases.** A prescribed base can move. It needs an enforcing reaction after other inputs are declared. The same reaction can change acceleration while doing zero instantaneous work at zero base velocity. Assigned torques and a prescribed path are not inherently invalid if their residual reaction and power are accounted for.
2. **Correct the Replay Inference.** With identical distal equations, inputs and compatible initial state, prescribing the baseline base path reproduces the distal solution under uniqueness when the removed input enters only base equations. Persistence is a consistency property; it does not prove feedback unimportant. Distinguish instantaneous intervention, integrated response, fixed input history and recomputed feedback policy.
3. **Distinguish Mass From Trajectory Authority.** Bounded-load, finite-time mass limits are not arbitrary prescribed accelerating paths. Force capacity, stiffness and feedback gain are separate assumptions. A translating hub does not acquire whole-body anatomy by having finite mass.
4. **Make Coordinate Dependence Concrete.** A manufactured cart-pendulum fixture diagonalizes inertia in horizontal COM coordinates while retaining the cart force in the angular generalized load. Newton balances, kinetic energy, force covectors and power establish that coordinate simplification does not remove physical interaction.
5. **Close the Declared Energy Boundary.** Include enforcing power, conservative storage once, represented flexible kinetic energy, dissipation and numerical projection work. Internal passive constraint powers cancel under compatible relative motion. Distinguish grip power, projected moment, rotational power and work. Numerical convergence is not physical-model validation.
6. **Bound the Provider Comparison.** Separate native inertia/bias operators from the shared contact law and update procedure. The spatial same-force geometry controls are postprocessing; the planar coincident-grip branch is a new continuation. A one-arm model needs explicit added contacts before it can answer two-hand questions.
7. **Carry Forward the Existing Contact-Moment Qualification.** Chapter 20 already documents the noncentral vector-damping force-pair moment under AffineDrift #4724 and UpstreamDrift #11195. Propagate the qualification to Chapter 17 without claiming a new discovery, a whole-system angular-momentum residual or the cause of the negative club moment. Chapter 16's central fibers are a distinct model.
8. **Bound Human and Control Inferences.** Nesbit/McGinnis use measured 3D markers mapped to a rigid planar club model; Miura combines measured illustrations and simplified models. Neither identifies a universally beneficial whole-body intervention. A failed model-controller experiment counts against the tested combination; separating causes requires evidence.

## Read and Evidence Scope

- Entire canonical `articles/proximal_distal_companion/chapters/ch17_moving_base.qmd`, originally approximately 2,098 words; relevant complete Chapter 20 qualification and Chapter 16 contact distinction.
- Entire provider `_ch06b_coupled_base_flex.qmd` and `_ch06cc_spatial_forward_contact.qmd` at UpstreamDrift `85cce4d3307bb7ad3953d9fc6e583e370803515c`; complete `spatial_forward_engines.py`, selected contact-contract, spatial-study and planar-runner sections. No new simulator run or complete provider-code audit.
- Nesbit/McGinnis 2009: publisher PDF abstract, Methods/Subjects and hub-path results; those methods were rechecked during implementation. Four right-handed amateurs, one selected swing per person, rigid planar inverse estimates driven by projected 3D markers. https://www.jssm.org/volume08/iss2/cap/jssm-08-235.pdf . No new complete-paper review is claimed.
- Miura 2001: published PDF abstract, measurement examples, single-link and moving-pivot emulation sections. https://people.stfx.ca/smackenz/Courses/DirectedStudy/Articles/Miura%202001%20Parametric%20acceleration%20effect%20of%20inward%20pull.pdf . The prescribed-pivot calculation is not a measured human intervention.
- Read-only archived-array probe reproduces the already known contact-pair moment at the newer pinned archive, SHA-256 `29b955b16aaba2e348060248d50fe954dd54a351e143055c8e29e2b7af51694a`. Maximum summed pair-moment norms are approximately 0.08261/0.08274 N m; after driver removal, approximately 0.03364 N m. This is not a newly integrated trajectory or a reconstructed whole-system momentum residual.
- Additional manufactured QA probes checked a corotational contact-law illustration and 102 coordinate-transformation cases. They do not replace the provider law or establish that its negative-moment result survives a physical model change.

## Delegation and Adjudication

Twelve completed supplied-text agy CLI `gemini-3.8-flash-high` jobs: initial
inventory, provider extraction, rejected 1D example, cart-pendulum draft,
objectivity table, coordinate algebra, figure-function draft, test refactor,
editorial inventory, PDF helper draft, turnover draft and PR-description draft.
The lead retains scientific responsibility and independently checked the
mechanics. No delegated agent ran the provider simulation.

Corrections to delegated outputs include:

- Reject the claim that the planar coincident-grip control merely postprocesses fixed forces; that description applies to the spatial controls.
- Reject the first 1D fixture's unsupported explanation of its distal response, blanket Lyapunov-time cutoff, and claims of exact dense-output replay.
- Keep gravitational load at general angles; zero speed alone does not eliminate it.
- Replace the test draft's guessed paths and broad file glob with the exact Chapter 17 and generator paths. Remove its six-argument function and default constructor; use explicit typed fixtures and independent numerical balances.
- Revise the figure labels for fit and move the reaction arrow away from the orange link so it remains visible. Both panels permit base motion. A prescribed trajectory is not an immovable base.

## Checkpoint Validation

The new module has 17 cases: 14 manufactured mechanics checks and three guards
against specific retired editorial claims. RED: the three guards fail against
the original source/figure, while all numerical cases pass. GREEN: all 17 pass
after revision. The guards do not certify scientific completeness.

Ruff passes; Black formatting applied; 653 source-title checks pass. The longest
new test function is 35 lines and none has more than four arguments. The figure
was regenerated and visually inspected; a minor reaction-arrow overlap was then
corrected. Its final appearance and all Chapter 17 PDF pages were inspected. A later
heading-only rebuild restores the book's required navigation landmarks;
that final output still needs its follow-up checks.

The 96 historical route findings are snapshotted in
`moving-base-prior-review.json`. Their scientific semantics and verification
commits must remain unchanged. No new finding binding or completed-source credit
has been assigned at this checkpoint.

## Delivery Dependencies

The source branch starts at measured-golfers integration
`5d3b569fb132b0c3e25037b9b8676b612987a7eb`. PR #4770 is verified on remote main as
`099dc2cbfcf506941b3b0d306b43b7a1ccc5e767`. PR #4772 remains open with protected
auto-merge armed and exact-head CI `36937087586` running. Its earlier run failed
one page-settling check on secondary-axis-stability.html; the failure is retained
in its receipt, with a passing targeted local reproduction and no claimed fix.

The related technical monograph's dependent contact claims remain a consistency
follow-up; do not award it a full-source audit from this chapter correction.

## Final Editorial and Publication Follow-Up

The editorial inventory prompted definitions for actuator/external power,
prescribed coordinates, rigid-point velocities, grip-wrench components and
contact coefficients. The large-mass statement now uses resultant force;
grip power explicitly assumes a locally rigid grip region. The initial figure
and revised PDF pages 117–124 plus boundaries 116/125 were visually inspected.
The source's chapter-level heading follows the existing hierarchy filter;
the delegated suggestion to change it to a level-one heading was rejected.
Repetition in the worked example, general inference and reader exercise serves
different explanatory purposes and was not mechanically deleted.

The delegated PDF helper's broad exception/fallback and guessed page limit
were rejected; the existing fail-fast pypdf/pdftoppm workflow was retained.
The turnover draft's file-URI links and confusion between the new branch head
and main commit were corrected. The PR draft's phrase “no simulation runs” is
too broad: the manufactured fixture integrates an ODE; no provider simulation
was rerun. The planar and spatial benchmarks do not share one contact law;
it is the spatial native-engine comparison that shares its law and update.

Initial local browser verification failed solely because the preview lacked
public-site-manifest.json. Supplying the generated one-route scope manifest
resolved all four cases, with zero serious/critical axe findings. The production
verifier and website sources were unchanged. Seven display equations were
individually materialized and inspected at 390/1440 pixels. Wide mobile equations
use keyboard-focusable horizontal scrollers; they are not asserted to fit
without scrolling. The table also uses a focusable scroll region. A first QA
probe incorrectly expected SVG MathJax output; inspecting the actual CHTML DOM
corrected the probe. Four inline lazy placeholders had not been visited at that
checkpoint and must not be reported as fully materialized.

Full regression before the final heading correction: 6,406 passed, one failed,
29 skipped, 187 deselected; 78.97% combined src/scripts coverage. The failure was
the book contract requiring “How the Mechanism Works” and “Where the Picture
Breaks” in each chapter. Those reader landmarks were restored in the source;
the test was not changed. No claim of a wholly passing full run is made from
this result. Final focused validation is recorded separately.

The related technical monograph is an immutable provider projection, including
its pinned PDF. UpstreamDrift #11195 remains open and explicitly requires the
qualification to reach the source monograph and dependent publications after
the provider resolves the contact interpretation. This chapter carries the
qualification now; no silent rewrite of pinned provider bytes or full-source
monograph credit is claimed.

Final source acceptance: the heading correction passes all 72 focused mechanics,
companion, contact, audit and root-hygiene tests. All 12 publication gates pass
again. The final 225-page PDF matches its public copy, and all revised pages
117–124 plus boundaries 116/125 were inspected again. Four final browser profiles
pass with zero serious/critical axe findings. Visiting every Chapter 17 math
node at 390/1440 pixels yields 69 rendered containers, seven display equations,
zero math errors, zero remaining placeholders and zero page overflow. The
earlier full-suite failure is retained; a second full run is not claimed.
The dependency receipt verifies 126 unchanged paths and three changed shared
dependencies against 5d3b569fb: Chapter 17, the whole-book PDF, and the shared
generator. An AST comparison confirms only make_moving_base changed among
generator functions. The target figure pair is new evidence for this audit.
