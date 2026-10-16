# F-AD-026

**review_commit/verification_commit/source_revision are unverifiable 40-hex strings**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | governance | medium | S | proposed |

**Locations:** `data/trust/claim_registry.json:25`, `src/affine_control/ztcf_contract.py:53`

## Finding

- Severity: Low  - Category: governance
- Confidence: medium
- Location: data/trust/claim_registry.json:25-33; src/affine_control/ztcf_contract.py:53
- Evidence: pydantic validates `^[0-9a-f]{40}$`; nothing checks the commit exists or contains the referenced file
  at the referenced sha256. In a shallow clone (as deployed) they cannot be checked at all.
- Proposed change: in `regenerate_claim_audit_evidence --check`, when `.git` is present, `git cat-file -e <sha>` and
  `git rev-parse <sha>:<path>` → blob sha; else skip with a warning (not silently pass).
- Effort: S

## Draft Pull Request

**Title:** `feat(trust): verify recorded commit SHAs exist when git is present`

### Why This Matters (The Pitch)

Commit fields in the claim registry and ZTCF contract are checked only for 40-hex shape, so a made-up SHA passes. When `.git` is present, verify with `git cat-file -e` and `git rev-parse <sha>:<path>`; otherwise skip with a visible warning.

### Proposed PR Body

## Problem
`data/trust/claim_registry.json:25-33` and `src/affine_control/ztcf_contract.py:53` validate `^[0-9a-f]{40}$` only; nothing checks the commit exists or contains the file at the referenced digest, and a shallow clone cannot check at all.

## Change
- [ ] In `regenerate_claim_audit_evidence --check`, when `.git` is present, run `git cat-file -e <sha>` and `git rev-parse <sha>:<path>`
- [ ] Otherwise skip with a warning, not silently

## Verification
`--check` fails on a fabricated SHA in a full clone and warns in a shallow one.

## Risk and Rollback
May fail on existing placeholder SHAs; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-026


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
