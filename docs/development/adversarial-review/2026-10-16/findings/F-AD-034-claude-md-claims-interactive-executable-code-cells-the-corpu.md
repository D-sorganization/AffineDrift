# F-AD-034

**CLAUDE.md claims interactive/executable code cells; the corpus has zero executable cells**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | docs | high | S | proposed |

**Locations:** `CLAUDE.md:13`, `CLAUDE.md:99`, `AGENTS.md:379`

## Finding

- Severity: Low  - Category: docs
- Confidence: high
- Location: CLAUDE.md:13, 99; AGENTS.md:379-381
- Evidence: regex over 396 .qmd: 0 `{python}`/`{ojs}`/`{javascript}` executable fences; 40 non-executable
  ```` ```python ```` listings. The ">20-line inline Python is forbidden" rule is vacuously satisfied; Quarto is
  being used as a Markdown renderer.
- Proposed change: say so (it is a good decision: reproducibility comes from `src/` + tests, not from render-time
  execution). Delete the rule and the check that exists for it.
- Effort: S

## Draft Pull Request

**Title:** `docs(claude): state that the corpus has no executable Quarto cells`

### Why This Matters (the Pitch)

CLAUDE.md promises interactive code cells and executable models, but the 396 .qmd files contain none. Say so, and delete the vacuous inline-Python rule and its check.

### Proposed PR Body

## Problem
`CLAUDE.md:13, 99` and `AGENTS.md:379-381` describe executable cells; a regex over 396 .qmd files finds 0 executable fences and 40 non-executable python listings.

## Change
- [ ] Reword the docs to say reproducibility comes from `src/` plus tests, not render-time execution
- [ ] Delete the >20-line inline Python rule and its check

## Verification
Docs no longer claim executable cells; the removed check is gone from CI.

## Risk and Rollback
Docs-only; revert to roll back.

## Handoff
None

Refs: adversarial review 2026-10-16, F-AD-034

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
