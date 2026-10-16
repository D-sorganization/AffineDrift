# F-AD-024

**Clamped-free shaft modes with no tip mass; the open critical critique targets the shipped model**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | correctness | medium | M | proposed |

**Locations:** `src/affine_control/golf_model.py:38`, `src/affine_control/golf_model.py:109`, `src/affine_control/golf_model.py:157`, `critiques/tip_mass_omission.md:9`, `data/trust/claim_critique_ledger.json:493`, `articles/zero-torque-counterfactual.qmd:22`

## Finding

- Severity: Medium  - Category: correctness / docs
- Confidence: medium
- Location: src/affine_control/golf_model.py:37-38, 104-114, 135-163; critiques/tip_mass_omission.md:9-27; data/trust/claim_critique_ledger.json:490-496; articles/zero-torque-counterfactual.qmd:22
- Evidence: `_BETA_L = (1.8751, 4.6941)` are clamped-**free** Euler–Bernoulli eigenvalues; `shaft_blocks` integrates
  `rho * phi_k` over the shaft only. The critique (severity `critical`, disposition `open`, no date) says exactly
  this. The docstring (golf_model.py:1-8) is honest that it is "an instantaneous inertia example, not a flexible
  simulation", but the article caveats call the evidence level "Qualified Multi-Body".
- Failure scenario: a referee reads the critique page (it is public) and the ledger that says it is critical and
  open, and asks why the manuscript's model was not fixed first.
- Proposed change: add `tip_mass` to `GolfModel` (one term `m_tip φ_j(L) φ_k(L)` in `M_ηη`, `m_tip φ_k(L) r_i(L)`
  in `M_qη`) and switch to clamped–tip-mass mode shapes, or formally close the critique as "out of scope for the
  rigid counterfactual" with a date.
- Verification: `test_a_light_carrier…` still PD; new test that `M_ηη` grows by `m_tip` at η-tip.
- Effort: M

## Draft Pull Request

**Title:** `fix(golf-model): add shaft tip mass or formally close the critique`

### Why This Matters (The Pitch)

The repository's own public ledger carries a `critical`, open critique that the shaft model omits the tip mass, and the shipped fixtures use that model. The shaft modes are clamped-free Euler-Bernoulli eigenvalues with the inertia integrated over the shaft only. A referee who reads the critique page and the ledger will ask why the manuscript's model was not fixed first, and the article describes the evidence as "Qualified Multi-Body". The docstring is honest that this is an instantaneous inertia example, not a flexible simulation. There are two honest exits: add `m_tip` terms to `M_etaeta` and `M_qeta` and switch to clamped-tip-mass mode shapes, or close the critique with a date as out of scope for the rigid counterfactual. Either answers the referee before they ask. Effort is M, and confidence on this finding is medium.

### Proposed PR Body

## Problem
`src/affine_control/golf_model.py:37-38, 104-114, 135-163` uses `_BETA_L = (1.8751, 4.6941)` (clamped-free) and integrates `rho * phi_k` over the shaft only. `critiques/tip_mass_omission.md:9-27` and `data/trust/claim_critique_ledger.json:490-496` record this as `critical` and `open`; `articles/zero-torque-counterfactual.qmd:22` labels the evidence "Qualified Multi-Body".

## Change
- [ ] Add `tip_mass` to `GolfModel`: a term `m_tip phi_j(L) phi_k(L)` in `M_etaeta` and `m_tip phi_k(L) r_i(L)` in `M_qeta`, with clamped-tip-mass mode shapes
- [ ] Or formally close the critique as out of scope for the rigid counterfactual, with a date

## Verification
`test_a_light_carrier...` still passes (positive definite); a new test that `M_etaeta` grows by `m_tip` at the tip.

## Risk and Rollback
Model change will alter fixture numbers and parity digests; the close-out alternative is docs-only. Revert to roll back.

## Handoff
Follow-ups: regenerate fixtures and parity digests if the model changes.

Refs: adversarial review 2026-10-16, F-AD-024

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
