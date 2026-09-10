# Constraint Forces: Complete Technical Review

Governing issue #4351, under #4009/#4021/#4054; also resolves the Chapter 7
caption finding in #4320. Reviewed 10 September 2026 in the technical-review
worktree, based on 18c3840c58ef1a151f7288813fd612176dcbfeff. Both complete
original editions were read (approximately 5,671 print-source and 4,657
web-source words). This audit covers the complete replacement, not a search
for isolated phrases. The remaining corpus is unfinished.

## Argument and Scope

Constraints connect geometry, compatible acceleration, reaction loads, interface
power and control authority. These relationships make golf an informative
coupled-mechanics problem. They do not establish that muscles are inactive,
that squeezing supplies no mechanical work, or that a universal sequence of
joint locks optimizes a swing. The replacement explains which measurements and
system boundaries would allow those stronger hypotheses to be tested.

The paired chapter preserves existing print labels and callout keys, all 24
historical web destinations, six exercises with worked answers, and links to
the neighboring mechanics, control and energy treatments. A shared computed
figure replaces the dimensionally incorrect force/angular-rate schematic.

## Findings and Derivation Decisions

1. **Compatibility:** Define Phi(q,t)=0, J=Phi_q, Jv+Phi_t=0 and
   Ja+gamma=0. Gamma includes the configuration Hessian, mixed derivatives and
   second time derivative. Tangent velocity does not imply tangent acceleration;
   a circular constraint supplies an independent curvature counterexample.
2. **Reaction solve:** With Ma=r+J-transpose lambda and a0=M-inverse r,
   S=J M-inverse J-transpose gives S lambda=-J a0-gamma. The original treatment
   double counted free acceleration. Independently solve the signed KKT system
   [M,-J-transpose; J,0][a;lambda]=[r;-gamma] to verify the corrected Schur result.
3. **Rank and units:** Positive definiteness of S requires positive-definite M
   and independent constraint rows. Dimension is n-rank(J), locally at a regular
   configuration. Rescaling an equation rescales its multiplier but preserves
   the generalized reaction. A multiplier is not automatically a force in N.
   Redundant constraints require an appropriate independent basis or additional
   physical modeling; an arbitrary minimum-norm multiplier is not load sharing.
4. **Projection:** Acceleration minimizes one-half (a-a0)-transpose M(a-a0)
   subject to Ja=-gamma. This is a mass-metric projection onto an affine
   acceleration set, not an ordinary projection into the velocity null space.
5. **Power:** Pc=v-transpose J-transpose lambda=-lambda-transpose Phi_t.
   Stationary ideal constraints have zero summed reaction power; moving
   boundaries need not. Full energy balance includes applied generalized power,
   reaction power and explicit potential time dependence.
6. **Physical bodies:** For coincident contact points, an internal force pair
   contributes opposite F dot v powers. Relative rotation contributes moment
   dot relative angular velocity. Coordinate blocks of one-half v-transpose Mv
   are not generally physical segment energies. Use each body's COM translation
   plus centroidal rotation and verify segment force/moment/energy balance.
   Positive power adds energy to the declared receiver; negative power removes it.
7. **Kinematic models:** q1+q2=constant fixes world orientation of link 2;
   q2=constant is a relative hinge lock. An ordinary two-link chain still has a
   connecting joint when neither extra angular restriction is imposed. A hand
   moving with the club is not a world-fixed support. Corrected the forearm
   anatomy while retaining the extensor carpi radialis brevis terminology check.
8. **Control:** Reaction depends on applied actuation, with derivative
   -S-inverse J M-inverse B. Projecting the input map can remove directions of
   instantaneous acceleration authority while increasing reaction load. Neither
   zero ideal reaction power nor constrained motion identifies muscle effort.
9. **Engagement:** For stationary perfectly plastic capture,
   Lambda=-S-inverse Jv-minus and v-plus=v-minus+M-inverse J-transpose Lambda.
   Kinetic-energy change is -one-half (Jv-minus)-transpose S-inverse(Jv-minus).
   The old incompatible incoming velocity cannot simply be inserted into smooth
   constrained equations. Impulse-free release preserves position and velocity;
   it does not automatically inject energy. Elastic or active engagement needs
   a different event model and energy budget.
