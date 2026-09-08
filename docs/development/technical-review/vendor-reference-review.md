# Launch Monitor Vendor Reference: Technical Review

Date: 2026-09-08. Issue #4290; parent epic #4009 and corpus #4021;
applied-article batch #4059. Status: complete article corrected and locally verified; protected submission pending.

## Scope and Delivery

The complete original `articles/launch-monitor-vendor-reference.qmd` was read.
Its related `technology-launch-monitors.qmd` has not yet been reviewed in this
batch. Do not extend this audit's status to that companion. Branch
`fix/4290-launch-monitor-metrology` starts at rotation PR head
643804e2590d18a2676c00961d8541e0942fbd27. Replay only this batch's commits onto
protected main before the first push. Claim codex/session technical-review-20260906
expires 2026-09-08T20:43:17.367005Z. Issue filing exemption is false; #4290 was
created and attached as an epic child before edits.

## Findings to Correct

- Sensor processing, learned inference and commercial software tiers do not
  separate measurement from nonmeasurement. Specify the measurand, observations,
  model, calibration and uncertainty. Patents disclose possible embodiments;
  they do not establish the implementation shipped in a particular device.
- Point velocities satisfy v_Q = v_P + omega cross r. Differences between face
  and head-center path can be valid conventions. A vendor's illustrative three
  degrees is not a universal correction or evidence that a coaching target
  causes a slice. Face-to-path remains defined even when its conventions require
  an explicit mapping to the contact model.
- Angular speed divided by point speed is not generally reciprocal screw-axis
  distance: nonzero screw pitch changes the denominator to sqrt(rho^2+h^2).
  Projected closure is not the angular-speed norm. Rate per distance is invariant
  to pure positive time reparameterization of the same spatial/orientation path,
  not to arbitrary changes in swing speed or dynamics.
- TrackMan's historical 2017 statement distinguishes preimpact speed/path/attack
  processing from face/loft averaged over collision. Maximum compression is not
  universally halfway through contact. The angle change depends on angular
  motion, measurement weighting and the chosen event.
- Human repeatability includes real swing variation. ICC depends on population
  variation and model; CV is problematic for signed angles near zero. Concurrent
  device comparison is informative conditional evidence, not inherently circular
  or proof of either system's absolute accuracy.
- Leach et al. Table 6 bands are centered on the median difference, not zero.
  The original article misstates both their interpretation and some percentages.
  Wedge club measurements were excluded from individual-club analysis, retained
  in pooled analysis. Calibration traceability does not independently validate
  every club quantity or remove event/geometry differences.
- TrackMan publishes some amateur averages (launch angle and swing plane), so
  the universal claim that none exist is false. This does not establish a
  representative population distribution of path or face-to-path.
- Current FlightScope main definitions use geometric center for club speed.
  Garmin explicitly identifies R50 cameras and sticker-point club reporting.
  GEARS provides face-center and impact-point orientation variants and projected
  angle definitions. Scope statements by device, date and software.
- A visible shaft line cannot geometrically identify axial rotation without
  additional information; a learned prior can still estimate it with uncertainty.
  Another markerless system's errors do not quantify Sportsbox accuracy.
- Normal-pressure arrays support vertical resultant and center of pressure
  (hence horizontal moments about the reference origin), not the complete ground
  wrench. Marker placement, curved faces, flexible shafts and coordinate alignment
  require explicit uncertainty and model assumptions.

## Primary Source Readings and Boundaries

- TrackMan, `https://www.trackman.com/blog/club-data-definitions`: complete
  main text, dated 2017-08-21. Driver offsets and timing numbers are vendor
  illustrations. Its historical scope must remain visible.
- FlightScope, `https://flightscope.com/pages/flightscope-data-parameters`:
  complete main text. Geometric-center speed/path; radial speed/acceleration
  profiles require separate interpretation. Marketing's energy language is not
  adopted as mechanics.
