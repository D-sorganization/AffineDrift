# Affine Structure: Complete Mechanics and Control Review

## Scope and State

Issue #4349 under epic #4009, corpus #4021 and Physics #4054. Both original
editions were read completely, prioritizing the approximately 5,681-word print
chapter. The replacement covers every section and all seven exercises in both
editions. Branch `fix/4349-affine-structure-rigor`, initially stacked on brain
PR #4348 head `4f73040fa9ecccd1b9f25f84b4db7168e4e895b9`.
PR #4350 is open; protected delivery remains pending. The corpus is unfinished.

The central purpose is to connect mechanical structure to a defined control
question. Affine dependence on input is useful, but does not prove that skilled
swings maximize drift, that acceleration measures energy supply, or that a
particular torque schedule is optimal. Preserve peer impact/Chapter 29 work,
immutable publication bytes, scientific-authority pins and existing destinations.

## Findings and Decisions

1. **Incomplete dynamics.** The old explicit drift omitted the second
   velocity-bias contribution and mixed incomplete gravity calculations with
   inverse-inertia entries. Define one relative-angle model, its COM positions,
   inertias, potential and complete bias before evaluating acceleration.
2. **Incorrect inverse inertia.** In a coupled system, `(M^-1)[1,1]` is not
   `1/M[1,1]`. Derive the Schur complement and compare free and locked distal
   coordinates as separate experiments. A smaller diagonal inertia does not
   establish a larger free response.
3. **Ambiguous zero input.** Zero generalized actuator torque retains the
   declared joints and grip contact. It is neither zero muscle excitation nor
   releasing the club. Activation, coactivation and material memory require
   additional states or an explicit effective-plant definition.
4. **Incorrect affine definition.** State dependence may be linear or nonlinear.
   Affine combinations of inputs combine derivatives at a fixed state, not
   entire nonlinear trajectories. The upper zero block in the input matrix does
   not prove finite-time uncontrollability of position.
5. **Unsolved vector-field figure.** A two-coordinate slice of a four-state
   pendulum need not be invariant. Replace the arbitrary arrows/path with a
   computed reduced pendulum under an explicitly imposed ideal distal lock.
   Its reaction is retained and has zero power; the free plant is different.
6. **DCR conflations.** Define capacity, realized input, output scaling and input
   origin separately. A norm ratio is not a work fraction, skill score or
   directional reachability test. State the zero-capacity cases without an
   arbitrary dimensionally unexplained epsilon.
7. **Unsupported phase and energy claims.** Remove universal address/top/impact
   regimes, inconsistent 180 g versus 180 m/s² claims, invented phase torques,
   summed-torque “effort,” effortless follow-through and elite/novice rankings.
   Clearly manufactured states illustrate the equations without posing as data.
8. **Unsupported optimality.** “Align with drift,” “maximize DCR” and “apply torque
   early” are not universal consequences of control-affine form. Specify the
   plant, initial condition, horizon, constraints and objective. A solved scalar
   counterexample establishes early, constant or late optimal input depending
   on the plant. Pontryagin conditions are necessary under their assumptions;
   dynamic programming is a value-function formulation with its own verification
   conditions. Neither identifies a neural algorithm from a fitted trajectory.
9. **Incomplete exercises.** Supply all parameters and seven worked answers,
   including component calculations, nested feasible input sets and the limits
   of transferring the same mathematical structure to throwing.

## Derivation and Independent Calculations

For independent local coordinates with `v = qdot`, use
`M vdot + c + g = B u`, `g = grad V`, positive-definite `M`, and the complete
velocity bias `c`. Then `f = (v, -M^-1(c+g))`, `G = (0, M^-1 B)`.
General rigid-body representations may instead require `qdot = N(q)v` with
different dimensions. Solve mass systems numerically; inverse notation describes
the analytical mapping.

For the fixed-pivot planar two-link model, `q1` is measured from downward
vertical and `q2` relative to the first link. Torques are conjugate to these
relative coordinates. With COM inertias, define
`A = I1 + m1 r1² + m2 l1²`, `D = I2 + m2 r2²`, `b = m2 l1 r2`.
The matrix has entries `M11 = A+D+2b cos(q2)`, `M12 = D+b cos(q2)`, `M22 = D`.
The bias is `b sin(q2) (-2v1v2-v2², v1²)`. Differentiating the stated potential
gives both gravity loads; both enter each component of `-M^-1(c+g)`.
Independent COM-Jacobian and finite-difference energy tests check the formulas.

Manufactured parameters are `m1=2.5`, `m2=0.4` kg, `l1=0.35`, `r1=0.175`,
`r2=0.5` m, `I1=0.025`, `I2=0.030` kg m² and `g0=9.81` m/s². The report
`affine-structure-numerical-results.json` retains full precision. Rounded results:

