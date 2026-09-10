# Flexible Shaft: Paired Technical Review

Issue #4333 is a native child of #4009; corpus #4021 and Physics #4054 remain
unfinished. Branch fix/4333-flexible-shaft-rigor starts at muscle delivery
3bbd540408133dd142625be27386d9e107e06f8f. PR not created. Complete original
print (indexed 6,049 words) and web editions, including all six exercises, read.

The scoped title search found only peer impact epic #4253, whose impact/acoustic
synthesis and joint-friction chapter are excluded. Issue filing exemption is
false. Claim was free; lease comment 5611874462 expires 2026-09-10T04:45:16Z.
Presence comment 5611878716 expires 04:45:52Z. Immutable publication is excluded.
No subagents and no Git mutation during tests, rendering or visual QA.

## Confirmed Findings

- Passive elastic/damping forces are confused with an unactuated acceleration: the chapter says shaft dynamics belong entirely in drift and run on autopilot despite ongoing hand/joint actuation. The coupled mass matrix and precise input channel are missing. The fifth state derivative is incorrectly equated to the fifth state rather than the sixth.
- Beam assumptions, boundary conditions, moving-grip forcing, mode normalization and convergence are underspecified. Modal forcing is called force in a mass-normalized acceleration equation. A clamped-free bare beam is treated as an exact loaded grip/shaft/head model.
- The worked example's 7000 N/m stiffness, 15 rad/s frequency, effective mass and approximately 0.3 N s/m damping are mutually inconsistent. The prescribed sinusoidal grip has maximum deceleration at the claimed start of deceleration; its hand-authored plotted values do not reproduce the stated function or a solved ODE. Prescribed grip motion is mislabeled as a zero-input counterfactual.
- Elastic storage and release are conflated; lower stiffness is incorrectly said to store more energy at the same bend in print and an exercise. Constant-force and constant-displacement comparisons give opposite stiffness dependence. The energy balance omits other kinetic/gravitational changes and initial elastic state; isometric contraction is treated as stored potential energy.
- Axial/centripetal acceleration is conflated with transverse bending and universal centrifugal stiffening. Gravity is said to increase during the downswing. Prestress energy, parameter variation and power exchange are omitted.
- Claims of inevitable shaft lag at impact, optimal snapback timing, universal slow-golfer benefit, frequency-rating equivalence and 5–15% (print) versus 1–5% (web) extra speed exceed the specified evidence. Deterministic motion, sensitivity and shot dispersion are interchanged.
- Print/web figures and qualifications differ; six exercises include a false premise, an ambiguous decay/envelope question and underdetermined fitting conclusions.


## Primary Source Review

