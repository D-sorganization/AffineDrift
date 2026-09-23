# Force and Mobility: Technical Review — #4436

## Scope and Argument

Read the complete public article, its algorithm, critics' responses, lay
summaries, scope statement, related-link annotations and bibliography companion.
The legacy converter names a missing Force_Mobility_Matrices.tex file; the
extant QMD is authoritative for this correction. No paired print edition was
found. This full review supersedes the limited September 13 route review under
#4058. The work belongs to corpus #4021 and epic #4009.

The argument now connects task geometry, declared rate/load budgets, inertia,
constraints, constitutive response and finite-time outcomes without using one
quantity as evidence for another. It retains the golf investigation's focus on
configuration-dependent mechanics while separating algebraic consequences from
unmeasured physiological capacities or recommended swing strategies.

## Corrected Findings

1. **P1 — Mapping and Units:** A Jacobian maps rates, not forces to motion.
   Spatial velocities and wrenches require matched frames and reference points;
   local orientation derivatives are not automatically angular velocities.
   Task normalization transforms forces dually and preserves power.
2. **P1 — Conditional Reciprocity:** Derive the weighted rate image and load
   preimage. Reciprocal radii require dual normalized budgets. Independent
   capacity metrics can give large radii in the same direction. Baseline loads
   shift the admissible set; box, friction and unilateral limits are different
   feasible sets. A force ellipsoid is not a structural-strength certificate.
3. **P1 — Singular Geometry:** An unbounded force preimage means the ideal
   generalized-load budget supplies no bound in that direction. It does not
   require infinite force, certify infinite capacity or imply instability.
   Second-order axial motion at an extended two-link posture is compatible
   with zero instantaneous axial velocity authority.
4. **P1 — Dynamics and Compliance:** Acceleration uses inverse inertia and
   velocity bias. A constrained impulse uses the constrained inverse inertia;
   task inertia retains internal dynamics. Joint stiffness, preload and contact
   compliance require separate constitutive models. Force capability does not
   establish impact duration, restitution, dissipation or passive stability.
5. **P1 — Closed Chains and Human Interpretation:** Closure alone does not
   prove redundant constraints. Allowable rates, constraint reactions and
   grasp internal forces use different maps. Co-contraction cannot change a
   fixed Jacobian/load-metric quadratic form. The lay text and critics now
   reflect these limits; unsupported elite-posture and speed/strength claims
   and an unverified video attribution were removed.
6. **P2 — Algorithm and Bibliography:** The SVD example includes all ambient
   task directions for tall matrices, validates input and exposes its relative
   rank tolerance. The companion distinguishes inspected sources from reading
   candidates, restores Monika Serrano's authorship and removes two impossible
   outgoing citation edges from earlier papers to later books.

## Independent Numerical Checks

The initial executable-example run reproduced four failures: incomplete task
bases for tall and zero matrices, unsupported relative tolerance, and accepted
empty input. The corrected example and independent mechanics are checked in
tests/test_force_mobility_rigor.py; the planar-scope contract remains intact.

- Finite differences of two-link Cartesian position give singular values
  1.86405738 and 0.50000558 at angles (0.3, 1.2), with reciprocal force radii
  0.53646417 and 1.9999777 for the article's specified unit budgets.
- A pseudoinverse inequality alone admits an impossible velocity outside the
  map's range; a separate range condition is necessary.
- The weighted support direction saturates both dual budgets and their unit
  normalized power pairing. Rescaling task coordinates preserves power only
  with the dual force transformation.
- J = diag(2, 1) with independent load weight diag(0.01, 1) gives force radii
  (5, 1), not reciprocal velocity radii. A scalar bias shifts the interval
  from [-1.5, 1.5] to [-2, 1].
- The same J with M = diag(100, 0.25) gives input-to-acceleration gains
  (0.02, 4), reversing the kinematic preference. Changing joint stiffness
  instead changes compliance while leaving the chosen force ellipsoid fixed.
- For masses diag(2, 3) constrained to equal velocity, the projected impulse
  response matches the augmented constraint equations. Effective mass in the
  first direction becomes 5, compared with the unconstrained value 2.
- Finite differences verify axial acceleration -2 for the prescribed extended
  linkage motion and tangent stiffness 4 for the loaded scalar spring.

These are declared algebraic or ideal-mechanics examples. None represents a
human measurement, identified golfer model, tissue limit or physical experiment.

## Primary-Source Access and Limits

Read the publisher's Modern Robotics transcripts for
[statics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-2-statics-of-open-chains/),
[manipulability](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-4-manipulability/),
[task-space dynamics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-6-dynamics-in-the-task-space/)
and [constrained dynamics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-7-constrained-dynamics/).
The task-space transcript assumes a square invertible Jacobian. The article's
rectangular, weighted, singular and compliance extensions are explicit
derivations supported by the independent checks, not claims about that video's
scope. No video playback or complete textbook review is claimed.

The [NumPy SVD reference](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)
documents the full/reduced shapes independently exercised by the tests.
The [JSSM record](https://www.jssm.org/hfabst.php?id=jssm-04-520.xml) was consulted
for Nesbit and Serrano's metadata and abstract only. Other companion entries
remain reading candidates; no uninspected reference-list edges are asserted.

## Verification and Publication Boundary

The source and render report are frozen together before the route's reviewed
status is rebound to their exact commit and hashes. Browser evidence records
mobile/desktop, both themes, all math, keyboard-expanded summaries and axe
checks. The first raw render exposed the existing legacy-polyfill CSP failure;
the production check uses the repository's existing deployment sanitizer.
The initial mobile displays were too small, so a page-local stylesheet retains
reading-size equations with horizontal scrolling. No global style is changed.
The legacy summary controls changed their ARIA state without exposing the text.
Both wrappers now use the site's existing native details/summary pattern;
their corrected prose is retained and keyboard visibility is checked again.

The broader corpus remains unfinished. At the user's request this is the last
current development item: validate, publish through a regular protected PR,
verify exact remote main, save the turnover, then pause without selecting work.
