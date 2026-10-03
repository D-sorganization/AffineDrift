# Glossary Review Preparation — Issue #4839

Status: preparation only. No source edits, claim, complete scientific acceptance, or corpus decrement. All 72 plain/technical entries and symbols in data/glossary.yml at b5d6426c3a7b64026d1c013dc6139411fcfc8b6f were read. Canonical comparisons below cover selected relevant passages, not fresh complete reviews of all linked articles. Preserve glossary keys/anchors and regenerate pages/glossary.qmd from YAML.

## Principal Connections to Preserve

The glossary must retain the distinctions already established in the long articles: a declared input is not necessarily muscle activation; a state derivative is not an integrated trajectory; available acceleration is not realized effort; a speed ratio is not an energy fraction; a task null space is not a constraint null space. A short definition must remain true when the reader follows its canonical link.

## Findings and Review Directions

- drift, affine-control-system, affine-decomposition, control-input: specify complete state and declared plant/input. Do not translate zero command into no active muscles or split whole motion into additive trajectories. Affinity is instantaneous at fixed state/mode; input choices and retained activation/impedance matter.
- drift-control-ratio: canonical capacity denominator, same acceleration space/metric, explicit regularizer; can exceed one. Not a motion proportion, achieved-input ratio, or physiological effort measurement.
- zero-torque-counterfactual: restore pointwise, stitched, forward and branched constructions. Only forward/branched are integrated trajectories. Frozen plant and retained states remain declared.
- state-space: 2n is a regular minimal second-order mechanical special case. Activation, elasticity, controller memory or hybrid mode may add state; redundant configuration representations need constraints.
- underactuation: use reduced independent mechanical acceleration/force map rank, not count of anatomical joints vs muscles or full-state dimension. Bounds and reachable sets require their own treatment.
- control-authority, reachable-set: distinguish local admissible acceleration image from finite-horizon reachability with initial state, dynamics, contact mode and state/input limits.
- constraint-force: J^T lambda is generalized reaction; lambda itself depends on constraint scaling. Workless total power requires ideal stationary constraints; prescribed moving supports can supply work. Opposite reactions can transfer power between subsystems.
- null-space: specify the matrix. Constraint kernel gives compatible instantaneous velocities; task kernel gives task-preserving velocities. Neither proves finite displacement, physical mobility at singular descriptions, or control authority.
- degrees-of-freedom, generalized-coordinates: local configuration dimension and independent regular constraints; ambient dimension is not spatial dimension times bodies. Minimal coordinates are local; redundant representations also exist.
- dynamic-coupling, induced-acceleration, equations-of-motion, forward-dynamics, inverse-dynamics: declare external loads, actuator map and compatible constraints. Off-diagonal mass entries alone do not describe all coupling. Inverse dynamics does not uniquely identify individual muscle forces or all contact reactions.
- generalized-forces, power, work: dot products, consistent points/frames, include force and couple contributions. Translational and rotational work are contributions to a common virtual-work relation, not universally interchangeable expressions.
- angular-momentum: declare origin/frame, sum particle moments; I_COM omega is rigid-body spin about COM, not arbitrary total momentum. Moment-of-inertia: scalar about an axis vs tensor about a point/frame.
- kinetic-energy, potential-energy: quadratic mass form assumes time-independent kinematics; generalized conservative force is minus coordinate gradient. Avoid mixing Cartesian F and generalized Q.
- aerodynamic-drag, aerodynamic-lift, magnus-effect: relative airflow; drag magnitude versus vector direction; lift perpendicular to airflow need not be upward; spin force coefficients depend on regime.
- clubhead-speed: current plain/technical disagree (face center vs COM). Define a declared tracked point; vendor convention can differ. Trackman uses geometric head center, not exactly COM or face center.
- coefficient-of-restitution: signed normal relative contact-point velocity, not how much absolute speed remains. smash-factor is a speed ratio, not an energy-transfer fraction.
- impact: remove universal 400 microsecond/10kN values; duration, mean/peak force depend on collision. ball-compression: distinguish static rating/test protocol from dynamic compression and restitution.
- center-of-mass: mass weighting, not weight weighting in general. center-of-pressure: planar pressure centroid with nonzero normal load, residual free couple and conditioning caveats.
- lag, wrist-cock, wrist-hinge, radial-deviation, ulnar-deviation: coaching labels are not universal anatomical coordinates. Forearm-shaft angle depends on grip and 3D configuration; deviation is not the whole release. Wrist complex includes midcarpal contribution; state anatomical convention without pretending fixed perfectly orthogonal axes.
- flexion, extension, pronation, supination: anatomical-reference descriptions, not global palm-up/down in arbitrary arm posture. Pronation/supination belongs to radioulnar articulation.
- proximal-to-distal, kinetic-chain: peak angular-speed sequence is an observation; it does not establish a torque-peak order, energy flux, or one-way transfer.
- feedback-control, feedforward-control: output/history-based feedback need not require full state/error explicitly; feedforward need not be fixed before movement or exclude simultaneous feedback.
- ideomotor-theory, motor-program: theoretical accounts, not identified neural implementation or proof of a stored open-loop sequence in golf.
- governed, provenance, protected, qualified: process definitions must not promise scientific truth, universal cryptographic verification or universal review requirements. Actual repository policies and recorded evidence control scope.
- acceleration, angular-acceleration, angular-velocity, backswing, downswing, double-pendulum, cost-function, fail-closed, ground-reaction-force, launch-angle, linear-momentum, muscle-torque, phase-portrait, spin-rate, torque, vector-field: inspect remaining scope carefully. Avoid automatic claims that all phase portraits are position-vs-speed plots, all swing phases are monotone accelerations, torque necessarily creates rotation, or vector fields require physical position space. No final unchanged verdict yet.

