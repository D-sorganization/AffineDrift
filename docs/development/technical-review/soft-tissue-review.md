# Soft-Tissue Mechanics and Evidence Review

Issue #4315; native child of #4009, corpus #4021, Physics #4054.
Worktree C:/Users/diete/Repositories/AffineDrift-technical-review, branch
fix/4315-soft-tissue-mechanics, starting at parent PR #4314 head
082f9589113fcb51e7ba97c863a0cefd64bd2a45. Replay only this batch after that
base when the parent merges. No subagents. Codex lease, session
technical-review-20260906, expires 2026-09-09T19:33:34Z. The central presence
CLI/guide are not available locally; the existing claim/lease workflow applies.

## Complete Original Reading

Both complete sources and all seven exercises are read: 6,628 indexed print
words and 6,208 web words. Original source copies and 31 historical rendered
destinations are saved in local scratch. The web edition adds repeated
illustrative qualifiers and a medical disclaimer but retains the principal
mechanical errors and unsupported conclusions. Those findings informed the paired
rewrite and independent checks below.

## Findings and Derivation Plan

The printed oscillator parameters m=1 kg, k=5000 N/m and c=200 N s/m give
zeta=sqrt(2), not 0.38. Its roots are approximately -29.2893 and -170.7107 per
second; a released displacement with zero velocity does not ring. A prescribed
base and a freely moving two-mass system also have different relative modes.
The latter has reduced mass m_r m_w/(m_r+m_w). Amplitude of acceleration does
not specify its frequency content. The original 500 m/s² upper-arm estimate is
not established by a club or whole-body model citation.

For base displacement X_r exp(i omega t), the Kelvin-Voigt tissue response is
H=(k+i c omega)/(k-m_w omega²+i c omega). External dynamic mass is m_r+m_w H;
the old formula loses the numerator damping term. It is a complex harmonic
response, not a literal time-varying mass or an explanation of elite athletes.
Derive reaction, phase, mean dissipation and low/high-frequency limits, then
compare with direct ODE integration. A closed two-mass model must preserve total
momentum and account for actuator work, stored energy and dissipated heat.

Skin movement is a physical deformation and a measurement error relative to a
bone target; it is not necessarily separable high-frequency noise. Filtering
cannot uniquely recover bone motion or tissue center-of-mass motion. A 1 cm
sinusoidal marker displacement has acceleration amplitude A(2 pi f)², which is
39.4784 m/s² at 10 Hz. Include a same-frequency ambiguity example and distinguish
accelerometer specific force from coordinate acceleration.

Organ totals double-count or mislocate mass (including whole-body blood in the
torso), and centrifugal acceleration does not determine tissue displacement.
Use a declared rotating-frame point model only, with Coriolis, angular
acceleration and translational-frame terms included when applicable. Do not
retain 2–3 cm displacement, 5–10% inertia shifts or universal accuracy tables
without direct evidence. Express angular momentum with internal relative motion;
I dot(omega)+dot(I) omega is only a special scalar case. Never append the full
dot(M) qdot to an already consistent Coriolis vector. Derive the augmented mass
matrix and gravity from one coordinate/energy model.

Pressure acts through a vector surface traction and a pressure difference.
Vertical force uses projected area, not the curved diaphragm's total area.
Uniform pressure over a complete closed surface has zero net force and torque,
while individual regions can carry substantial loads. Generalized pressure work
is p dV. A volume-preserving ideal twist has no direct hydrostatic pressure
torque; wall tension, geometry, prestress and muscle action can alter the full
structure's stiffness. Neither pressure times area nor local indentation
stiffness establishes spinal compression, dynamic stability, injury prevention
or club speed. Compare pressure support with the forces required to contain it.

Compliance stores energy; damping dissipates it. Raising stiffness at fixed
deformation changes stored energy and requires an energy source. X-factor is a
measurement convention, not a single tissue strain. All seven exercises need
resolvable assumptions and worked answers, replacing an unsupported clinical
training-prescription exercise with an evidence/validation design question.

## Primary Evidence and Reading Boundaries

