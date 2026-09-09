# Interdisciplinary Synthesis Review

Date: 2026-09-09. Issue #4313; native child of epic #4009; corpus #4021.
Branch: fix/4313-interdisciplinary-synthesis, based on launch-monitor PR #4312
head 3cce3cb74c164cf3001d2b91c3a5602168a32dcd. Replay only this issue's commits
after that base when the parent merges. No subagents. No commit, push or branch
operation during local tests, rendering, PDF or browser QA.

## Original Reading and Findings

Read both complete original chapter 13 editions, including all eight exercises:
7,554 indexed words in print and 6,690 in Quarto. Print additionally contains a
discipline map and expanded living-systems framework. Prior #4161 corrected a
cross-reference only; this is the first complete paired review.

The chapter conflates drift with uncontrollability and natural/passive motion,
changes of initial state with changes of vector field, and zero-torque rollouts
with unique causal contributions. It asserts speed-dependent loss of authority
without a horizon, task map or input constraints. It treats proximity to a
zero-input endpoint as a minimum-effort theorem without a metric or cost.

Its neural hierarchy is presented as established anatomy; forward and inverse
models are conflated. Shoulder EMG timing is asserted without evidence and the
print edition misassigns supraspinatus external rotation. Robots are described
as lacking compliant actuation and adaptive learning. Impedance is reduced to
stiffness, and a phase schedule is prescribed without identifying the task.

The print edition misdefines restitution as smash factor and as transferred
energy fraction. Both editions infer compression/launch/spin relationships and
equipment prescriptions without controlled evidence. Fiber orientation claims
reverse the axial/shear tradeoff. A shaft is assigned a scalar COR without an
impact experiment. Launch reports are claimed to identify whole-body initial
states, tissue parameters and separate drift/control fields. Three-dimensional
club delivery is reduced to path and face azimuth. Net joint torque is treated
as individual tissue load, with unsupported injury-prevention and rehabilitation
prescriptions. Coaching examples confuse hypotheses with proven interventions.
The eight exercises embed these unsupported premises and require replacement
with resolvable questions and worked answers.

## Evidence and Reading Boundaries

- Pink, Jobe and Perry (1990), DOI10.1177/036354659001800205: public abstract
  read at https://pubmed.ncbi.nlm.nih.gov/2343980/. Eight muscles of both shoulders
  were studied; the abstract describes muscle- and phase-dependent activation.
  The complete paper was not read. It does not establish the chapter's universal
  early-activation/late-cessation claim or identify a zero-torque counterfactual.
- Arakawa et al. (2006), DOI10.1299/kikaic.72.3826: complete English abstract and
  metadata read on J-STAGE. Its rigid-steel normal-impact experiment reports
  decreasing restitution and contact time with increasing inbound speed, while
  normal compression increases. This is a counterexample to a universal trend,
  not a ranking of contemporary balls or a driver-fitting prescription. Japanese
  full paper not read.
- Robinson et al. (2024), DOI10.1136/bmjsem-2023-001844: downloaded eight-page
  author-institution PDF; read abstract, study design/recruitment and discussion,
  limitations and conclusion. Main results tables and supplements not fully
  audited. The 910-person five-month observational cohort did not measure swing
  biomechanics. Self-report, 57.6% response and selected population limit causal
  interpretation. Do not convert an observed injury association into evidence
  that a particular torque policy prevents injury.
- Roylance, Laminated Composite Plates (dated February 10, 2000; MIT OCW 2007
  course): read introduction, orthotropic constitutive law and stress/strain
  transformation discussion through equation 10, then the worked compliance
  example and laminate force/moment integration through equation 25 (pages5–9).
  The full 17-page document and all figures were not reviewed. Engineering shear
  strain is twice tensor shear strain. NASA Nettles
  RP1351 metadata was found but PDF fetches failed (403 through web, 429 direct);
  no claim that its body was read.
