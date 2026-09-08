# Inverse-Dynamics Manuscripts: Technical Review

Date: 2026-09-08. Issue #4291; epic #4009; corpus #4021; batches #4058/#4062.
Branch fix/4291-inverse-dynamics-manuscripts starts at vendor PR head09a2471d.
Replay only this batch after that head onto protected main before first push.
Claim codex/session technical-review-20260906 expires21:54:42UTC.

## Complete Original Readings and Scope

Read the complete main7333-word TeX manuscript, technical ChatGPT2392-word,
layperson ChatGPT2230-word and Gemini1737-word drafts, both related FBPost
Markdown notes, the package README, and both public inverse-dynamics articles
with their shared mechanics includes. The public includes already contain
correct wrench/power and applied-load/drift conventions and are the consistency
baseline. Existing PDF and HTML companions must be regenerated or explicitly
reconciled rather than left asserting obsolete conclusions. Historical figure
fix/summary logs are records, not certification of the corrected version.

## Technical Decisions and Acceptance

1. Recover net hand wrench from total momentum rate after subtracting known
external wrenches; translate with (r_C-r_P) cross F_h. Keep all vectors in one
frame. An arbitrary moving origin needs transport terms if used directly in an
angular-momentum balance; translating a recovered wrench avoids that trap.
2. Pure couple has zero resultant; one offset force does not. Replace false
same-motion diagrams with actually equivalent force-plus-couple systems.
3. General wrench moment changes deterministically with reporting point.
Reference changes are not an uncertainty interval or proof of the actual
pressure center. General 3D wrench may have nonzero pitch and no single-force
representation; contact force feasibility and torsional moments matter.
4. Grasp-map null space identifies load-allocation ambiguity under a declared
contact model. Equal/opposite collinear additions at two points are invisible
to club rigid motion; opposite transverse forces usually create a couple.
5. Standard ID already returns applied generalized load. Drift is a partition
relative to specified inputs, not a physical reservoir or measure of effort.
Constraint reactions can depend on actuation; actuator redundancy requires a
rank/consistency test. Net torque does not identify muscle recruitment.
6. Wrench power is invariant for consistent rigid point transport; force and
moment contributions separately depend on point. Pure redirection can require
large real loads; this does not imply low physiological effort.
7. Omitted aero bias equals the omitted wrench at the same point. Keep relative
wind, drag/lift directions and intrinsic moment explicit. Retain the old40%
number only as a verified hypothetical signed example with the original
geometry; reverse projection changes the conclusion. Saved video stills can verify displayed values but not the full basis or iron drag calibration.
8. Test analytical limits and dimensional examples independently. Compile every
changed edition, inspect every page, reconcile any distributed artifacts and
run required repository content/static checks. No commit/switch during QA.

## Primary Source Reading

Northwestern Modern Robotics3.4 complete transcript read: wrench translation
and power duality; https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/.
Henrikson, Wood and Hart2014 DOI10.1016/j.proeng.2014.06.123 metadata confirmed
in Sheffield Hallam archive. Complete6-page author PDF read through references
at https://pgamagazine.com/wp-content/media/2014/07/PING_Turbulator_Science.pdf;
physical page4 drag/lift chart visually inspected. It has draft2013 pagination;
use published2014 journal metadata. Two matched driver heads, one with crown
features; wind tunnel angles/speeds linked, including90deg at96mph. Chart gives
roughly9 versus6.6N drag there, text2.3N difference. Lift changes sign. Forty
playershandicap<=10; mean speed increased about1mph;4ydcarry is modeled, not
measured carry. No iron data, universal drag center or torque correction follows.
Use a short evidence paragraph; derive mechanics and chosen scenarios separately.
Initial PyMuPDF import failed (not installed); used existing Poppler instead.
Poppler warned missing Symbol display font; inspected chart/text are legible.

## Governance

Repo AGENTS/CLAUDE/SPEC and GAAI read. Older GAAI staging/no-auto-merge language
conflicts with explicit user authorization to push/merge frequently and the
workspace topic-branch/main workflow. Continue established protected PR/squash
flow; never bypass checks or self-approve. No new production Python planned.

## Original Images Changed the Reviewer's Interpretation