- Garmin, `https://www.garmin.com/en-US/blog/outdoor/3-key-differences-between-garmin-approach-r50-and-r10/`:
  complete article, dated 2025-10-17. R50 three cameras versus R10 radar;
  sticker-point versus strongest radar-return club reporting.
- GEARS, `https://www.gearssports.com/articles/gears-golf-club-ball-metrics/`:
  relevant club/shaft definitions read. Ground XZ, target Z, vertical Y;
  attack and spin-loft definitions use ZY projections. Path-relative closure,
  face-center and impact-point variants distinguished.
- Leach et al., DOI 10.1016/j.measurement.2017.08.009: complete 14-page
  accepted manuscript read, downloaded through the public Loughborough Figshare
  API (article 9562799, file 17195102). Scratch `vendor-leach-0.pdf` and text.
  January 2015 experiment, eight golfers, 240 attempted shots, TrackMan Pro IIIe
  and GC2+HMT, 5400 Hz GOM reference. Manufacturer supplied club CG; comparison
  normals differed by vendor. Reference ball uncertainty simulation and rotating
  sphere validation do not independently quantify every club output. Authors
  discuss simultaneous-system interference and nonoptimal combined setup.
  Table 6 needs visual cell verification before publication: research ball
  speed 98/84, launch angle 87/97, direction 76/71, spin 83/54; head speed54/29,
  attack38/67, path45/58, face66/26, loft65/33 (TrackMan/Foresight).
  Coaching face89/46. Thresholds are authors' judgment, not certification.
- Shaw et al., DOI 10.1519/JSC.0000000000004554: accepted manuscript methods,
  results and discussion read through main-text end, tables partly read.
  Twenty-one low-handicap golfers, three accepted shots per club/session;
  >20-yard directional misses repeated. CV/ICC describe the complete protocol;
  no controlled-motion reference isolates device error. Public Cardiff PDF:
  `https://pure.cardiffmet.ac.uk/ws/portalfiles/portal/5799959/TrackMan_Reliability_Accepted_Manuscript_Rhodri_Lloyd.pdf`.
- Bishop et al., DOI 10.1080/02640414.2024.2314864: abstract/search excerpts
  only. Publisher and Middlesex PDF attempts returned access errors. Abstract
  units appear inconsistent; do not reproduce those SEM units without tables.
- Brennan et al., DOI 10.1519/JSC.0000000000004685: complete PubMed abstract
  only. Twenty-nine youth golfers, ten driver/6-iron shots, Mevo+/TrackMan4.
  Do not relabel its reported confidence interval as limits of agreement without
  full methods. No full text obtained.
- Bliss and Langdown, DOI 10.1016/j.jsampl.2025.100128: search excerpts only.
  Mevo+/TrackMan4; estimated-spin exclusions. Publisher/Open University PDF
  requests failed and PMC returned a challenge. No full text obtained yet;
  do not retain precise table assertions without verifying them.

## Next Work

Finish root coverage run, then render and inspect the entire article at desktop
and mobile widths in both themes. Verify all31 historical anchors, equations,
tables and bibliography. Complete protected submission and exact publication
checks. Next long-source findings are filed as #4291 after full original reading;
no correction has begun there. Corpus remains unfinished.

## Draft Implementation and Additional Evidence

The complete article is now rewritten (455 lines, approximately 5,820 whitespace
words). It retains all 31 historical section-anchor names, replacing inaccurate
heading text with explicit IDs. The catalogue retains all original vendors;
unsupported rankings, unverified ranges and universal absence assertions are
removed. The historical newsletter discussion is narrowed to the retrieved
issue7; issue9 returned503, so its tolerance table is not reasserted. No evidence
of archive completeness or permanent document loss is inferred.

The new treatment derives rigid point translation, path and face azimuth
derivatives, positive time-reparameterization invariance, nonzero-pitch screw
speed, temporal weighting, event-time perturbation, shape-normal sensitivity,
covariance, pressure moments, and a three-dimensional spin-loft dot product.
It connects those observables to coupled body/ground/shaft/head/ball dynamics
and explains why an impact display does not identify unique muscle strategy.

