# Spatial Algebra, Inertia and Recursive Dynamics Review

## Current Delivery

PR #4319 merged normally on 2026-09-09 at 20:01:13Z as
c4c1fee6db8915eee49a80b3572ece9ccfe57cd5. Main CI 34398520012,
textbooks 34398520049 and performance 34398520065 pass. Deployment
34398520017 is verifying every public page; exact live evidence remains
pending. Earlier pending-merge statements below are implementation history.

Issue #4318, native child of #4009; corpus #4021. Worktree
C:/Users/diete/Repositories/AffineDrift-technical-review, branch
fix/4318-spatial-algebra starts at pending parent #4317 head
dc73460f606682abf1a7a75296c0f46f07d9f4ce. No #4318 commit or PR yet.
Codex/session technical-review-20260906 lease expires
2026-09-09T20:37:49.785553Z. Claim check was clear; filing-exemption check was
false; scoped open-issue searches found no duplicate. No subagents.

## Original Reading and Findings

Both entire originals and all fifteen print exercises are read. Indexed word
counts are 6,595 (print) and 862 (web); the old web companion omitted most of
the chapter. Original copies and the five historical heading destinations are
saved in local scratch. The following errors informed the complete paired rewrite:

- Force/motion duality needs a minus sign; the old supplied vectors give 0.65
  and -0.65, not equal values.
- The skew-square identity, energy proof, general parallel-axis expression,
  planar cross product and planar off-diagonal inertia signs conflict.
- A point mass has rank-three spatial inertia, and a thin line mass rank five;
  the positive-definiteness exercise is false. Positive-definite rotational
  matrices can still violate the physical principal-moment triangle inequalities.
- Pose direction, reporting point and axes are conflated. A wrench's moment
  already includes the force moment; its interpretation double-counted it.
  The composite routine inverted a transform against its declared direction.
- General finite-pitch twists are not zero-pitch Plucker line coordinates;
  homogeneous line coordinates have scale/sign equivalence. Pure translation,
  a pure couple and the zero vector need separate interpretation.
- Body-coordinate acceleration derivatives differ from ordinary Cartesian
  acceleration. Momentum about a moving origin needs a transport term.
- Composite locked-subtree assembly is linear-time; dense serial mass-matrix
  construction is quadratic and generic dense factorization cubic. ABA has a
  different elimination structure. A planar matrix's smaller storage does not
  establish a universal fourfold runtime speedup or planar golf dynamics.
- Dual-quaternion poses are constrained objects, not arbitrary six-dimensional
  spatial vectors. Inertia needs an operator and a pairing.

## Derivation and Implementation Decisions

Use angular-first motion and moment-first force throughout. T_AB maps point
coordinates B to A, while X_i in the tree maps parent motion to child motion.
Derive force and inertia transforms from invariant power and kinetic energy.
Particle velocity maps independently check the transformed inertia. The
spatial inertia energy is omega^T I_C omega + m|v_O - [c] omega|^2, fixing the
coupling signs and the exact positive-definiteness hypothesis.

Reuse src.affine_control.dynamics, screw_examples.adjoint and PreparedTree.
The new src/tools/spatial_inertia_examples.py adds only frame re-expression,
composite assembly and joint-matrix construction. It does not duplicate the
existing spatial primitives or purport to solve contact. The existing inertia
function's docstring now states physical input preconditions and permits
semidefinite idealizations; numerical behavior is unchanged.

Checks compare CRBA with independently propagated body Jacobians on a branched
tree with distinct rotations/offsets, and with direct center-of-mass velocities
for the two-link example. The declared geometry L1=0.6 m produces M11=0.6175+
0.3 cos(q2), M12=0.0675+0.15 cos(q2), M22=0.0675 in kg m^2. Rates (1,-2) at
q2=0 give 0.15875 J. The pressure-independent constraint example gives reduced
inertia 5, physical acceleration (0.2,-0.2), multiplier -0.6 and zero reaction
power. Coordinate scaling preserves that physical acceleration.

The chapter adds fifteen worked answers, two paired PDF/SVG figures and a
short shared-code example. Print labels and five old web destinations are
preserved. The draft and conversion scripts are scratch; stage canonical
chapter sources, shared implementation, tests and figure generator explicitly.

## Primary Reading Boundaries

The public Featherstone v1 documentation was read for transformation rules,
motion/force cross products, body inertia, fixed-base tree contracts and
forward/inverse algorithm roles. Complete crmp, mcIp, mcI and HandC source
listings were read through their linked sourceText pages. This is a declared
historical companion version; v2 differs in external-force and gravity APIs.
The attempted guessed v2/source URLs failed and were not used as evidence.

