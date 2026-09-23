# Zero-Torque Review Preparation — #4427

## Scope and Status

Read both complete Chapter 6 sources and the standalone canonical article,
including exercises and the normative intervention contract. Read the complete
registered adapter, fixture v2 and intervention tests. This work is a native
child of Physics #4054, with standalone scope under #4058 and corpus #4021/4009.
Lease receipt 5785442576 expires 2026-09-23 00:42 UTC. Branch
`fix/zero-torque-counterfactual-rigor` starts at IAA head 03db46ff.

All three sources are rewritten. Ten independent mathematical checks passed
before editing; the published-value regression failed against the old chapter.
After correction, all eleven new checks and twelve existing contract checks
pass. Print/web rendering, complete visual review, link/anchor review and final
source/evidence binding remain pending. This checkpoint is not acceptance.

## Findings and Reasoning

The old print and web mass matrices disagree and both mix pivot/COM inertias.
Velocity bias drops a factor-two cross term, the distal squared-rate term and
the entire second component. Gravity uses the wrong cosine for 115 degrees and
omits a proximal contribution numerically. The final acceleration solve changes
the sign of the velocity term. Inverse recovery uses only diagonal mass entries.
The invented torque schematic contradicts the article's own force convention;
it is removed, not treated as measured or computed evidence.

The replacement derives inertia from Cartesian COM kinetic energy and gravity
from potential energy for two uniform rods. At q=(45,70) degrees, v=(8,12) rad/s,
M=[[0.15287515,0.01010424],[0.01010424,0.006]], hv=(-3.78884065,0.72168393),
hg=(3.20524786,-0.12437655). Thus a0=(11.69948358,-119.25363140) rad/s².
For ar=(2,8), the complete coupled solve recovers u=(-0.19700856,0.66551586) N·m.
The test independently assembles M with COM Jacobians, differentiates it to
check Euler–Lagrange bias, and differentiates V to check gravity. These numbers
are analytical mechanics illustrations, not a registered two-link ZTCF rollout.

For second-coordinate acceleration and input bounds (2,0.2) N·m, the exact
box support value is 62.29919587 rad/s²; DCR=1.914208197. Uniformly doubling
rates quadruples hv but not gravity, so the ratio becomes 10.69329167, not
four times the original. No measured late-swing phase or muscle bound is claimed.
Direction and horizon counterexamples separate DCR from correction authority.

Same-state subtraction holds at every common state. Branch acceleration
differences also include changed drift after state separation. The standalone
100-minus-85 illustration is valid only for a component of inertial generalized
load Ma, not when 100 is already an inverse-dynamics input. ZVCF is a distinct
velocity reset with explicit internal-state and constraint feasibility, not
universally gravity-only. Large acceleration alone does not imply stiffness.
Force plates measure ground contact; grip loads need another instrument or
inference. EMG is electrical activity, not a direct muscle-force measurement.

## Source and Authority Boundaries

- Existing Lynch2017 and Featherstone2008 bibliography entries are unchanged.
  Northwestern's official Chapter 8 overview was inspected for the standard
  mass/velocity/potential structure. The attempted individual video page was
  inaccessible. No claim of newly reading the entire textbook is made.
- SUNDIALS v6.0.0 CVODE mathematical documentation, section 4.2, was read at
  https://sundials.readthedocs.io/en/v6.0.0/cvode/Mathematics_link.html.
  Its stiffness explanation informs the short numerical distinction; this is
  not a new CVODE execution or parity claim.
- The original Nesbit/MacKenzie citations did not establish the specific
  general assertion about isolating passive forces; that unsupported assertion
  and empirical torque ranges are removed. No new human experiment is claimed.
- The exact rigid v2 fixture, schema, model and adapter are unchanged. No
  two-link adapter, flexible state or second-engine capability is added.

## Delivery Dependencies

Putting #4424 is shipped at ded63640. Deployment35792227837 and live
artifact10722988337 pass960/960, including four putting cases; publication
receipt is committed with this successor work. IAA #4426 has protected
auto-merge enabled after putting publication; its new head03db46ff corrects
only a test constant and binds evidence to9981bddf. Source/render bytes remain
06c948b7. Verify IAA's main deployment before merging this successor.

## Next Action

Build the isolated Chapter 6 PDF with the real preamble and both public HTML
routes, inspect all equations and pages, and finish the adversarial review.
Then bind findings to a committed source/render checkpoint and open a regular
PR. Keep the goal active. Local disk headroom is approximately120 MB and can
fall due concurrent external activity; do not start a full-book local build.