All twelve original JPGs were visually read in full: eight midpoint sheets
IMG_8157 through IMG_8164 and four aerodynamic images IMG_8166 through IMG_8169.
They remain unchanged. The original eight-page Inverse_Dynamics_Claude.pdf was
extracted and read in full, as was the 3495-word old HTML conversion. Both stale
Markdown summary logs were read fully and now have prominent superseded notices.

Important correction to the review itself: before viewing the handwritten drag
sketch, I assigned positive transverse force to a newly chosen y axis while
retaining the old negative moment sign. That produced an apparent incompatibility
between the 5.5 lbf force and 40% moment reductions. The original diagram places
hand force and drag in the same transverse direction on opposite sides of the
COM; its moments about COM have opposite signs. In a right-handed frame with x
toward the head, use F_h,y^0=-7.5 lbf and M_h,P,z^0=-18.4 N m. Then F_a,y=-2 lbf
reduces both magnitudes. The original sketch is mechanically consistent. The
uncommitted intermediate main and layperson drafts and the premature commentary
were corrected. Never cite the abandoned sign-error diagnosis as a finding.

The video stills show F_beta,user=7.5 lbf, alpha torque=-18.4 N m and CHS=97.0 mph;
the handwritten note says 95 mph. Neither still verifies the complete axis map,
iron geometry or aerodynamic load. The old HTML also incorrectly labeled the
7.5 lbf component alpha. The corrected text labels its own local y/z axes and
explicitly avoids claiming a validated reanalysis of the video.

A separate original contact-position calculation is valid and is retained:
F_L=-10 lbf, F_R=15 lbf; positions relative to fixed midpoint (-2,+1) inches
versus (-1,+2) inches. Counterclockwise moments are +35 and +40 lbf in, or
3.9545 and 4.5194 N m; the original clockwise convention gives negatives.
The 14.3% relative change is the original approximate 15% illustration. Actual
forces move, so this changes the wrench. It must not be confused with changing
a reporting point or adding a grasp-map null load to preserve the wrench.
The old eight-page PDF additionally reversed a sign-change inequality: positive
M_m times (1-d_i/d_m) is negative when the ratio exceeds one, not positive.
The new vector/signed-coordinate examples replace that erroneous argument.

## Independent Mechanics Checks

Ran 100 seeded random three-dimensional cases checking wrench-power invariance,
central-axis residual moment, rank-five two-point force-only grasp maps,
collinear null additions and visible transverse additions. Also solved 100
positive-definite mass/independent-constraint examples and verified the full
acceleration constraint after inserting the derived reaction. All passed.
Checked the pendulum 4.905 N m hold/free-motion limit and radial tension
227.4525 N for the stated 0.25 kg, 1 m, 30 rad/s point-mass example.

The first independent conversion caught an arithmetic slip in the new table:
0.8255 m times 8.896443230521 N is 7.344013886795085 N m, not 7.3430. Corrected
all table entries to 7.3440, -25.7440 and -11.0560 N m. The 39.9131% correction
rounds to 39.9%. Moment transport through COM and direct subtraction about P
agree; this checks bookkeeping, not independent experimental validity. Repeat
with the final negative transverse force convention before accepting artifacts.

Read the complete Northwestern constrained-dynamics supplement (8.7) and
verified Featherstone's Springer DOI/book metadata. The reduced-input rank test
now explicitly follows constraint elimination; full rank of a redundant-coordinate
B alone does not identify unknown constraint loads.

## Artifact Decisions and First Visual Pass

Four complete revised TeX editions compile through three pdflatex passes.
The main is 13 pages after restoring the original contact example and provenance;
technical four, coaching five and Gemini four. Every page of that first complete
set was visually inspected. Found crowded PGFPlots x tick labels in main page4
and coaching diagram text crossing the club line on page2; fixed explicit ticks
and moved the label block. Also clarified aerodynamic arrow labels as signed
inequalities and the reduced-coordinate rank test. Recompile and re-inspect
changed pages and any repagination before distribution.

The old HTML had literal TeX in its title, missing diagrams and malformed formulas,
as well as the old scientific errors. No maintained converter or publishing
reference to it was found. Replaced it with a semantic reading guide linking the
complete revised PDF and maintained public inverse-dynamics articles. The two
existing PDF paths will both carry the verified current long manuscript, generated
from its one TeX source. Short companion TeX files are maintained; their QA PDFs
remain scratch outputs. Do not introduce independent binary source versions.

