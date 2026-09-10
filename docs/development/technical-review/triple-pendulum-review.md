# Triple Pendulum: Complete Dynamics and Evidence Review

## Scope and State

Issue #4345 under #4009, #4021 and Physics #4054. Both original editions were
read completely, prioritizing the approximately 5,821-word print chapter.
The paired replacement is implemented; complete print/web reading and all final
local checks pass. Protected CI, merge and live deployment remain pending. Branch `fix/4345-triple-pendulum-rigor`, stacked parent
5a58618418479fc27ec23b93f0ad3e07983858c0. Preserve peer Chapter 29/impact work,
immutable publication bytes and scientific-authority pins. Related caption
finding #4320 is included in this complete chapter scope.

## Findings and Decisions

1. The original changed between torso/arm/club and upper-arm/forearm/club while
   claiming three links were a universal minimum. Define the latter with a fixed
   shoulder and ideal planar hinges. Two-link arm/club models already include a
   wrist. Planar grip angle does not resolve anatomical wrist planes or face pose.
2. Original inertia definitions were about proximal joints, but formulas added
   the parallel-axis terms again. Define COM inertias and independent COM offsets.
   Absolute link rates are cumulative relative rates. Configuration is locally
   represented in radians; it is not globally one Euclidean angle chart.
3. Original M11 omitted I2 and I3; M22 and M12 omitted I3. Re-derive M from
   translational COM Jacobians and angular Jacobians and give all six independent
   entries with explicitly defined constants. Positive COM inertias establish SPD.
4. Original numeric M has a negative eigenvalue, approximately -0.009046 kg m².
   Its claimed inverse is not its inverse. Compute the complete specified matrix
   at both q2 and q3, its eigenvalues and inverse. Separate Mii, the free Schur
   complement and inverse response. Withdraw automatic motion and inertia rankings.
5. Original velocity bias omitted the kinetic-energy gradient. Use the complete
   Christoffel expression and verify v·c = 0.5 v·Mdot·v independently of RNEA.
   The old dM23/dq2 club-whip example is identically zero. Derive actual c3 and
   distinguish generalized force from the coupled acceleration response.
6. An ideal stationary lock has zero reaction power. Removing it without impulse
   preserves q, v and energy; acceleration changes. A compatible KKT example
   verifies the multiplier and acceleration jump. Locking an already moving joint
   is a separate impact problem. Neither operation models muscle release by fiat.
7. A pose alone specifies no stored energy. Separate an ideal lock, active holding,
   elastic stiffness and viscoelastic history. Remove unsupported anatomical angle
   ranges and 5–10 J wrist stores; give a declared spring/damper energy balance.
8. The original forward example claimed integration but used inconsistent units
   and assigned accelerations. Reuse the existing checked RNEA and GolfModel with
   a -pi/2 shift of q1 to bridge downward-vertical and horizontal conventions.
   DOP853 integration, tolerance/step refinement and energy closure are performed.
9. The corrected initial state is a counterexample to inevitable distal speedup:
   over 50 ms, absolute club rate falls 57 to 15.120 rad/s, tip speed 23.976 to
   7.924 m/s, and club kinetic energy 31.241 to 5.419 J. Relative final wrist rate
   is -33.881 rad/s; it is not the absolute club rate. No golf-calibration claim.
10. Withdraw unsupported DCR 50–100, 800–1000 Nm bias, fixed speed comparisons,
    20–30% gains and negligible wrist control. Define torque input and task Jacobian;
    separate instantaneous capacity, realized contribution, finite-time sensitivity
    and event timing. Neither a ratio nor high sensitivity proves precision.
11. Compare reduced and full models through an explicit constraint embedding,
    Mr = NᵀMN, preserving masses and kinetic energy. Extra freedom enlarges an
    optimization feasible set only if previous trajectories remain admissible under
    the same input limits. Removing a mechanical lock need not satisfy that premise.
12. Segment energy requires COM translation and absolute rotation. Internal joint
    force powers cancel globally but can transfer energy between bodies. Joint
    couple powers sum to torque times relative rate. Angular-rate peak sequencing
    is not a complete power ledger or a causal intervention.
13. A spine connection alone is serial. A second reconnecting path creates a loop.
    Both hands on a shared club require explicit loop/contact treatment.
14. All six exercises now have worked answers without leading unsupported premises.
    The malformed companion energy-transfer link is repaired. The misleading
    absolute-angle diagram is replaced with a shared reproducible vector figure.

## Primary Sources and Reading Boundaries

- Sprigings and Mackenzie (2002), *Examining the Delayed Release in the Golf Swing
  Using Computer Simulation*, DOI 10.1046/j.1460-2687.2002.00094.x. Official Wiley
  abstract and bibliographic metadata read. It models torso/arm/club, compares
  optimized strategies with torque generators, and reports an advantage from
  active wrist torque after release alongside power transfer by joint forces.
  Only abstract-level findings are used; full-paper reading is not claimed.
  https://onlinelibrary.wiley.com/doi/abs/10.1046/j.1460-2687.2002.00094.x
