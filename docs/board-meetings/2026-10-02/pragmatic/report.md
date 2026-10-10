# Pragmatic Programmer Review — AffineDrift (work portfolio, week of 2026-09-25)

**Reviewer:** Pragmatic Programmer (staff role)
**Scope:** `docs/development/DEVELOPMENT_LOG.md` process health, plus a skim of
the ~90 PRs merged into `main` over the preceding 7 days (content-audit fixes,
web consolidation batches, and infra chores).

## Executive Summary

1. **The development log has stopped doing its job.** It is documented as "a
   state table for every feature in flight," with a declared WIP limit of 2
   and a companion archive for shipped work. In practice it carries 150
   entries, 74 of them still live (37x the declared limit) and 76 already
   `shipped` but left inline instead of moved to
   `DEVELOPMENT_LOG_ARCHIVE_2026.md` (which holds only 17). The file is 2,163
   lines — a size that defeats its own purpose as a thing anyone reads before
   starting work.
2. **A formatting bug is quietly destroying the log's plain-text value.**
   Numbers and the words next to them are being concatenated with no space in
   `Last verified` and `Summary` fields across the file (993 regex hits),
   e.g. `premerge33afa bytes`, `65 affected checks pass`, `124 full-source
   audits`. This isn't a style nit — it breaks grep, breaks a human skim, and
   is evidence the log is being written by a template or generator that
   nobody is reading the output of.
3. **The content-audit and web-consolidation work itself is a good example of
   the fleet applying its own playbooks.** PR Queue Consolidation
   (`fb377e96`, `3471f7d3`, `019a25a4`) is visibly in use — nine reviewed web
   PRs landed as one batch with a shared test suite — and this is worth
   protecting as the volume of content-fix PRs grows.

Overall health: **Needs Attention**, driven almost entirely by process
bookkeeping rather than code quality. The actual code and content changes
reviewed this week are narrow, well-scoped, and individually testable.

## Principle Assessment

### DRY — Needs Attention
The development log violates DRY at the document level: 76 `shipped` entries
sit duplicated in both the live narrative and (partially) the archive, and
the live file keeps re-stating resolved state instead of pointing at a single
authoritative shipped record. `scripts/claim_audit_*.py` and
`scripts/generate_claim_*.py`, by contrast, are a good counter-example — each
has a single, non-overlapping responsibility (ids, types, evidence, report,
inventory, ledger) and there's no copy-paste between them.

### Orthogonality — Healthy
The week's PRs are narrowly scoped (one chapter, one claim, one audit route
per PR), which keeps blast radius small. The consolidation batches
(`fb377e96`, `3471f7d3`) bundle *already-independent* fixes rather than
coupling unrelated ones, which is the right way to do it.

### Reversibility — Healthy
No findings this week. Content fixes are additive/corrective per-chapter;
infra changes (`.nvmrc` pin in `83f6c0bc`, devcontainer in `15c87673`) are
externalized configuration, not hard-coded assumptions.

### Tracer Bullets — Healthy
No findings. Front-matter schema (`6344508a`) and volume-numbering unification
(`1f52fd88`) both shipped as working end-to-end slices rather than big-bang
rewrites.

### Design by Contract — Not assessed this week
No new module interfaces were reviewed; scope was dominated by content and
process, not API surfaces.

### Broken Windows — Concerning
This is the headline. Two broken windows, left unrepaired across many commits:
- `docs/development/DEVELOPMENT_LOG.md:10` declares `WIP limit: 2`; 74 entries
  currently carry a live state (`proposed`/`in_progress`/`in_review`/`parked`).
  Nobody has updated the limit or enforced it in ~150 entries' worth of
  history — the number is decorative.
- The `premerge33afa`-style number/word concatenation (993 occurrences) has
  clearly been present long enough to propagate across dozens of entries
  (e.g. `DL-#4815`, `DL-#4756`) without anyone noticing or filing it.
- `Last audited: 2026-08-28 by bootstrap` is 5 weeks stale against a file that
  received dozens of edits in the period reviewed.

### Good Enough Software — Needs Attention
The log's structure (per-entry `State`/`Owner`/`PR`/`Issue`/`Branch`/`Paths`/
`Started`/`Last verified`/`Summary`/`Next step`) is good enough and need not
grow. The problem isn't under- or over-engineering of the schema — it's that
the *process* around archiving isn't being followed, so the "good enough"
design is drowning in entries it was never meant to hold indefinitely.

### The Power of Plain Text — Concerning
Directly tied to the Broken Windows finding: concatenated numbers/words make
the log harder to `grep` for a specific check count or digest, and harder for
a human to proofread. A document that's supposed to be the single source of
truth for "what's in flight" is actively degrading in readability every time
an entry is updated by whatever is producing this pattern.

### Use the Shell — Healthy
The claim-audit tooling (`scripts/claim_audit_*.py`,
`scripts/generate_claim_audit_inventory.py`) and the consolidation batches
show good automation discipline — shared pytest suites ride along with
content fixes (e.g. `tests/test_equation_cross_references.py` in `fb377e96`).

### Transforming Programming — Not assessed this week
No findings; out of scope for this week's content-dominated diff set.

## Patterns Observed

- **Process debt accumulates invisibly in documentation, not code.** Every
  individual PR this week looked disciplined (small diff, test alongside
  content, SPEC.md changelog row). The debt is entirely in the shared
  bookkeeping file that every PR is required to touch, which nobody owns the
  overall shape of.
- **Garbled auto-generated text is a leading indicator, not a cosmetic one.**
  When a `Last verified` field reads as a run-on of digits and words, it's a
  sign the thing writing it isn't validating its own output — the same class
  of failure that, elsewhere, produces silently wrong numbers.

## Improvement Pathways

1. **Enforce or retire the WIP limit.** Either the declared limit of 2 is
   real (in which case 74 live entries is a stop-the-line finding) or the
   portfolio has outgrown a limit sized for a different cadence and the
   number itself needs the Board's sign-off to change. Leaving it at 2 while
   routinely running 70+ serves neither purpose.
2. **Archive on ship, same commit.** When an entry's `State` flips to
   `shipped`, move it to `DEVELOPMENT_LOG_ARCHIVE_2026.md` in that same
   commit instead of leaving it inline. This is exactly the kind of
   mechanical step `shared_scripts/development_log.py` (referenced in the
   file's own header, not present in this checkout) should be able to flag or
   automate — worth confirming with Repository_Management whether that
   validator already does an archive check.
3. **Find and fix the source of the number/word concatenation.** 993
   occurrences across 150 entries means this is systemic, not a one-off typo.
   Whatever agent or template assembles `Last verified`/`Summary` text should
   insert a space before/after inline digests and counts.
4. **Re-audit the log's "Last audited" line on a cadence tied to its edit
   rate, not a fixed calendar date** — a file edited by nearly every PR merit
   more frequent spot checks than one that's quiet for months.

## Commendations

- The PR Queue Consolidation playbook is being used correctly and
  productively (`fb377e96`, `3471f7d3`, `019a25a4`): independently-reviewed
  web fixes are batched with their own tests intact, rather than being
  force-merged one at a time or coupled into unrelated work.
- `scripts/claim_audit_*.py` and `scripts/generate_claim_*.py` are a clean
  example of orthogonal decomposition — ids, types, evidence, and reporting
  each own one file with no overlap, which is exactly the shape that keeps a
  growing content-audit pipeline maintainable.