Independent scratch checks verify point velocity against finite rotation;
100 random path and face-angle differentials against finite differences;
100 spin-loft formulas against independent Cartesian dot products; the
nonzero-pitch0.447213595 counterexample; pressure moments against direct
cross-product sums; and100% median-band acceptance with0% zero-band acceptance.
The numerical point example gives2.544804380 degrees. These checks test the
derivations without introducing production code or superficial wording tests.
The title audit passes all631 sources. Content/static checks are running;
render and visual verification have not begun.

Additional primary evidence:

- VIM2.48/2.49 definitions and notes fully read through ordinary HTTP/HTML
  extraction; algorithms are explicitly included in measurement functions.
- Full Swing KIT data guide main text and selected patent description/claims
  read. Rapsodo patent club-scan/reconstruction passages read. Neither patent
  is treated as proof of a shipped configuration or ownership/licensing state.
- Current Foresight measurement overview, club glossary and marker guide read.
  The latter distinguishes one/four markers by model. Its own inconsistent
  detailed one-marker parameter list is not copied into a universal table.
- Current Uneekor AI Studio page replaces the old404 URL and documents
  sticker-free XR/XO/XO2 configurations. Current SkyTrak technology page
  identifies radar/camera architecture and a comparative claim.
- Ernest Sports current support/overview and historical Tour Plus PDF retrieved;
  PDF read through data/mode sections (physical pages1–20), not claimed as a
  complete manual audit. This directly falsifies the old permanently-lost claim.
- Rapsodo FAQ, June2025 GCQuad comparison and setup guide read. Comparison
  retained as vendor-published evidence, not independent qualification. Setup
  guide's7.5ft/250cm mismatch is explicitly noted without prescribing a guess.
- Sportsbox accuracy report and shaft-angle help read. Body measures only in
  the cited comparison; no other system's markerless error is transferred.
- Swing Catalyst sensor/setup documentation read; normal-force resultant/COP
  argument independently derived. Hardware and display-software roles separated.
- TrackMan launch-angle, swing-plane, spin-loft and2025 help definitions read.
  Male and female amateur Combine groups disprove the original universal claim.
- Garmin English support requests returned403; localized indexed support and
  official2022 RCT blog establish why ordinary-ball conditions cannot become
  a universal indoor spin limit. No unverified tolerance table is reproduced.

Bliss/Langdown full open-access XML was successfully retrieved from Europe PMC
after publisher/repository failures. Complete main text and tables read. XML
identifies CC-BY and online2025-12-18; journal volume7 is2026. Scratch XML and
text retained. One golfer;410 attempts,207 retained (58driver/80iron/69wedge).
Exclusions include missing fields, estimated-spin flags and carry thresholds.
Article correctly reports loft differences as sample-specific. Mean-rating ICC
and absolute/consistency distinction are retained; low ICC is not interpreted
as complete physical disagreement. Same-sample95% agreement limits cannot
independently establish practical equivalence. Some source table entries have
internal arithmetic/CI inconsistencies; the article does not reproduce those
rows or infer causes from them. Its dynamic-loft-versus-spin-loft prose error
is not adopted. Leach Table6 physical page13 was visually inspected and all
retained cells confirmed.

Five study bibliography records were checked against Crossref metadata;
HTML ampersand entities were decoded for BibTeX, Brennan's issue year set to2024,
and Bishop's2023-volume/2024-online distinction is explicit in prose.

Initial replacement patch failed because delete/add targeted the same path.
No file changed. The exact authored draft was recovered from this task's own
tool-call input and applied; first recovery lookup used the wrong payload key
and failed before writing, second succeeded. No unrelated task data was read.

## Initial Validation Results