- https://royfeatherstone.org/spatial/v1/documentation.html
- https://royfeatherstone.org/spatial/v1/sourceText/crmp.txt
- https://royfeatherstone.org/spatial/v1/sourceText/mcIp.txt
- https://royfeatherstone.org/spatial/v1/sourceText/mcI.txt
- https://royfeatherstone.org/spatial/v1/sourceText/HandC.txt

The complete official Modern Robotics wrench transcript was read at
https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/.
The Featherstone seminar PDF was opened for extracted overview only; its
figures/full slide set were not visually reviewed and it is not added as a
chapter source. Featherstone's, Lynch/Park's and Murray/Li/Sastry's books remain
broader further-reading references; this batch does not claim full rereading.
The chapter's numerical examples and energy arguments are independently derived.

## Completed Local Validation

The full regression passed 5,050 tests with 29 skips, 131 deselections and
79.14% coverage (75% required). The final affected checks passed 37 tests;
content lint passed 130 with four skips; all 34 static contracts and 634
source-title checks passed. Ruff, Black (682 configured files plus the figure
generator), the tracked-file quality gate and mypy (89 source files) passed.
The two published 26-line programs are byte-identical after extraction and
execute both the mass-matrix and 0.15875 J assertions successfully.

The complete final chapter, physical pages 138–150 (printed 124–136), was
visually read in the 232-page volume. All fifteen exercises and worked answers,
both figures and all 26 displays are readable. Final chapter build logs have
no overfull boxes or undefined references. Physical 1–15 and 225–232 were
visually inspected for navigation, index and bibliography layout. Three long
headings have controlled print breaks, the listing uses the existing readable
color overrides, and the energy annotation is clear of both curves.

The complete web chapter was visually read in 22 overlapping desktop captures.
Final browser checks pass 287 math expressions, 26 displays, five historical
destinations, fourteen width/theme cases, loaded accessible figures and no
broken internal fragments or duplicate IDs. Both themes have zero serious or
critical axe findings; the existing moderate landmark-unique finding remains.
Twenty-nine overflowing inline groups were checked at both ends in both themes
and by keyboard. All sixteen overflowing display/figure right edges and eight
critical dark-theme displays were visually inspected. The code's horizontal
ends and keyboard scrolling pass in both themes. Both lists contain exactly
fifteen direct numbered items. The final reference paragraph retains the book
title that raw LaTeX emphasis had initially dropped in the web conversion.

Initial RED and layout failures were genuine intermediate findings, not final
passes: two test-fixture mistakes were corrected before the meaningful RED;
the first print build had row-spacing/label syntax errors and two later text
overflows; the first browser run found two short unwrapped calculations.
Each has been resolved. Tests regenerated unrelated dated trust summaries;
those outputs were inspected and restored rather than included in this change.

A separate volume-wide follow-up remains: the existing nomenclature on printed
page xii overflows at the DCR definition, and its blanket positive-definite
mass-matrix wording needs qualification. This source remains Indexed in the
corpus ledger with those findings recorded. Pre-existing duplicate figure PDF
destinations and other chapter overflows belong to the whole-volume consistency
pass; this chapter's clean log is not a claim that the entire volume is clean.

## Parent Publication Evidence

Synthesis #4313/#4314 is published as fc76f2e1d214fd66101e616ae94fce6d31d6af26.
Main CI 34388745153, textbook compilation 34388745237, performance 34388745123
and deployment 34388745225 passed. Exact live artifact 10119982807 was downloaded
and read: 956/956 evidence records, 239 routes, zero failures, serious/critical
axe findings, retries, transients or exhausted retries. The local evidence is
synthesis-live-fc76f2e1/live-every-page.json. A separate contributor's apt repair
was preserved; no protection was bypassed.

Soft-tissue #4315/#4317 merged normally at 2026-09-09T19:06:05Z as
b657813291e89def6269d9bb0f258a9e26c3dd8a. Main textbook 34393037136 and
performance 34393037120 pass; CI 34393037135 and deployment 34393037121 remain
running at this checkpoint. Replay only #4318 after dc73460f onto protected
main before first push. Keep the corpus epic open; remaining sources need review.

## Protected Delivery Checkpoint

Implementation 36159f73 was replayed alone after dc73460f onto protected
main b6578132 before first push, producing 245926b2c107d560be1f64d5df56954204053e50.
The parent trees were identical and no reviewed content changed. An empty
AGENT_HANDOFF index-stat difference initially prevented rebase; refreshing the
index cleared it without discarding content. SVG trailing whitespace was
normalized before the commit, with token-identical geometry preserved. All
normal commit and push hooks, including mypy, bandit and pytest, passed.

Ready PR #4319: https://github.com/D-sorganization/AffineDrift/pull/4319.
The actual PR has one SPEC change-log row. Protected checks/review, normal
merge and exact live verification remain; no corpus completion is claimed.
