# F-AD-020

**CSS budget saturated at 3393/3400 lines**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | governance | high | S | proposed |

**Locations:** `config/css_quality_budget.json:3`, `styles.css:1`

## Finding

- Severity: Low  - Category: governance
- Confidence: high
- Location: config/css_quality_budget.json:3; styles.css:1
- Evidence: `check_styles_budget.py` → "lines: 3393 (max 3400)". `!important` 47/212 (budget 4.5× actual).
- Failure scenario: the first PR that adds 8 lines of CSS either fails or bumps the number; the fleet rule
  (AGENTS.md "Never loosen a … budget to turn CI green") then forces a `Tolerance-Change-Evidence` trailer for a
  stylesheet, which nobody will measure.
- Proposed change: budget the *bundle* bytes (`_site/styles.css` after `bundle_css.py`) gzip'd, not the import
  root's line count; set `max_important` to 60.
- Effort: S

## Draft Pull Request

**Title:** `chore(css): budget bundled stylesheet bytes instead of import-root lines`

### Why This Matters (The Pitch)

The CSS line budget sits at 3393 of 3400, so the next stylesheet PR either fails or loosens a budget the fleet rules forbid loosening. Budget the gzip'd bundle instead and set `max_important` to 60.

### Proposed PR Body

## Problem
`config/css_quality_budget.json:3` allows 3400 lines and `styles.css` is at 3393; `!important` is 47 against a budget of 212.

## Change
- [ ] Budget the bundled `_site/styles.css` (after `bundle_css.py`) gzip'd rather than import-root line count
- [ ] Set `max_important` to 60

## Verification
`check_styles_budget.py` reports against the new bundle-size budget.

## Risk and Rollback
Config and script change; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-020


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