- Reuse the explicitly bounded primary-source reading in brain-review.md and
  biology-review.md for feedback, adaptation, impedance and muscle activation.
  Those records distinguish complete papers, selected sections and abstracts.

## Verification Plan

Independently derive input reparameterization, fixed-inertia authority, finite-
horizon minimum-energy costs, work balance, unidentifiable stiffness/input pairs,
coactivation loads, rotated orthotropic response and collision energy partitions.
Replace every exercise and retain historical destinations. Rebuild both editions,
inspect every affected print page and the full responsive web chapter, then run
repo checks and normal protected delivery. All calculations are teaching models;
none alone establishes a clinical effect or a neural implementation.

## Current State

Original reading and issue/lease registration complete. Paired rewrite is about
6,300 print words and 6,500 web words with two figures and eight worked answers.
All25 focused tests pass: independent ODE response, input baseline, Gramian costs,
optimal controls, stiffness/input ambiguity, coactivation, power duality,
time-varying elastic storage, tensor-rotated ply stiffness, collision balance and
paired publication guards. Final local verification is complete as recorded below;
protected PR delivery remains.

## Derivation and Editorial Checkpoints

The first independent run caught an incorrect provisional ball-energy expected
constant (0.508584). Exact rational arithmetic and an independent momentum/
restitution linear solve agree on 0.5086342499712668. Correcting that test leaves
the intended four publication guards failing against the original sources;
17 mathematical cases pass. After the paired rewrite all21 pass. Four additional
checks verify optimal-control coefficients, elastic work, virtual power and
preservation of all22 displays/eight exercises and answers; all25 pass.

The minimum-energy example has W inverse [[12,-6],[-6,4]]. For endpoint errors
(0.1,-0.1) and (0.2,0.3), costs are0.28 and0.12. The first draft answer incorrectly
printed 1.0-1.8t; independent integration corrected it to0.8-1.8t before either
canonical edition was published. The second control is0.6-0.6t. Both endpoint
components are independently verified. Distances use declared nondimensional
position/velocity scales; no metabolic or clinical claim follows.

Rotating strain and stress as tensors independently verifies the engineering-
shear stiffness calculation at0,30,45,90degrees. With E1=135,E2=10,G12=5GPa,
nu12=.3, Qbar11(45)=43.0033557047 and Qbar66(45)=34.9832214765GPa. These are
constrained-strain coefficients, not unconstrained moduli or a shaft rating.

For M=.2kg,m=.04593kg,e=.83, exact-rational results are smash1.48822835766275,
ball fraction.508634249971267, lost fraction.058101179197333 and the remaining
mass fraction.433264570831401. The inferred97.431284153mph from145mph ball speed
is explicitly conditional, not another independent measurement.

Historical rendered headings were saved before conversion:29 destinations,
including the main title and bibliography. Additional source-only headings and
old implicit theorem-box labels are retained. Five misleading headings were
rewritten while retaining their old URL destinations. Both editions contain all
22 intended displays. The original print-only overview/living-systems sections
now also appear in the web edition. Final publication inspection is recorded below.

A direct count of registry statuses beginning 'Indexed;' gives 223 after these
two rows were updated. This corrects the earlier narrative count of 221 under
that explicit definition; other statuses include partial audits, so its complement
must not be described as the number of fully completed technical reviews.

## Final Local Verification — September 9, 2026

The final regression passes 4,974 tests with 29 existing skips, 131 deselected
and 92.65% coverage. The first full run exposed two stale figure-inventory
expectations: replacing one unpaired TikZ map with two paired PDF/SVG figures
changes the actual book inventory to 33 print figures, 21 TikZ environments,
12 includegraphics, 13 web figures and 20 remaining missing web figures. Both
precise inventory assertions are updated against the independent audit output.
Final affected checks pass 48/48; content lint passes 130 with four existing
skips; all 34 CI static contracts, the site-link gate and all 633 title checks
pass. Ruff, mypy on 88 files, code-quality and CSS checks pass. Configured Black
checks 679 Python files plus the new figure generator. An initial explicit-file
Black invocation incorrectly bypassed the configured exclusion of the managed
bump_spec_version.py; that file is unchanged, and the configured command passes.

