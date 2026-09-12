# Constraint Null Spaces, Dynamics and Golf Inference

## Scope and Starting State

Issue4371, native child of4009, under core-article audit4058 and corpus4021.
Branch `fix/4371-nullspace-rigor` starts at b862099ac3b1afc58eadbbd08d4f4e5b1060b9e9,
the regular muscle-torque PR4372 head. All exact-head checks subsequently passed;
protected squash merge 3f87332512858febf2c131fbda44b62acad8d222 completed at
22:13:28Z September12. Local integration is
5a576fc612541a3ab0c72c0f2f7441fcd95d1e7c. Deployment34722147597 is still running
at the last observation; merge is not yet a live-publication attestation.
No subagents.

The complete original article was read, including its nontechnical explanations,
critics' responses, appendices, reference list and related links. The complete
bibliography companion was also read in successive chunks. Its directed
reference graph contains impossible chronology (for example,1994 to2017 and
1997 to2002) and unsupported source-specific reading guidance. No such edge
will be retained as verified citation evidence without inspecting the source.

## Findings Requiring a Coherent Rewrite

- Regular level sets, singular descriptions and actual mobility are conflated.
- Prescribed moving constraints require affine velocity and acceleration sets.
- An arbitrary null-space frame defines reduced speeds, not automatically
  coordinates; reconstruction and integrability must be explicit.
- An acceleration saddle solve is mislabeled as the original index3 DAE.
- Euclidean and mass-weighted force/velocity projectors are mixed; curvature
  is absent from the displayed drift; reduced acceleration is mislabeled speed.
- Clubhead acceleration omits the changing-Jacobian term.
- Full instantaneous input rank is incorrectly required for controllability.
- The26-coordinate golf example omits necessary coordinates and Jacobian blocks;
  fixed point constraints are confused with rigid orientation constraints.
- Basis choice and PCA are promoted to physiological synergies without data.
- Normal reaction load is called wasted energy and supports unsupported
  effortless-swing, singular-wrist and last-instant-control prescriptions.
- Figure/table placeholders, universal SVD threshold and recursive formulas
  need actual checked replacements and declared numerical assumptions.

## Primary Reading Boundaries

- Tedrake, *Underactuated Robotics*, multibody chapter:
  https://underactuated.mit.edu/multibody.html. Generalized-speed and bilateral
  position passages read (retrieved lines32-54, September12). Independently
  check signs in the dual formulation and transposes in velocity-constraint
  formulas; a primary reference can still contain typographical errors.
- Same author's acrobot chapter: https://underactuated.mit.edu/acrobot.html.
  Modal/general controllability and underactuation passages read (lines84-100),
  plus displayed stabilizability and control discussion through148. This is
  bounded reading, not a claim that the complete book has been inspected.
- Nesbit2005: https://www.jssm.org/volume04/iss4/cap/jssm-04-499.pdf. Abstract,
  introduction and methods through physical PDF page3, line232, read in text.
  The model couples prescribed kinematics with flexible club and wrist/ground
  treatment. It explicitly omits hands and gives translational wrist flexibility
  to avoid an indeterminate closed loop. This does not validate the article's
  rigid-grasp assumptions. Remaining paper/figures are not yet fully reviewed.
- The Caltech MLS author site says its first-edition PDF is no longer publicly
  distributed. The1994 book has not been read in this review.

## Independent Verification Design

Use direct saddle solves and analytic special cases, not copies of a projector
formula alone. A2-coordinate anisotropic mass example separates force and
velocity maps; a unit-circle trajectory exposes missing normal acceleration;
a moving guide checks reaction power. A rotating tangent frame distinguishes
an integrable distribution from a non-coordinate basis. A2-mass spring example
has one input acceleration direction but a full-rank4-state controllability
matrix. A declared planar two-arm/club model must satisfy its own closure,
include rotating grip offsets and distinguish admissible motion from motion
of a selected club point. All examples are constructed, not fitted golfer data.

## Recovered Implementation and Decisions

The previous turn's oversized shell write did not modify the article. Fresh git
and file inspection proved that the original source remained. The complete
rewrite was therefore written in three bounded literal chunks, then rendered.
No failed write was treated as successful.

The article now derives affine velocity/acceleration constraints, moving-frame
reconstruction, mass-metric velocity/force duality, curvature-complete drift,
task acceleration and reaction power. It replaces the undeclared26-coordinate
example with a fully specified7-coordinate planar two-arm/club mechanism.
Its4-by7 Jacobian includes both rotating grip offsets and is independently
finite-differenced. Compatible motion and selected-point stationarity have
different nullities. No physiological synergy is inferred from a basis.

The spring system supplies both a rank counterexample and an actual control.
The2-second minimum squared-force integral59.6394085294 N^2 s exceeds the
50 N^2 s upper bound for an input capped at5 N. This is a necessary impossibility
certificate for that target and deadline, despite unrestricted controllability;
the squared-force cost is explicitly distinguished from work or metabolism.

