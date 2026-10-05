# Reviewed Book Edition Links

## Scope and Decision

Issue #4961 is a final delivery amendment under #4009. The accepted scientific
source is PR #4953, head fbee4da94fd699e9710f4c29b42a73a5113f08d4. The navigation work began on fix/current-reviewed-book-links in the former
final-partial-sources worktree and is now combined with the required protected-main
conflict repair for existing regular PR #4953. This document records pre-merge
evidence; the final protected-merge and publication receipts are maintained in
epic #4009.

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
pin the corrected edition and state its edition date. Do not weaken the test.
The initial plan used fbee4da94 temporarily and proposed replacing it with the
protected merge revision in a separate PR. The integration decision below
supersedes that plan: retain the immutable reviewed source revision and prove
that its linked bytes also reached protected main.

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

Source checkpoint: 3ddafd5d1dda8b150f4e7f88b0abf7bd38659611. The central pre-PR
runner passed all eight gates against fbee4da94 on 5 October 2026. Its affected-test
mapper found no Python tests for this documentation diff; that result does not
replace the separate 65 focused publication tests. The runner also reported three
collection skips for unavailable Streamlit. This checkpoint result must be rerun
after the final conflict resolution and incorporation into the delivery PR.

Pending: wait for the preceding PR's protected merge and inspect #4953's actual
conflict state. If a genuine conflict requires repair, use the integration
sequence below. Do not push this correction to the already queued consolidation
PR or bypass its queue. #4953's full CI passed;
auto_merge became null with the PR still open, indicating the queued state.
The final epic closure also requires public-site revision, route evidence and
the advertised PDF download checks.

## Advertised PDF Delivery Checks

A further agy Gemini 3.8 Flash pass enumerated PDF links extracted from the five
book navigation pages. Lead inspection confirmed five distinct targets: the
proximal-to-distal monograph and Volume V as relative website downloads, plus
Volumes I, III and IV at the reviewed GitHub revision. Volume II offers chapter
sources here, not a PDF link. This inventory is scoped to those five pages.

After deployment, resolve the actual rendered links and compare downloaded PDF
SHA-256 values with the corresponding declared edition's Git bytes. For GitHub
blob links, verify the displayed revision and fetch the raw target for hashing;
do not hash GitHub's HTML viewer. For relative links, fetch the public website
route and compare it with the deployed source revision. Preserve the upstream
monograph's immutable publication contract. Check that responses are PDFs, not
error pages. Local hashes alone do not prove successful public delivery, and a
PDF header/footer alone does not prove complete or correct contents. The helper's
suggested generic commands are therefore a checklist input, not delivery proof.

## Queue Integration Preview

PR #4958 merged at e1ec8f62d804567f3a480c02242e0792d815185e on 5 October 2026,
11:26:23 UTC. PR #4942 then preceded #4953, with its site check still running.
A read-only `git merge-tree` preview of accepted head fbee4da94 with queued prefix
56cb9b8ade267fc6493713ddf9d7711ab5d4c0d7 produced tree
243745286e21c013858e8d8e41815d2be4eab1f7. It confirmed actual prospective conflicts
in claim_audit_inventory.json and generated/claim_audit_report.json, all beneath
data/trust/. The evidence presentation registry merged automatically.

There are three conflict blocks in each file, six total. All concern evidence
hashes, not review identities or scientific prose. The Flash helper ambiguously
described three across both files; the lead counted the extracted blocks directly.
All 145 frozen artifact hashes match the preview tree. This is prospective
integration evidence, not proof of protected merge or publication.

Once the preceding change is on protected main and a real conflict requires
resolution, preserve the automatically merged records and underlying source
changes. Resolve only the conflicting hash entries to restore parseable JSON,
then run `python -m scripts.regenerate_claim_audit_evidence` and its `--check`.
Do not select an entire ledger from one side: that could discard the other
branch's review records. Compare review identities before and after regeneration,
recheck the 145-artifact manifest, and run the applicable integration gates.
Neither queued branch was edited during this preview. If GitHub instead merges
the review successfully, use the actual protected result and skip this contingency.

## Single-PR Delivery Decision

The prospective queue conflict makes a further integration check likely. Avoid
an additional full CI cycle solely to change an already immutable source pin.
All 50 manuscript/PDF references in the four amended pages were individually
compared between reviewed commit fbee4da94 and prospective tree 243745286e21:
every SHA-256 matches. The receipt is
reports/technical-review/reviewed-book-target-correspondence.json. The source
commit is an immutable reviewed edition; it is not described as a protected
merge commit. Its correspondence with the final protected revision remains a
required completion check, alongside the original 145-artifact manifest and
the four revised page hashes.

If #4953 is released from the queue with the anticipated real conflict, resolve
that conflict against actual protected main, then incorporate the already
committed #4961 navigation correction and these handoff records into #4953.
Preserve both branches' review identities, regenerate affected audit evidence,
rerun applicable publication/integration checks and the central pre-PR runner,
and update the PR body to include Closes #4961 and its validation boundaries.
Use the central merge guard after the repair; never push to a queued PR.
This changes packaging, not scientific scope or evidence requirements.

If #4953 merges without requiring a repair, use the existing separate follow-up
path for #4961. In either path, retain the reviewed source pin only after verifying
all 50 target hashes against the actual protected tree. Public delivery must
also prove the four amended pages are deployed and their advertised PDFs match
the stated edition. The prospective comparison alone cannot close the epic.

## Actual Main Integration

