# Muscle Forces to Joint Torques: Review Audit

## Scope and Current State

Issue #4369, under epic #4009 and corpus #4021. September12,2026.
Both original Chapter16 sources were read completely: print5283 and web4636
approximate original whitespace words. Both editions have now been rewritten. The initial sixteen-page isolated print preview was fully read; final whole-book and web visual review remain in progress. The chapter is not complete. Preceding strokes PR4368 merged at93bbfd29 after its precision repair passed all protected checks; exact deployment verification remains pending. The earlier failed reproduction run34714267081 is retained as failure history, not current PR status.

## Original Source Findings

- The print and web matrices use rows for muscles yet interpret columns as muscles;
  their displayed transpose product gives (25,22), not the stated (31,12).
- With positive tensile force and length increasing on lengthening, skeletal work
  is minus tension times length change. Define L=dell/dq and A=-L^T explicitly;
  do not copy a transpose-only force relation from a spatial-force Jacobian.
- Axis torque needs the projection of r cross F onto a declared unit axis.
  A scalar distance and a position vector cannot share an unexplained symbol.
- The two biceps examples disagree: print asserts maximum moment arm near full
  extension; web asserts roughly90degrees. Neither generic anatomy numbers nor
  lower-limb Delp1990 establish personalized elbow moment arms.
- Nullspace algebra alone does not ensure nonnegative, capacity-bounded forces.
  A null direction may redistribute synergist force rather than co-contract.
  Co-contraction does not by itself prove asymptotic stability or useful impact
  performance. Tangent stiffness must specify held states, geometry and feedback.
- Net inverse dynamics is an estimate conditional on inertial/contact models;
  EMG is activation-related electrical evidence, not direct tensile force.
  Dynamometry does not isolate every individual muscle and need not be invasive.
- State-dependent torque feasibility, floating-base/contact equations and actuator
  states matter. A torque-controlled model does not prove unique human recruitment
  or establish what objective the nervous system optimizes.
- Biarticular force produces coupled torques; signed powers determine whether it
  generates, absorbs or transfers work. Tendon storage is a separate energy term.
- Unsupported grip percentages, muscle-specific strong/weak-grip leverage,
  forearm/wrist axis equivalence and stiff-at-impact prescriptions need evidence
  or withdrawal. Triceps heads and wrist/finger flexors need anatomical precision.
- Fix web heading/list artifacts and all eleven exercise premises and answers.

## Primary Source Reading, Precisely Bounded

Sherman, Seth and Delp2013 author PDF, DOI10.1115/DETC2013-13633:
https://nmbl.stanford.edu/wp-content/uploads/ShermanSethDelp-2013-WhatIsMuscleMomentArm-Final2-DETC2013-13633.pdf
Downloaded763426bytes through a plain public HTTP request after web tool403.
Full extracted text of nine pages, including references, read. Pages4and5 were
also rendered and inspected; page6render exists but was not yet visually read.
Relevant scope: workless-path assumptions, coupled coordinates, generalized speeds
and force transmission. It concerns modeling definitions, not validated golf advice.
Its displayed equations2/3 have a positive excursion derivative; do not claim this
paper alone verifies our negative lengthening convention. Reconcile using explicit
skeletal work and independent current implementation documentation.

OpenSim FunctionBasedPath API4.5 documentation, Detailed Description and force
method parameters, read: negative length derivative, lengthening-speed convention,
workless-path assumptions, generalized-speed distinction and positive tension.
https://opensim-org.github.io/opensim-moco-site/docs/1.3.0/html_user/classOpenSim_1_1FunctionBasedPath.html

Rice NMSM Surrogate Model Creation complete technical page read. It explicitly
uses a negative length derivative and illustrates consistent polynomial length,
velocity and moment-arm functions. No empirical golfer inference is supported.
https://nmsm.rice.edu/guides-and-publications/tool-overviews/treatment-optimization/surrogate-model/

PMC full-text URLs returned bot checks; web-tool author PDF failed403 and another
university copy cache-missed. Plain public author-PDF download succeeded without
credentials. Van den Bogert2011 abstract/search result located, not full text read.

## Next Actions