| State (Degrees; Rates in Rad/s) | Drift Acceleration (Rad/s²) | Capacity (Rad/s²) | Capacity DCR |
| --- | --- | --- | --- |
| `(0,0); (0,0)` | `(0,0)` | 1068.2363 | 0 |
| `(45,0); (0,0)` | `(-28.8732,33.7484)` | 1068.2363 | 0.0415771 |
| `(150,-70); (0,0)` | `(-16.9466,5.2045)` | 651.1134 | 0.0272268 |
| `(140,-60); (5,0)` | `(-35.7444,42.1629)` | 717.3638 | 0.0770535 |

Capacity here uses an unweighted angular-acceleration norm and a centered 30 N m
Euclidean torque ball. It is not a componentwise 30 N m box or an identified
muscle set. At the moving state, velocity bias contributes
`(-13.6289,28.9563)` rad/s² and gravity contributes `(-22.1155,13.2066)` rad/s².
Their vector sum is the complete drift, not an energy-source fraction.

For free distal motion, proximal response uses
`1/(M11-M12²/M22)`; with an imposed lock it uses `1/M11`. At zero relative angle,
these are 8.8597 and 2.3778 rad/s² per N m. At 90 degrees the free response falls
to 6.6418 despite a smaller `M11`, disproving the claimed universal folded-leverage
rule. The examples do not compare different golfers.

The energy identity `v^T c = (1/2) v^T Mdot v` yields `Edot = v^T B u` for the
declared ideal plant. Velocity-dependent inertial terms do not create energy;
gravity exchanges kinetic and potential energy. Normal acceleration does not
identify work. Cartesian acceleration requires `J vdot + Jdot v`; collision
impulses require a separate event model.

For the ideal locked figure, integrate
`(A+D+2b) q1ddot + g0(m1r1+m2l1+m2r2) sin(q1) = 0` from `(0.9,0)` for 2 s.
DOP853 solutions at two tolerance/step settings agree to the tested 1e-8 bound;
the refined energy range is about 9.77e-15 J. Arrow directions use data
coordinates (`angles=xy`, `scale_units=xy`) after the displayed unit scaling;
their normalized lengths are not acceleration magnitudes.

For a declared map `W`, `C_W = max_U ||WGu||` and `D_W = ||Wf||/C_W` where the
capacity is positive. A Euclidean ball gives the largest-singular-value formula.
The example `f=(1,0)`, `G=diag(100,0.01)`, unit ball shows that a small capacity
ratio can coexist with almost no authority in the second direction. Coordinate
changes require transporting the metric/output; nonlinear configuration changes
also transform acceleration with a velocity-quadratic term. Shifting the input
origin to a nominal feedback changes the designated drift while leaving the
physical attainable set unchanged when the input set is transformed consistently.

Along a trajectory, task sensitivity uses the state-transition kernel and the
integrated input perturbation, with activation, delay and event-time corrections
where applicable. Expanding a nested admissible input set cannot worsen the best
objective for the otherwise identical problem; increasing DCR by weakening an
actuator is therefore not a general performance improvement.

The normalized scalar problem `zdot=az+u`, `z(0)=0`, `z(1)=1`, minimum integral
of `u²` has `W_a = integral exp(2a(1-t)) dt` and
`u*=exp(a(1-t))/W_a`. Cauchy–Schwarz proves the global minimum `1/W_a` for this
unconstrained task. Independent quadrature checks the endpoint and cost for
`a=-2,0,2`. Negative, zero and positive rates give late, constant and early
optimal input respectively. Active bounds change the solution. This is a
counterexample to a universal timing claim, not a golf prescription.

## Primary Evidence and Reading Limits

