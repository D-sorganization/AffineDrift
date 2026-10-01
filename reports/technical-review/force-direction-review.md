# Force Direction and Reference Points — Chapter 9 Review

Issue #4742, epic #4009. Entire chapter source read and revised from Chapter 10 delivery checkpoint `39ae90999281574623b568b47c8d2f03ee60e8b6`. This is a scoped chapter review, not a new whole-book certification. Publication checks and final evidence bindings remain pending.

## Corrections and Derivations

- A force applied at hand point H has zero moment about H. Its moment about the club center G uses the actual center-to-hand lever arm; the straight-link scalar is minus the hand-to-center distance times the declared shaft-transverse component. An intrinsic grip moment remains a separate load. The corrected illustration labels both points and the lever arm.
- Shaft components are not automatically trajectory-normal/tangent components. Moving-hand acceleration and all external loads enter the rigid-body balance; an axial grip force can do positive work. A fixed-center circular net-force formula is not a general grip-force equation.
- Virtual work maps the specified force to generalized load. At a fixed state the reduced mass matrix mixes that load into acceleration, potentially with opposite coordinate signs. Unreduced constraints need their reaction solve. The free-particle example x=q² shows why even the complete velocity-bias vector does not transform independently under a nonlinear coordinate change.
- Distinguish kinematic tangential/centripetal reaction reconstruction from the declared cross-rate/squared-rate coordinate bins. A rotating observer's inertial terms must not be added a second time to an inertial free-body balance. Passive model conditions do not establish passive muscles.
- Coordinate-axis rotation at a fixed observer preserves a dot product; changing the translating observer changes force power. Moving the wrench reference point preserves total power only with the consistent velocity on the same rigid body, for the same observer.
- Two contacts generate common-force, differential-force and intrinsic-moment terms. Reversing the separation reverses only the differential-force couple. Collapse requires bounded differential force; an axial internal differential load is invisible to the resultant wrench. These algebraic controls do not themselves produce dynamically feasible interventions.
- Sensor calibration includes moment transport, sensor-side inertial corrections, synchronization and uncertainty. A one-degree axis error can reverse a small transverse component of a predominantly axial load. A resultant wrench cannot recover local contact deformation work or biological force allocation.

## Reading and Evidence Scope

- Choi and Park 2020: publisher full text at https://pmc.ncbi.nlm.nih.gov/articles/PMC7374515/, abstract through discussion/limitations (HTML73–241), especially inverse-dynamics methods. Nine right-handed male professionals; internal grip sensor plus kinematics; heavier instrumented grip, hand overlap and foam-ball impact limit interpretation. No new replication. The legacy key `koike2020` already resolves to these authors and is retained.
- Koike 2016: four-page proceedings PDF https://ojs.ub.uni-konstanz.de/cpa/article/view/6828/6125 read in full text. Single instructor; static calibration, fixed palm contacts and neglected handle-piece inertia limit the reconstruction. No new human validation or figure-data digitization.
- Featherstone 2008 remains a background reference; no new full-book reading claimed.
- Immutable provider revision and exact file hashes/read ranges are in `force-direction-provider-checks.json`. The force-balance, coordinate-source and two-hand chapters supply conventions. No provider ODE, raw trajectory archive or human experiment was rerun. Earlier two-hand and Chapter 10 reviews retain their own scopes.
- The provider defines separation and differential force with opposite ordering, giving a minus sign in its couple formula. This chapter defines d=r1−r2 and D=(F1−F2)/2, giving plus d×D; those conventions are consistent. A provider phrase equating positive generalized drive with positive coordinate acceleration is not carried into this chapter: the mass-matrix example demonstrates the limitation.

## Independent Checks

Two source-contract checks failed against the original chapter while seven independent mechanics checks passed. All nine pass after correction; 32 combined Chapter 9, Chapter 10 and two-hand checks pass. Manufactured cases verify zero hand moment/nonzero center moment, coupled acceleration signs, nonlinear-coordinate bias, common/intrinsic moment survival, bounded versus unbounded collapse, translating-observer power and sensor-axis leakage. They do not establish a human mechanism.

Only `make_force_projection` has a changed function body in the shared figure generator (AST comparison against the base); `_arrow` and `_box` receive explicit `Axes` type annotations. Type-safe scalar scatter arguments regenerate identical SVG/PDF bytes. The scoped figure was regenerated with the existing style and hash salt. SVG line endings are normalized to LF for Git/evidence parity. Prior route findings are snapshotted in `force-direction-prior-review.json`; their historical verification commits must be retained when digests are refreshed.

## Delegation and Adjudication

Five agy Gemini 3.8 Flash High jobs performed supplied-text mechanics/inference inventories, two notation passes and a PR-description draft. They used no tools, network or source edits. Lead retained all scientific decisions. Accepted inconsistent shaft terminology, missing local symbol definitions, reference-point wording and bounded-force clarification. Rejected the suggestion that the full velocity-bias vector is independently coordinate-invariant; the nonlinear free-particle counterexample disproves it. Rejected treating a fixed-force projection as a feasible dynamical intervention. The citation-key rename was unnecessary. Excerpt-only complaints about the already-defined center G and the opening cart analogy are not chapter defects. Different power terms and point velocities need consistent physical pairing, not indiscriminate renaming.

## Outstanding Delivery

Final 216-page PDF and HTML render successfully. All eight chapter pages, contents and adjacent boundaries were visually inspected; 157 downstream pages retain identical extracted text after removing numeric footers. Four browser cases and axe pass, with all 74 chapter expressions rendered; displayed equations and the figure were manually inspected. All 12 publication gates and 184 content checks pass (four skips). Full repository regression, claim bindings, corpus completion, source commit and regular protected PR remain required. No Chapter 9 completion credit or remote-main delivery is claimed by this checkpoint. Chapter 10 PR #4741 remains a separate pending dependency; do not overwrite peer PR #4740 or reopen superseded #4738.

The PR draft was not accepted verbatim: it invented an original positive-drive acceleration assertion, a general circular grip-force equation and double-counted balance equations that were not present in this chapter. Those sections add qualifications and examples; only the actual hand-reference error and unqualified power-invariance wording are described as such. Provider reruns are outside this scoped review, not promised follow-up validation.