Finish figure typography and review all final PDF chapter pages and the full web
reading, then run the production route verifier and bind durable evidence. The
paired rewrite and nine independent mechanics checks are implemented. Preserve
original destinations and the precise primary-source reading boundaries above.
A further source reread identified notation to clarify before publication: use
a distinct speed-coordinate contact Jacobian in the whole-body equation and
define its relation to the coordinate-rate contact Jacobian.
Do not commit downloaded papers/screenshots as redistributable deliverables.

## Elbow Geometry Source: Complete Reading

Murray, Delp and Buchanan1995, Journal of Biomechanics28(5),513-525,
DOI10.1016/0021-9290(94)00114-j. Author copy:
https://nmbl.stanford.edu/publications/pdf/Murray1995.pdf
Retrieved879802bytes. Thirteen scanned PDF pages have no extractable text; all
were rendered and visually read, including the blank fourth page, figures, tables,
methods, discussion and references. This is a two-cadaver study (ages90and82)
and a geometric model, not measurements of golfers. It supports configuration
and forearm-position dependence, not a universal maximum at full extension.

The paper's methods and Figure4 caption explicitly negate the tendon-excursion
slope for their positive-flexion convention. Its displayed equation1 omits that
minus; the chapter must declare its own sign and check skeletal virtual work.
The discussion identifies path approximation, measurement and sample limitations.
Do not turn model/specimen discrepancies or population-size unknowns into coaching
rules. The author publication list located this exact PDF; a general lower-limb
model citation was inadequate evidence for the chapter's elbow-specific numbers.


## Independent Mechanics Checkpoint

Eight tests in `tests/test_muscle_torque_rigor.py` pass locally (September 12).
They verify constructed mechanics examples, not the still-unrevised chapter or
empirical golfer parameters. Black100 formats the file; no production utility is added.

1. A rotating insertion and fixed anchor give the same torque from the physical
   cross product and minus tension times a central finite difference of length.
2. With muscle-by-coordinate L=[[-.05,0],[-.02,-.04]], tensions (500,300) N
   produce (31,12) Nm through -L transpose. At speeds (2,-3) rad/s, path rates
   are (-.10,.08) m/s and skeletal power is 26 W, equal to -F dot length rate.
3. The second muscle alone produces joint powers (12,-12) W at speeds (2,-1),
   but absorbs 24 W at (2,-3). Biarticular anatomy does not determine power flow.
4. For A=[[.04,.02,-.03],[0,.03,.02]], F0=(100,200,50) N, capacity
   (400,300,250) N, and null vector (13,-8,12), F0+t*n preserves torque
   (6.5,7) Nm. Nonnegative capacity bounds restrict t to [-25/6,50/3].
5. Independent linear programs give coordinate maxima (22,14) Nm, yet that
   simultaneous torque pair is infeasible. A rectangle of separate limits is
   insufficient for coupled muscle feasibility.
6. The constraint q=(s,2s) changes effective arms to (.05,.10) m and reduced
   torque to 55 Nm; virtual work agrees with the unreduced torque projection.
7. A fitted arm field (.02+.01*q2,.01) has a nonzero closed-loop work integral
   (-1 J at fixed 100 N tension around the unit square). It cannot be minus the
   gradient of one smooth, single-valued path length on that region.
8. A taut positive-stiffness spring between an anchor and rotating insertion
   has negative angular energy curvature at its maximum-length alignment:
   Kq=k*(length derivative)^2+F*(length curvature)=-20/3 Nm/rad.
   Finite differences of energy confirm the geometric term. Positive material
   stiffness alone does not establish a stable joint equilibrium.

These independent examples will guide the correction and worked exercises.
For configuration-only workless paths, derive skeletal power explicitly; for
moving guides or explicit time dependence, include the additional guide work.
Do not promote a fixed-state elastic example into a universal physiological law.

## Upper-Extremity Model Source: Bounded Reading

Holzbaur, Murray and Delp (2005), DOI10.1007/s10439-005-3320-7, author PDF:
https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf
The prior reading covered extracted pages1-3,5-9 (one figure caption truncated),
and pages10-11 through the discussion/conclusion. Table page4 was subsequently rendered and fully inspected; its footnotes distinguish measured architecture from compartment PCSA distribution fitted to maximum isometric moments. Full visual figure/reference review remains outstanding. The model has15 degrees of freedom
and50 muscle compartments; it omits intrinsic hand muscles. Muscle parameters
were partly adjusted against joint-moment measurements, while selected coupling
comparisons offered separate checks. Prescribed scapular motion, generic geometry
and tendon-slack-length sensitivity limit inference. This is useful evidence for
stating what was calibrated and tested; it does not validate golf grip prescriptions.

