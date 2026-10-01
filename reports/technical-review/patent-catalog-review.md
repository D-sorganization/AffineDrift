# Patent Catalog Technical Review — Issue #4766

## Status and Scope

In progress under epic #4009 and corpus issue #4021. The lead read the complete
patent compendium and linked patent-landscape chapter. The initial appendix contained
167 distinct patent macros; the current catalog preserves those identifiers after two kind-code corrections and contains 168 macros plus a Gazette link. Research capture covers the original identifiers plus
six verification records. Both chapters have been revised and the 80-page book rendered and inspected. Final per-entry adjudication and audit binding remain open; no full-review credit or legal determination is claimed.

The review distinguishes the technical content of a publication from a
commercial implementation, performance validation, ownership history, enforceable
claim scope and freedom to operate. Patent text is a technical primary source;
the Google Patents index's dates, assignees and status labels are transcriptions
requiring their own qualifications. Downloading a record is not reviewing it.

## Verified Corrections in Progress

1. **Publication Identifiers.** The Topgolf documents are US10898757B1 and
   US11771957B1. The original B2 URLs return 404; the B1 publications identify the
   relevant radar/image tracking and trajectory-extrapolation inventions.
2. **Garmin Mechanism and Product Mapping.** US11351436B2 claim 1 describes two
   laterally separated cameras with clubhead-speed-dependent capture timing.
   Claim 9 adds a radar trigger. Calling the document the R10 patent or a complete
   Garmin portfolio is unsupported. The revised entry describes the disclosed
   arrangement without inferring a product implementation.
3. **Missing AccuSport Evidence.** US7209576B2 identifies AccuSport as original
   assignee and describes golf-ball image processing. It contradicts the earlier
   absence claim. Failure to find entries for other named vendors establishes
   neither their absence nor dependence on a particular historical technology.
4. **USGA Attribution.** US6186002B1 belongs under the United States Golf
   Association rather than the Acushnet list. Its first claim uses a ballistic
   light-screen array, controlled launches and crossing times to fit aerodynamic
   coefficients against Reynolds number and spin ratio. This is not arbitrary
   launch-monitor identification of all flight-model parameters.
5. **Dates and Catalog Limits.** Twelve leading table entries disagree with the
   retrieved indexed priority year. All twelve leading years have been corrected to explicitly indexed priority years; related-note dates remain separate.
   The current TrackMan marking notice contains 47 unique US numbers, including
   US12702912B2; the original count of 45 and absent-from-page notes have been corrected or removed.
   A marking list is not an exhaustive estate search.
6. **Rights and Mechanisms.** Both source files make unsupported whole-stack
   expiry and free-use claims. The USPTO explains that a patent provides a right
   to exclude, not permission to practice, and distinguishes nonprovisional
   filing, maintenance and term adjustments. The technical review replaces
   the claimed freedom-to-operate map with a scoped research map, preserving
   useful mechanism descriptions and explicit evidence limits.

7. **Radar Spin, Not Camera Spin.** US11513208B2 and US12105184B2 use radar
   radial-velocity variations around a center velocity. The lead read both
   abstracts and first claims; the camera-based label was corrected.

## Source Receipts

