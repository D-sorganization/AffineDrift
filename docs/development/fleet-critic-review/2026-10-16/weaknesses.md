# Weaknesses — Forward Dynamics Matching Book (2026-10-16)

## Weakness: Quantitative Cross-Repo Claims Verified by Path Existence, Not Content

### Summary of Concern

Chapters 2 and 3 state specific numeric results — marker RMS in millimetres,
pelvis-yaw percentage error, pass/fail gate outcomes, test counts, boolean
qualification flags — and attribute each to a named file at a single pinned
UpstreamDrift commit. The only check this repository runs against that
commit is whether the cited path exists locally in a one-time snapshot; no
test or CI gate verifies that the quoted numbers actually appear in, or match,
the content at that path.

### Location

- **File/Document:** `articles/forward_dynamics_matching/03_historical_lessons.qmd`, lines 19, 24–27, 33, 37
- **File/Document:** `articles/forward_dynamics_matching/02_upstream_inventory.qmd`, lines 35, 41, 45, 47
- **Supporting evidence:** `articles/forward_dynamics_matching/link_validation.json` (every entry: `"live_http_status": "pending_network_stop"`, `"scope": "Local path validation only; HTTP and claim validation are separate"`); `docs/development/forward-dynamics-matching/validation.md` ("local existence is not HTTP or claim verification"; "Live external links and primary-source metadata still require validation.")
- **Claim or Equation:** e.g. "whole-marker RMS 20.267 mm, early RMS 9.995 mm, club-cluster RMS 8.389 mm, pelvis-yaw error 0.610 percent... The terminal RMS is 40.303 mm versus a 35 mm gate" (`03_historical_lessons.qmd:25`)

### Nature of the Issue

- [x] Empirical insufficiency
- [x] Unstated assumption (that a pinned commit hash + path existence is sufficient provenance for a quoted number)

### Why This Is a Problem

A hostile reviewer only needs to check one of these numbers against the
actual UpstreamDrift commit to test the whole chapter's reliability, and
nothing in AffineDrift's own test suite performs that check. The project's
own Cross-Repo Dependencies policy (`CLAUDE.md`) requires AffineDrift to
"consume, validate, and pin schemas and manifests published by upstream
fleet repositories... verifying SHA-256 digests and cryptographic/schema
provenance." This book's sourcing method falls short of that standard: it
records a commit SHA and a file-existence boolean, not a content digest of
the cited artifact. If the UpstreamDrift commit were ever force-pushed,
rewritten, or if the pinned SHA in `source_manifest.json` were a typo (it is
hand-transcribed prose, not generated from a diff), none of AffineDrift's
tests would catch the drift — the numbers would sit in a rendered textbook
indefinitely, read as established fact by anyone who does not cross the repo
boundary to check. The caveat that would warn a reader off doing exactly that
("local existence is not HTTP or claim verification") is filed in
`docs/development/`, a path no site visitor or PDF reader reaches.

### Evidence / References

- `articles/forward_dynamics_matching/link_validation.json` (53 entries, all HTTP status "pending_network_stop")
- `docs/development/forward-dynamics-matching/validation.md`
- `CLAUDE.md` § Cross-Repo Dependencies ("verifying SHA-256 digests and cryptographic/schema provenance without arbitrary runtime imports")
- Compare: `src/affine_control/programming_companion/` already implements SHA-256-verified upstream consumption for schemas/manifests — the precedent this book's evidentiary claims do not follow.

### Severity

- [x] Medium (argument tightening required) — the hedging language already present keeps any single wrong number from invalidating a load-bearing AffineDrift claim, but the chapters read as more rigorously sourced than the verification behind them supports.

### Suggested Remedies

- Record a content hash (not just a path-existence boolean) per cited UpstreamDrift artifact in `link_validation.json`, and add a test that recomputes it against a fetched or vendored snapshot of the pinned commit before claiming parity.
- Add an inline caveat at the top of `02_upstream_inventory.qmd` and `03_historical_lessons.qmd` — not only in `docs/development/forward-dynamics-matching/validation.md` — stating that quoted numbers are transcribed prose, unverified against upstream content, and may drift from the live UpstreamDrift repository.
- Narrow present-tense claims ("The terminal RMS is 40.303 mm") to explicitly sourced quotations ("the cited UpstreamDrift handoff reports a terminal RMS of 40.303 mm") throughout, to make the attribution, not the number, the thing being asserted.

---

## Weakness: Book Test Suite Checks Structure and Self-Consistency, Not Claim Correctness

### Summary of Concern

