# Textbook Energy Transfer Review — Issue #4320

## Scope and Current State

Both complete original editions of Physics of Golf Chapter 10 and all six
exercises were read. Original indexed lengths are 6,507 and 5,530 words. This
is a distinct textbook correction following article #4202/#4205. The immutable
articles/proximal_distal_energy_transfer/ publication remains untouched.

Issue #4320 is a native child of epic #4009 and references #4021/#4054.
Claim was clear; codex lease for session technical-review-20260906 expires
2026-09-09T21:37:23.216478Z. Branch fix/4320-textbook-energy-transfer starts at
parent #4319 head 4f8ce5a3e254a4bc18f7b5b3c7c87c53f0b14a9d. The complete paired
correction, shared examples, two figures and six worked answers now pass final
local validation. Protected publication is next. The complete corpus remains
unfinished. The source filename is ch10, while the compiled book numbers this
as Chapter 11 because an earlier inserted chapter changes the sequence.

## Confirmed Corrections

Mechanical energy conservation needs a closed ledger of active and external
work, stored potential and losses. Gravity is counted either as power or as
potential change, never both. qdot.T C qdot is generally nonzero: it cancels
half qdot.T Mdot qdot in the kinetic-energy derivative. Coupling entries are
not independent segment-energy sources.

The editions disagree on two-link kinetic energy and omit essential COM,
relative/absolute-rate, quadratic and gravitational terms. Use explicit
absolute angles from downward for the shared RodPair implementation and a
constant chart map for relative-coordinate derivation. State the central
inertias and mass-center offsets separately from joint inertias.

Interface force power uses the shared hinge velocity while the ideal contact
remains enforced. Segment COM velocities differ. Equal/opposite interface
powers can be nonzero; direction is state-dependent. Wrist actuator power is
torque times relative angular rate; club-side moment power uses absolute club
rate. A stationary support can exchange impulse without work. Moving supports,
sliding contact, compliance and impacts require their own balances.

Original phase snapshots do not specify a valid triple-pendulum trajectory.
A 36 J decrease cannot identify eccentric braking or particular losses without
a work ledger. At zero total kinetic energy, the club fraction is undefined.
Potential-energy fractions depend on the reference. The print budget has
115 J where prose and web use 200 J; adding 100 J from gravity contradicts
the stated 15 J elevation energy and double-counts stored potential.

Lag is an angle, not a constitutive energy reservoir. An ideal lock with zero
relative speed need not store energy. Removing a lock does not remove the
hinge or create energy; imposing a lock at nonzero relative speed requires an
impulse/reset or finite actuator model. Different starting energies cannot
isolate a timing intervention. 150/60 in energy gives sqrt(2.5) in speed for
the same one-dimensional inertial model, not a doubling.

Sequential peaks, minimal inertia, passive late downswing, hip-drive advice,
X-factor storage and generic efficiency numbers are not consequences of the
identities. Define compared quantities, body/system boundaries, signed work,
positive work, stored energy and the outcome event. Angular acceleration can
coexist with total segment-energy loss. Residual body motion is not synonymous
with dissipated heat. A video lag angle alone cannot predict club speed.

## Independent Calculations and Implementation

New src/tools/energy_ledger_examples.py reuses RodPair dynamics but computes
COM kinetic/potential energies, their physical derivatives and Newton-force
interface power independently of the generalized power identity. Central
rotation, translating COMs, gravity, base and relative-hinge motors are explicit.
The helper is a teaching model, not an anatomical or metabolic estimator.

Meaningful RED: six failures and three passes. Four failures were the absent
ledger routine and two were paired-publication boundaries. The seven mathematical
cases now pass; the two publication guards remain pending until the rewrite.
No full regression has run for this batch. Existing article tests were read as
cross-checks; they are not substituted for independent new-helper validation.

Two unit rods with no gravity or motors, absolute angles (0,-pi/2) and rates
(2,2), have total energy 10/3 J, arm 2/3 J, outer rod 8/3 J and interface power
+1 W into the outer rod. Mirroring the second angle gives -1 W. A solve_ivp
trial (rtol 1e-11, atol 1e-13) preserves 10/3 J over 2 s; the outer fraction
rises from 80 percent to approximately 99.98 percent at 0.5 s, then decreases
to 58.09 percent at 1.75 s. This is a declared free mechanism, not a golf swing.
The aligned braking counterexample gives accelerations (-12/7,18/7) in absolute
coordinates and segment mechanical powers (-8/7,-6/7) W.