Checkpoint root validation: 5305 passed,29 skipped,132 deselected,59 warnings; exit0. Log: `muscle-checkpoint-root.log`. Six unrelated generated outputs were checked and restored: date-only JSON or formatting/line endings.


## Paired Rewrite and First Render Review

September12: rewrote the full print and web sources (approximately5561 and5742
whitespace words before final notation refinements). Preserved every original
explicit print label and box key, plus all35 original web heading destinations.
Added five primary-source bibliography citations through four new entries and the
existing Holzbaur2005 entry. No invented publication year for the undated Rice
technical page: its bibliography explicitly uses n.d. and records access date.

The chapter now derives the negative-transpose map from positive tensile work;
checks a nonsymmetric two-joint example against power; derives force-box
feasibility, a bounded null-space family, a stiffness counterexample, coupled
coordinate forces and biarticular power; qualifies torque-driven control and
inverse estimates; and replaces unsupported grip/anatomy prescriptions with
contact mechanics and a testable measurement design. All eleven exercises have
worked answers. A ninth independent test verifies the synergist exercise's
750-1000 N interval and its60 Nm capacity limit.

The new SVG/PDF figure shows the feasible torque polygon and two different signed
power outcomes for one muscle. Its reproducible drawing script is
`build_muscle_torque_figures.py` in this directory. Scientific parameters are
constructed, not fitted golfer data. The first full-size figure was visually
inspected; typography in the scaled print figure warrants further refinement.

Both book-local HTML and root-selected website HTML render successfully.
`render_selected.py` restores the exact root configuration after the selected
render. Only `strip_legacy_math_polyfill` normalizes generated HTML; never call
the pruning program against the local docs tree.

The initial isolated PDF had two overfull headings; explicit print-only heading
breaks resolved them. BibTeX and two resolution passes now produce a16-page
preview with no overfull boxes or unresolved-citation warnings. Every initial
page was visually read. That review prompted explicit units on both force bounds,
consistent units in the synergist answer, a speed-coordinate contact mapping,
and darker example title bars. Final changed pages require rereading.

Full textbook compilation with BibTeX and two resolution passes succeeds:
`muscle-torque-full-book.pdf`,535 pages. This source file appears as Chapter13 in
the print book, with the chapter at zero-based pages178-192; do not confuse the
filename ch16, isolated preview Chapter16, root website or nested book numbering.
Only the changed chapter is currently being audited, not all535 pages.

Playwright CLI web QA completed:163 expressions,16 displays, no duplicate IDs or
broken internal fragments, and the new image loaded with descriptive alternative
text. All14 width/theme cases (320,375,390,768,1024,1440,1920 in light/dark) have
no document overflow or math errors. All68 display/figure region checks and24
keyboard-scroll checks passed. Only the existing moderate landmark-unique axe
finding remains; no serious/critical findings. Twenty-nine full reading captures
were produced but have NOT yet all been visually reviewed. Preserve this
boundary; passing automation does not equal complete reading.

Browser session muscle-torque-review is closed. The CLI stores scratch beneath
this directory. The first revised root suite (`muscle-torque-revised-root.log`) finished with
5317 passed and one failure: the figure inventory still expected eight TikZ
figures. The actual replacement removes one TikZ sketch, adds its shared PDF/SVG
pair and reduces the book's missing web figures from seven to six. Updated the
explicit inventory counts and added checks for Chapter16 parity, its preserved
figure label, PDF target and both asset files. All32 focused figure-audit and
mechanics tests pass. The full rerun is `muscle-torque-checkpoint-green-root.log`.
Configured CI mypy passes all91 files; Ruff and Black100 pass the three changed
Python files. The rerun exits0:5318 passed,29 skipped,132 deselected,59 warnings in197.95s;
coverage79.35%. Six unrelated generated outputs were restored after verifying
JSON changes were only generated_on or text changes were only line endings.
The complete revised web source was reread, and reading captures00-10 were
visually inspected. Capture09 confirms the figure needs larger labels at normal
reading size. Captures11-28 and final print pages remain unread. The captures
also show a stale highlighted table-of-contents entry; verify with settled live
scrolling before deciding whether this is a capture timing issue or a site defect.
No protected PR exists for4369 yet. Remaining acceptance work: final typography,
complete final PDF/web reading, all required checks, durable evidence, regular PR,
protected merge and exact live-publication verification.