The bibliography companion was rewritten as a bounded reading map. Unsupported
directed citation edges were removed; five actually inspected primary sources
are now configured in references/nullspace-rigor.bib. Hairer's June2011 cover and
sectionIV.4 (printed34-36, physical PDF38-40) were read, including the index1
saddle formulation and consistent-initialization discussion. SciPy1.18.0's
function description, rcond parameter, returns and examples were read directly.
The derivations are independent; source-specific summaries stay bounded.

## Validation and Outstanding Review

- TDD: nullspace-red.log records the missing-module failure before implementation;
  nullspace-green.log records16 passing independent checks. A fresh
  `py -3.12 -X utf8 -m pytest tests/test_nullspace_article_rigor.py --no-cov -q`
  again passes16 after the article rewrite.
- `py -3.12 -X utf8 scripts/check_title_case.py`:636 sources pass.
- `py -3.12 -X utf8 docs/development/technical-review/render_selected.py articles/null-space-constraint-jacobian.qmd`:
  exit0, session18391 reaped. Root configuration restored byte-for-byte by helper.
- BeautifulSoup inspection of the actual output finds all44 old heading IDs,
  five resolved bibliography entries and209 math source nodes. This does not
  establish successful runtime typesetting or full visual review.
- Full revised source is4436 whitespace-delimited words. All scientific sections,
  the explanatory/critical callouts, derivation appendix and eight-row equation
  table are present. No figure/table placeholders remain.
- Still required: complete browser reading and equation inspection in both themes,
  narrow-screen interaction and link/panel verification, full repository gates,
  durable review binding and inventory reconciliation. No complete-route review
  or empirical golfer validation is claimed at this checkpoint.

## Checkpoint Gates and Presentation Repair

Full root `py -3.12 -X utf8 -m pytest --cov` passes5334, with29 skipped,
132 deselected and59 warnings in198.20s. Coverage is79.29%, not the79.35%
previously transcribed for the preceding muscle boundary run. Direct comparison
of both logs shows that muscle's final run was79.21%; every existing module's
statement/missing counts are unchanged, and the new154-statement builder misses12.
The earlier muscle delivery run really was79.35%; only its final boundary result
was copied incorrectly into turnover prose. Correct that result in place.

Ruff passes; Black100 leaves709 files unchanged; configured mypy passes91 files
and the new builder independently passes. Content-lint selection exits0
(131 passed,4 collection/test skips). Both article and companion render.

Initial browser run78009 failed the dark-theme axe check: Quarto moved the
special appendix into a separately styled area with insufficient contrast.
Removing the special appendix class keeps the same heading and proof within
normal article flow. Render67529 and targeted browser82629 both exit0.
All209 expressions typeset with zero MathJax errors; dark axe now reports only
the existing moderate landmark-unique issue. The corrected appendix screenshot
was read. Initial full-reading captures00-11 were read;12-28 and final full
reading still require inspection. Do not mistake saved screenshots for review.

The initial browser generated29 reading captures and equation detail captures,
but stopped before completing dark detail checks. Full updated width/theme,
panel, bibliography and production-route review remains outstanding. Console
messages include the render-only legacy polyfill CSP rejection and axe attempts
to fetch external font styles; apply the production polyfill normalization only
to the selected generated output before the final route check. Never call the
deployment-pruning entry point on the working docs tree.

All test/render/run-code sessions are reaped; browser nullspace-review is closed.
The six unrelated generated summaries/registries were restored only after
line-ending or parsed-JSON equality (excluding generated_on) was established.
The repo-local shared_scripts development-log checker is absent; use the
central Repository_Management copy, preserving known peer metadata errors.


## Readability and Static-Check Checkpoint

Latest source uses the existing css/duality-chapter.css without editing that
shared file. Nested responsive rules previously compounded display-math scaling
to roughly10px on mobile; inherited sizing and horizontal scrolling preserve
legibility. Four latest light mobile equation details were visually inspected.
Both short callouts now remain expanded: real keyboard testing found that the
shared collapse header's role and tabindex did not implement Enter activation.
That shared defect is tracked separately in epic child4374; no shared JS was
changed. TOC highlighting4370 and moderate landmark-unique findings remain.

Render94019 and browser56238 completed successfully:209 expressions,46 displays,
14 width/theme cases,184 regions,46 successful keyboard scroll checks. The
supplement verifies eight visible callout cases, four keyboard-scrollable table
cases and eight bibliography viewport/theme cases. All29 initial article
captures and six light bibliography captures have been read. The29 newest
article reading images and six dark bibliography images remain unread; a
truncated five-image tool output is not visual evidence. Production-route
verification, full final reading and durable review/inventory binding remain.

Static CI103632789676 at a8bd721056f29b236872f025e3d45a6c7d882e94 rejected two
unnamed9.81 test literals. The test now declares its own GRAVITY_M_S2 constant,
independent of the builder. Focused16 tests, Ruff and Black100 pass. The real
checker applied to735 tracked Python files finds zero issues; its unfiltered
local scan includes175 unrelated scratch findings and is not a passing result.
Latest root nullspace-readable-root.log:5334 passed,29 skipped,132 deselected,
59 warnings in193.45s, coverage79.29%. All validation processes were reaped and
the browser closed before committing. This checkpoint does not claim full
route review, empirical golfer validation or completion of the corpus.