- Nesbit (2005), *A Three Dimensional Kinematic and Kinetic Study of the Golf Swing*,
  JSSM 4:499–519, PMID 24627665. Primary abstract, introduction and methods through
  ground-contact/model-driving details read from PMC. Subsequent targeted retrieval
  returned a CAPTCHA; no attempt to bypass it and no results-section reading claim.
  The chapter uses bounded abstract/method findings, not uninspected numeric torque
  results. Its motion-driven inverse model is not a randomized timing intervention.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3899667/
- Existing bibliography key `Sprigings2000` names a shaft-flexibility article;
  it is not silently repurposed for the wrist-torque paper surfaced in search.
  A new verified 2002 key is used. Further bibliography-wide review remains queued.
- Secondary search pages were not used as technical authority. Mathematical
  identities are derived here and independently checked in repository models.

## Reproduction and Independent Checks

Canonical reproducer:
`python -m docs.development.technical-review.build_triple_pendulum_figures`.
It imports the existing `GolfModel`, `PlanarChain` and `PlanarLink`; it does not
replace or change their production dynamics. Inputs, numeric report and shared
SVG/PDF outputs are explicit. The JSON report is a manufactured model result,
not empirical or publication-authority evidence.

The first test run failed because the reproducer did not exist and both source
editions lacked the required corrected argument (`triple-red.log`). After the
reproducer was added, an independently handwritten test constant was exposed:
I2 + m2*c2² + m3*L2² is 0.03925, not the initially entered 0.03175. Correcting
that arithmetic made the independent closed entries agree with COM assembly;
the production mechanics did not change to fit the test. Six numerical controls
then passed while the two source controls remained RED. After the paired rewrite,
all nine focused checks (including the prior relative-wrist regression) passed.

Checks cover random-configuration matrix agreement and positivity, RNEA versus
Christoffel bias, the zero false derivative, energy identity, the constrained
reaction/acceleration relation, full segment energy and converged unforced motion.
The old relative-wrist source regression was updated for explicitly defined compact
constants, preserving its physical purpose rather than the old symbol spelling.

Baseline DOP853 settings are rtol=1e-10, atol=1e-12, max_step=0.001 s; refined
settings are 1e-12, 1e-13, 0.0005 s. Both use a 501-point output grid over 0.05 s.
Initial observed energy range was 7.82e-14 J and maximum state difference 4.44e-14;
the article reports conservative verification bounds of 1e-7 J and 1e-8 per state
component. These are numerical checks of a declared rigid model, not uncertainty
estimates for human motion.

## Rendering and Delivery

The final full-book PDF has 545 pages. The entire corrected chapter, physical
pages 124–136 (printed 94–106), was visually read, together with bibliography
page 536. Final figure labels, exercise pagination and the short running title
were rechecked after polishing. No chapter overfull boxes or undefined references
remain; one harmless underfull paragraph warning remains. All original explicit
and 13 macro-generated print labels, all 20 old web section destinations and the
bibliography destination are retained. A callout heading whose ID Quarto dropped
was given an explicit anchor, then checked in the rendered DOM.

Initial direct-file Quarto rendering selected the nested book instead of the
root site. The root selected-page render revealed missing fence separators and
a corrupted table alignment delimiter from the local prose conversion. These
were corrected in canonical QMD. Final root rendering has 9 callouts, 1 table,
195 mathematical expressions and 25 displays, with no literal fence debris.
The entire web article was read in 24 overlapping captures. Additional final
figure, table and wide-equation endpoint captures were inspected after polishing.

The canonical public-site verifier passes all 14 evidence items for this one
route at seven widths in both themes; axe reports no serious/critical violations.
Separate exhaustive interaction checks pass 162 region cases (27 regions at
1440, 320 and 390 pixels in both themes) and 102 keyboard-scroll checks. Every
image loaded with alt text; no duplicate IDs or broken in-page fragments remain.
The detailed axe run also records the existing moderate landmark-unique finding;
zero findings of every severity is not claimed. The persistent browser's earlier
console history is not represented as a clean console session.

The first canonical gate invocation used an invalid axe enum; the corrected
invocation then failed solely on the obsolete Pandoc polyfill script's CSP
violation. Applying the repository's existing deployment HTML cleanup to the
local chapter output removed that script. The unchanged canonical gate then
passed 14/14. No CSP, accessibility gate or production source policy was weakened.
This is selected-route local QA, not a new full-site build claim.

The first full regression had 5,144 passes and two failures. One was the expected
figure inventory conversion from TikZ to a shared PDF/SVG; the other was a legacy
PDF-contract test that literally preserved the incomplete Christoffel expression
and the false nonzero coupling derivative. The controls now assert the corrected
equations and display delimiters. Final full regression: **5,146 passed, 29
skipped, 132 deselected; 92.88% coverage**. Final focused figure/mechanics checks:
31 passed; content lint: 131 passed; static gates: 34 passed; title audit: 636
sources passed; site-link gate passed. Ruff and Black 100 pass for all five
changed Python files. An initial broad mypy invocation rejected its excluded
scripts directory; the exact configured CI target list then passed. No production
dynamics implementation was changed.

Parent fascia/DCR PR #4344 protected-squash-merged at
0e30c134de1ae491e4fce245308983c5ef7df090. Its exact deployment 34452462094 was
still building at this checkpoint. After all local QA sessions are reaped,
replay only commits after 5a586184 onto that squash and verify tree equality.
Continue normal protected delivery and independently inspect live evidence.
The remaining corpus and companion DCR critique issue #4340 remain open.
