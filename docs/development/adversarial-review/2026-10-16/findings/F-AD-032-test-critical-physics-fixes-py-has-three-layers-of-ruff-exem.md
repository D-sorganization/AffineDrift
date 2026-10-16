# F-AD-032

**test_critical_physics_fixes.py has three layers of ruff exemption including F821**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | hygiene | high | S | proposed |

**Locations:** `pyproject.toml:165`, `pyproject.toml:187`, `tests/test_critical_physics_fixes.py:1`

## Finding

- Severity: Low  - Category: hygiene
- Confidence: high
- Location: pyproject.toml:165, 187; tests/test_critical_physics_fixes.py:1
- Evidence: in `[tool.ruff] exclude` *and* `per-file-ignores = ["F821", "E402", "E731", "F401"]` *and* `# ruff: noqa`
  on line 1 — three layers of exemption for a 415-line test file (`F821` = undefined name).
- Proposed change: remove all three; fix what ruff reports (mid-file imports at 74, 168, 260 are E402 by design;
  move them up).
- Effort: S

## Draft Pull Request

**Title:** `chore(lint): remove triple ruff exemption on test_critical_physics_fixes`

### Why This Matters (The Pitch)

One 415-line test file is exempt from ruff three times over: excluded, per-file-ignored for F821 among others, and a blanket noqa. Remove all three and move the mid-file imports to the top.

### Proposed PR Body

## Problem
`pyproject.toml:165, 187` exclude the file and ignore F821, E402, E731, F401; `tests/test_critical_physics_fixes.py:1` has `# ruff: noqa`. Mid-file imports at lines 74, 168, 260.

## Change
- [ ] Remove the `exclude` entry, the per-file-ignores and the `# ruff: noqa`
- [ ] Fix what ruff reports, moving the mid-file imports up

## Verification
`ruff check .` passes with the exemptions removed.

## Risk and Rollback
Lint-only; revert to roll back.

## Handoff
None

Refs: adversarial review 2026-10-16, F-AD-032

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