- Pain and Challis (2006), DOI 10.1016/j.jbiomech.2004.10.036: complete main text
  and tables read from the author's 11-page accepted-manuscript deposit
  (two cover pages; manuscript pages 1–9). One man, two 0.43 m heel-first drops;
  tissue measurements came from separate controlled impacts. Parameters were
  partly fitted, and trunk tissue response lacked an independent measurement.
  Similar segment kinematics can accompany different computed loading; the
  study does not establish golf-specific tissue amplitudes or accuracy limits.
  Both figure images are also inspected on physical PDF pages 5 and 8. Source:
  https://s3-eu-west-1.amazonaws.com/pstorage-loughborough-53465/coversheet/17273561/1/pain20061.pdf.
- Stokes, Gardner-Morse and Henry (2010), DOI 10.1016/j.clinbiomech.2010.06.018:
  complete main text, equations and Table 1 read from the eight-page author PDF,
  https://www.uvm.edu/~istokes/pdfs/abd.pdf. Static model with specified pressure,
  curved muscle paths and an optimization criterion predicts unloading;
  discussion explicitly recognizes greater real coactivation and potential
  underestimation of compression. All figures are inspected on physical pages
  3–6, including the continuation of Figure 3 and Figure 4. Its stated
  0.6 kPa/Nm for 10 kPa and 60 Nm is arithmetically inconsistent; do not repeat
  that ratio. The conclusion also rounds 10 kPa to 70 rather than 75 mmHg.
- Hodges et al. (2005), DOI 10.1016/j.jbiomech.2004.08.016: complete public
  abstract and publisher experimental-design excerpt read. Three prone subjects,
  phrenic stimulation, posteroanterior indentation at L2/L4; increased pressure
  accompanies increased measured stiffness. Full paper not read. Source:
  https://pubmed.ncbi.nlm.nih.gov/16023475/.
- Shirley et al. (2003), DOI 10.1152/japplphysiol.00939.2002: complete public
  abstract plus publisher methods and discussion read through search retrieval;
  direct page opening failed. Eight subjects; composite posteroanterior response,
  respiratory tasks at held volumes. Both inspiratory and expiratory effort can
  increase stiffness; the paper explains confounding muscle activity and why
  this is not isolated intervertebral stiffness. Full results/figures not read.
  Verified PubMed record: https://pubmed.ncbi.nlm.nih.gov/12970374/.
- Nachemson, Andersson and Schultz (1986): complete public abstract and metadata
  read, https://pubmed.ncbi.nlm.nih.gov/3750086/. Four subjects, five isometric
  tasks, pressure/EMG measurements; four tasks had increased rather than
  decreased compression with Valsalva. Full paper not read; do not treat this
  small task-specific experiment as a general prescription either.
- Existing intra_abdominal_pressure_golf key resolves to a general 1997 McGill
  review, not a direct golf-pressure experiment. Existing haykowsky2003resistance
  is a 1996 three-case report, and bo2004pelvic a 2005 measurement review.
  Their broad bibliography notes are corrected after reading the complete
  Haykowsky and Bø public abstracts and selected McGill modeling/load-sharing
  passages. Full Haykowsky, Bø and McGill papers were not read. Stable keys are
  retained; dates in the actual entries remain 1996 and 2005.
- Fuller et al. (1997), DOI 10.1016/S0167-9457(96)00053-X: complete publisher
  abstract read; full paper unavailable. The overlapping skin/pin frequency
  content supports the limited filtering argument. No participant-level
  accuracy values or golf validation are inferred. Author metadata was checked
  against primary-paper references; direct publisher opening returned 403.

## Continuation

Initial RED run: 13 mathematical cases pass and three publication guards fail
against the unchanged originals. The tests independently integrate the closed
two-mass work/momentum balance and harmonic response, verify reduced mass,
coordinate-transformed gravity, pressure surface quadrature, reversible inertia
changes and stiffness/energy comparisons. Reuse the existing bibliography key
Stokes2010AbdominalPressure rather than adding a duplicate.

## Corrected Models and Validation

