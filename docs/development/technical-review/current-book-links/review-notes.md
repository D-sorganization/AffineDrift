# Reviewed Book Edition Links

## Scope and Decision

Issue #4961 is a final delivery amendment under #4009. The accepted scientific
source is PR #4953, head fbee4da94fd699e9710f4c29b42a73a5113f08d4. The running PR
is unchanged. Work is isolated on fix/current-reviewed-book-links in the former
final-partial-sources worktree.

A completion audit found 53 manuscript/PDF links across five book pages. Of
those, 43 hard-pinned targets differ from the accepted tree, four hard-pinned
targets are identical, and six follow main. A byte difference alone is not a
scientific error. The material problem is that chapter links in four landing
pages bypass the corrected manuscript and reach earlier snapshots. The book
index's existing main link needs no change.

Two agy Gemini 3.8 Flash jobs independently audited embedded page/link data.
The lead verified the targets against Git objects. Reject the helpers' claims
that every older reference has different content: four pinned targets are
identical. Preserve notebook scaffolds and empirical boundaries. Do not turn
this into another science rewrite.

The first edit tried floating main links. The existing publication test requires
revision-pinned manuscript references. Retain that reproducibility contract:
pin the corrected edition to PR #4953's protected merge revision and state its
edition date. Do not weaken the test. The temporary local pin is fbee4da94 and
must be replaced with the verified protected merge revision before the PR opens.

## Changes and Boundaries

- Amend only tangent-space-methods, control-is-motion,
  biomechanics-biology-to-systems, and human-motor-control under books/.
- Update 47 earlier manuscript/PDF targets. Two Volume IV links become duplicates
  of already offered corrected sources and are removed.
- Bind the existing moving manuscript targets in these four pages to the same
  reviewed edition. Keep the separate book-index main link unchanged.
- Preserve all 43 notebook URLs exactly, including historical scaffold pins.
- Replace edition notes that conflate chapter sources and notebook snapshots.
  Use PDF bookmarks instead of promising build-dependent page numbers.
- Scientific arguments, chapters, notebooks, upstream publications, and all PDFs
  are unchanged. Historical scientific review identities are preserved; this is
  a bounded navigation amendment, not an automatic renewal of those reviews.

## PDF Comparison

Downloaded all eight artifacts from successful Compile Textbooks run 37291711515
at the accepted head. Committed and CI page counts agree: Volume 0 234, I 152,
II 103, III 79, IV 84, V 55, Physics 534, and Launch Monitor 105.

Text extraction is not byte-identical. Both pypdf and pdftotext expose font
encoding differences: ligatures, scalable brackets, bullets, roots and integrals.
Volume I's title date changes from October 3 to October 5. Physics has pagination
shifts within an unchanged total page count, so page-by-page text differences
must not be called scientific changes. Examples of apparent numeric changes in
its contents are page references (212 to 213), not altered model coefficients.
Raw comparisons are retained in local QA. They do not establish identical layout
or replace the earlier scoped PDF inspections. No PDF is replaced on the strength
of text extraction alone.

## Validation and Next Steps

The first focused run exposed stale page digests and the intentional immutable
manuscript-link requirement. Keep both gates intact. Refresh only affected source
and evidence hashes, regenerate the book report and canonical claim-audit reports,
then rerun the focused tests. Four original scientific review metadata records
are preserved in prior-scientific-review-metadata.json.

All 65 focused tests pass with the original immutable-reference contract intact.
The book audit and canonical evidence regeneration checks pass. All four Quarto
renders pass. Eight browser checks at widths 390/1440 find no document overflow
or MathJax errors and resolve 50 manuscript links to the intended local accepted
revision. All 43 notebook URLs and all 29 math expressions remain byte-identical.
The top views and edited mobile links/notes were visually inspected. Existing
mobile title wrapping and a recurring preview notification remain known layout
limits; this is not global accessibility clearance. The first screenshot helper
could not find an offscreen lazy heading through its accessible role; direct DOM
scrolling produced the final edited-content captures without changing page CSS.

Acceptance details: reports/technical-review/reviewed-book-links-validation.json.
The four pages do not overlap the original 145-artifact delivery manifest.

Pending: save the source checkpoint, wait for #4953's protected merge, verify its
145-artifact manifest, rebase only the new navigation commit(s) onto that main
revision, replace the temporary manuscript pin, and finish central pre-PR checks.
Then open a regular follow-up PR against main. Do not push this correction to the
already queued consolidation PR or bypass its queue. #4953's full CI passed;
auto_merge became null with the PR still open, indicating the queued state.
The final epic closure also requires public-site revision, route evidence and
the advertised PDF download checks.

Repository_Management #1998 is merged at e03344f3d5d0306f990ff295f767dbb1ba74ecd9.
Thirty-eight of its 39 changed files exactly match the accepted head. The remaining
test file has only an independent main addition to SCRIPT_COPIES; the repair is
intact. Its issue receipt is posted and its lease and presence are released.
