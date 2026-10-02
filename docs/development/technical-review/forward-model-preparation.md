# Chapter 18 Preparation — No Acceptance Credit

This is preparation for `articles/proximal_distal_companion/chapters/ch18_forward_model.qmd`, the next longest pending source (about 2,052 words), now queued as [issue #4817](https://github.com/D-sorganization/AffineDrift/issues/4817). No claim, source edit, finding binding or corpus credit has been created. Chapter 28 follows at about 2,051 words. The current goal remains 105 source audits plus whole-book consistency.

## Reading Completed

- Full Chapter 18 source and `make_solver_loop()` in `scripts/make_proximal_distal_companion_expanded_figures.py` were read. The figure presents state/controls, constrained dynamics, integration and audits. Preserve unrelated generator functions if this figure changes.
- At pinned UpstreamDrift revision `85cce4d3307bb7ad3953d9fc6e583e370803515c`, read the full documents under `docs/research/proximal_distal_energy_transfer/`: `chapters/_ch05b_forward_two_hand.qmd`, `chapters/_ch06_methods.qmd`, and `OPEN_RELEASE_QUALIFICATION.md`. The first output was truncated; the missing portion was subsequently read. These were source-document inspections, not fresh dynamics runs. Implementation and saved numerical datasets have not yet been checked for this audit.
- The planar two-hand provider example declares seven coordinates, four bilateral constraints and three admissible degrees of freedom, conditional on full rank. It uses a fixed 0.4-second horizon, projection and prescribed smooth commands. Its ideal whole-system constraint power differs from one-sided hand-to-club power. Projection energy is numerical, not physical work; the declared projection-energy magnitude exceeds its raw energy-work residual, so cancellation deserves explicit treatment.
- The two-DOF study's “impact” is a club-angle event, not a ball-contact simulation. Its filter preloads the initial torque; command rise-time sensitivity does not identify human activation. Open-release hash/qualification checks are not fresh solver validation. Pose-only adapters are not five-engine dynamics parity. Subject-specific and held-out human qualification remain open.

## Proposed Technical Review Focus

Distinguish a fixed bilateral contact mode from unilateral contact/separation/impact; state SPD/rank assumptions for the KKT solve; declare multiplier units and signs; count gravity, elastic and dissipative terms once. Mixed force/acceleration residuals require scaling, and refinement need not improve each diagnostic monotonically. A finite torque step is not an impulse; first-order filtering is not a hard slew-rate bound, and delay alone does not smooth a signal. Retain actuator state and preloading explicitly.

Explain rheonomic initial-velocity compatibility, physical impact versus numerical projection, moving-boundary work and one-sided versus whole-system power. Inverse/forward agreement can be algebraic rather than independent validation. Avoid treating a consistent coordinate change or a legitimate different physical model as a required gate failure. Raw energy growth with positive supplied work is not an energy-balance failure. Spatial-vector algorithms are not a coordinate representation competing with minimal/maximal coordinates. Compare properly mapped physical observables, with frame/point and observer qualifications. Finite verification cases do not prove global model properties or human validity.

## Helper Adjudication and Literature Limits

`forward-model-inventory-flash.txt` was produced by agy CLI `gemini-3.8-flash-high` and read. Retain useful issue pointers; reject its unsupported approximate 0.5-ms collision duration, blanket statements about navigation applications, insistence that unilateral contact always needs an LCP/QP, claim that moving constraints necessarily do nonzero work, same-state treatment of ZVCF, and energy-growth failure criterion. Architectural recommendations must not be relabeled as empirical assertions.

DOI opens for MacKenzie/Sprigings 2009 and Balzerson/Banerjee/McPhee 2016 failed. Exact-title searches located the primary author PDF and Waterloo accepted manuscript below, but only search snippets have been seen; neither PDF has been read. Do not cite snippets as full-paper review or adopt their quantitative details before verification.

- https://sashomackenzie.com/publications/MacKenzie%202009%20A%20three%20dimensional%20forward%20dynamics%20model%20of%20the%20golf%20swing.pdf
- https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/8e0140f3-6680-4736-a83f-b0515d4e8003/content

Next action after delivery work: claim the bounded Chapter 18 issue, inspect pinned implementation/data and primary literature, then settle the technical argument before delegating tests, inventory or prose mechanics.

## Subsequent Implementation Reading

Read full pinned `scripts/research/proximal_distal_energy/forward_two_arm.py` and `tests/research/test_forward_two_arm.py`. No provider test or simulation was executed. Five finite tests cover a 30-ms driven rollout, a 40-ms zero-torque comparison at two steps, a 20-ms branch from a 50-ms baseline, coincident grip offsets and two invalid requests. Those checks cannot establish general convergence, integrator order, long-term conservation or human validity.

`forward-model-provider-tests-flash.txt` was completed and read. Correct its divergence threshold unit: the seven-coordinate Euclidean norm mixes angular and translational coordinates, so it is not simply metres. Correct its blanket statement that all initial velocities are zero: the branched rollout begins at a moving achieved state, although baseline initialization is at rest. “Zero control” does not remove gravity. Its projection and callback pointers are valid reading leads, not demonstrated provider bugs.

The loop evaluates velocity-dependent acceleration using a projected half-step velocity, then projects again. Its Verlet-shaped structure alone does not establish a particular convergence order or symplecticity. Initial projection records a correction norm but initializes projection-energy change to zero; state clearly whether the ledger starts before or after that correction. Repeated callback evaluations during stepping and later diagnostic reconstruction require a deterministic, side-effect-free control law for consistent records. The published prescribed time law meets that narrow interpretation; arbitrary hidden actuator memory would require an expanded state and a different contract.

Direct web opens of both primary PDFs subsequently failed (author host timeout; Waterloo cache miss). Full-paper reading remains outstanding; no literature claim is newly accepted.

## Primary Methods and Validation Sections Now Inspected

Subsequent retrieval succeeded for the Waterloo manuscript and the MacKenzie paper at the author's university directory. The personal author host had a certificate-chain error; no certificate verification was bypassed. PDFs and extracted text are retained locally, not included in the publication. Only the sections listed here were read; neither paper is claimed as fully reviewed, and extracted equations were not used as validated formula transcriptions.

| Primary Source | Local PDF SHA-256 | Reading Scope |
| --- | --- | --- |
| [MacKenzie and Sprigings (2009)](https://people.stfx.ca/smackenz/Publications/MacKenzie%202009%20A%20three%20dimensional%20forward%20dynamics%20model%20of%20the%20golf%20swing.pdf) | `3c277cd7e1e0b31ab575854b1c1f8dedcbc12a376595dd15d908693125a076e3` | Abstract/introduction; sections 2.1, 2.3–2.6, 3.1 and conclusion; 11-page PDF. |
| [Balzerson, Banerjee and McPhee (2016), Accepted Manuscript](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/8e0140f3-6680-4736-a83f-b0515d4e8003/content) | `fc961125d7147e470e9ed0f4219a2d19ba01ce782f5d2f259dc542ace0fee204` | Abstract/introduction and golfer methods through section 2.1.4; sections 2.2.4, 2.3.1, 2.4.1, 2.6 and conclusion; 14-page PDF. |

MacKenzie/Sprigings adjusted torque-generator timing and scale to fit the selected fastest swing of one golfer. Single-camera measurements limited the quantitative comparison to planar projections; axial rotation was not checked quantitatively. A separate optimization then targeted clubhead speed. Torque generators represented aggregate joint actions rather than identified individual muscles. These distinctions support describing a fitted model and bounded comparisons, not independent validation of arbitrary three-dimensional interventions.

Balzerson and colleagues combined a four-degree-of-freedom golfer, flexible shaft, impact and flight models. The golfer was fitted to earlier motion data; shaft, impact and flight comparisons had separate datasets and scopes. These component checks provide useful evidence but do not by themselves establish independent predictive validity for every optimized outcome of the assembled model. Do not relabel the reported component comparisons as absent merely because the whole-system claim needs narrower wording.

Both observations guide the planned chapter revision; neither confers corpus acceptance or constitutes a new human study. The issue records eight bounded correction areas and publication/regression acceptance criteria under #4009 / #4021 / #4059.
