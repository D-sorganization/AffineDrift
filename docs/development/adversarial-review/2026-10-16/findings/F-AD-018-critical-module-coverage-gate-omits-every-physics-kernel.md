# F-AD-018

**Critical-module coverage gate omits every physics kernel**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | governance | high | S | proposed |

**Locations:** `scripts/check_critical_module_coverage.py:28`, `scripts/check_critical_module_coverage.py:66`

## Finding

- Severity: Medium  - Category: governance / tests
- Confidence: high
- Location: scripts/check_critical_module_coverage.py:28-80
- Evidence: targets are `check_site_health`, `check_links`, `update_navigation`, `generate_sitemap`,
  `golf_simulation.*`, `ilqr_solver`, and `swing_optimizer` (the mock wrapper, F-AD-004). Absent: `dynamics`,
  `golf_model`, `double_pendulum_affine`, `rnea`, `lqr`, `ztcf_contract`, `swing_analysis`, `impact_contact_models`.
- Failure scenario: the gate that is supposed to protect what the manuscript depends on protects the link checker.
- Proposed change: list the eight kernel modules at ≥95 % with their test files; drop site tooling from "critical".
- Verification: run the script.
- Effort: S

## Draft Pull Request

**Title:** `fix(ci): point critical-module coverage gate at the physics kernel`

### Why This Matters (The Pitch)

The gate that is supposed to protect what the manuscript depends on protects the link checker. Its target list covers site health, links, navigation, sitemap, golf simulation, ilqr_solver and the mock swing_optimizer wrapper. It omits dynamics, golf_model, double_pendulum_affine, rnea, lqr, ztcf_contract, swing_analysis and impact_contact_models, which is the scientific kernel. A coverage regression in any of those currently passes silently. List the eight kernel modules at 95 % or higher with their test files and drop the site tooling from "critical". It is a small config edit that puts the guardrail where the science is, and a coverage regression in the equations would then fail loudly instead of passing quietly.

### Proposed PR Body

## Problem
`scripts/check_critical_module_coverage.py:28-80` lists `check_site_health`, `check_links`, `update_navigation`, `generate_sitemap`, `golf_simulation.*`, `ilqr_solver` and `swing_optimizer`, but none of `dynamics`, `golf_model`, `double_pendulum_affine`, `rnea`, `lqr`, `ztcf_contract`, `swing_analysis` or `impact_contact_models`.

## Change
- [ ] List the eight kernel modules at >=95 % with their test files
- [ ] Drop site tooling from the critical list

## Verification
Run `scripts/check_critical_module_coverage.py`.

## Risk and Rollback
If any kernel module is currently under 95 %, the gate will fail until tests are added; set thresholds to measured values first if needed. Revert to roll back.

## Handoff
None

Refs: adversarial review 2026-10-16, F-AD-018

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
