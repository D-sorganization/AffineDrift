# Muscle Force Generation: Paired Technical Review

Issue #4331 is a native child of epic #4009; corpus #4021 and Physics textbook
#4054 remain unfinished. Branch `fix/4331-muscle-force-rigor` starts from motor
delivery checkpoint `71e80bb98531798d6d7c438d2858e932697fe469`; PR #4332.
Both complete original chapter editions and all seven exercises have been read.
The print source is indexed at 6,139 words. Peer joint-friction work is excluded.

Claim check was free; lease comment 5610965947 expires 2026-09-10T02:49:29Z.
Central presence comment 5610973267 covers both editions and book bibliography
through 02:50:17Z. No subagents; no Git mutation during tests, rendering or QA.

## Confirmed Findings

The print and web editions diverge despite sharing serious model errors. Local
fiber speed is confused with clubhead speed and absolute whole-arm motion.
Shortening sign and normalization are inconsistent; 2–4 fiber lengths/second
for a 0.10 m fiber is 0.2–0.4 m/s, not 5 m/s. The hyperbolic concentric law is
called linear, extrapolated to negative force and used to prove inevitable
control failure. The web eccentric expression tends to
F_asym + (F_asym−1)/k, not F_asym, as signed velocity tends to minus infinity.

Active cross-bridge overlap, recruitment and total passive tension are mixed.
The passive exponential is negative below its unstated threshold. A Gaussian
does not have an exactly flat plateau or a finite zero. Fiber percentages,
specific tension and latissimus/triceps swing profiles lack suitable evidence.
Lower-limb publications are used as sources for forearm muscle parameters.

The CE/parallel-PEE network cannot have CE force equal to tendon force when
PEE is loaded. Pennation and tendon/fiber kinematics must be stated together.
The tendon-energy exercise integrates force over strain without slack length
and supplies insufficient compatible parameters. Stiffness is conflated with
a dimensionless exponential coefficient; elastic return is treated as free
energy or a universal shaft/coaching advantage.

Activation time constants, pure onset delays, EMG and full recruitment are
confused. The timing example places half force at 250 ms and impact at 300 ms,
then calls them simultaneous. Neural excitation is mistaken for muscle output.
The state excludes activation/elastic memory while calling the system Markovian;
the control-affine expression equates a state derivative with a scalar torque.
Measured inertial demand I*qddot is mislabeled as free drift. Joint moment
ranges and phase sequencing are not validated by their citations, and inverse
dynamics does not identify individual muscle forces or a unique optimal policy.

## Verification and Correction Plan

Derive a consistent teaching model from architecture to signed musculotendon
geometry, tensile force curves, massless force balance, tendon work and state
augmentation. Independently test limits, units, power duality, activation timing,
redundancy and finite-horizon effects. Use reproducible figures and seven fully
specified exercises with worked answers. Preserve historical labels/links;
render and visually inspect both editions and run all required checks before
protected delivery. Both chapters are now rewritten; render and full validation
are in progress. Publication is not yet claimed.

## Primary Evidence Read So Far