A balanced hypothetical ledger can retain the original 0,25,87,115,115 J
stored totals by declaring cumulative work (0,25,90,120,120) J and cumulative
losses (0,0,3,5,5) J. These are bookkeeping values, not measured physiology.
For an isolated, collinear collision with masses 0.2 and 0.04593 kg, incident
speed 45 m/s and assumed restitution 0.8: final speeds 29.8724 and 65.8724 m/s,
initial 202.5 J, residual head 89.2360 J, ball 99.6491 J and lost 13.6148 J.
No swing-phase losses are added again to this collision ledger.

## Source Reading Boundaries

The official Nesbit and Monika Serrano 2005 article was reopened. Selected
methods/results/discussion text was read, and PDF pages 520, 523 and 524 were
visually inspected. The first page verifies Monika; the linked editable energy
bibliography incorrectly named Rafael. That name is corrected under this issue.
The book bibliography already has the correct author in key Nesbit2005b.

- https://www.jssm.org/jssm-04-520.xml-Fulltext
- https://www.jssm.org/04-4-520.p_d_f

Do not transcribe the printed paper's equations without reconciling conventions:
Eq. 3 prints reversed integration limits and a subtraction of strain energy;
Eq. 6 lacks the usual half for a linear spring. The chapter will state its own
stored-energy sign and derive its balance independently. This is a warning about
using those printed formulas, not a reanalysis of the paper's underlying data.

Tedrake's current multibody chapter was read specifically for the simple
point-mass double pendulum, manipulator/Christoffel identity, velocity-coordinate
map, bilateral constraints and joint locking. Other sections are not claimed
fully read: https://underactuated.mit.edu/multibody.html. Our distributed-rod
and interface-energy results are independently derived, with compatible limits.

## Paired Draft and Publication Inspection

The complete replacement is now written in both editions: approximately 4,700
print-source words, 26 displayed equations, two shared vector figures and six
exercises with six worked answers. Every original explicit TeX label is retained
at a corrected treatment of its topic. All 21 original web destinations are
accounted for, including colon-containing aliases. A browser check caught a
duplicate exercise destination caused by adding an alias identical to the
automatic heading ID; the converter now assigns that heading's ID directly.

The independent relative-chart check transforms the separately implemented
absolute-rod dynamics at four geometries and verifies M, both bias components
and both gravity components. Further checks close collision momentum,
restitution and energy, compare physical energies to the shared total and
verify that inputs remain unchanged. Combined new and existing energy tests:
31 passes. The first figure-parity run correctly detects the additional paired
figure: two stale total-count expectations fail while 32 other checks pass.
The directly read audit gives 35 print figures, 19 TikZ, 16 includegraphics,
35 labels, 17 detected web figures and 18 remaining unmatched figures elsewhere
in the book. The regression expectations are updated to those observed totals.

Style: Ruff and configured Black (684 files) pass; strict mypy checks 90 sources.
The quality checker identified a missing nested-helper docstring and two repeated
gravity literals. Those are fixed; the subsequent full tracked quality check
passes. Content 130 passes with four skips; static 34, titles 635 and site gate
pass before the final citation/link changes. Full root regression remains pending.

Initial complete print inspection covers physical pages 156--167 (printed
128--139), all equations, both figures, the 17-line program and every exercise
and answer. Eight navigation/reference pages 9, 11, 12, 25, 26, 27, 537 and 539
are also visually read. The 548-page book compiles with no chapter Overfull or
undefined warnings. Citation formatting was improved to parenthetical citations;
direct links/references now connect the constraint, inverse-dynamics, synthesis
and complete-swing treatments. Final rebuild/reread and full browser checks
remain in progress. Do not treat this paragraph as completed final QA.

The figure-list review also exposes unrevised neighboring claims: Chapter 7's
caption confuses contact power with generalized coordinate rates; Chapter 8's
caption implies constraint release establishes a universal cascade. These are
follow-ups in the unfinished corpus, not corrections claimed by this batch.
The earlier computational-brain figure-list entry also crowds its page number;
retain that layout item for the full-volume navigation pass.

## Final Validation and Remaining Delivery

Final root regression: 5,061 passed, 29 skipped, 131 deselected, 59 warnings,
549.21 seconds; configured coverage 79.17 percent. Final affected 34 and content
130/four skips pass; static 34, title 635, site gate, tracked quality, Ruff and
Black pass. Earlier full configured Black verifies 684 files and strict mypy
verifies 90 sources. The 17-line code extracted from both final publications is
identical and executes all energy assertions. Figure integration preserves
10/3 J within 2e-9 J over the declared two-second interval.