- [MacKenzie and Sprigings (2009), shaft stiffness](https://people.stfx.ca/smackenz/Publications/MacKenzie%202009%20Understanding%20the%20role%20of%20shaft%20stiffness%20in%20the%20golf%20swing.pdf):
  full primary prose from abstract through methods, results, discussion and
  conclusion read. Table 2 and Figures 5--7 visually checked on PDF page 5. Four torque
  generators, three flexible-shaft fits and a rigid comparison; stiffness fit
  to static loading, damping chosen for agreement. Kick velocity and the
  difference between complete flexible/rigid simulations are different quantities.
  The authors explicitly discuss changing grip motion and possible model limits.
  Do not use their simulation as proof of universal golfer benefit or impotence.
- [MacKenzie and Sprigings (2010), shaft deflection](https://people.stfx.ca/smackenz/Publications/MacKenzie%202010%20Understanding%20the%20mechanisms%20of%20shaft%20deflection%20in%20the%20downswing.pdf):
  full primary prose through conclusion read. Table 1 and Figures 6--8 visually checked on PDF pages 4--5. Offset head mass and grip forces explain why radial loading
  can also bend the shaft. The force-isolation interventions are specified
  replays, not a unique energy attribution or a general human control proof.
- [MacKenzie and Boucher (2017)](https://people.stfx.ca/smackenz/Publications/MacKenzie%202017%20The%20influence%20of%20golf%20shaft%20stiffness%20on%20grip%20and%20clubhead%20kinematics.pdf):
  complete primary prose through conclusion read; Figures 2--6 visually
  checked on PDF pages 4--5. The matched-assembly study supports a distinction
  between relative kick and whole-club speed. Nonsignificance is not equivalence;
  the design does not uniquely distinguish passive reaction from motor adaptation.
- [Parks, MIT beam lecture (2004)](https://www.ocw.mit.edu/courses/2-002-mechanics-and-materials-ii-spring-2004/bc25a56b5a91ad29ca5c7419616686f7_lec2.pdf):
  text extraction inspected; the cantilever derivation (slide 9) and vibration
  equation (slide 15) were visually read because equations did not extract.
  It covers elementary beam theory, not validation of rotating composite clubs.

## Derivation Rationale

Use a declared small-deflection beam with variable EI, mass per length and
boundary conditions; identify modal normalization and tip-mass contributions.
Keep bending rigidity (N m squared), translational modal stiffness (N/m) and
rotational spring stiffness (N m/rad) distinct. Explain controlled load versus
controlled deformation energy comparisons before discussing dynamic timing.

Use an exact two-mass translation/spring example to show that an unactuated
elastic coordinate can have a nonzero row in the acceleration input map:
T = 0.5*m_b*x_dot^2 + 0.5*m_h*(x_dot+eta_dot)^2, input force on the base.
Then M = [[m_b+m_h,m_h],[m_h,m_h]], B = [1,0]. Inverting M couples the input
into eta acceleration. Independently verify the Lagrange equations, energy
identity and zero-input state evolution; this is a manufactured demonstration.

Replace the hand-drawn trajectory with a solved, consistent base-excited
oscillator, including forcing sign, initial conditions, base power and damping.
A prescribed base is an external input, not the zero-input trajectory of the
full golfer/club. Distinguish relative deformation velocity from changes in
absolute clubhead speed between different coupled trajectories. Derive moving-
frame kinematics and account for tip slope/orientation as well as tip position.

Prestress can change tangent stiffness but does not make every transverse
forcing vanish. If an externally prescribed effective stiffness varies, retain
its time-dependent energy term; a complete rotating model accounts for the
corresponding work in its coupled coordinates. Separate this teaching case from
peer-owned full impact/prestress operators.

## Validation and Delivery

Both canonical editions now contain the connected beam, modal, coupled-input,
energy, counterfactual, measured-evidence and fitting treatment. All six exercises
have corrected premises and worked answers. Historical print labels and all 18
web heading/reference destinations are retained. Two computed SVG/PDF pairs
replace both unpaired TikZ figures. The figure inventory now records 14 remaining
book-wide gaps; those other chapters are not certified by this change.

The new tests independently integrate static curvature/energy, check mode
normalization, invert the coupled mass matrix, verify momentum and power,
contrast force/displacement control, convert frequency units, compare a forced
ODE with a matrix exponential and work quadrature, differentiate parameter
energy and rotating-frame kinematics, and find the decay zero independently.
The first RED run caught an inaccurate expected decimal in the new decay test;
replacing it with a numerical root check gave 10 numerical passes and the two
intended publication failures. Corrected chapters then passed all 12 new tests.
Combined figure/tree checks passed 59 tests after updating the inventory's
explicit counts for the two converted figures.

Initial full regression: 5,141 passed, 29 skipped, 132 deselected; two old
notation contracts failed. The inertia guard expected constant-EI expanded
notation; it now checks variable-EI inertia and its uniform limit. The old
stiffness-subscript guard now also requires the time-varying storage derivative,
while retaining rejection of the invalid adjacent-subscript form. Final root regression passed 5,143 tests, with 29 skips and 132 deselections.
The final content suite passed 131 tests (four skips); all 34 static contracts,
636 title checks, link gate and affected tests passed. Black, quality and
configured mypy checks passed; Ruff identified
an assert in the figure builder, replaced with a checked solver error.

Four-pass full-book compilation succeeds. Final current PDF has 550 pages;
all 13 revised chapter pages 273--285 were visually read. Two initial inline
math overflows were repaired by shorter notation; the chapter's final log has
zero overfull boxes. Other chapter warnings remain outside scope. The chapter
is numbered 20 in the assembled book; an initial extraction script incorrectly
looked for literal Chapter 12 and was corrected to the actual adjacent chapter.

Initial canonical web verification passed 14 width/theme cases with no serious
or critical axe finding in its sampled checks. A separate full-page light/dark
axe pass caught dark reference contrast, showing why that narrower result was
insufficient. The chapter now includes the existing computational-brain.css
reference-background fix; no shared CSS was changed. Final full-page axe checks
in both themes have zero serious or critical findings; the shared moderate
landmark-unique finding remains. All 14 width/theme cases and 16 keyboard scroll
checks passed. All 24 complete-reading captures and 46 targeted left/right
captures were visually read, covering 186 math expressions and 23 displays.
Final PDF polish retained 550 pages; the changed counterfactual and bibliography
pages were read again. A scratch manifest setup first
used a regex object as a string replacement and failed before creating its
manifest; the corrected setup uses the deployment regex's sub method. These
local QA setup failures are not hidden as successful validation.

Parent muscle PR #4332 merged normally as
fd464eed3dc493b3e31363cfb1396ac69e849142. Exact production verification remains
pending: its deploy run 34432094332 was cancelled; descendant deployment
34433303512 is running. Main CI 34432094338 and textbook compilation 34432094441
passed. Do not infer publication from the protected merge. Replay only shaft commits after 3bbd5404 onto this squash (or a checked
descendant) before first shaft push; do not replay the muscle commits.

Motor PR #4330 is published as 8c383f9c with exact live artifact 10133005315:
all 956 records / 239 routes verified. Corpus remains unfinished. No subagents,
Git mutation during QA, peer ch29 edits or immutable-publication edits.

Implementation b58e86af6bfbbc7d7ea3d8d22e88150452e09b65 is in PR #4335.
Only the two shaft commits were replayed onto protected a81f99c0 after proving
the muscle parent and squash trees identical. The validated shaft implementation
tree differs only in the two subsequently synced fleet policy files; those
changes were read. The agent-context catalog is absent, so direct source
inspection remains the fallback. Normal commit and push hooks passed. Final
polish web verification again passed all 14 cases with no serious/critical axe
finding; rendered forward-counterfactual wording and proper name were checked.
The development-log checker reports only the preserved #3903/#3902 metadata
defects; this feature has a concrete verifying SHA and PR.


## Protected Publication

PR #4335 merged normally as de57acae49ea206d0232ecf4de8a7f9cd0b5da03.
Deployment 34437073824 succeeded. Exact production artifact 10137269737 was
inspected record by record: all 956 records across 239 routes passed HTTP 200
with no inspection failures, axe findings, retries or transients; 239 routes
were scanned by axe. This closes the publication check for #4333.
Parent muscle publication is also verified through a81f99c0 and exact live
artifact 10135966540; earlier pending statements above describe the delivery
checkpoint, not the current release state.
