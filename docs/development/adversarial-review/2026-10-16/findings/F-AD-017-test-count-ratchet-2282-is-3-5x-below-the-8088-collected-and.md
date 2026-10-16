# F-AD-017

**Test-count ratchet (2282) is 3.5x below the 8088 collected and can never fire**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | governance | high | S | proposed |

**Locations:** `.github/workflows/ci-standard.yml:420`, `.github/workflows/ci-standard.yml:481`

## Finding

- Severity: Low  - Category: governance
- Confidence: high
- Location: .github/workflows/ci-standard.yml:420, 479-481
- Evidence: `BASELINE_TEST_COUNT: 2282`; local `pytest tests --co -o addopts=""` → 8088 collected. A PR could delete
  5,800 tests and pass.
- Proposed change: either auto-ratchet (write the collected count to `config/test_count_baseline.json` on main and
  compare on PR) or delete the step. A count is a weak proxy anyway; prefer mutation score on the kernel (§4).
- Verification: the baseline file changes in the same PR that adds/removes tests.
- Effort: S

## Draft Pull Request

**Title:** `fix(ci): replace stale test-count baseline with auto-ratchet`

### Why This Matters (The Pitch)

The test-count guard cannot fire. Its baseline is 2282 and the suite collects 8088, so a PR could delete 5,800 tests and still pass. Either auto-ratchet the count from main or delete the step.

### Proposed PR Body

## Problem
`.github/workflows/ci-standard.yml:420, 479-481` sets `BASELINE_TEST_COUNT: 2282` while `pytest tests --co -o addopts=""` collects 8088.

## Change
- [ ] Write the collected count to `config/test_count_baseline.json` on main and compare on PR, or delete the step

## Verification
The baseline file changes in the same PR that adds or removes tests.

## Risk and Rollback
CI-only; a wrong baseline blocks PRs, so revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** Follow-ups: mutation testing on the kernel as a stronger signal than a count.

Refs: adversarial review 2026-10-16, F-AD-017


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
