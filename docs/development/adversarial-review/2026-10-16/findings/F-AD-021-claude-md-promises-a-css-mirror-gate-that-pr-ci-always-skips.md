# F-AD-021

**CLAUDE.md promises a CSS mirror gate that PR CI always skips**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | docs | high | S | proposed |

**Locations:** `CLAUDE.md:93`, `CLAUDE.md:109`, `.github/workflows/ci-standard.yml:152`, `.gitignore:22`

## Finding

- Severity: Low  - Category: docs / governance
- Confidence: high
- Location: CLAUDE.md:93, 109; .github/workflows/ci-standard.yml:148-156, 367-377; .gitignore:22
- Evidence: "CI validates that `_site/` mirrors match" — the step is `if [ -d _site ] … else echo Skipping`, and
  `_site/` is git-ignored, so in `static-checks` it never runs (the workflow comment at 369-371 admits this). It
  runs only in deploy, after merge.
- Proposed change: delete the sentence or move the mirror check into the e2e lane after `quarto render`.
- Effort: S

## Draft Pull Request

**Title:** `docs(claude): drop or relocate the CSS mirror gate claim`

### Why This Matters (The Pitch)

CLAUDE.md says CI validates that the `_site/` CSS mirrors match, but in PR CI `_site/` is git-ignored and absent, so the step prints Skipping every time. It only runs at deploy, after merge. Delete the sentence or move the check into the e2e lane after `quarto render`.

### Proposed PR Body

## Problem
`CLAUDE.md:93, 109` promise CI validates `_site/` mirrors; `.github/workflows/ci-standard.yml:148-156, 367-377` skips the step when `_site` is missing and `.gitignore:22` ignores it.

## Change
- [ ] Delete the claim, or move the mirror check into the e2e lane after `quarto render`

## Verification
Either the docs no longer make the claim, or the e2e lane fails on a deliberately mismatched mirror.

## Risk and Rollback
Docs or CI-lane change; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-021


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
