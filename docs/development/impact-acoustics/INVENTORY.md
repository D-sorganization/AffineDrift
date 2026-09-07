# Impact, Shaft and Acoustics Capability Inventory

Inventory date: 2026-09-07. Scope: relevant existing implementations, research
artifacts, tests, model limitations and integration ownership in the three
requested repositories. A file's existence is not proof of runtime or scientific
qualification. Tests listed below are discovery/verification entry points;
execution results are recorded separately in each repository handoff.

## Revision and Inspection Contract

- AffineDrift review base: `39fa6cca` (fresh `origin/main`). Initial checkout
  inspected at `3f2216d1`; source corrections use the isolated fresh-base tree.
- Tools provider base: `b4875be1986e14a8d21d2cd116f564e57cdd3e02`.
- UpstreamDrift base: `40308a0cf103ceb9a8b81b0fa62d4f5a34b24b83`.
  Its tracked Tools gitlink is `eab74a901a7c8467e1997049a73e2cfd2df74428`;
  provider-main availability is not equivalent to availability at that pin.
- Used `rg --files`, focused symbol/content searches, source/doc/test reads,
  handoffs and scoped GitHub issue lookups. Generated codemaps were not used as
  authority; UpstreamDrift lacked `docs/codemap.md`, so source search supplied
  navigation. Stale handoff completion labels were checked against actual scope.
- Isolated worktrees preserve original branches, generated AffineDrift files
  and UpstreamDrift's modified vendor entry. No vendor edit, native campaign
  execution, hardware intervention or participant experiment was performed.

Paths below are relative to the named repository. References to research modules
are navigation points, not permission to regenerate protected evidence.

## AffineDrift: Theory and Evidence

| Existing Surface | Capability and Evidence | Integration Decision |
|---|---|---|
| `articles/technology-heavy-hit-impact-coupling.qmd` | Time-scale, lumped coupling and apparent-mass discussion; old route had categorical isolation claims and inconsistent arithmetic | Rewrite this canonical route; include acoustic/research chapters, retain route and navigation |
| `articles/impact-mechanics-and-ball-flight.qmd`; `tests/test_impact_vector_rigor.py`, `test_impact_contact_rigor.py`, `test_impact_aerodynamics_rigor.py` | Detailed contact/flight, normal/tangential geometry and publication counterexamples | Link, do not duplicate the complete contact/flight derivation |
| `models/hybrid-impact-contact.qmd`; `src/affine_control/impact_contact_{models,fixtures,uncertainty,protocol}.py`; `tests/test_hybrid_impact_contact_protocol.py` | Hybrid contact fixtures, declared model/uncertainty protocol and evidence controls | Reuse methodology and explicit fixture limits; not a calibrated shaft/head acoustic model |
| `articles/impact-optimality-and-model-limits.qmd` | Impact criteria and model-fidelity boundaries | Tie optimality to declared observables, not undefined hit quality |
| `resources/research-review-shaft-flexibility.qmd`; `articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd`, `ch28_impact_collision.qmd` | Existing educational shaft/collision treatment | Link the corrected theory and track downstream reconciliation; do not edit generated `.tex` counterparts directly |
| `articles/proximal_distal_energy_transfer/chapters/_ch06_shaft_contributions.qmd`, `_ch06bb_shaft_beam_reference.qmd`, `_ch06bbb_forward_modal_shaft.qmd` | Governed shaft-energy, FE and moving-base modal publication projections | Immutable upstream evidence boundary; use as evidence/navigation, not a new contact validation dataset |
| `articles/proximal_distal_companion/chapters/ch15_shaft_memory.qmd` | Elastic state/history exposition | Connect pre-impact modal memory to matched-state design |
| `content-development/technology-research/impact-collision-dossier.md`; `critiques/04_impact_evasion.md` | Prior source collection/critique | Discovery inputs; recheck primary sources rather than inherit conclusions |
| `src/affine_control/programming_companion/`; `data/trust/` | Pinned provider manifests and claim-evidence framework | Consume qualified results by version/hash; no mutable sibling imports and no silent trust promotion |
| `_quarto.yml`, `references/affine-drift.bib`, publication/content tests | Existing route, citation and title conventions | Add `references/impact-acoustics.bib`; run title, citation, content and render checks |

## Tools: Canonical Shared Physics