- [USPTO Patent Essentials](https://www.uspto.gov/patents/basics/essentials):
  right to exclude, territorial scope, filing basis and term conditions.
- [USPTO Kind Codes](https://www.uspto.gov/patents/search/authority-files/uspto-kind-codes):
  A, A1, B1 and B2 have document-type meanings; B1/B2 do not indicate generations.
- [TrackMan Marking Notice](https://www.trackman.com/legal/patents) and
  [Uneekor Marking Notice](https://uneekor.com/en-us/legal/patents): captured
  October 1, 2026. The latter expressly disclaims completeness of its list.
- The corrected publication links and source records are preserved in local
  QA `patent-catalog-sources/`. Every captured HTML has a SHA-256 receipt.
- US12702912B2 was unavailable through Google Patents. Its identity, filing and
  provisional-priority dates and first claim were read in the
  [USPTO Official Gazette](https://patentsgazette.uspto.gov/week32/OG/html/1549-2/US12702912-20260811.html),
  retrieved successfully with a direct HTTP request after the browser fetch failed.
  A missing aggregator page is not evidence that a patent does not exist.

## Flash Delegation and Lead Adjudication

Two initial supplied-text Gemini 3.8 Flash jobs provided a claim inventory and a
parser draft. Twenty-five small abstract/metadata comparison batches completed through three
agy CLI workers (all exit zero; 172 packet records). These are drafts, not scientific signoff.

The lead rejected the inventory's description of old US A grants as utility
models, its B1/B2 generation terminology, and its unverified category counts.
The parser draft would collect repeated citation-table dates and nested claim
fragments. The actual capture uses the leading bibliographic fields and top-level
numbered claims; coverage is checked separately from retrieval success.

Early comparison drafts incorrectly treated an expiration label as corroboration
that a patent is absent from a marking page. Those are independent facts. Shared
titles/abstracts do not establish a continuation relationship. The final catalog
must check that relationship or use neutral related-document language.

## Revised Chapter and Catalog Checkpoint

Five further supplied-text agy Gemini 3.8 Flash jobs completed: a chapter mechanism comparison, three remaining-draft triage packets and a revised-chapter editorial check. The first oversized Windows invocations failed before launch; splitting packets below the command-line limit resolved the failure. Total completed patent jobs: 32. The lead inspected the results and selected primary first claims. Draft claims that an omitted assignee in a row contradicts its section heading, that a filing year must equal an explicitly labeled priority year, or that a missing abstract term disproves an embodiment were rejected.

The revised chapter distinguishes spectral spin, receiver-pair timing, projected radar axes, image-based rotation, launch-to-flight models, staged display and probable-club spin inference. It replaces broad free-use claims with measurement validation questions and explains why ball outputs do not uniquely identify a golfer's force or joint-torque history. The table keeps its original cross-reference label.

The appendix removes unverified expiry, product and continuation shorthand. US5333874A is a historical rebound-based inference entry with qualified assignment information. US12544624B2, US11964188B2 and US9162132B2 have separate mechanism descriptions rather than inheriting their former grouped rows. US12702912B2 links to the available USPTO Gazette. Sports Sensors' speed and swing-duration tasks, Rapsodo's radar-feature neural estimator, and Weibel's simultaneous CW/FMCW arrangement are distinguished.

All 167 original macro identifiers remain represented after the two explicit B2-to-B1 corrections. The appendix now contains 168 unique macros plus the new Gazette link. All 111 leading table priority years agree with their captured index records. This checks transcriptions, not legal priority entitlement. The book-local research dossier links every macro publication and the institutional sources.

EP1735637B1 contains 42 sequentially numbered English claims, not repeated translations; the earlier translation concern was a hypothesis and is rejected. WO2003032006A1 contains 21 numbered claims despite an absent declared-count field. Missing extracted abstracts do not prevent a claim-based technical summary.

The company-authored September 30, 2024 license announcement was read through its Nasdaq syndication when the original Business Wire URL was unavailable. It concerns portable-monitor screen technology and expressly does not establish adoption of another company's ball-flight algorithm. The source URL and interpretation are retained in the book dossier.

## Remaining Work

Finish the final per-entry disposition for retained narrower details, including receiver geometry, commercial implementation labels that remain in other chapters, and the technical scope of secondary references. Compare the revised patent chapters against the rest of the launch-monitor book, without awarding completion to unreviewed chapters. Then run final publication/regression checks, bind findings, update the corpus and deliver a regular PR. The 122 pending full-source audits and whole-book consistency requirement remain unchanged.

PR #4755 is merged on remote main as 394a7b40bbff4327789e8d98dfcd5390dd845a0b. The later geometry PR #4765 remains open and conflicts with that update; its CI36893253026 was still running at the latest check. Integrate the delivered changes with source/evidence preservation before subsequent PR delivery. Do not close other predecessors merely from branch ancestry or an apparent duplicate title.

## Earlier Checkpoint Validation (be207dfd0)

The 35 book-publication/claim-inventory tests, 653-source title audit and LaTeX
structure baseline check pass. Claim-audit digests were already current: this
partial edit does not create a new completed scientific finding. The repository
bibliography checker passes on its 169-entry JSON authority; that check does not
validate this book's separate BibTeX file. The optional Python `bibtexparser`
package was unavailable, so its attempted check did not run. The installed Biber
tool subsequently parsed the book file and exited zero; its 54 datamodel warnings
are exactly the same as a separately parsed pre-edit baseline. These warnings
include missing author and publication-date fields and remain to be reviewed;
this is not a warning-free bibliography validation. A separate key/date check
confirms 83 unique entry keys and both changed marking-source access dates.
The first direct bibliography-script invocation lacked the repository import
path; the corrected module invocation passed. No full regression or newly
rendered book is claimed for these partial patent edits.

## Rendered-Checkpoint Validation

The book build passed using its existing MiKTeX/Biber workflow with halt-on-error and undefined-reference checks. The final PDF has 80 pages. The lead visually inspected all Chapter 7 pages (PDF 26–30) and Appendix D pages (58–66), then rechecked the final two appendix pages after keeping the closing section together. Wider patent columns, ragged text cells and targeted heading-space reservations remove box warnings from both edited chapters; warnings elsewhere in the book are not claimed resolved. The shared preamble adds only the needed `needspace` package.

The 35 focused book-publication/claim-inventory tests, 653-source title audit and LaTeX structure check pass. Claim-audit digests remain current; no finding is newly bound by this checkpoint. Identifier preservation and all 111 leading indexed priority years were checked. Optional Python `fitz` was unavailable; installed Poppler rendered the review images instead. No full regression or completed scientific audit is claimed yet. Source/PDF hashes and commands are in `patent-catalog-checkpoint-validation.json`.

## Retained Details and Cross-Chapter Consistency Checkpoint

Six additional supplied-text agy Gemini 3.8 Flash jobs are complete (38 patent jobs total): three retained-detail comparisons, one cross-book inventory, one camera-condition search comparison and one patch consistency review. The lead read the drafts and selected primary claims/description passages. The extra handoff-deduplication job belongs to geometry integration, not this patent count.

US11191998B2 claim 1 uses speed/angle-based estimates both to replace unavailable mark-derived spin and to correct available mark-derived spin. Chapter 7 now explains why that corrected output is not independent evidence for its input relationship. US12002222B2 distinguishes database-derived dynamic loft/backspin from motion-vector axis inference. The catalog also corrects golf-surface versus screen impact (US11875517B2), fixed-plane/image measurement versus unsupported simulator lifecycle labels (US8758103B2), and unconditional markerless/camera-count language (US11439886B2). US12263393B2 claim 1 concerns fix-line angle; claims 3/4 expressly add known geometry to the three-dimensional reconstruction.

Retain supported details: US11452911B2 describes range radar as an embodiment; US9958527B2 describes phase-comparison monopulse; US5471383A describes retroreflective material; US5501463A describes face orientation/contact location. Missing words in a first claim do not refute descriptions. US9333409B2's low-speed-camera passage states a motivating difficulty rather than a performance guarantee, so the table now describes candidate-trajectory processing. US9514379B2 likewise states the inference mechanism rather than a low-resolution capability promise.

The abstract, introduction, camera discussion, design guidance and implementation appendix now agree with Chapter 7's evidence boundaries. Removed blanket expiry dates, public-domain recipes, direct commercial lineage and automatic optical-accuracy claims from the identified passages. Camera count, visibility, calibration, geometric priors and model dependence are connected explicitly. These focused edits do not constitute full audits of the five additional sections. Their other hardware, numerical, vendor-comparison and performance statements still need the corpus review.

The final Flash review suggested explicit Creatz attribution and clearer phased optical headings; those clarity edits were accepted. Its claim that the word measured is inherently incompatible with calibrated reconstruction is too broad; the correction avoids an unconditional promised capability without declaring all calibrated measurements invalid. Its Tier 3 reference actually concerned Tier 4. No new patent fact was accepted solely from that draft.

Geometry main integration aab6c3999 is pushed to PR4765 and normally merged here as 7fcd86945. Its current-head static/Python/JS/link checks pass; E2E was still running at this checkpoint. Patent final per-entry adjudication, secondary-reference review, scientific binding and full regression remain pending. Corpus credit remains unchanged at 122 pending full-source audits plus whole-book consistency.

The final consistency build remains80 pages with no undefined citations/references. All22 affected/reflowed pages were visually inspected, and final heading/attribution pages29/36/53/59 rechecked. Thirty-eight focused tests, three final handoff checks,653 titles,LaTeX structure,SPEC and evidence digests pass. All168 appendix macro identifiers and111 leading priority rows remain unchanged from a9d46717e. The final receipt preserves source/PDF hashes and remaining validation limits in `patent-consistency-validation.json`.

## First-Claim Catalog Dispositions — October 1, 2026

Nine more agy Gemini 3.8 Flash jobs (three parallel workers per wave) compared 36 leading entries with their abstracts and first claims. The lead inspected every supplied claim and followed up in descriptions where absence was mistaken for contradiction. There are now 47 completed patent support jobs and 76 selected first-claim reads; 42 leading rows still await that stage. Secondary references and the final combined disposition remain open.

`patent-catalog-dispositions.json` records all36 decisions, source HTML and first-claim hashes, scope and exact final catalog rows. Twenty-two subjects were refined and14 retained. These are not36 discovered errors: many changes distinguish methods more precisely, while supported summaries remain unchanged. The chapter distinguishes target-frame mapping from image-feature correlation, projected axes from components, shared-range calibration from independent validation, and terrain-constrained depth from independently observed height.

Important rejected draft diagnoses: US10473778B2 does describe target deviation; US8912945B2 permits camera images; US11446546B2 discusses phase differences; US10471328B2 includes target-line overlay; US10989791B2 includes range-rate alternatives; both composite-imaging documents describe a radar master-clock example. US12042698B2 explicitly uses toppling; US10953303B2 and US11612801B2 discuss golf clubs. US10379214B2 has a two-radar first claim and an explicit single-radar embodiment in Figures13/14, so the catalog now preserves both. US12586211B2 includes reduced-power states, and US11951372B2 includes mishit filtering. None of these details is disproved merely by absence from the first claim.

The 80-page build passes without undefined references or citations. All14 patent-chapter pages were visually inspected; the38 focused checks,653-source title audit,LaTeX structure and evidence-digest checks pass. All168 appendix identifiers and111 leading priority rows remain unchanged from0b96bd668. Each of the36 committed row/hash records was independently checked against the final source and captured claim. `patent-disposition-validation.json` records hashes and limitations. No full regression, final finding binding or corpus completion credit is claimed. PR4765 current-head E2E remains live; the other reported lanes pass.

## Remaining Leading Entries — October 1, 2026

The lead reviewed the remaining42 abstracts and first claims, with targeted description checks for image features, unsynchronized cameras, antenna geometry and brightness compensation. There are now118 selected first-claim reads and no pending leading-entry reads. The consolidated disposition file contains78 records from the two disposition checkpoints:47 refined subjects and31 retained subjects. Earlier selected reviews remain documented in the preceding checkpoints; these counts do not imply an all-claims legal review.

Twenty-five additional subjects were refined and17 retained. The significant corrections distinguish air-density-derived effective altitude from environment-robust tracking (US11573082B2), radar-timed capture from generic sensor fusion (US9955126B2), surface features from mandatory applied markers (US11170513B2), and an image-size database from unrestricted single-camera depth reconstruction (US9605960B2). US11747461B2 retains its expressly disclosed camera/radar association while distinguishing its radar-track first claim. US20230364468A1 expressly separates the ball-image and swing-radar representations rather than integrating their positions.

Retained details are source-supported: US9448067B2 describes unsynchronized cameras, US10587797B2 connects brightness compensation to spin marks, US11311789B2 describes non-uniform antennas, and US8414408B2 describes ball return. Missing words in claim1 alone do not refute those embodiments. US9737757B1's first claim uses two camera-defined planes; its abstract's ground-plane example is not a universal camera-count requirement.

The new chapter discussion connects synthesized timing, launch-origin association, prediction-conditioned track selection and environmental inference to golf-swing interpretation. Interpolated frames are not additional exposures; selection using a predicted trajectory conditions the resulting agreement; shared aerodynamic-model error can persist across multiple trajectory-derived wind estimates; density-equivalent altitude does not encode the entire atmosphere.

Six supplied-text comparisons were dispatched through agy CLI gemini-3.8-flash-high, in two waves of three. All ended with provider HTTP500 or503 errors and returned no review. They are recorded as failed attempts, not added to the47 completed patent support jobs. The lead completed these42 source comparisons and decisions directly. The final secondary-reference review, combined scientific binding, full regression and regular PR remain pending; corpus credit remains122 pending full-source audits plus whole-book consistency.