## Preceding Delivery

PR4368 is merged through ordinary protection at
93bbfd29d3e69147dedef153749a47a1b650dfe9 (September12,20:36:25Z).
Every exact-head check passed for ec994491, including Linux Python, E2E and
quality-gate. Its live deployment still requires independent verification.
The paired rewrite was committed and pushed as655b6514. Main squash93bbfd29
was then integrated at84640cab; conflicts affected only our own status records,
and scientific source/test bytes remained identical to the tested checkpoint.


## Latest Typography, Contact Notation and Citation Checkpoint

The figure now uses16-point labels on a10-inch canvas (approximately8.8-point
labels at5.5-inch print width), larger legends and two-line titles. Both panels
remain shared SVG/PDF outputs; the SVG writer removes trailing whitespace.
The final figure was visually inspected at full size, in final web reading
capture09, in mobile light-left/dark-right detail10, and on physical PDF page184
(printed page154). Labels are substantially more readable without clipping the
full figure. Horizontal scrolling retains both panels on narrow screens.

Both sources now distinguish the speed-coordinate contact Jacobian J_v from
the coordinate-rate Jacobian J_c: J_v=J_c N, hence J_v^T lambda=N^T J_c^T lambda.
The actuator map also explicitly produces forces conjugate to generalized
speeds. Final web reading capture12 was visually read for this clarification.

Latest full root run `muscle-torque-final-root.log` exits0:5318 passed,29 skipped,
132 deselected,59 warnings in204.43s; coverage79.35%. Changed Python lint and
Black100 pass, title audit636 passes, and bound evidence remains current.
Six generated outputs were restored only after verifying date-only JSON or
newline-only changes. All local verification sessions and the browser are closed.

The latest selected root website render succeeds. Final browser QA log is
`muscle-torque-final-browser-qa.log`:170 expressions,16 displays,14 width/theme
cases,68 regions and24 successful keyboard scrolls. Only the existing moderate
landmark-unique axe finding remains. It generated29 NEW reading captures named
`muscle-torque-final-reading-00.png` through28. Only09 and12 have been visually
read from this final set; the earlier00-10 reading used the previous rendering.
Do not conflate either partial reading with a complete final article review.

The535-page full-book preview was NOT citation-complete. Although BibTeX exited0,
its search path read stale chapter auxiliary files from the source directory,
omitting the four new references. A first BIBINPUTS correction still searched
that directory ahead of the current output. The successful correction runs
BibTeX from `docs/development/technical-review` with the current directory FIRST:

```powershell
$priorBibInputs = $env:BIBINPUTS
try {
    $env:BIBINPUTS = '.;C:/Users/diete/Repositories/AffineDrift-technical-review/articles/The_Physics_of_Golf;'
    bibtex muscle-torque-full-book
} finally {
    $env:BIBINPUTS = $priorBibInputs
}
```

Then run two pdflatex resolution passes from the book source directory with
jobname muscle-torque-full-book and the same absolute output directory. Logs
`muscle-torque-final-book-pass5.log` and pass6 record the corrected build. The
final536-page PDF has all four new bibliography entries and no undefined
citations. The changed chapter's log has no overfull boxes; unrelated chapters
still have overfull warnings and are not certified by this review. The chapter
remains zero-based pages178-192 (physical pages179-193, printed149-163).
Final PNGs are `muscle-torque-final-print-179.png` through193. Only180 and184
have been visually read so far. Page180 visibly resolves Murray1995 correctly.

Remaining work: read the complete final chapter PDF and website, inspect the
new bibliography entries in the full-book back matter, check settled TOC
highlight behavior, run the production route verifier, save durable review
evidence and reconcile inventory, then open a regular PR and verify protected
merge/publication. The broader corpus remains unfinished. Preceding strokes
deployment34717587828 has completed build103617517729 and is running deploy
job103620128020; this is not yet evidence of live publication.