The final paired chapter derives the closed two-mass equations, prescribed-base
transfer function and work balance; separates physical tissue motion from
measurement ambiguity; includes complete rotating-frame acceleration and relative
angular momentum; derives projected pressure forces, closed-surface resultants
and pressure work; and reconstructs augmented mass, gravity and time-dependent
Euler–Lagrange equations. The explicit coordinate-dependent mass counterexample
also verifies energy conservation without an extra total mass derivative.
Seven exercises have seven corresponding worked answers. Unsupported anatomical
numbers, performance percentages and clinical prescriptions are replaced by
identified assumptions and bounded evidence. Two reproducible PDF/SVG figures
replace the unpaired schematic. Existing section destinations and print labels
are preserved; cross-chapter links connect estimation, spine, damping and synthesis.

Root regression: **4,991 passed, 29 skipped, 131 deselected, 50 warnings** in
336.41 s, **92.65% coverage**. Final affected checks: **40 passed** (17 new
mechanics/publication cases and 23 figure-audit cases). Content checks: **130
passed, 4 skipped**. Static CI contracts: **34 passed**; title case: **633
sources passed**; site-link gate passed. Configured Black checks pass 680 files
plus the figure generator; Ruff, mypy (88 sources) and tracked code-quality
checks pass. The first quality pass requested a named gravity constant; that
style-only correction passes the final focused and style checks. Test-generated
trust outputs were inspected and restored to their pre-run state.

The final five-pass print build has 552 pages. Complete physical chapter pages
303–317 (printed 275–289), the following part divider, relevant contents and
figure lists, bibliography and index were visually read. Two long headings and
one text line initially exceeded the print margin and were corrected. The final
chapter has no overfull box or unresolved citation/reference. A final bibliography
note cleanup leaves every chapter page's extracted text unchanged; only physical
pages 534–543 reflow. All ten final bibliography pages were visually read without clipping or overlap.

Complete web reading uses 23 overlapping desktop captures. Structural checks
verify **181 math expressions, 21 display equations, 31 historical destinations,
two loaded figures with alt text**, no duplicate IDs, raw math delimiters or
broken local fragments. Fourteen width/theme combinations (320–1920 px) have no
page overflow or MathJax errors. Serious/critical axe findings are zero; the
inherited moderate landmark-unique finding remains. Existing external-resource
CSP/font console messages remain, not failed mathematical rendering.

Eight long inline groups at 320 px have both ends visually inspected in both
themes and keyboard movement verified; all 12 overflowing display/figure right
edges are inspected. Eight critical dark-mode display crops are read. Figure
regions support keyboard scrolling and full-size opening. Visual reading caught
a missing blank line before the first exercise; the final rendered DOM now has
seven direct list items in each of the question and answer lists, and the
corrected numbered questions were visually read. The print answers and web
answers match.

## Protected Delivery

Implementation checkpoint: SELF. Parent PR #4314 remains open at 082f9589 with
normal squash auto-merge enabled. All textbook jobs and static/spec/link checks
pass. CI Standard 34383426258 attempts 1 and 2 fail before Python tests at the
Google Chrome apt repository with a package-index Hash Sum mismatch. The e2e
job is cancelled; no article or test failure is shown.
An attempted job retry during the still-running workflow was rejected, then the
normal failed-job retry was accepted after completion. Do not bypass checks.
The #4313 lease was renewed through 2026-09-09T20:11:26Z.

Parent #4314 subsequently merged at 2026-09-09T18:23:52Z as
fc76f2e1d214fd66101e616ae94fce6d31d6af26. A separate contributor added
the apt-source/lock correction in 66681652 and triggered 6373aff3; CI Standard
34386484598 and all required checks passed. Preserve those changes. Commit
this isolated batch, replay only its commits after 082f9589 onto updated main
before first push, then create its focused PR against main. Complete protected
checks/review, merge normally and verify exact production evidence. This
chapter does not complete the corpus: 221 of 405 index rows remain Indexed;
other rows can represent partial audits. No subagents, immutable-source edits,
managed-policy edits or branch operation during local QA.

Delivery checkpoint: ready PR #4317, https://github.com/D-sorganization/AffineDrift/pull/4317, targets main. Implementation
0f89dad6529a314644abc9f93adc613a8d3c8661 replays only d75c7ec2 after 082f9589 onto fc76f2e1.
The before/after comparison differs only by inherited CI and managed-policy
changes; all reviewed content and assets are identical. Normal commit/push
hooks pass. This documentation checkpoint adds the single actual PR-keyed
SPEC row and updates the current implementation handoff and development log.