## Evidence Read This Session

- NOTATION.md: canonical plant, four ZTCF constructions and DCR sections, through line109.
- Relevant passages of affine-nature-golf-swing, drift-control-ratio, wrist-universal-joint (opening through180), null-space-constraint-jacobian, technology-force-measurement, impact-mechanics-and-ball-flight, ideomotor-theory-and-predictive-brain and proximal-distal-energy-transfer. Reopen exact sections before final wording; no fresh full-article audit claimed.
- Lynch/Park [Constrained Dynamics transcript](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-7-constrained-dynamics/): full transcript. Ideal equality constraints are assumed workless; projection removes reactions from acceleration-relevant torque, not all possible reaction loads. No video/full-book review.
- Lynch/Park [Configuration and Velocity Constraints transcript](https://modernrobotics.northwestern.edu/nu-gm-book-resource/2-4-configuration-and-velocity-constraints/): full transcript. Independent holonomic constraints reduce configuration dimension; nonholonomic velocity restrictions need not. No video/full-book review.
- Lynch/Park [Wrenches](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/): page opened; full transcript still to inspect in this package before relying on details.
- [Trackman club-data definitions](https://www.trackman.com/blog/club-data-definitions): 2017 manufacturer explanatory prose, especially tracked-point convention. Different head points have different velocities during rotation; the stated geometric-center convention must not be silently replaced by face center or COM. No independent instrument validation or diagram audit.
- [Trackman smash-factor page](https://www.trackman.com/blog/smash-factor): search excerpt and opening only; full main text still to read. Do not copy its informal efficiency language as a mechanical energy fraction.
- Crisco PMID21248214: search title only this session; direct page returned one line. Prior wrist article summarizes cadaver evidence, but no fresh primary abstract/full-paper inspection is claimed here.
- Tedrake multibody/intro pages: search excerpts only this session; full relevant sections still to inspect.

## Execution and Acceptance

First deliver PR4838, archive only its owned development-log entry, release its lease, then claim4839 and use an isolated topic branch. Preserve parent review evidence and all other agents' records. The 99 pending sources are the original corpus; the expanded glossary is additional. Record an entry-by-entry disposition and bounded primary sources. Test meaningful numerical counterexamples where appropriate; do not call phrase checks scientific validation. Run existing generator freshness, glossary schema/links, tooltip integration, publication gates, render/browser checks and repository regression with a fresh isolated pytest basetemp. No render during tests/hooks. Archive untracked preview and packaging scratch before hygiene checks. Use regular PRs only.

Agy Gemini3.8Flash already returned HTTP429 insufficient credits twice; four earlier screw helpers were completed/adjudicated. Do not retry repeatedly or claim new helper evidence. Lead retains conceptual review responsibility.

## Additional Integration Findings

The current /pages/glossary.html route is ad-route-39185f792b9a, marked reviewed with zero findings under 45d9fca0d0acc78791555a049042103fd6b7931d (#4588), while its source digest now covers the expanded generated page. Preserve the prior route record before accepting a new review. Bind both canonical YAML and generated page in the new evidence, not only the generated prose. Existing test_pages_glossary_qmd_exists_and_covers_all_terms checks names and anchors but does not actually compare generated definitions with YAML; its docstring promises freshness beyond its assertions. A meaningful generated-content equivalence check should catch stale definitions. This is publication integrity, not a scientific proof by text matching.

The tooltip filter reads only plain definitions for tooltips, escaping HTML; technical definitions appear in the generated page. Therefore correct both plain and technical statements. Preserve existing keys and anchors; inspect accessible rendering after regeneration. Repeated shortcode IDs may require separate review if encountered; no defect/acceptance claimed without reproducing it.

Tedrake's multibody page was subsequently opened and the manipulation/coordinate representation discussion through the opening bilateral-position-constraint setup (lines14–43) read. It explicitly distinguishes generalized speed v from qdot through N(q), and identifies B as the generalized-force input map. The remainder and full intro were not yet read. This supports representation scope, not empirical golf claims.

The reviewed Physics of Golf glossary (#4232/#4233) is a useful consistency source. Selected entries read here include acceleration, affine system/decomposition, angular acceleration/velocity, backswing, compression, COM, clubhead speed, COR, extension/flexion, feedback/feedforward, forward dynamics, generalized coordinates/force and radial deviation. Several already contain the exact scope distinctions missing from the new short glossary. Reuse the established meaning rather than inventing competing definitions; preserve the textbook's accepted text. The new site glossary's brevity still needs individual review, especially what remains visible in plain-language tooltips.

Additional Tedrake multibody reading covers bilateral-position constraints through the primal/dual discussion (lines40–55). The stated reaction solve includes the curvature term Hdot v and separate generalized-speed map. Its pseudoinverse convention is numerical and coordinate-dependent; do not borrow 'smallest force' language without a declared metric. The intro was opened at the wrong section (robot/animal motivation), so its underactuation definition remains unread in this package. Repeated PubMed opens returned empty content; stop retrying that endpoint and use an accessible primary abstract/full-text route if needed.