| Existing Surface | Capability and Limitation | Existing Tests / Follow-On |
|---|---|---|
| `src/shared/python/golf_club/impact_coupling.py` | 1-D ball–head–hands spring/damper chain; head/hands initially at rest in a translating fixed-anchor reference; no spatial offsets, rotation, preload, modal history or radiation | `tests/shared/python/golf_club/test_impact_coupling.py`; IA-T2 #5071 |
| `docs/specs/HEAVY_HIT_COUPLING.md`; historical #4562/#4568/#4577 | Existing report wire and UI ancestry; spec's fixed-COR/rigid-bound prose differs from later caveats in package handoff | Preserve v1 wire; correct semantic claims, do not reopen or claim reimplementation of historical work |
| `src/shared/python/swing_sim/impact/{models,solver,types,contact,gear_effect,dplane,delivery}.py` | Rigid, penalty and geometry/gear-effect paths; `KelvinVoigtContactLaw` has unilateral clamping and a force cap; scalar effective-MOI assumptions persist | `src/shared/python/swing_sim/impact/tests/`; qualify event/restitution behavior and avoid double-counted gear effect in IA-T4 #5073 |
| `golf_club/shaft_profile.py`, `shaft_serialization.py`, `shaft_scaling.py`, `shaft_assembly.py` (same shared root) | Immutable station EI/GJ/mass profiles, trimming/scaling and assembly contracts | `tests/shared/python/golf_club/test_shaft_{profile,serialization,scaling,assembly}.py`; reuse in IA-T3 |
| `golf_club/shaft_statics.py` | Euler–Bernoulli static response and torsional compliance | `test_shaft_statics.py`; static-limit authority |
| `golf_club/shaft_dynamics.py` | Two uncoupled bending eigenproblems with distributed shaft mass, clamped butt/free tip; explicitly excludes head/grip coupling, rotary inertia and applied damping | `test_shaft_dynamics.py`; extend via qualified model tier, not silent semantic expansion |
| `golf_club/shaft_delivery.py` | `quasi_static_centrifugal_alignment/1`: scalar tension factor, alignment, dynamic amplification, prescribed recovery fraction; refusal above frequency-ratio limit | `test_shaft_delivery.py`; useful fitting estimate, not contact-band prestressed FE or a calibrated kick prediction |
| `golf_club/mesh_mass_properties.py`, `fitting_document.py`, `fitting_engine.py` | Mesh-derived COM/full inertia, versioned fitting documents and counterfactual comparison | Existing golf_club test directory; reuse full tensor and comparator rather than create competing representations |
| `golf_club/_validation.py` | Finite vectors, rotations, physical inertia, immutable normalization | Reused by new IA-T1 `impact_mobility.py`; new stricter invertibility boundary is explicit |
| `swing_sim/model_interchange/{body_chain,parsers}.py` | Runtime-free MJCF/URDF/OSIM parsing and explicit hand-body reduction | `model_interchange/tests/test_model_interchange.py`; XML mass sums are not measured impedance or constrained contact inertia |
| `swing_sim/delivery_interchange/{trajectory,adapters}.py` | Versioned delivery trajectories and engine adapters | `delivery_interchange/tests/test_delivery_interchange.py`; extend to elastic/prestress/wrench state without fabricating missing fields |
| `swing_sim/variation/` | Grouped sampling, global sensitivity, paired attribution, provenance and trace resampling | `variation/tests/test_global_sensitivity.py`, `test_paired_attribution.py`, `test_wire_identity.py`; reuse for impact studies |
| `swing_sim/flight/impact_solution_{contract,solver,adapter}.py` | Impact-solution family contracts and report routing | `flight/tests/test_impact_solution_families.py`; keep acoustic outputs explicitly optional/qualified |
| `swing_sim/putting/impact.py`; `golf_club/putter_head.py`, `putter_fitting.py` | Putting impact/fitting with offset/MOI and approximated twist pathways | Putting and golf_club tests; separate duration/ball-speed regimes from driver assumptions |
| `swing_sim/ground/impact_impulse.py`; `rust_core/tools-core/src/flight_ground/impact_runtime.rs` | Ground-impact/bounce kernels | `ground/tests/test_impact_impulse.py`; turf/ground events must not be confused with ball–face contact |
| `src/rate_of_closure/simulation/impact_{scene,kinematics}.py`; `web/src/model/impactPhysics.ts`, `impact.ts` | Python/React impact presentation, scene geometry and existing comparisons | `tests/rate_of_closure/test_impact_{outcomes,kinematics,scene}.py` and colocated TS tests; reuse surfaces after provider qualification |

## Tools: Signals, Audio and Other Reuse

