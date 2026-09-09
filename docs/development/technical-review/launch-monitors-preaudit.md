# Launch Monitor Technology: Complete Reading and Next Audit

Historical preparation record. Authentication subsequently recovered, issue
#4309 was created and leased, and the complete canonical manuscript was rewritten.
Use [launch-monitors-review.md](launch-monitors-review.md) for current derivations,
validation and delivery status; the initial constraints below are historical.

Read the full `articles/technology-launch-monitors.qmd` on September 9, 2026,
including all equations, tables, references and related-concept links. No
canonical edits or new issue yet: GitHub authentication currently fails and
the required claim cannot be verified. This is independent read-only preparation
while #4307 finishes local validation.

## Priority Findings to Derive and Source

- Single monostatic radar twist observability is structurally constrained, not
  just weakly conditioned by a small aperture. For sensor s, reference O,
  point p and u=(p-s)/distance, r=p-O gives
  `r cross u=(s-O) cross u`. Each Doppler row depends only on
  `v_O+omega cross (s-O)`. One instantaneous sensor's six-column twist matrix
  therefore has rank at most three, regardless of the number of spatially
  resolved scatterers. The null family has `delta v_O=delta omega cross (O-s)`.
  Verify independently with an SVD and zero-radial-velocity construction.
  Multiple receivers/physical baselines, bistatic paths, tracked point motion
  and temporal assumptions require their own observation models. Smoothing
  cannot be said automatically to resolve all missing information.
- The anchor formula `R0 exp(integral omega-hat dt)` is false for general
  time-varying axes. Declare body/spatial angular velocity and solve its
  corresponding left/right matrix ODE or ordered product. A face normal alone
  is not full pose. Correlated anchor/rate errors, bias and event-time error
  belong in propagation. A late anchor is not automatically most informative.
- A twist's ISA is not a uniquely defined swing plane. Pure translation has
  zero angular velocity and no finite axis; rest is another degeneracy. Chasles'
  finite displacement and the instantaneous twist must be distinguished.
- Face-center velocity need not be leftward and shallower for every motion.
  Translational curved trajectory and head angular velocity are not the same
  object. The claimed swing-arc and shaft-closure contributions risk counting
  an assumed rotation twice. Use declared vectors and point transport, test
  opposite signs and pure translation; retain vendor examples as conditional.
- CG and geometric center are distinct; the modality-wide split, 6 mm claim,
  7 mph toe/heel difference and universal 3-degree comparison need evidence.
  Reference event and actual contact location matter. A 3-degree convention
  difference does not establish a slice, an intercept correction or a learned
  compensation in all commercial systems.
- All radar face-angle algorithms cannot be asserted to be D-plane inversion
  from public vendor definitions. A hidden face can be reconstructed from a
  known head's visible geometry; invisibility is not an identifiability proof.
  If analyzing an inverse model, label it conditional and propagate its actual
  variables. `1/.76` versus `1/.85` is about a 12% relative amplification increase,
  not twice the sensitivity; bias in path and coefficient must also enter.
- Reuse the fully read Wood/Henrikson source boundaries from #4307: filtered
  horizontal sample sizes, CI rather than shot SD, separate vertical projection,
  reused data, friction and obliquity limitations, no sole-study or universal
  monotonic-curve claim. No automatic inference from spin error to launch-angle
  inversion without an actual algorithm.
- A radar feature's micro-Doppler amplitude depends on rotation axis, feature
  radius and sightline geometry. Spectral harmonics may not uniquely identify
  the fundamental spin frequency under symmetry, short observation or weak
  scattering. Source actual patents, avoid unverified legal status/litigation.
- Track inversion using lift-axis orthogonality alone needs rank, sign and
  magnitude analysis, aerodynamic assumptions, air-relative velocity and
  differentiation uncertainty. Indoor versus outdoor is not a binary divide
  between measurement and inference.
- SO(3) eigenvector sign, near-zero/pi rotation and inter-frame aliasing must be
  addressed. Texture ambiguity, camera calibration and timing enter spin
  reconstruction; it is not universally markerless or restricted to 30 cm.
- Two parallel grooves yield one vanishing direction; they do not generally
  identify a complete plane normal without additional metric/calibration/pose
  information. Deflectometry needs reflection geometry, calibrated illumination,
  surface correspondences and often shape-distance information; it has a model.
  Specular flashes depend on beam geometry, finite surface and alternative
  glints, and supply at best conditional normal constraints rather than full
  pose. Passive tags/ISAR/IMUs require observable states and mounting/calibration.
