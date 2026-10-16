# F-AD-002

**Corpus and the only executable ZTCF contract define ZTCF as forward-integrated; manuscript says pointwise**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟧 High | docs | high | M | proposed |

**Locations:** `src/affine_control/ztcf_contract.py:176`, `data/ztcf/planar_golf_forward_fixture_v2.json:9`, `src/affine_control/golf_model.py:258`, `src/affine_control/ztcf_explorer.py:8`, `NOTATION.md:56`, `articles/zero-torque-counterfactual.qmd:18`

## Finding

- Severity: High  - Category: docs / correctness
- Confidence: high
- Location: src/affine_control/ztcf_contract.py:176; data/ztcf/planar_golf_forward_fixture_v2.json:9; src/affine_control/golf_model.py:258-294; src/affine_control/ztcf_explorer.py:6-12; NOTATION.md:47-59; articles/zero-torque-counterfactual.qmd:16-18, 158, 184; src/affine_control/double_pendulum_affine.py:16-20
- Evidence:
  ```python
  construction: Literal["forward"]          # ztcf_contract.py:176 — the only admissible value
  ```
  ```yaml
  # zero-torque-counterfactual.qmd:18
  - "ZTCF computes the forward-dynamics trajectory that results when muscular torques are set to zero."
  ```
- Failure scenario: the paper says "ZTCF is f(x(t)) evaluated pointwise; it is not a forward trajectory"; the
  supplementary site, NOTATION.md and the interactive explorer say the governed construction is `forward`.
  Reviewer 2 quotes both. (The pointwise implementation exists — `GolfModel.drift_acceleration`,
  `SwingAnalysis.joint_acceleration_components` — but is not the thing the contract, fixture and widget publish.)
- Why a newer engineer misses this: the definition evolved; the code and ledgers froze the earlier one, and the
  terminology gate (`check_terminology.py`) only checks the acronym *expansion*, not the construction.
- Proposed change: decide once. If the manuscript is right, (a) rename `ztcf_trajectory`/`ZTCFIntervention` to
  `drift_rollout`/`DriftRolloutIntervention` with `construction: Literal["forward","branched"]` and reserve "ZTCF"
  for the pointwise sample; (b) add a `PointwiseZTCFSample` contract (state, τ, f, Gτ, residual) and make it the
  governed executable; (c) rewrite qmd:18 and the abstract. If the family stays, the manuscript must adopt the
  qualifiers and say so in its definitions.
- Verification: `grep -rn "forward.*ZTCF\|ZTCF.*forward" articles NOTATION.md` returns only qualified uses;
  `tests/test_terminology_contract.py` asserts the abstract's key-takeaway sentence.
- Effort: M

## Draft Pull Request

**Title:** `docs(ztcf): reconcile forward ZTCF contract with pointwise manuscript`

### Why This Matters (The Pitch)

Reviewer 2 will quote the paper and the supplementary site against each other, and today they disagree on the central definition. The manuscript treats ZTCF as a pointwise evaluation of f(x(t)). The only governed executable (`construction: Literal["forward"]`), the fixture, the explorer widget, NOTATION.md and the article abstract all define it as a forward-integrated trajectory. The pointwise implementation exists in GolfModel and SwingAnalysis but is not what the contract, fixture or widget publish, and the terminology gate checks only the acronym expansion, not the construction. A paper whose product is credibility cannot ship with its own supplement contradicting its thesis. The finding asks for one decision, encoded once: either rename the forward objects as drift rollouts, add a pointwise sample contract and rewrite the abstract, or keep the family and have the manuscript adopt the qualifiers. Either way the reader of the paper and the reader of the site end up looking at the same definition. Authors and reviewers both save a round of correspondence.

### Proposed PR Body

## Problem
`src/affine_control/ztcf_contract.py:176` allows only `construction: Literal["forward"]`, and `data/ztcf/planar_golf_forward_fixture_v2.json:9`, `src/affine_control/ztcf_explorer.py:6-12`, `NOTATION.md:47-59` and `articles/zero-torque-counterfactual.qmd:18` define ZTCF as the forward-dynamics trajectory. The manuscript defines it pointwise; the pointwise code (`GolfModel.drift_acceleration`, `SwingAnalysis.joint_acceleration_components`) is not the governed executable.

## Change
- [ ] Decide the definition once (manuscript pointwise vs. a qualified family)
- [ ] If pointwise: rename `ztcf_trajectory`/`ZTCFIntervention` to `drift_rollout`/`DriftRolloutIntervention` with `construction: Literal["forward","branched"]`
- [ ] Add a `PointwiseZTCFSample` contract (state, tau, f, G tau, residual) and make it the governed executable
- [ ] Rewrite `articles/zero-torque-counterfactual.qmd:18` and the abstract; otherwise add the qualifiers to the manuscript definitions

## Verification
`grep -rn "forward.*ZTCF\|ZTCF.*forward" articles NOTATION.md` returns only qualified uses; `tests/test_terminology_contract.py` asserts the abstract's key-takeaway sentence.

## Risk and Rollback
Renames touch the contract, fixture and widget parity; the fixture digests will change. Revert the commit to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** Follow-ups: update the explorer widget and parity fixtures to match the chosen vocabulary.

Refs: adversarial review 2026-10-16, F-AD-002


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
