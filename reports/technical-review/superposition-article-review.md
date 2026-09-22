# Superposition Reference Article: Complete Reread and Remaining Corrections

## Scope

Issue [#4418](https://github.com/D-sorganization/AffineDrift/issues/4418) is a
child of foundations #4058, within corpus #4021 and epic #4009. The complete
standalone `articles/superposition.qmd` was read sequentially, including the
abstract, all three formulations, examples, modeling discussion, conclusions,
references and related links. This is distinct from the paired textbook chapter
reviewed under #4227. The earlier article corrections are retained and are not
represented as new findings in this pass. The resulting source has approximately
8,223 word-like tokens, including mathematical notation.

## Findings and Technical Decisions

1. **P1 — Algebraic versus feasible inputs.** The all-real-input affine identity
   does not imply that allowed inputs form a vector space. State-dependent
   capacity and contact conditions may exclude sums, negatives and zero. A
   feasible reference gives the exact difference `G(u-u_star)` and attainable
   set `G(U-u_star)`. The scalar example with `a=3+2u` and `U=[1,2]` distinguishes
   allowed acceleration `[5,7]`, reference increments `[-1,1]`, and an infeasible
   formal zero-input baseline. This is a mathematical example, not a golfer's
   torque envelope.
2. **P1 — Constraints and task authority.** Derive the constrained inverse-mass
   map from the regular bilateral KKT equations. For `A=J M^-1 J^T`, the map
   `W=M^-1-M^-1 J^T A^-1 J M^-1` annihilates reaction covectors, and `J W=0`.
   Curvature remains in total acceleration through `-M^-1 J^T A^-1 gamma`.
   Same-state acceleration differences are tangent to the constraint; total
   acceleration need not be. The two-kilogram circular-guide example gives
   inward acceleration9 m/s² at speed3 m/s and radius1 m. Radial force changes
   reaction, while tangential force changes tangential acceleration. Specify
   independent constraint rows, moving-support and impact boundaries, and the
   extra feasibility conditions needed for unilateral/frictional contact.
3. **P2 — State, mechanical and task maps.** The previous authority summary
   called `G U` acceleration increments, although `G` acts on the full state
   derivative. Distinguish its mechanical block `H`, the task map `J_y H`, and
   the common task bias. Replace the incorrect related-link claim that
   constraint forces absorb hidden velocity components with the admissible
   velocity/reaction-covector distinction. The virtual-work statement uses
   virtual displacements, not an unidentified component of actual velocity.
4. **P2 — Equation presentation.** Three existing groups exceeded the desktop
   text column; two multiline derivations also produced stray automatic
   equation numbers. Use aligned groups with the original (3.15), (4.14) and
   (4.15) tags, and declare the suppressed argument dependence. Desktop
   displays now fit. Wide mobile expressions retain the site's horizontal
   scrolling rather than being claimed to fit without scrolling.

The physical explanation remains one of conditional transmission: state,
geometry, force bounds and active contacts determine the instantaneous effect
of an input on a chosen task. This does not identify unique muscle forces,
physiological effort or finite-outcome causal shares. Earlier trajectory,
coordinate, input-convention and activation-state qualifications remain intact.

## Independent Mechanics and Sources

Eleven article checks pass. Existing cases cover affine baseline subtraction,
body-frame velocity transport, spatial-inertia energy and the uniform-rod
mass matrix. Added cases cover feasible-reference bounds, three direct KKT
solutions for the circular guide, an independently solved coupled KKT system
versus the Schur expression, reaction annihilation and task-bias cancellation.
The general two-link example is checked using unequal COM offsets and inertias:
Cartesian center accelerations and separate body force/moment balances recover
both torques from the printed manipulator equations. Kinetic energy and the
potential-energy rate independently agree with the generalized expressions.
These are model-identity checks, not human-outcome validation.

Primary material checked for this reread:

- [Featherstone spatial-vector reference](https://royfeatherstone.org/spatial/v2/),
  including the linked `mcI` and `crf` implementations, for inertia signs,
  angular-first conventions and the force cross-product operator.
- [Modern Robotics, constrained dynamics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-7-constrained-dynamics/),
  for workless reaction covectors and elimination of multipliers. The article
  independently derives the acceleration form and states its regularity limits.
- [OpenSim activation dynamics](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090590),
  for excitation versus activation and model-dependent time constants/bounds.
  The article's constant-time-constant law remains an explicitly simplified
  example, not a claim that all OpenSim muscle models share that law.
- [Hutchinson's author page](https://faculty.cc.gatech.edu/~seth/SHV/) confirms
  the retained 2005 publication year for _Robot Modeling and Control_; no
  bibliography change was justified merely by other listings using2006.

## Rendering, Evidence and Limits

The root-configuration Quarto render and public-site verifier pass all four
viewport/theme cases with zero serious/critical axe violations. Settled full-page
scrolling renders416/416 expressions in each case with no MathJax errors,
lazy placeholders, broken local anchors or page overflow. Visual inspection
covers all13 main-section opening views on mobile, the two new sections in
selected desktop/mobile and light/dark views, and the changed equation/task-map
views. This is not a claim of pixel-by-pixel review of every viewport position.

No desktop display exceeds its parent. Twenty-one mobile display groups are
wider than their text column; every corresponding overflow container was tested
at390 px/dark and reached its horizontal endpoint. An initial immediate read of
smooth scrolling returned zero; the definitive test used instantaneous scrolling
and verified the full displacement. The saved JSON distinguishes scrollability
from fitting without scroll.

Black100, Ruff, the changed-test quality checker, the638-source title audit and
29 article/inventory checks pass. Source and test bytes must match the committed
checkpoint before final review binding. Protected merge and live publication
remain separate gates. No new whole-book or corpus acceptance is asserted.