## Completed Local Reading and Delivery Checkpoint

The final reading boundary now includes all29 web captures00-28, all fifteen
chapter PDF pages179-193 and the four new bibliography entries on530-533.
The previous paragraph's partial reading status is historical. The full536-page
book is not certified: only this chapter and the named bibliography pages were
visually reviewed. The final image28 includes all five web references without
clipping or unresolved citations.

The first attempt to prevent an orphaned exercise line, clubpenalty10000 before
the enumerate environment, had no visible effect. It was removed. An explicit
tcolorbox break before exercise4 now keeps the question on physical page192.
The complete changed ending was reread in `muscle-torque-explicit-break-191.png`
through193. Build `muscle-torque-explicit-break-pass1.log` exits0, remains536
pages and has no unresolved citations or changed-chapter overfull boxes.

Production-style gate47646 was reaped with exit0. Its14 records were each
checked for HTTP200, pass, empty record/inspection failures, zero overflow,
one successful navigation attempt, no retries and no axe violations. The gate
scans axe once for the route; the separate final browser QA scans both themes
and retains the existing moderate landmark-unique result. Do not describe
that as fourteen independent axe scans.

A fresh browser `muscle-torque-nav` reproduced incorrect settled TOC selection:
clicking the muscle-Jacobian link reaches its heading but highlights Grip
Stiffness and Impact. The generated Quarto tracker compares pageYOffset with
section.offsetTop despite positioned parent sections. Example: the late grip
heading has offset2037 but document top18280. This is now native subissue4370
under4009; no shared site files were changed. The browser is closed. This
known presentation defect is explicit in the durable scientific review.

Durable records are `reports/technical-review/muscle-torque-complete-review.md`
and `muscle-torque-render-verification.json`. The latter retains structured
browser evidence, every local route record and actual source SHA-256 values.
An actual committed implementation revision must be bound in the inventory
before recording the route as reviewed. Hosted CI, protected merge and live
publication remain separate gates. Ruff, Black100(706), configured mypy91 and
title636 pass; the fresh delivery root test result is recorded in the handoff.

Strokes delivery is now independently verified: exact run34717587828 for
93bbfd29d3e69147dedef153749a47a1b650dfe9 succeeded. Downloaded live artifact
10305443224 contains956 unique viewport/theme records across239 routes. Every
record was inspected: HTTP200/pass, no inspection/record failures, overflow,
navigation retries or axe violations. Both the strokes article and critique
have all four expected records. DL-#4358 is shipped; its governed critique
remains open. This supersedes the earlier pending-deployment observation.


## Deployment-Evidence Boundary Repair

The completed review/report checkpoint447634a4 is pushed. Inventory binding
first exposed a deployment-survival failure: root run96214 had5317 passes
and one failure because its evidence included the drawing script under docs/.
That directory is generated output and cannot hold durable bound evidence.
The builder is now `scripts/build_muscle_torque_figures.py`, with its CLI root
adjusted to preserve the same publication destination. Its exact SVG drawing
bytes match the reviewed asset after excluding date metadata. Direct mypy
exposed pyplot.Axes as an invalid exported type; importing matplotlib.axes.Axes
fixes typing without changing the plot. Direct mypy, Ruff and Black pass;
all51 boundary/inventory/mechanics/figure checks pass. No pruning gate was
weakened. The source relocation must be committed before binding its real SHA;
the subsequent full root run remains required before push.


The source relocation is now committed as a2d482bff6252be13cbced65cddb3b3f353027ac.
All nine declared evidence paths and hashes were independently compared with
that commit before updating review_commit and all four verification_commit
fields. Original and rebuilt PDF figure rasters are pixel-identical at1500x780;
SVG drawing bytes differ only in timestamp metadata. The route retains an
open p2 TOC finding for4370. The repaired full root gate is the final local
push gate; its exact result is recorded in the current handoff and DL-#4369.

Final repaired root `muscle-torque-boundary-root.log`:5318 passed,29 skipped,
132 deselected,59 warnings,187.39s,coverage79.35%; session78917 reaped exit0.
All local verification handles are closed. Generated unrelated timestamp/format
drift was compared semantically with HEAD before restoring only those six files.