10. **Wrench interpretation:** Q=J_P-transpose w at a declared point/frame/order.
    Shifting point by r changes moment to mu-r cross F and velocity to
    v+omega cross r, preserving power. Dividing generalized torque by an
    arbitrary lever length cannot recover a unique spatial joint force.
11. **Golf observations:** Distinguish local pressure, net hand force, six-axis
    wrench, internal two-hand wrench and muscle-resolved contact load. Define
    which bodies belong to the system; ground force is external to golfer plus
    club. Friction, unilateral support and center-of-pressure feasibility limit
    ideal contact. COM-force power is distinct from actual contact-point power.
    Removed unsupported force ranges and claims that high-speed video identifies
    ideal locks or that inferred reactions are independent of muscles.
12. **Testing the message:** A causal coaching argument needs declared boundary
    powers, load measures, model assumptions, uncertainty and comparable tasks.
    Mechanical coupling is a useful mechanism; a prescribed release order or
    instruction to relax/grip harder needs separate evidence.

## Reproduced Examples

`build_constraint_forces_figures.py` reuses the affine chapter's declared
two-link operators and parameters, avoiding a second incompatible model.
Run `py -3.12 -X utf8 -m docs.development.technical-review.build_constraint_forces_figures`.
The canonical JSON and shared SVG/PDF contain manufactured results, with no
golfer calibration or physiological authority.

At q=(45,70) degrees and compatible v=(8,-8) rad/s, the mass matrix is
[[0.3284453201,0.1539414100],[0.1539414100,0.13]] kg m². Velocity bias is
(4.2098229411,4.2098229411) N m and gravity vector is
(5.7841302480,1.7781758782) N m. Free acceleration is
(-19.8639077028,-22.5393912212) rad/s²; the world-orientation guide gives
(-26.6065877611,26.6065877611), with multiplier 5.3509995921 N m.
Coordinate powers are +/-42.8079967370 W; they are explicitly not body powers.
The ideal external guide moment has zero actual power because link 2 has zero
absolute angular velocity. An independent body-2 force/moment balance checks
the moving attachment's physical power and kinetic-energy derivative.

Capture from incompatible (8,12) rad/s instead gives
(11.1802620218,-11.1802620218), impulse -2.5238600429 N m s, and total kinetic
energy 34.64862561 -> 9.41002518 J: loss 25.23860043 J. Independent COM-based
body energies sum to those totals. This is not zero-work redistribution.

At 0.1 s, free angles are (83.88564444,22.75882070) degrees and guide angles
(81.73079376,33.26920624). A relative lock starting from (8,0) instead reaches
(85.34277402,70), but has a different initial energy and is not a fair equal-state
performance comparison. Energy variation is at most 1.25e-14 J and refinement
difference at most 1.07e-14 in the reported runs; tests use conservative 1e-9 bounds.

Additional checks: 100 N along 4 m/s supplies 400 W to the receiving body;
constant power for 0.01 s gives 4 J. A 2 kg, 0.7 m uniform rod at downward
vertical with 10 rad/s needs upward pivot force 89.62 N, including weight.
An illustrative 80 kg golfer-club COM accelerating upward at 2 m/s² requires
944.8 N summed vertical support (784.8 N when vertical acceleration is zero).
This is an SI calculation, not a typical golfer range.

## Primary Evidence and Reading Limits