- The methods table labels several proposals Novel despite no prior-art search.
  Replace unsupported novelty and commercial-performance labels with evidence
  status. Regularization is a prior, not sensor information. Unscaled singular
  values mix translation and rotation units and can mislead sensor design.
- The force-plate/wrench and motion-capture/twist analogy needs calibration,
  processing and point definitions. Rigidity through impact is an approximation,
  not a universal 500-microsecond switch. Near-hand ISA priors are hypotheses.
  The heavy-hit link currently asserts muscle effort cannot act during impact,
  conflicting with the reviewed continuing-force/contact treatment.
- Source chronology, current hardware specifications and patent status must be
  rechecked. The unlinked long-form companion and 'behind every trajectory model'
  Bearman claim need correction or substantiation. Preserve existing useful
  hypotheses and explain how a discriminating experiment could test them.

## Next Steps

Independent NumPy/SciPy calculations now verify instantaneous Doppler matrix
ranks 3, 5 and 6 for the declared one-, two- and three-sensor examples. The
single-sensor null-family residual is 5.6e-17. The two-sensor null rotation lies
along their baseline; the third noncollinear sensor removes it in this example.
These are ideal separate monostatic observations, not a claim that an arbitrary
commercial receiver array has that observation model. Known body-feature
positions and their range/angle associations can themselves supply pose
information; the nullspace result concerns the Doppler equations alone.

A 60-degree spatial x rotation followed by 45 degrees about y differs from
the exponential of the summed rotation vectors by 22.50047 degrees. A 270-degree
interframe z rotation has the same rotation matrix as the principal -90-degree
rotation, exhibiting temporal aliasing. Point transport with reversed angular
velocity reverses both directional changes. The inverse launch gains are
1.31579 and 1.17647, a ratio of 1.11842. Reproducible scratch calculations and
results are `launch_monitor_counterexamples.py` and
`launch-monitor-counterexamples.json`; retain their stated assumptions.

Initial primary-patent reading: the descriptions of
[US8845442B2](https://patents.google.com/patent/US8845442B2/en) discuss harmonic
spin-frequency extraction and aerodynamic trajectory inference. The inspected
passages of [US10850179B2](https://patents.google.com/patent/US10850179B2/en)
instead use receiver phase differences for angular positions of Doppler
components, with explicit resolution requirements. This is a disclosed
alternative to curvature-only inference, not proof of a particular product's
implementation or accuracy. Reading is partial so far; legal status and
litigation outcomes have not been verified. The Murray book landing page initially
failed to open; its working author archive now confirms the PDF was withdrawn
from public distribution in 2020. Use the author's accessible chapter summaries
or an independently accessible primary kinematics source rather than assuming
the old download still works.

Further technical reading on September 9 covered US8845442B2's trajectory
projection and homogeneous axis equations (10–22), and US10850179B2's
phase/angle relation, resolution requirement and four proposed ways to recover
the remaining spin component (description paragraphs corresponding to web
lines 374–460). The latter distinguishes the line-of-sight transverse projection
from the full axis. Nonparallel views, another measurement or a stated prior
are needed to complete that determination. Patent disclosure establishes a
method's description, not its independent validation or use in a named product.
Do not claim a complete patent/legal review; the claims and legal history
have not been reviewed in full.

Independent derivation to retain: with a declared Magnus model
`L = k (omega cross v_air)`, `k > 0`, one instant determines only the
component perpendicular to air velocity. In particular,
`omega_perp = (v_air cross L)/(k |v_air|^2)` and adding any multiple of
`v_air` leaves the modeled lift unchanged. If total spin magnitude is separately
known, the remaining parallel component can still have two signs. A sequence
of nonparallel lift vectors can identify an unsigned constant axis through
a rank-two homogeneous system, whereas parallel lift vectors cannot. Resolve
sign with the stated force law and assess conditioning and uncertainty;
normalizing an arbitrary homogeneous solution does not supply that information.

Restore GitHub authentication, check exemptions/claims and create a focused child
of #4009/#4021 before canonical edits. Check existing vendor-reference and
screw/rotation chapter reviews to reuse verified mathematics and source scope.
Build independent numerical counterexamples for radar nullspace, noncommuting
integration, point-transport signs, spin aliasing and inversion uncertainty.
Then rewrite the complete article with an explicit estimation and validation
programme, retaining useful cross-links and historical anchors.
