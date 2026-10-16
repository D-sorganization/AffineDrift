# F-AD-028

**Hard-coded Windows user path in a committed script**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | hygiene | high | S | proposed |

**Locations:** `scripts/find_magic_numbers.py:15`

## Finding

- Severity: Low  - Category: hygiene
- Confidence: high
- Location: scripts/find_magic_numbers.py:14-16
- Evidence: `r"C:\Users\diete\Repositories\AffineDrift\articles\The_Physics_of_Golf"`.
- Proposed change: `Path(__file__).resolve().parents[1] / "articles" / …`; or delete the script (nothing imports it).
- Effort: S

## Draft Pull Request

**Title:** `chore(scripts): remove hard-coded Windows path from find_magic_numbers`

### Why This Matters (The Pitch)

A committed script hard-codes a personal Windows path. Derive it from `__file__`, or delete the script since nothing imports it.

### Proposed PR Body

## Problem
`scripts/find_magic_numbers.py:14-16` hard-codes `C:\Users\diete\Repositories\AffineDrift\articles\The_Physics_of_Golf`.

## Change
- [ ] Use `Path(__file__).resolve().parents[1] / "articles" / ...`, or delete the script

## Verification
Run the script from a different checkout location, or confirm it is removed.

## Risk and Rollback
Trivial; revert to roll back.

## Handoff
None

Refs: adversarial review 2026-10-16, F-AD-028

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