- [Millard et al. (2013)](https://nmbl.stanford.edu/publications/pdf/Millard2013.pdf),
  DOI 10.1115/1.4023390: indexed abstract and author-hosted main paper through
  modeling sections 2.1–2.4, benchmark methods/results and discussion/conclusion
  read. Appendix and all reference entries are not claimed as read. PDF pages 2
  and 4 visually checked for force balance, activation and pennation equations.
  Comparison data are rat/cat soleus, not golf. A cached local author PDF/text is
  available; PMC direct access returned a CAPTCHA. Do not bypass access controls.
- OpenSim official Thelen-model documentation: text read, including the fact that
  its implementation differs from the original 2003 formulation and its inverse
  can be singular. Web math did not extract; no equation verification from that
  rendering is claimed. Its linked original paper failed to open.
- Rajagopal et al. (2016), PMID 27392337: complete primary indexed abstract and
  metadata read. The actual title ends in Human Gait, and the model has muscle-
  actuated lower limbs and torque-actuated upper body. The book's author list,
  title and note claiming upper-limb muscle parameters are wrong. Correct them
  and withdraw use as a forearm-force source. No full-paper claim yet.
- Nordez et al. (2009), PMID 19359617: full primary indexed abstract read.
  Electrically stimulated gastrocnemius in nine subjects separates some onset
  events, not all proposed delay components. Use only a bounded illustration of
  why EMD definitions/protocols matter; no universal golf latency.
- [Holzbaur et al. (2005)](https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf):
  abstract, methods, results and discussion through limitations and closing
  model-scope paragraphs read. No claim to have visually verified every table
  or figure. The chapter uses bounded model scope, parameter selection and
  sensitivity statements, not table-derived golf force estimates.
- [Roberts and Gabaldón (2008)](https://pubmed.ncbi.nlm.nih.gov/21669793/): complete
  indexed abstract read; turkey hindlimb EMG/force/fascicle measurements support
  distinguishing these signals, not calibrating human forearm force. Full paper
  methods not claimed as read.
- OpenStax [contraction](https://openstax.org/books/anatomy-and-physiology-2e/pages/10-3-muscle-fiber-contraction-and-relaxation)
  ATP/cross-bridge/calcium paragraphs and [fiber classification](https://openstax.org/books/anatomy-and-physiology-2e/pages/10-5-types-of-muscle-fibers)
  explanatory paragraphs read. No universal fiber distribution or golfer
  composition inferred.
- [OpenSim activation documentation](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090590/First-Order+Activation+Dynamics):
  complete explanatory text and implementation qualifications read; equations
  did not extract. The replacement fixed-time-constant model and its solutions
  are explicitly declared teaching equations, not transcribed OpenSim code.

## Derivations and Decisions

Use shortening-positive w = -fiber_length_rate / Vmax, with Vmax expressed in
meters/second. The k=0.4 concentric law gives 0.573913 at w=0.175. The constructed
eccentric branch tends to 1.4; choosing c=4/35 matches its slope to the concentric
branch at zero. It is not attributed to Thelen. Power peaks at w=0.348331 and
normalized power 0.1213348; an independent grid verifies the stationary point.

The active Gaussian has no finite zero. The passive curve is unilateral and
normalized at length ratio 1.6. Its slack derivative is discontinuous, explicitly
noted rather than hidden. Tendon stiffness is dF/dlength, distinct from the
dimensionless exponential shape parameter. Tendon work includes slack length;
direct quadrature and differentiating energy verify 0.2247501 J at the declared
0.008 m extension and 100 N endpoint force.

Fixed-height pennation gives fiber_rate = cos(alpha)*(path_rate-tendon_rate),
not the constant-angle relation. This and force projection preserve the power
identity. An independently differentiated two-joint path verifies moment arms
and virtual work; a moving-joint example has zero total path rate. An antagonist
counterexample demonstrates non-identifiability of muscle forces from net torque.

Activation is a state, not an instantaneous torque command. The fixed 25 ms
time constant gives t95=74.8933 ms; Euler at 5 ms reaches the discrete threshold
at 70 ms. Direct time quadrature independently verifies the finite-horizon
position/velocity expressions. The augmented control-affine matrix enters the
activation derivative and requires fixed time constants and admissible muscle
equilibrium. No global controllability or universal optimal golf sequence follows.

## Validation

Initial tests exposed both old chapter claims, as intended, and one erroneous
decimal in the new fixture. The decimal was replaced with an independent
geometric-series identity. All 13 muscle cases pass: 11 numerical checks and
two edition checks. Figure parity exposed two old aggregate counts, corrected
against the independently regenerated inventory (37 print figures, 21 web
figures, 16 missing elsewhere). The combined muscle/parity suite has 36 passes.

Root regression: 5,131 passed, 29 skipped, 131 deselected, 79.2% coverage.
After final prose/layout refinements, content checks: 131 passed, four skipped;
all 34 CI static contracts, 636-source title audit, internal/site links, tracked
Ruff, Black (100), quality checks and mypy (91 files) pass. Commands and complete
outputs are retained in the local muscle-*.log files. The root suite preceded
the final inline-layout and percent-sign correction; affected suites were rerun.

The full 550-page PDF compiled successfully. All 15 revised chapter pages
197–211 were visually read after final print edits, as were affected contents,
figure-list and bibliography pages 12, 28, 538–540. The revised chapter has no
undefined references or overfull boxes. Existing empty-year BibTeX warning for
TedrakeMultibodyEnergy is outside this chapter and remains recorded.

The web chapter has 260 math expressions, 36 displays, two loaded figures with
alt text, all 12 historical heading destinations, no duplicate IDs and no broken
local fragments. Complete final desktop reading: all 28 overlapping captures
visually read. Original detailed QA covered 132 equation/figure cases and 28
keyboard-scroll checks; all 94 narrow captures were visually read. Final inline
polish added 36 targeted detail cases, 12 keyboard checks and 48 captures, all
visually inspected. All 14 width/theme cases pass from 320 to 1920 pixels.
Inline overflow initially missed by the page-width check was corrected by
splitting chains and promoting five long calculations to displays.

The final desktop read caught nine percent signs removed by the scratch
TeX-to-Quarto conversion inside math. The paired regression failed only on the
web edition before escaping those signs; the correction preserves the PDF and
adds a rendered percent-symbol check. All nine percent glyphs and their assistive
MathML text pass; the repeated 14 width/theme checks show zero inline overflow.
Twelve final percent-context captures were inspected. Initial scratch probes
incorrectly queried empty CHTML text nodes; the corrected probe checks rendered
glyphs and assistive MathML. This demonstrates why successful MathJax
parsing and a clean page-width report alone do not establish correct mathematics.

The canonical 14-case site verifier passes after supplying its page-record
helper a relative output path. An initial scratch manifest incorrectly passed
an absolute path and therefore tested 404 URLs; those failures remain in the
scratch log, not attributed to the chapter. Only the deployment's exact obsolete
polyfill removal was applied to the selected generated HTML. Custom axe checks
have no serious/critical findings, but shared moderate landmark-unique findings
remain. Earlier browser console errors/warnings are not reported as clean.

## Delivery Context and Remaining Work

Motor-learning PR #4330 is merged and published as
8c383f9cfb46cc19be832ce81e8fe356279c29c7. Exact live artifact 10133005315 was
checked record by record (956 records, 239 routes, all passing). Nonlinear repair
#4329 is published as 1fe7997e with exact artifact 10131240380. Motion/rotation
publication is verified through 4cf3514d, artifact 10130399466.

The six render-generated trust side effects were inspected and restored: run
dates, platform-dependent source hashes and JSON formatting only. Claim-audit
freshness passes. The portable devlog checker reports only preserved peer
DL-#3903 missing SHA and DL-#3902 missing PR/Last verified.

Only audit 0897c9a0 and implementation 762a5b51 were replayed after 71e80bb9
onto motor squash 8c383f9c before first push. Parent trees and resulting
implementation trees were identical. Final implementation is
88fc30eae28ae0b9bfc463e5a47c5ce504a38087. All normal commit/push hooks pass.
PR #4332 references Fixes #4331 and has agent/scientific labels; SPEC has one
actual-PR row. Protected checks and exact publication remain. Preserve peer
joint-friction work and immutable publication. No subagents or Git mutation
during QA. The corpus has 405 rows and 210 Indexed statuses; partial sources
and whole-book consistency audits remain additional work. The next longest
unreviewed chapter is shaft flexibility, followed by passive dynamics.

Protected PR #4332 merged normally as fd464eed3dc493b3e31363cfb1396ac69e849142.
Main CI 34432094338 and textbook build 34432094441 passed. Deployment
34432094332 was cancelled; descendant run 34433303512 remains in progress.
Exact live publication is pending and is not inferred from the merge.

Production verified through a81f99c06c34d3a98ad215a26218537861e49d1a, whose only
changes beyond the muscle squash are fleet policy documentation. Deploy
34433303512 succeeded; exact live artifact 10135966540 passed all 956 records
across 239 routes, including 239 axe route checks, with HTTP 200, no inspection
failures, no axe findings, no retries and no transient responses.