The complete rebuilt Physics PDF has 551 pages. All 17 affected physical pages
466–482 (printed 438–454) were read visually, as were contents pages 23–24,
list-of-figures page 27, bibliography pages 534, 541–542 and final index page 551.
The chapter has no overfull-box or undefined-reference warnings. Title and long
section breaks were adjusted, and the laminate calculation was split into two
aligned lines. This is affected-page verification, not a claim that the entire
551-page book has completed technical review.

The complete web text was read in 27 overlapping desktop captures. Final checks
verify 158 mathematical expressions, 22 displays, all 29 historical destinations,
two loaded figures with alt text, and no duplicate IDs, raw display delimiters or
broken in-page fragments. Fourteen viewport/theme combinations from 320 through
1920 pixels have no page overflow or MathJax errors. Both figures now fit the
desktop column; narrow views retain 600-pixel diagrams in focusable horizontal
scroll regions. All 12 overflowing display/figure right edges were inspected;
both figures move 40 pixels by keyboard. Six long inline groups preserve normal
math size. An additional 320-pixel check caught the short 0.03(200-100)=3 formula
inside a 165-pixel list column; its explicit wrapper fixes that final overflow.
The three overflowing inline groups respond to keyboard scrolling (7, 40 and
40 pixels), and no unwrapped inline formula exceeds its reading column.

Final desktop figures, changed narrow sections and eight critical equation
crops confirm complete superscripts, transposes, braces and matrix glyphs.
Both ends of all three overflowing inline calculations were also inspected
at 320 pixels in both themes; the full expressions and final units are reachable.
SVG lettering uses reproducible paths. Axe finds no serious or critical issue;
the inherited moderate landmark-unique warning remains. Five console errors
are the existing blocked external polyfill and Google Fonts requests, including
axe stylesheet fetches; the console is not described as clean.

Scratch render/build evidence stays in docs/development/technical-review.
The immutable proximal-distal publication is untouched. Root tests regenerated
unrelated trust dates, formatting and byte-sensitive digests; those outputs are
restored after comparison and are not part of this technical correction.

The first commit hook rejected five unexplained E402 suppressions in the figure
generator. Each now states why the headless backend must be selected before
plotting imports. No runtime or scientific result changed; normal hooks are rerun.

## Protected Delivery Checkpoint

All commit hooks pass at e1fa05c3. Only that implementation commit was replayed
after parent head 3cce3cb7 onto published main bc252297, producing 58c2419a.
The reviewed implementation tree is unchanged; the only whole-tree differences
are main's new fleet-managed AGENTS.md and CLAUDE.md sections, read before
further work. Their development-log requirement is recorded as DL-#4313.
The central communication CLI and guide are absent locally, as is the local
portable development-log checker; the existing issue lease remains in force.
The central portable checker is available. No local codemap is present.

The first push's filesystem-wide Bandit scan found an unqualified urlopen in
an untracked primary-source download helper. The helper now explicitly requires
HTTPS and documents its fixed source URL; no source, evidence or public model
changed. All normal push hooks, including Bandit and pytest, then pass.
Ready PR #4314 is open at
https://github.com/D-sorganization/AffineDrift/pull/4314. Protected checks, review,
merge and production verification remain. SPEC receives exactly one PR-keyed
row; no spec-version field or other contributor's row is changed.

The central development-log checker predates SELF support and requires a literal
issue token. The new entry uses #4313 and the verified implementation SHA
58c2419a. Remaining checker findings concern pre-existing #3903/#3902 entries;
their owners' records are preserved. This local checker limitation is not a
failure of the chapter's mathematical or publication checks.