`tests/test_forward_dynamics_matching_book.py` is the only automated gate on
this book. Its five tests check: directory/artifact presence, recovery-doc
presence, chapter count/H1 headings/manifest-hash match, Quarto sidebar
wiring, and bibliography key resolution. The manifest-hash test
(`test_all_26_chapters_exist_with_valid_headings_and_manifest_hashes`)
recomputes each chapter body's SHA-256 and compares it to
`source_manifest.json` — but that manifest was generated from the same
chapter files it is checked against, so the test only proves the files have
not been edited since the manifest was written. No test reads a claimed
number out of the prose and checks it against anything external.

### Location

- **File/Document:** `tests/test_forward_dynamics_matching_book.py`, lines 115–141
- **Section:** `test_all_26_chapters_exist_with_valid_headings_and_manifest_hashes`

### Nature of the Issue

- [x] Empirical insufficiency
- [x] Terminological ambiguity ("contract tests" in the PR title, but the contract being tested is file structure, not scientific content)

### Why This Is a Problem

A reviewer skimming the PR title ("add contract tests") could reasonably
infer that the numeric and methodological claims in the book are
machine-checked. They are not: a future edit that silently changed "40.303
mm" to any other number, or removed a hedge sentence, would pass every test
in this file as long as chapter count, H1 headings, and bibliography keys
were preserved. This mirrors a pattern the 2026-10-16 mechanical adversarial
review flagged elsewhere in this repository (`docs/development/adversarial-review/2026-10-16/`:
"the pytest suite are prose-presence tests on t[he]..." family of findings) —
this book was merged the day before that review and was not in its scope, so
the same class of gap recurs here uncaught.

### Evidence / References

- `tests/test_forward_dynamics_matching_book.py:115-141`
- `docs/development/adversarial-review/2026-10-16/README.md` (sibling finding on prose-presence tests elsewhere in the repo)

### Severity

- [x] Low (clarification needed) — no false scientific claim currently depends on this gap, but the gap itself is unguarded.

### Suggested Remedies

- Rename the test module's docstring/PR-facing description to "structural integrity tests" rather than "contract tests" to avoid implying content verification that does not exist.
- If specific numbers are meant to be load-bearing (e.g. the 35 mm / 40.303 mm gate comparison), add a narrow regression test asserting the exact string appears verbatim, so an edit to that number is a visible diff reviewers are asked to justify rather than a silent prose change.

---

## Weakness: Internally Noted Model-Card Inconsistency Is Disclosed in Prose Only, with No Re-Check Mechanism

### Summary of Concern

Chapter 3 states there is "an internal inconsistency" in UpstreamDrift's own
records: "the later model-card turnover states measured speedups and lists
several models as promoted, while the artifact and validation receipts retain
diagnostic, synthetic-only or unmeasured status," and commits to "decline to
repeat promoted speed values until source-hashed model weights and run logs
reconcile the statuses." This is a sound editorial stance, but it depends
entirely on the author's memory to re-apply at every future edit — nothing
enforces it.

### Location

- **File/Document:** `articles/forward_dynamics_matching/03_historical_lessons.qmd`, lines 45–47
- **File/Document:** `articles/forward_dynamics_matching/26_neural_proposals.qmd`, line 125

### Nature of the Issue

- [x] Unstated assumption (that the "decline to repeat" policy will be remembered and consistently applied by every future editor of this 26-chapter, ~49,500-word book)
- [x] Empirical insufficiency (no automated check that a future chapter edit, or a new chapter, doesn't reintroduce an UpstreamDrift "promoted" speedup number)

### Why This Is a Problem

A 26-chapter book drafted by "four Luna agents" with "the primary agent"
reviewing (per `docs/development/forward-dynamics-matching/validation.md`) is
exactly the kind of corpus where a locally-scoped editorial decision ("don't
repeat promoted values") is easy to honor in the two chapters that state it
and easy to silently violate in a future chapter, translation, or summary
that doesn't carry the same context. There is no test asserting that
speedup/promotion language from the UpstreamDrift model cards does not appear
unqualified anywhere in this book.

### Evidence / References

- `articles/forward_dynamics_matching/03_historical_lessons.qmd:45-47`
- `articles/forward_dynamics_matching/26_neural_proposals.qmd:125`

### Severity

- [x] Low (clarification needed)

### Suggested Remedies

- Add a lightweight repo-local check (even a `ruff`/custom script grep, not necessarily a full test) that flags the word "promoted" or specific UpstreamDrift speedup figures appearing in `articles/forward_dynamics_matching/*.qmd` without an adjacent "diagnostic"/"unmeasured"/"declines to repeat" qualifier, so the policy survives future edits by agents without this chapter's context.