The final 548-page Physics PDF rebuild passes all five required stages. All
twelve chapter pages and eight affected navigation/reference pages were
visually read; final changed citation and cross-chapter-reference regions and
the exercises/answers were reread after the last build. The affected chapter
has no Overfull or undefined warnings. Other chapters are not certified by
this bounded review.

Complete web visual reading covers all 19 overlapping body captures. All
144 math expressions and 26 displays render; 21 original destinations resolve,
with no duplicate IDs, fragment failures, unloaded figures or page overflow.
Both themes pass all seven widths (320 through 1920 pixels), with zero
serious/critical axe findings. Six questions and six answers are verified in
the DOM. All 15 overflowing display/figure edges, both endpoints of twelve
inline regions in both themes, eight dark-theme equations and both code-block
ends are visually inspected. Figures, inline regions and code support keyboard
scrolling. The shared moderate landmark-unique finding remains a site-level
follow-up. Four fresh console errors are existing CSP-blocked Google Fonts
fetches; no HTTP error responses occurred in the bounded bibliography check.

The linked bibliography's corrected Monika entry is visually checked at
390 and 1440 pixels in both themes, with fourteen responsive/theme cases and
zero serious/critical axe findings. The original JSSM PDF URL was reopened and
successfully resolves to the same fourteen-page primary paper; no link change
is needed. Selected primary-source reading remains bounded as stated above.

Six unrelated generated trust files were regenerated by testing. Their changes
were inspected before restoring the baseline files. They are not all merely
date changes: the existing checked-in registries have stale protocol revisions
and an older atlas digest. The protocol summary and atlas bytes exactly match
HEAD; the actual baseline atlas SHA is cc26136004fc20b6606f7f6a95a0f77c009a20a90f1c5b0e5f5a8f516be311c4.
After accounting only for generated dates, JSON layout, protocol source-revision
fields and that atlas hash, all remaining contents match. These unrelated
baseline refreshes are excluded from the chapter commit, with no claim of new
research validation. Root configuration is restored; immutable sources and the
original checkout are untouched. No local test/build/browser processes remain
at this validation checkpoint.

## Protected Delivery Checkpoint

Implementation e4e1e3143860db3b9d680304b1c9f7c9ce827b1a was saved after all
local QA completed, then replayed alone after parent anchor 4f8ce5a3 onto
protected main c4c1fee6 as 989bf4580bf07b4032e0a3a987d774a59679b5c2. The old and merged parent
trees were identical. PR https://github.com/D-sorganization/AffineDrift/pull/4321
merged normally as 4aea9755711b462498d8cddae531dab3131f5989 at 21:19:27Z. All normal commit and push hooks
pass. The first push stopped on Bandit B102 in the untracked local publication
example executor; its reviewed-local-source boundary is now documented with a
specific B102 annotation. The normal push was rerun successfully. No hook was
bypassed. SPEC has exactly one actual-PR row. Final-head and main CI pass; exact production
verification for energy is complete as recorded below; never mutate Git during local QA.

Spatial #4318 / PR #4319 merged normally on 2026-09-09 at 20:01:13Z as
c4c1fee6db8915eee49a80b3572ece9ccfe57cd5. Main CI 34398520012, textbooks
34398520049 and performance 34398520065 pass. Deployment 34398520017 passes. Exact live artifact 10123816915 was downloaded and all 956 records across 239 routes were read and checked: zero failures, serious/critical axe findings, retries, transients or exhausted retries.

Soft-tissue #4315 / PR #4317 is published as b657813291e89def6269d9bb0f258a9e26c3dd8a.
Main CI 34393037135, textbooks 34393037136, performance 34393037120 and deployment
34393037121 pass. Exact live artifact 10121457373 passes 956/956 records across
239 routes with zero failures, serious/critical axe findings or retries.
Keep the corpus epic open; 217 indexed sources still await complete review.

Energy #4320 / PR #4321 merged normally at 2026-09-09T21:19:27Z as 4aea9755711b462498d8cddae531dab3131f5989. Final-head CI 34403603438 and main CI 34406274957 pass; main textbooks 34406274978 and performance 34406275036 pass. Deployment 34406274993 passes. Exact live artifact 10126445934 was downloaded and all 956 records across 239 routes were read and checked: HTTP 200, zero failures, serious/critical axe findings, retries, transients or exhausted retries; axe ran on all 239 routes.