- [Tedrake, Multi-Body Dynamics](https://underactuated.mit.edu/multibody.html):
  read the relevant manipulator, constraint and contact-mode treatment. Derived
  signs and transposes independently; source formulas are not copied as an oracle.
- [Hicks, OpenSim Joint Reactions Analysis](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53089600/Joint+Reactions+Analysis):
  read technical overview, inputs/outputs, best practices and inverse-dynamics
  distinction; page updated 14 March 2019. Its documentation supports reporting
  body/frame and actuator-representation qualifications, not a golfer load range.
- [Choi and Park (2020)](https://doi.org/10.3390/s20133672): read abstract,
  introduction, methods, results and discussion/limitations through the start
  of the conclusion in the 14-page publisher PDF. The conclusion ending and
  reference pages were not fully read. Nine professionals, instrumented split
  grip and rigid-body inverse dynamics demonstrate internal hand-load sharing.
  The 551 g instrumented club, foam balls, hand overlap and rigid-segment
  assumptions limit interpretation. No muscle-activation inference or universal
  grip-force prescription is drawn. Bibliography entries are paired and verified.

## Verification and Failures Corrected

- TDD: initial 12 numerical tests failed because the reproducer did not exist;
  final 16 cover independent KKT, curvature, scaling, impulse/energy, physical
  segment decomposition/balance, moving power, input-reaction coupling, wrench
  reference shift, trajectory convergence and paired source contracts.
- Root `py -3.12 -X utf8 -m pytest --cov`: 5,229 passed, 29 skipped,
  132 deselected, 59 warnings; configured coverage 79.29%. Final focused
  constraint/glossary/parity checks: 55 passed. Content-lint: 131 passed,
  four skipped. Static workflow contract: 34 passed; title audit: 636 sources;
  site link gate, configured mypy (91 files), focused code-quality, Ruff and Black100 pass.
- Full 542-page PDF rebuilt. Read every chapter page 108-122, following page
  123 and added bibliography entries on pages 526-527. Final citation-spacing
  change altered only pages 112/117/119 by extracted-text comparison; all three
  were rendered and reread. No final chapter layout/undefined warnings.
- Read all 27 full web captures, all sections, examples, six answers and
  references. Exhaustive inspection rendered 199 math expressions, including
  33 displays and one shared figure, over 14 viewport/theme combinations;
  204 element regions and 106 keyboard-scroll checks. All 24 historical IDs
  resolve, with no duplicate IDs, broken local fragments or unloaded figures.
- Canonical fresh browser gate independently inspected all 14 records for the
  actual chapter route: HTTP 200, no failures, one axe-scanned route with zero
  serious/critical findings. Separate exhaustive light/dark axe scans retained
  only the shared moderate landmark-unique finding. Its accumulated console
  log included four errors and twelve warnings; this is not a zero-console claim.
- First browser pass exposed seven duplicate IDs, fixed in conversion. Print
  review caught cramped/underfull numerical paragraphs and missing citation
  spaces, corrected before final reading. A source test initially matched a
  negated unsupported claim; narrowed it to the old categorical statement.
  Figure parity changed from 11 to 10 TikZ and 27 to 28 includegraphics figures,
  with web figures 28 to 29 and remaining missing parity 10 to nine.
- A disk-full scratch write was detected and rewritten completely after removing
  verified untracked old contact-sheet images. No source/publication was deleted.
  Scratch screenshots/logs and generated trust-file churn are not staged.

## Delivery Boundary

Implementation and local reading are complete; protected PR and exact live
verification remain. Keep the immutable proximal-distal publication, authority
pins and peer-owned #4253/#4255/Chapter 29 scope untouched. The branch contains
only canonical chapter sources, numerical evidence, tests and review records.

## Protected Delivery Checkpoint

Implementation 004676b40889c7dee980fefd3ebf039663f40a0c preserves validated tree d15d6f93fe09346c203f6ebe437b36711bcaf189 after replay onto affine squash 60d0298826880ca24580908127e8032565407216. Parent/squash trees matched. Normal commit/push hooks passed. Ready PR #4352 closes #4351; protected checks and exact live publication remain. Git whitespace inspection reports Matplotlib-generated SVG path-line trailing spaces; these are inert serializer formatting, not prose or rendering defects.

## Protected Merge

All protected checks passed; PR #4352 squash-merged as b5362af0005c8ae1ad00e81390e9151991157155. Exact deployment 34470677053 succeeded. All 956 records covering 239 routes in revision-matched live artifact 10150223079 were independently inspected: HTTP 200/pass, no failures, retries or axe violations. Parent head and squash share tree 2a9a8515b25be8562aaca24c86438bae93095b14. This chapter is shipped. Preserve the complete local implementation and reading evidence above.
