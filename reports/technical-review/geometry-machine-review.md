# Geometry Chapter Technical Review

Issue #4763 is a child of epic #4009 and continues corpus review #4021. The
complete Chapter 4 source and its moment-arm figure were inspected. The review
corrects nine connected arguments, with exact provider scope in
`geometry-machine-provider-evidence.json`. It does not claim a new provider
simulation, full audit of every extracted provider chapter, or human validation.

## Scientific Decisions

1. **Point, Plane and Moment Arm.** Define moment about a point without requiring
   that point to be inertial; distinguish this definition from angular-momentum
   balance. Define in-plane transverse direction separately from the plane
   normal. Collinear force has exactly zero ideal moment, but may transfer power
   or produce translation. Replace the misleading reference-to-arrow-tip dashed
   segment with the force line and its perpendicular distance from the reference.
2. **Reference and Observer.** A pure couple is reference-independent; a small
   nonzero resultant needs a bounded shift and tolerance. Transport both moment
   and rigid-body point velocity to preserve power. Component rotation differs
   from a moving physical observer, whose force power changes. Retain distributed
   force–velocity pairings when one rigid twist is insufficient.
3. **Jacobian Duality.** Explicit time-dependent kinematics adds prescribed-motion
   velocity and power. A Jacobian transpose maps an applied force into its
   generalized-force contribution, without requiring equilibrium or frictionless
   contact. Generalized speeds need not be coordinate derivatives; preserve dual
   forces and coordinate units when changing variables.
4. **Singularity Scope.** Distinguish inverse velocity amplification from force
   transmission. The independent diagonal example gives reciprocal scalings and
   exposes the force nullspace at exact rank loss. No infinite physical force,
   independent force control or universal biological non-identifiability follows.
   Instantaneous rank limits are not global path-reachability results.
5. **Inertial Response.** Same-state acceleration change depends on inverse inertia
   and applicable constraints. A positive off-diagonal mass entry can yield a
   negative cross-acceleration. Diagonalizing the example's mass matrix preserves
   the reconstructed response. Constraint reactions must change consistently with
   command; raw entries are not invariant mechanical causes.
6. **Two-Hand Controls.** Separate exact point-force couples from free moments,
   midpoint common/differential decomposition from other references, and a
   physical reversal from co-rotation or relabeling. Separation scaling assumes
   forces held fixed; dynamically recomputed reactions can change that scaling.
7. **Allocation Matching.** The provider fixes club inertia times a same-state
   control-only angular-acceleration difference at8 N m. It does not match the
   whole wrench or trajectory. The blend parameter interpolates two independently
   normalized actuator controls, not direct-moment fractions. At the wrist-only
   endpoint, opposing contact-force moments compensate direct moments above8 N m.
8. **Metrics and Optima.** Hand-force RMS is across two control-only vector norms
   at one instant, not a time RMS or total contact load. The norm of a difference
   is not a difference of norms. Torque cost is an unweighted six-command norm.
   Recompute stored extrema, closure residuals and grid minimizers; distinguish
   this restricted blend scan from all admissible allocations and human optima.
9. **Evidence and Mechanism.** Remove unsupported empirical specificity and retain
   the review citation as context. A negative force projection and geometric
   identity do not establish persistence or performance under changed reactions.
   Connect geometry to state, constraints, inertia, objectives and measurement.

## Provider and Literature Scope

Provider records are pinned to UpstreamDrift
85cce4d3307bb7ad3953d9fc6e583e370803515c. The existing published
`preload_transmission_study.npz` is byte-identical to the provider's full
allocation/preload archive; no duplicate binary is introduced. The independent
summary reproduces all seven matched-task fields exactly and records each
angle's metric-minimizing sampled blend. Original contact-force vectors are not
stored in this archive, so the review verifies the reported norm calculation in
code and the summary extrema in arrays, not a fresh force reconstruction.

The inspected allocation implementation uses minimum-norm controls in two
subspaces, zero initial velocity, and a fixed club-center position with
constraint-consistent arms at each angle. Selected functions in
`two_arm_closed_loop.py` confirm coordinate ordering, total-minus-zero-command
attribution and the contact-wrench argument meanings. The full lower-level
constrained solver was not newly audited or executed for this chapter.

Official Modern Robotics transcripts for wrenches and singularities were read.
Tedrake's multibody notes were checked for speed/coordinate mappings and bilateral
constraints. These support the declared mathematical conventions; the numerical
counterexamples are independently constructed. McPhee's review identity/scope
was previously checked, and no new detailed empirical result is attributed to it.

## Delegation and Adjudication

Supplied-text agy Gemini3.8 Flash jobs cover chapter inventory, provider chapter,
allocation code, test drafting, notation and a handoff checklist. The first combined provider/code
invocation did not start because the Windows command could not be launched;
the two smaller invocations completed. The lead rejected these draft claims:

- Force-moment definition requires a fixed/inertial origin.
- Jacobian-transpose mapping requires equilibrium or frictionless contact.
- Every kinematic Jacobian requires minimal coordinates, and nonholonomic
  constraints necessarily add explicit time dependence to the point-position map.
- A singular force direction cannot be structurally supported.
- The provider's zero contact-wrench arguments are accelerations; they are velocities.
- Coordinates0–5 are all club translations; the two-arm ordering contains four
  arm coordinates, two club-center coordinates and one club angle.
- The sweep fixes a grip origin; the code fixes the club center.
- Direct hand sensing is the only conceivable way to constrain allocation;
  additional independent information and assumptions must instead be declared.
- Roundoff closure proves all mechanistic or physiological claims, or this scan
  rules out every universal optimum. Its evidence is narrower.

The independent tests use three-component cross products, avoiding the draft's
deprecated two-component NumPy cross-product form. The initial figure regression
failed before the perpendicular-distance construction was corrected. All nine
numerical/figure checks pass. The full configured regression exits zero: 6418
passing progress symbols, 29 skips, 79.0% configured coverage and
93.0% source-only coverage. All 66 affected checks, 12 publication gates,
653 source title audits, Ruff, Black (838 files) and CI-scoped mypy (94 files) pass.
The 221-page canonical/public PDFs are byte-identical; the lead inspected every
Chapter 4 page (25–30), boundaries 24/31, and all four mobile display equations.
Four viewport/theme checks pass with zero serious/critical axe findings; all
63 mathematical expressions render without errors or page overflow.

The Flash handoff draft mislabeled the absent solver rerun and human validation
as pending acceptance tasks. They are explicit limits on the scientific claim.
Its four mobile profiles and 653 document/section titles are corrected to four
display equations and 653 source documents. Evidence binding and protected PR
delivery remain separate steps; no corpus credit is awarded before binding.

Notation review improved the applied-force system convention, unit-vector
declaration, signed observer-power shift and explicit reference point. The
lead retained the correct negative midpoint-decomposition sign and explained
its consistency with the earlier pure-pair example. Reject the draft's claim
that rounded numerical bounds conflict with “about,” its invented exact6e-15
maximum, and its labeling of all Jacobian-nullspace motion as unactuated.
No blanket radial-force-to-angular-acceleration claim was added: the full
constrained response and system boundary must be specified.