At 12:13:41 UTC, #4942 and #4892 merged through the protected queue. Fetched
main is bc07fb7a34d83827dd94147c31b334682bc97c03. GitHub reported #4953 as dirty,
with no merge-queue entry, before repair began. This is a real conflict repair,
not an update of a green or queued branch merely to follow main.

The navigation branch already contains the accepted review head, so merging the
actual protected base into it produces the combined candidate without replaying
the scientific edits. Preserve both specification changelog rows (#4558 and
#4902). Resolve only the six evidence-hash conflict blocks, then regenerate the
canonical inventory and reports. Do not adopt an entire ledger from either side.

Candidate tree ba2d631caea204720007b278cd2d7929b3f3deab preserves all 145 original
artifact hashes, all 50 linked manuscript/PDF hashes, and all four amended-page
hashes. Compared with the navigation checkpoint, the inventory has 86 changed
hash values and no changed scientific metadata, rationale, identity or decision.
The conflict regeneration itself changes seven hashes. An initial QA comparison
misread a UTF-8 snapshot using the Windows default encoding; explicit UTF-8
decoding eliminated the false rationale differences. No rationale was edited.

An additional Flash review classifies the protected-main QMD diff as 14 appended
related-article sections, an image presentation change, and digest-table updates.
Lead inspection confirms that scope. The underlying protocol library, public
summary and atlas changes are hashes only. The evidence presentation registry
also advances its generation date from 3 to 5 October; that is preserved as
generation metadata and does not renew a scientific review. See
reports/technical-review/final-navigation-integration-checks.json and
flash-main-integration.txt for evidence and limits.

The integrated tree passes 55 focused publication, navigation, title, link and
claim-inventory tests. This supplements the earlier 65-test navigation checkpoint
and preserves the original full-regression receipt at its stated revision.
Finish canonical audit checks, commit the merge, and run central pre-PR gates.
Then fast-forward the existing consolidation branch to this combined result,
update regular PR #4953 to close #4961, and use the central merge guard. Final
protected-tree and public-site receipts still belong on #4009 before closure.

## Final Gate Repairs

The first central pre-PR run at 4e401bd8f passed 378 affected tests and failed one
MuJoCo import because the process used MUJOCO_GL=egl on Windows. The installed
MuJoCo implementation permits EGL on Linux, not Windows, and explicitly supports
MUJOCO_GL=disable. Using that setting creates no graphics context; all three
URDF/mechanics tests pass. No DLL paths, engine code or tolerances were changed.

The fleet policy gate also found inherited documentation defects: protected main
contains a 271,632-byte development log and a DL-#4558 record missing required
metadata. The combined log was 202,689 bytes, above its unchanged 200,000-byte
limit. Shared collation helpers restore PR #4892 and the verified merge reference,
preserve owner claude and the existing evidence, and state that the original start
date is unknown while recording the real PR creation date. The entry remains in
review pending its owning publication workflow; no other task state was changed.

The shared archiver moves 35 older terminal entries intact to the yearly archive,
leaving 155,832 bytes in the active log. Every archived entry body and every other
entry's fields are preserved. Two archived headings (#3904 and #3903) subsequently
receive the capitalization required by the title gate, without changing their
wording or bodies. The development-log validator now passes with only
the existing portfolio WIP warning. Current change fragments were neither
collated nor deleted. The reusable existing-entry metadata gap is tracked in
Repository_Management #2008; its library fix is separate from this delivered
documentation repair. See final-navigation-policy-repair.json for the receipt.

The second central run at 4bbf61314 passes all 379 affected tests with graphics
disabled and passes the fleet documentation gate; only those two archived heading
capitalizations require correction before the final run.

Repository_Management #1998 is merged at e03344f3d5d0306f990ff295f767dbb1ba74ecd9.
Thirty-eight of its 39 changed files exactly match the accepted head. The remaining
test file has only an independent main addition to SCRIPT_COPIES; the repair is
intact. Its issue receipt is posted and its lease and presence are released.

## Final Local Gate Receipt

All eight central pre-PR gates pass at 504c7dd07eb9369965ba36aa607f2840f83e81fd.
The affected-test run has 379 passes; the earlier integrated publication and
claim-inventory run has 55 passes. Three Streamlit modules are skipped during
collection because that optional package is unavailable. The gate runner reports
its optional absent fleet scripts explicitly; the development-log validator ran
and passed. No tests, tolerances, coverage floors or protection rules changed.
See integrated-pre-pr-final.txt for the exact output. Only this receipt and its
log were added after the gate run. Final protected-main, advertised PDF and
public-site verification remain required before epic closure.

## Delivery Checkout

Use C:/Users/diete/Repositories/Worktrees/AffineDrift-final-partial-sources-review
and local branch fix/current-reviewed-book-links for this combined candidate.
The separate consolidated-20261005 checkout remains at fbee4da94 with pre-existing
local changes; Git refused its fast-forward, and those files were preserved.
Push the validated candidate directly to the existing remote branch
feat/technical-review-consolidated-20261005 without force. PR #4953 remains the
delivery PR. This routing note changes no reviewed source or gate input.

## Pre-Push Formatting Receipt

The normal push hook removed one blank line before `steps` in the inherited
architecture-map-contract workflow. Parsed YAML before and after is identical.
The scoped central workflow-lint gate passes with actionlint and official
ShellCheck 0.11.0 (release archive SHA-256
8a4e35ab0b331c85d73567b12f2a444df187f483e5079ceffa6bda1faa2e740e).
This formatting correction changes no workflow behavior, scientific source,
artifact hash, or validation threshold. It supplements the eight-gate receipt
at 504c7dd07; that receipt is not represented as a rerun at this later commit.