| Existing Surface | Capability | Boundary |
|---|---|---|
| `src/shared/python/signal_toolkit/fitting.py` | Sinusoidal and exponential fitting families | Candidate analysis primitives; no claim of calibrated modal identification or acoustic-pressure units |
| `src/signal_processing_studio/python/signal_processing_studio/signal_bus.py` | Routes signal objects among existing GUI tools | Presentation/integration reuse; keep physics and numerical analysis independent of Qt |
| `src/media_processing/audio_processor/matlab/audio_signal_processor/utils/FrequencyAnalyzer.m`, `SpectrogramGenerator.m` | Windowed spectral/peak and spectrogram facilities | Existing MATLAB implementation, not a new Python calibrated measurement pipeline |
| Same audio package: `core/{AudioLoader,FFTFilters,AntiAliasingTools,ConvolutionReverb}.m` | Audio import, filtering and signal effects | Reverb/effects alter evidence; retain raw calibrated recordings and processing provenance |
| Same audio package: `tests/test_fft_filters.m` | Existing filter tests | MATLAB execution was not performed in this inventory |
| `src/pendulum_simulator/src/double_pendulum_golf/swing_objectives/impact_optimality.py` | Impact objective in reduced swing simulation | Objective definition is not finite-duration collision or sound simulation |

No inspected path establishes a calibrated clubhead exterior acoustic solver,
measured six-axis human grip impedance, a qualified pressure-calibration wire,
or blinded player-sweetness dataset. Generic audio capabilities are present;
that is different from a validated golf vibroacoustic pipeline.

## UpstreamDrift: Engine and Research Integration

| Existing Surface | Capability and Qualification Boundary | Tests / Integration |
|---|---|---|
| `src/shared/python/physics/impact_model/{models,solver,types}.py`, `_impact_physics.py`, `_impact_recorder.py` | Existing impact solver/recorder; scalar MOI approximation explicitly documented in rigid model | `tests/unit/physics/test_impact_physics_value_assertions.py`, `test_impact_friction_axis_and_gear_offset.py`, `test_impact_dedup_and_friction_7053_7054.py`; inventory duplicate/provider seams before migration |
| `src/shared/python/physics/{flexible_shaft,_shaft_model,_shaft_fem,_shaft_data,_shaft_properties}.py` | Rigid and FE shaft interfaces, distributed EI/mass, consistent mass, cantilever BC and Rayleigh damping | `tests/unit/test_flexible_shaft.py`, `test_shaft_engine_integration.py`; this alone is not a contact-band rotating composite model |
| `scripts/research/proximal_distal_energy/shaft_beam_reference.py` | Reuses shaft FE, adds tip mass/inertia, synthetic modal identification and reduced/full comparison | `tests/research/test_shaft_beam_reference.py`; preserve numerical-reference versus equipment-calibration distinction |
| Same research root: `moving_base_modal_shaft.py`, `run_moving_base_modal_shaft_study.py` | Moving-base/two-hand model with distributed bending basis and rigid/modal coupling | `test_moving_base_modal_shaft.py`, `test_moving_base_modal_shaft_evidence.py`; synthetic properties and existing qualification envelope |
| Same research root: `articulated_shaft.py`, `articulated_shaft_forward.py`, `articulated_shaft_atlas.py` | Linearized bend/torsion elastic states and articulated comparison/evidence | `test_articulated_shaft.py`, `test_articulated_shaft_forward.py`, `test_articulated_shaft_atlas.py`; do not treat atlas as measured impact/acoustic data |
| Same research root: `articulated_forward_attribution.py`, `articulated_contact_events.py`, distributed event/attribution modules | Energy/contact bookkeeping, declared events and manufactured verification | Protected #8557/#9153 handoff boundaries; same-trajectory attribution is not a divergent causal counterfactual |
| Same research root: `two_hand_wrench.py`, `bilateral_wrench_identifiability.py`, `bilateral_wrench_sensor_qualification.py` | Existing bilateral wrench/observability and qualification program | Read governed research contracts before connecting new sensors; no inference that hardware or human data is available |
| `e1c_impact_sensitivity.py` in research root | Rescores swing trajectories under impact-event/optimality definitions | This is event-criterion sensitivity, not ball–club contact dynamics |
| `src/api`, launchers and `tests/api/test_impact_explorer_mount.py` | Existing Impact Explorer host/API integration | Thin consumer adapters and report surfaces; use reviewed Tools wheel/gitlink without modifying vendored code |
| `docs/research/proximal_distal_energy_transfer/` and root `AGENT_HANDOFF.md` | Protected publication, registration and source/data provenance | Preserve immutable outputs and frozen external campaign restrictions |

## Gaps and Ownership

The immediate missing bridge is a versioned, energy-compatible handoff of rigid
delivery **plus** elastic/prestress state into a coupled contact solver. Launch
and ringdown must share initial conditions. A measured radiation transfer and
calibrated recordings then connect structural response to sound. Only controlled
perception tests address sweetness.

Tools owns reusable laws and contracts (#5068), UpstreamDrift owns engine/study
integration (#9700), and AffineDrift owns explanation/evidence (#4253). Existing
heavy-hit GUI issues #4566/#4567 remained open in the scoped GitHub lookup even
though older handoff text called H4 completed; reconcile their acceptance state
separately rather than closing them on the strength of this inventory.