- [Tedrake, Multi-Body Dynamics](https://underactuated.mit.edu/multibody.html):
  the double-pendulum/manipulator derivation, nonunique Coriolis factorization,
  generalized velocity map and constraint introduction were read. Supports the
  formal mechanics, not golfer validation. The entire online chapter was not read.
- [Tedrake, Trajectory Optimization](https://underactuated.mit.edu/trajopt.html):
  continuous-time necessary conditions and Pontryagin section were read. Used for
  the necessary-condition distinction, not a claimed global golf solution.
- [Tedrake, Dynamic Programming](https://underactuated.mit.edu/dp.html):
  HJB, sufficiency/verification and finite-horizon discussion were read. Used for
  the value-function formulation and its conditions. The entire chapter was not read.
- [Nesbit and Serrano, 2005](https://www.jssm.org/volume04/iss4/cap/jssm-04-520.pdf):
  abstract, introduction and methods through physical page 3 were read, not the
  full 14-page article. The bounded chapter statement identifies four amateurs
  and kinematically driven body/club estimates of work and energy. It does not
  generalize a DCR law, individual muscle activation or neural optimality.

Two Tedrake bibliography keys were added; the existing multibody key was retained.
All three now explicitly use `n.d.` because the pages did not supply a verified
publication date. Access dates and reviewed sections are recorded separately;
a copyright date is not invented as a publication date.

## Validation and Failure History

- New numerical/source tests first failed before the helper and rewrite existed;
  after the helper, nine numerical cases passed while the two edition contracts
  still failed. The complete replacement passes all 11. Ruff identified an
  assigned lambda, then Black identified formatting; both were corrected.
- `py -3.12 -X utf8 -m pytest --cov`: 5,213 passed, 29 skipped, 132 deselected.
  Configured src/scripts coverage is 79.29%, unchanged from the preceding run.
  Earlier 92.88% reports used src-only scope; they are not comparable denominators.
- Focused affine/figure-parity tests: 34 passed. Content lint: 131 passed.
  Static contracts: 34 passed. Title-case audit: 636 files. Site link gate,
  configured mypy (91 files), Ruff and Black100 passed. No coverage configuration,
  runtime mechanics library or scientific authority was changed.
- Replacing one legacy TikZ diagram changed parity to 11 TikZ/27 included print
  figures, 28 web figures and 10 missing web figures out of 38 print figures.
  The stale parity assertion failed, then passed after its expected inventory
  and the generated figure inventory were updated.
- Full book regenerated with pdflatex, BibTeX, pdflatex twice: 542 pages.
  All 13 affected chapter pages (physical 81–93, printed 51–63) were visually
  read. Initial title/example overflow and accidental unit-conversion text were
  corrected with a deliberate title break, multiline example and `mathrm` units.
  Final chapter log has no overfull/underfull or undefined-reference warning.
  Undated citation rendering was caught visually and corrected; affected pages
  82, 90, 156, 220 and bibliography 534 were subsequently visually read.
- Full web reading covered all 24 overlapping desktop captures, not just a fold
  screenshot. It found four summary headings rendered as literal Markdown; blank
  lines fixed their structure. The reachability callout needed a separate anchor
  because Quarto removes the heading ID when forming its callout title. Final
  DOM verification checks all 30 historical heading/bibliography destinations.
- The exhaustive browser run covered 187 math spans, 24 displays and one loaded
  SVG with alt text; 14 width/theme cases (320–1920 px), 150 equation/figure
  region cases and 60 successful keyboard-scroll cases. No document overflow,
  math errors or serious/critical axe findings. Existing moderate shared
  `landmark-unique` and accumulated session console messages remain; this is not
  a zero-all-severity or zero-console claim. Final heading repair is rechecked
  in the rendered DOM and read at the changed sections.
- Canonical fresh-page verification uses the actual affine route in all 14
  viewport/theme records, all independently inspected and passing. The first
  post-heading run failed mobile/light because the MathJax CDN hostname did not
  resolve; the normal fresh rerun passed all 14, with one route scanned by axe
  and no serious/critical findings. No verifier policy or retry gate was changed.
  It is additional layout evidence, not a substitute
  for the manual reading that found the conversion defect.

The numerical helper has a maximum function length of 31 lines. Six identified
render-only generated files were restored to exact HEAD bytes after confirming
only generated dates, formatting and a derived artifact digest differed.

Scratch build drivers, logs and captures are not publication inputs. Canonical
sources, the numerical reproducer/report, shared vector figure, tests, book PDF
and this audit carry the correction. Use normal protected PR delivery, then
inspect revision-matched live evidence. Continue the constraint-forces chapter,
queued DCR critiques #4340 and remaining corpus without promoting unreviewed
material to complete.

## Delivery Checkpoint

Normal commit and push hooks passed. Original implementation 8bb4d042 replayed
onto brain squash 688dda81c3f0c38759d9994cbc0d5c0cd0478bd2 as
332bfe2ffdcde038a0a4b5ee0577845c4ad73ef7, preserving validated tree
8d8b2fedeae9fa3c761e2beae1d021e3c4021119. Parent head and squash trees matched.
PR #4350 closes #4349; verify protected checks and exact publication next.
The central development-log checker initially rejected SELF as a verifying SHA;
the entry now names the implementation commit. Only pre-existing peer #3903/#3902
metadata omissions remain. No hook or protection bypass was used.

## Static CI Follow-Up

PR #4350 static job 102824664610 rejected the gravity constant name at head
83d9fd47. Renamed it to GRAVITY_M_S2 without changing its value or formulas.
All 11 numerical/chapter regressions, focused code-quality, Ruff and Black pass.
The unrestricted local quality scan also sees 174 findings in untracked scratch
files; these are excluded from commits and absent from the clean CI checkout.
The actual CI log identifies only the renamed tracked constant.

## Protected Merge

All checks passed at final head 18c3840c58ef1a151f7288813fd612176dcbfeff. PR #4350 squash-merged as 60d0298826880ca24580908127e8032565407216. Exact live verification remains pending; implementation and reading evidence above are retained.
