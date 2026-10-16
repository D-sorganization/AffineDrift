# F-AD-009

**11 MB of terminal transcripts committed, including 371 .exit files containing '0'**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | hygiene | high | S | proposed |

**Locations:** `docs/development/technical-review/putting-mechanics-review/bibliography-quality.exit:1`, `docs/development/technical-review/putting-mechanics-review/bibliography-quality.txt:1`, `reports/technical-review/zero-torque-render-verification.json:1`

## Finding

- Severity: Medium  - Category: hygiene
- Confidence: high
- Location: docs/development/technical-review/putting-mechanics-review/bibliography-quality.exit:1; docs/development/technical-review/putting-mechanics-review/bibliography-quality.txt:1; reports/technical-review/zero-torque-render-verification.json:1
- Evidence: `find -name '*.exit' | xargs cat | sort | uniq -c` → 313×`0`, 34×`1`, 4×`00`, 1×`000100` (a shell
  `>>` that appended successive exit codes). The matching `.txt` files are stdout captures ("INFO: Bibliography
  quality check passed (169 entries, 0 violations)."). 705 of the repo's 735 `.txt` files live here; reports/ is 18 MB
  with 448 JSON render logs whose `base_url` is `http://127.0.0.1:8770`.
- Failure scenario: `git clone` pulls 51 MB of history for a Python package; `grep` across the repo hits logs;
  the trust ledgers reference 243 of these logs as "evidence" (F-AD-005), so deleting them breaks the gate —
  which is how they became permanent.
- Why a newer engineer misses this: agents save their session evidence where they are told to (`docs/development/`),
  and a repo-root hygiene gate (`check_root_hygiene.py`) only looks at the root.
- Proposed change: delete `docs/development/technical-review/**/*.{exit,txt}` and `reports/technical-review/*.json`
  render logs; keep the `.md` summaries. Add `*.exit` to `.gitignore`. Move CI evidence to workflow artifacts.
- Verification: `git ls-files | grep -c '\.exit$'` → 0.
- Effort: S

## Draft Pull Request

**Title:** `chore(repo): remove committed terminal transcripts and render logs`

### Why This Matters (The Pitch)

This is a clean subtraction. 1,254 files and 11 MB of terminal transcripts sit under `docs/development/technical-review`, including 371 `.exit` files that contain "0" (and four "00", plus one "000100" from a shell append). The `.txt` files are stdout captures such as a bibliography check passing; 705 of the repo's 735 `.txt` files live here, and `reports/` adds 448 JSON Playwright logs against localhost. They bloat a clone that already pulls 51 MB of history for a Python package, pollute grep, and became permanent only because the trust ledgers cite 243 of the logs as evidence, so deleting them breaks the gate. Fix that first (F-AD-005) and these go. The `.md` summaries stay, `*.exit` goes into `.gitignore`, and CI evidence moves to workflow artifacts. Everyone who clones, searches or reviews the repo benefits.

### Proposed PR Body

## Problem
`docs/development/technical-review/` holds 1,254 files, including 371 `.exit` files (313 containing `0`, 34 `1`, 4 `00`, 1 `000100`) and stdout `.txt` captures, e.g. `docs/development/technical-review/putting-mechanics-review/bibliography-quality.exit:1`. `reports/technical-review/zero-torque-render-verification.json:1` is one of 448 localhost render logs. The trust ledgers cite 243 of these logs as evidence.

## Change
- [ ] Delete `docs/development/technical-review/**/*.{exit,txt}` and `reports/technical-review/*.json` render logs
- [ ] Keep the `.md` summaries
- [ ] Add `*.exit` to `.gitignore`
- [ ] Move CI evidence to workflow artifacts

## Verification
`git ls-files | grep -c '\.exit$'` returns 0.

## Risk and Rollback
Deleting evidence files breaks the claim-audit gate until the ledgers stop citing them; sequence after F-AD-005 or update the ledgers in the same PR. Revert restores files.

## Handoff
Follow-ups: F-AD-005 (ledger evidence paths) and F-AD-031 (PDFs).

Refs: adversarial review 2026-10-16, F-AD-009

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
