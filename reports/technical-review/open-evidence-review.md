# Open Evidence, Reproduction, and Model Validation — #4786

## Scope and Status

Full canonical Chapter 27 review at baseline
`09794b73a01bcbba643da5f165188da02bce33a0`:
`articles/proximal_distal_companion/chapters/ch27_open_evidence.qmd`.
Parent epic #4009, corpus #4021, companion #4059. Source corrections, manufactured checks and publication acceptance are complete;
source binding, regular PR and delivery remain pending. Corpus remains 116 pending plus
whole-book consistency until acceptance and binding. No provider simulation,
new participant evidence, or whole-book scientific completion is claimed.

## Scientific Decisions

1. **Distinct Evidence Questions.** Separate artifact identity, computational
   reproduction, independent verification and empirical validation. Define the
   chapter's reproduction/new-observation convention rather than treating
   terminology as universal. A repeated calculation can preserve a model error;
   two wrappers around shared dynamics are not independent physical validation.
2. **Comparison Contracts and Authenticity.** Raw hashes distinguish serializations
   even when decoded numbers agree; recomputing an erroneous result's checksum
   does not justify accepting it. The provider normalizes CRLF for named text
   suffixes and leaves binary bytes unchanged. Distinguish that contract from
   exact deployed-copy parity. A PDF magic header is not a cryptographic digital
   signature, and a bare digest does not authenticate authorship or science.
3. **Matched Observables and Uncertainty.** Specify body, point, observer, axes,
   units, event, interval and processing before comparing numbers. The 43 m/s
   versus 154.8 km/h example requires conversion. State nonnegative absolute and
   relative tolerances with correct dimensions, trajectory alignment and norm.
   Numerical error, measurement uncertainty and model discrepancy stay distinct.
4. **Reproduction Beyond Seeds.** Preserve sampled inputs and their case
   assignments, generator/call order, environment and execution evidence.
   A repeated seed with an extra draw assigns different samples. The binary64
   1e16, 1, -1e16 example illustrates order sensitivity without claiming all
   parallel runs are nondeterministic. A listed command is not a completed run.
5. **Verification Without Physical Validation.** The unit-inertia oscillator at
   two natural frequencies conserves each model's own exact energy but predicts
   different angles. Explicit-midpoint step refinement converges to each declared
   model, including the wrong model for a specified target. Algebraic contact
   power, integrated energy residuals, numerical convergence and empirical
   adequacy answer different questions. Golf transfer arguments require matched
   boundaries, signed powers, storage/loss terms, events and uncertainty.
6. **Actual Validator and Publication Scope.** The pinned entry point invokes
   manifest, numerical-claim, claim-evidence, external-review and PDF-profile
   checks; it is not merely a hash checker. Listing presets prints commands
   without executing them. Pinned computational qualification does not establish
   archival accessibility; reported tagging/font failures and unresolved human,
   equipment, tissue, full-contact and external-deposit requirements remain.
   Source inspection here is not a fresh provider qualification run.
7. **Representable Limits and Figure Provenance.** Preserve valid unresolved
   scientific statuses while blocking promotion. Distinguish schema failures
   from untested hypotheses, measurements from synthetic outputs, and numerical
   plots from schematics. No fake dataset is required for the reviewer-path
   illustration. Correct its caption/alt text to the six actual boxes, removing
   the previously claimed reproduction-result box; the figure itself is retained.
8. **Revision and Preservation.** Replace mutable provider-main links with the
   already reviewed immutable revision. Separate source identity, long-term
   availability, URL reachability and deployed-copy parity. Convert unverified
   universal descriptions of site compliance into explicit maintenance goals.
   Failed runs and contradictory implementations remain part of the record.

## Primary Sources and Reading Limits

- UpstreamDrift `85cce4d3307bb7ad3953d9fc6e583e370803515c`: complete
  `REVIEWER_WORKBENCH.md`, `OPEN_RELEASE_QUALIFICATION.md`, and
  `scripts/research/proximal_distal_energy/qualify_open_release.py` read.
  Selected data-dictionary common rules, recurring fields and model-boundary
  entries read; tool output truncated, so no full-dictionary reading claim.
  `release_bundle.py` metadata, artifact selection, canonicalization, manifest
  construction/validation and checksum functions read; a middle portion of its
  preset list was truncated. The imported validator call graph was not fully
  audited and no listed provider simulation or qualification command was run.