The initial static lane passed33/34 checks; content had129 passes,4 skips and
one failure. Both failures were the same shared bibliography evidence digest
in the neural-timing review record. The required regeneration refreshed the
inventory; its generated JSON report now has the matching new digest and must
be committed too. No neural-timing scientific assertion changed. The rerun
passes all34 static checks and130 content tests with4 skips. The root coverage
run subsequently passed; see final results below. Six generated date-only files should be restored only after
all QA ends and their semantic identity is checked.

All35 external document links were checked by ordinary HTTP:33 returned200;
GEARS and the historical Ernest PDF returned403 through this client, while both
were readable through the web source tool. This is an access difference, not
proof of a missing document. Verifier CLI has no --help flag; that exploratory
invocation failed and was replaced by reading its argument parser.

Rotation production verification is complete: protected squash072d5076,
main CI34265513801, textbooks34265513761, deployment34265513841 success;
exact live artifact10072974625 passes956/956 on239 routes with no failures,
serious/critical axe findings, retries or transient responses.


## Final Local Verification

The complete article renders successfully. Independent checks confirm rigid
point velocity, path and projected-closure derivatives, pressure moments,
three-dimensional spin loft, nonzero-pitch screw normalization and the
median-band counterexample. The root suite passes 4,828 tests with 29 skips;
configured src/scripts coverage is 79.04%, above the configured 75% floor.
The pass count was verified from pytest progress output because the doubled
quiet option suppressed its final count. The final content lane passes130,
skips4 and deselects4809 in20.06s. All34 static contracts pass; title case
passes631 sources. Stylelint passes the15-line page-local stylesheet.

Complete visual inspection covers167 body captures,12 equation right edges,
and27 table/bibliography captures across desktop light and phone light/dark:
all23 contact sheets inspected. A final7 bibliography captures (one contact
sheet) confirm repaired dark-mode contrast. All31 historical section IDs occur
exactly once; five bibliography entries resolve. Responsive verification passes
14/14 at all seven contract widths in both themes, with no failures,
serious/critical axe findings or navigation retries.

Initial visual QA found inherited mobile display-math shrinking and a white
bibliography background in dark mode. A page-local stylesheet preserves normal
math type and scroll reachability, and makes the appendix background transparent.
The final stylesheet was mirrored using the existing sync_one build helper;
no rendered CSS was hand-edited. No Python/JavaScript production code changed.
An initial responsive run caught Pandoc's legacy polyfill blocked by the site's
CSP. The existing deployment strip_legacy_math_polyfill cleanup was applied to
local rendered article output, then all14 checks passed. This was local build
preparation, not a source/security-policy change.

A mistaken -m content test selector selected no tests (exit5); the documented
content_lint lane above passed. Initial manifest construction tried a nonexistent
full manifest, then passed a docs-prefixed relative path to _page_record; both
failed before writing. The corrected source-derived single-page manifest was
used for successful checks. These failed attempts are not passing evidence.
Six generated date/JSON-format-only files were restored only after all QA ended
and semantic identity was checked. Both actual bibliography-digest JSON changes
remain required. All tests/builds/browser operations have ended before commit.
Protected integration and exact-revision publication remain pending.

## Next Manuscript Readings

The complete original long inverse-dynamics manuscript was read and its defects
filed as epic child#4291. The technical ChatGPT, layperson ChatGPT and Gemini
TeX companions were also read completely, along with both existing public
inverse-dynamics articles and their shared wrench/dynamics includes. The two
ChatGPT TeX files have systematic --- substitutions for equals signs in math
and TikZ syntax; their force diagrams also contradict resultant directions.
The Gemini draft misstates standard inverse dynamics as ignoring drift and
places internal forces in an unspecified Jacobian null space. No correction
or claim has begun for#4291. Current public includes already give the correct
wrench/power and inverse-dynamics bookkeeping and are the consistency baseline.
Northwestern Modern Robotics section3.4 full video transcript was read on
2026-09-08: https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/.
Its frame/power derivation supports the general wrench convention; numerical
examples and golf interpretations must be independently derived.
