# Patent Catalog Technical Review — Issue #4766

## Status and Scope

In progress under epic #4009 and corpus issue #4021. The lead read the complete
patent compendium and linked patent-landscape chapter. The appendix contains
167 distinct patent macros. Research capture covers those identifiers plus
six verification records. Source editing has begun; no full-review credit,
publication validation or legal determination is claimed.

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
   US12702912B2; the original count of 45 and absent-from-page notes need updating.
   A marking list is not an exhaustive estate search.
6. **Rights and Mechanisms.** Both source files make unsupported whole-stack
   expiry and free-use claims. The USPTO explains that a patent provides a right
   to exclude, not permission to practice, and distinguishes nonprovisional
   filing, maintenance and term adjustments. The technical review will replace
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

## Remaining Work

Finish every entry's technical and bibliographic comparison; resolve missing
abstract/claim extraction for foreign documents; review targeted complete claims
and descriptions; correct both source files and associated bibliography. Then
render and inspect the book, run appropriate regression/publication checks, bind
findings, update corpus/turnover records and deliver a regular PR. The 122 pending
full-source audits and whole-book consistency requirement remain unchanged.

The collected inventory records 173 attempted identifiers, 170 successful Google
Patents captures, two incorrect B2 identifiers corrected by B1 records, and the
new TrackMan document verified separately through the USPTO Gazette. The full
claim-count extraction remains incomplete for WO2003032006A1, and EP1735637B1 has
no extracted abstract. These are retrieval/coverage limitations, not evidence
about patent validity. The lead reviewed all captured title/date/assignee rows,
selected full technical claims, the batch 00–04/07/15/17/18/23 drafts, and a
cross-batch discrepancy extraction; remaining draft details need adjudication.

Do not mistake a grouped row's leading identifier for an erroneous reference to
its additional identifiers, as several Flash drafts did. Inventors, applicants,
assignees and product brands also require separate treatment. US5333874A lists
Kiraly and Wintriss among its inventors but its placement under a Foresight
portfolio is not established by shared inventorship.

## Partial-Checkpoint Validation

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