- National Academies (2019), DOI 10.17226/25303: Chapter 3 definition discussion
  and Chapter 4 reproducibility assessment/numerical-agreement discussion read.
  This is a selected primary-source reading, not the complete book. Definitions
  are explicitly conventional; original manufactured examples supply this
  chapter's numerical illustrations.
- NIST CSRC digital-signature glossary definitions read. No publication year
  invented and no certification or comprehensive security assessment claimed.

## Manufactured Checks and Delegation

`tests/test_open_evidence_review.py` checks JSON serialization versus numeric
content, unit/metadata contrast, floating-point order, PRNG call assignment,
analytic oscillator energy and RK2 convergence at both frequencies, and immutable
provider links. Valid RED: five numerical checks pass and one mutable-link
regression fails. GREEN: six pass. These do not mechanically certify prose,
realistic golf dynamics, every environment, or scientific reproducibility.

Six supplied-text agy CLI `gemini-3.8-flash-high` jobs completed: source inventory,
test draft, bibliography formatting, editorial review, binding-script draft and
PR-body draft. The latter two are workflow aids, not scientific acceptance. The lead verifies all
science and edits. Rejected helper suggestions: absence of unconsented data does
not establish human evidence; schematics need no fabricated one-to-one numeric
pairing; heading-keyword assertions were replaced by the substantive immutable-
link regression. Editorial suggestions improve explicit amplitude/frequency,
stiffness, tolerance definitions and step range. The claim that the manuscript
actually equated frequency with stiffness was too strong: changing frequency at
fixed inertia changes stiffness, now explicitly related. Existing book heading
levels are intentional because of the hierarchy filter. Different evidence
questions and the book's three summary labels are not inconsistent taxonomies.
The binding draft initially wrote review metadata at the route root and counted
only exact pending-status strings; both were corrected before execution. It now
preserves nested review evidence paths and uses the corpus status convention.

## Validation Record

The full local run recorded 6,481 passes, four failures, 29 skips and 187
deselections in 615.46 seconds; the configured coverage gate passed (78.97%
aggregate). Failures were one removed required mechanism heading, one Windows
non-UTF-8 temporary-file encoding error, and two root-hygiene checks caused by
Playwright's local output directory. The heading is restored. UTF-8 follow-up
execution and retaining browser/packaging outputs under QA address the local
execution conditions without weakening the tests. First focused follow-up found
an overly strict trailing-slash assumption in the new immutable-link test and
three packaging output directories; the assertion now accepts the exact pinned
tree root, and generated directories were moved intact into QA. Final affected
suite: 55 passes. No repeated full-green run is claimed.

Final PDF and HTML builds pass. The 226-page PDF's physical pages 188–194 and
222–226 were inspected; final changed pages 189–193 were reinspected after
restoring the book's hierarchy and shortening the visible commit label. Pages
188/194 and references 223–226 render pixel-identically to their inspected
predecessors. The full immutable target remains in the hyperlink. Canonical and
public PDF bytes match. Existing vectors remain unchanged.

Four final browser profiles pass, with zero serious/critical axe findings.
All 24 math containers (two displays) render at 390/1440 pixels without errors,
placeholders or page overflow. Mobile zoom opens/closes; the wide diagram's
labels remain small, with the six-part chain explicitly available in caption,
alt text and prose. No claim of uniformly large mobile labels is made.

Twelve publication gates, 653 title checks, Black, mypy and all 873 tracked
Python quality checks pass. Final Ruff passes after three justified S311
annotations for the deliberately noncryptographic PRNG example. Initial gate
failure on temporary generated TeX and raw-preview failures (legacy polyfill,
missing local manifest) are retained. The standard post-build polyfill stripping
and a validated single-route preview manifest precede final browser acceptance;
no full-site preview manifest or full-site browser sweep is claimed.

Dependency carry-forward preserves 138 prior evidence files and records three
shared changes: Chapter 27, appended bibliography and rebuilt book PDF. An NPZ
container regenerated during validation differed in bytes while all 43 member
payloads matched; its original container is retained. All 113 earlier finding
semantics and source verification commits remain historical. The lead corrected
the draft binder before use; raw Git-byte equality, unique findings and exact
corpus-row counts are asserted before the two output files are written.
