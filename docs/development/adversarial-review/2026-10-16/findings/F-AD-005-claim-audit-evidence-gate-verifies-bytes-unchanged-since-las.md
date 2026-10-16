# F-AD-005

**Claim-audit evidence gate verifies bytes unchanged since last regenerate, not claims**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟧 High | governance | high | M | proposed |

**Locations:** `scripts/claim_audit_evidence.py:59`, `scripts/claim_audit_evidence.py:207`, `scripts/regenerate_claim_audit_evidence.py:120`, `data/trust/claim_critique_ledger.json:490`, `data/trust/claim_registry.json:62`, `data/trust/site_trust_surface_audit.json:111`

## Finding

- Severity: High  - Category: governance
- Confidence: high
- Location: scripts/claim_audit_evidence.py:59-66, 207-230; scripts/regenerate_claim_audit_evidence.py:120-134; data/trust/claim_critique_ledger.json:15, 23, 490-496; data/trust/claim_registry.json:62, 113; data/trust/site_trust_surface_audit.json:10, 80, 111, 150; .github/workflows/ci-standard.yml:352-357; AGENTS.md:359
- Evidence:
  ```python
  # regenerate_claim_audit_evidence.py:120-134
  def _refresh_digest_map(root, holder, label):
      """Recompute ``holder['evidence_sha256']`` from ``holder['evidence_paths']``."""
      ... holder["evidence_sha256"] = fresh
  ```
  AGENTS.md:359: "after editing any file bound by `data/trust/*.json` … run `regenerate_claim_audit_evidence` and
  commit the result". Of 1016 distinct `evidence_paths`: 365 `articles/`, 243 `reports/` (JSON Playwright logs
  from `http://127.0.0.1:8770`), 109 `tests/`, 48 `src/`, 41 critiques, 11 `css/`, 56 refs to a PDF, 68 to a .bib.
  `claim_registry.json`: 11/12 claims `"critique_status": "not_reviewed"`. `claim_critique_ledger.json`: 27/35
  `open`, 1 `critical` (`crit-tip-mass-omission`, line 490) with no open-date while `defaults` declare
  "Critical <= 14 days". `site_trust_surface_audit.json:80-150` contains an "adversarial review" with
  `alternative_mechanisms`, `counterexamples` and `falsifiers` for the **About** page and for a placeholder
  "book reviews" page.
- Failure scenario: an agent edits a test to `assert True`, runs the regenerate command the docs tell it to run,
  commits; `--check` passes, and the ledger now "pins" the neutered test as evidence. Conversely, a byte-identical
  CSS file is "evidence" for a biomechanics claim. 2 MB of JSON that no reader will open presents as rigor.
- Why a newer engineer misses this: hashing feels like integrity. But integrity of *what*? A digest only tells you
  the bytes didn't change; the thing you need is that a specific assertion was executed and passed against the
  specific claim text, which is a *test run*, not a hash.
- Proposed change: (1) restrict `evidence_paths` to `tests/…::test_fn` symbols and `src/` symbols (the `::` form
  already exists); reject prose, CSS, PDF, bib and `reports/*.json`. (2) Make the claim-audit step *run* the
  referenced test node-ids (`pytest <ids> -q`) and record pass/fail + commit in the ledger. (3) Add `opened_on` to
  critiques and fail the gate when `critical` exceeds the declared SLA. (4) Delete the surface-audit entries for
  non-scientific routes (about, book-reviews, home).
- Verification: `python -m scripts.regenerate_claim_audit_evidence --check` fails when a referenced test fails.
- Effort: M

## Draft Pull Request

**Title:** `fix(governance): make claim-audit evidence run tests, not hash files`

### Why This Matters (The Pitch)

The claims gate is the repository's main answer to "how do you know?", and today it answers with checksums. It verifies that files have not changed since someone ran regenerate, not that any claim is true. Of 1016 distinct evidence paths, 365 are articles, 243 are localhost Playwright JSON logs, and others are CSS, PDFs and bib files. 11 of 12 registry claims are `not_reviewed`, 27 of 35 critiques are open, and one `critical` critique has no open date against a declared 14-day SLA. An agent can edit a test to `assert True`, run the documented regenerate command, and the ledger now pins the neutered test as evidence. A reviewer who opens this ledger sees roughly 2 MB of JSON that presents as rigor and is not. The proposed change restricts evidence to test and source symbols, makes the gate run the referenced node-ids and record pass or fail, and enforces the critical SLA. That converts the machinery from byte bookkeeping into an actual scientific check, which is what the manuscript is relying on.

### Proposed PR Body

## Problem
`scripts/regenerate_claim_audit_evidence.py:120-134` only recomputes `evidence_sha256` from `evidence_paths`; `.github/workflows/ci-standard.yml:352-357` checks that digest. `data/trust/claim_critique_ledger.json:490-496` holds a `critical` critique with no open date, and `data/trust/site_trust_surface_audit.json:80-150` contains adversarial reviews of the About and book-reviews pages.

## Change
- [ ] Restrict `evidence_paths` to `tests/...::test_fn` and `src/` symbols; reject prose, CSS, PDF, bib and `reports/*.json`
- [ ] Make the claim-audit step run the referenced node-ids (`pytest <ids> -q`) and record pass/fail plus commit in the ledger
- [ ] Add `opened_on` to critiques and fail the gate when `critical` exceeds the declared SLA
- [ ] Delete surface-audit entries for non-scientific routes (about, book-reviews, home)

## Verification
`python -m scripts.regenerate_claim_audit_evidence --check` fails when a referenced test fails.

## Risk and Rollback
Ledgers will need a one-time rewrite and CI time rises by the cost of running the referenced tests; revert the commit to restore the hash-only gate.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** Follow-ups: drop PDFs/render logs as evidence (F-AD-009, F-AD-031).

Refs: adversarial review 2026-10-16, F-AD-005


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