Both Markdown posts now explain the original experiments and individual image
groups. Historical summary logs remain, explicitly superseded rather than silently
certifying current mechanics. The package README records sources and build/QA
requirements without blanket publication-ready or perfect-layout claims.

## Attempts and Tooling

An oversized PowerShell authoring command failed with OS206 before writing.
Recovered the exact authored TeX from this task's own recent tool-call record;
initial extraction assertions failed safely, then the complete document was
written. First compile found an unused conflicting skew macro; removed it.
Second found non-scalable font expansion; added Latin Modern. Three-pass builds
then succeeded. A later Python replacement script had an unterminated quoted
string and made no edits; applied the intended explicit patch instead.
Windows rg wildcard arguments failed; used rg directory searches with -g.
A guessed index.md path did not exist; actual corpus index is corpus-review-index.csv.
The full repository root coverage lane is running. All34 static checks passed.
Title check before final additions passed631; final content/title/HTML/PDF QA pending.

## Previous Batch Delivery

Vendor issue #4290 / PR #4292 protected-squash-merged as
8a7bee22e63335c305b71cbef4fdf2f82a7c89e1. Main CI34275285462 and deployment
34275285576 were in progress at the last check; publication is not yet certified.
Replay only this batch after base09a2471d onto current protected main before
first push. Corpus remains unfinished.

## Final Local Artifact Checks

Final three-pass TeX logs have no overflow, underflow or unresolved-reference
warnings. Main13/technical4/coaching5/Gemini4 pages were rendered at1600px and
all26 inspected. Pixel comparison identifies exactly seven changed pages after
the last fixes: main4/8/11, technical3, coaching2, Gemini3/4. Reinspected all seven;
the other19 pages are pixel-identical to their already inspected versions.
Both tracked main and legacy PDFs now have SHA256
ca6753ad868288f4611d241b8985f14d272fc60cd50cc409f644115678886d67.
The final negative-transverse-force aerodynamic example and original contact
comparison were independently recalculated and passed direct/COM transport.

Initial HTML guide browser views were structurally sound but axe reported dark
link contrast with implicit canvas colors. Added explicit light/dark backgrounds,
text and link colors. A stale service-worker cache initially kept the old page;
unregistered it, cleared CacheStorage and used a fresh QA URL. Final eight full
views (320/375/768/1440px, both themes) have no horizontal overflow and were all
visually inspected in two contact sheets. Both final axe runs have zero violations.
No changed Quarto public source requires a site re-render in this batch.

First root run:4827 passed,29 skipped,one failure in the legacy-runtime fixture
that still required the old standalone article to load js/main.js. The replacement
is a static reading guide requiring no JavaScript, so removed that path from the
runtime-load list with an explanation; the remaining five cases pass. This is a
fixture scope correction for removed runtime behavior, not a hidden script token
or unnecessary runtime import. Final repository root lane is running again.
Content130 passed/4 skipped/4809 deselected; all34 static contracts, title631,
Ruff, Black668 and mypy86 pass. Changed no production Python.

## Final Repository Validation and Vendor Publication

Final `pytest tests/ --cov --timeout=120` passes4782 tests,29 skips and131
deselections in494.72s; configured source+scripts coverage79.04% exceeds75%.
The earlier root collection included46 benchmark tests, explaining the count
change; its only failure was the now-corrected legacy HTML runtime fixture.
All remaining five runtime fixtures independently pass. No checks were weakened.
Test-generated registry differences were parsed and verified identical apart
from generated_on and JSON formatting before restoring those six generated files.

Vendor main CI34275285462 and deployment34275285576 both succeed for exact
squash8a7bee22e63335c305b71cbef4fdf2f82a7c89e1. Downloaded artifact10076513252
contains956/956 passing checks across239 routes, zero serious/critical axe
findings and zero retries/transient responses. The previous batch is published.

## Pull Request Delivery

Committed as67111d8d, then replayed only the inverse batch after09a2471d onto
protected main8a7bee22. Replay had no conflicts and its final tree is identical.
Normal first push and all hooks passed. PR4293 targets main, references Fixes4291,
and carries agent:codex. Protected CI/merge and publication are pending.
