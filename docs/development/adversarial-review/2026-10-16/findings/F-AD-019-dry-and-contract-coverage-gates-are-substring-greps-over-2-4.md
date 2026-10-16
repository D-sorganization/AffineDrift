# F-AD-019

**DRY and contract-coverage gates are substring greps over 2-4 files**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | governance | high | S | proposed |

**Locations:** `scripts/check_dry_adoption.py:37`, `config/contract_coverage_rules.json:4`, `scripts/check_contract_coverage.py:38`, `scripts/check_dependency_boundaries.py:86`, `CLAUDE.md:89`

## Finding

- Severity: Low  - Category: governance
- Confidence: high
- Location: scripts/check_dry_adoption.py:37-41; config/contract_coverage_rules.json:1-19; scripts/check_contract_coverage.py:38; scripts/check_dependency_boundaries.py:86; CLAUDE.md:89
- Evidence:
  ```python
  checks = [("scripts/generate_feed.py", "collect_qmd_files"), ("scripts/generate_feed.py", "read_qmd_with_frontmatter"),
            ("scripts/add_meta_descriptions.py", "read_qmd_with_frontmatter")]
  ```
  CLAUDE.md:89 calls this "DRY adoption tracking — duplication metrics monitored". Both coverage/boundary scripts
  print `files scanned: 0` because `files_scanned=0` is hard-coded.
- Failure scenario: five RK4 copies (F-AD-007) and two double-pendulum models (F-AD-023) pass "DRY tracking".
- Proposed change: replace with `jscpd`/`radon` on `src/` with a committed threshold; or delete the two scripts and
  the CLAUDE.md sentence.
- Verification: `jscpd src --threshold 2` in CI.
- Effort: S

## Draft Pull Request

**Title:** `chore(ci): replace substring DRY and contract-coverage gates`

### Why This Matters (The Pitch)

Two gates that sound like duplication and contract enforcement are substring greps over two to four files, and the coverage and boundary scripts print `files scanned: 0` because the count is hard-coded. Five RK4 copies and two double-pendulum models pass "DRY tracking". Replace them with `jscpd` or `radon` on `src/` with a committed threshold, or delete the scripts and the CLAUDE.md sentence.

### Proposed PR Body

## Problem
`scripts/check_dry_adoption.py:37-41` runs three substring checks; `config/contract_coverage_rules.json:1-19` and `scripts/check_contract_coverage.py:38` hard-code `files_scanned=0` (also `scripts/check_dependency_boundaries.py:86`). `CLAUDE.md:89` describes this as duplication metrics monitoring.

## Change
- [ ] Replace with `jscpd`/`radon` on `src/` with a committed threshold, or delete the two scripts, the rules file and the CLAUDE.md sentence

## Verification
`jscpd src --threshold 2` in CI.

## Risk and Rollback
A real duplication threshold may fail at first; set it to the measured value. Revert to roll back.

## Handoff
Follow-ups: F-AD-007 (RK4 duplication).

Refs: adversarial review 2026-10-16, F-AD-019

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
