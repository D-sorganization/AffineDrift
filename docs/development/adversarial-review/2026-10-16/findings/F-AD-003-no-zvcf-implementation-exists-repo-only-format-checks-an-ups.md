# F-AD-003

**No ZVCF implementation exists; repo only format-checks an upstream manifest field**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟧 High | correctness | high | S | proposed |

**Locations:** `scripts/check_proximal_distal_evidence.py:2`, `scripts/check_proximal_distal_evidence.py:37`, `scripts/check_proximal_distal_evidence.py:172`, `NOTATION.md:73`

## Finding

- Severity: High  - Category: correctness / docs
- Confidence: high
- Location: scripts/check_proximal_distal_evidence.py:1-2, 37, 172-180; NOTATION.md:65-88
- Evidence:
  ```python
  """Validate the pinned proximal-distal publication evidence without recomputing it."""
  REQUIRED_COMPONENTS = {"total", "drift", "control", "zvcf"}
  ...
  if not _is_finite_number(components[name]): errors.append(f"{field}.{name} must be finite")
  ```
  `grep -rn zvcf src js` → zero implementations; 59 content files mention ZVCF.
- Failure scenario: the paper defines a_ZVCF = −M⁻¹h(q,0); nothing in this repo computes it, so the ZVCF numbers on
  the site are untraceable to code the reader can run. "Is finite" is the entire scientific check.
- Why a newer engineer misses this: a validator with 300 lines of field checks *looks* like verification.
- Proposed change: add `GolfModel.zvcf_acceleration(q, gravity) = -solve(M(q), gravity_torque(q))` (3 lines) and
  `SwingAnalysis.zvcf_components()`; assert `zvcf == drift` when q̇ = 0 and `|zvcf − drift| ≤ ‖M⁻¹Cq̇‖` otherwise.
- Verification: new pytest; a worked-example callout in the ZVCF section checked like `test_ztcf_pointwise_sample_at_rest`.
- Effort: S

## Draft Pull Request

**Title:** `feat(swing-analysis): implement ZVCF acceleration and test against drift`

### Why This Matters (The Pitch)

The paper defines a_ZVCF = -M^-1 h(q,0), and the site shows ZVCF numbers, but nothing in the repository computes it. A grep for zvcf across src and js returns zero implementations while 59 content files mention it. The only code that touches it is a validator whose entire scientific check is that a manifest field is finite. A reader who wants to trace a ZVCF number on the site to code they can run hits a wall, and a reviewer asking for the same will draw conclusions. The finding sizes the fix at S: roughly three lines on GolfModel plus a SwingAnalysis wrapper, with a clean mathematical test (ZVCF equals drift when velocity is zero, and differs by no more than the norm of M^-1 C qdot otherwise). That is a cheap way to turn a documented quantity into a verified one, and it gives the worked-example callouts something real to check against. Authors get traceable numbers; reviewers get code.

### Proposed PR Body

## Problem
`scripts/check_proximal_distal_evidence.py:1-2, 37, 172-180` validates the pinned evidence "without recomputing it" and only checks `_is_finite_number`. `NOTATION.md:65-88` defines ZVCF, yet `grep -rn zvcf src js` finds no implementation.

## Change
- [ ] Add `GolfModel.zvcf_acceleration(q, gravity) = -solve(M(q), gravity_torque(q))`
- [ ] Add `SwingAnalysis.zvcf_components()`
- [ ] Assert `zvcf == drift` when qdot = 0 and `|zvcf - drift| <= ||M^-1 C qdot||` otherwise
- [ ] Add a worked-example callout in the ZVCF section

## Verification
New pytest covering the two properties above; the callout checked like `test_ztcf_pointwise_sample_at_rest`.

## Risk and Rollback
Purely additive code; revert the commit to roll back.

## Handoff
None

Refs: adversarial review 2026-10-16, F-AD-003

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
