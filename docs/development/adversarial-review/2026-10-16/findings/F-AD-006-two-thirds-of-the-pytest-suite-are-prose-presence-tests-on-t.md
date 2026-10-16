# F-AD-006

**Two-thirds of the pytest suite are prose-presence tests on the content corpus**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | tests | high | M | proposed |

**Locations:** `tests/test_control_affine_scientific_trust.py:43`, `tests/test_dcr_reachability_contract.py:47`, `tests/test_secondary_axis_rigor.py:176`, `pyproject.toml:85`

## Finding

- Severity: Medium  - Category: tests
- Confidence: high
- Location: tests/test_control_affine_scientific_trust.py:43-48, 94-102; tests/test_dcr_reachability_contract.py:47-73; tests/test_secondary_axis_rigor.py:176-178; tests/test_proximal_distal_complete_claim_audit.py (84 string asserts); tests/test_deployment_integrity.py (73); tests/test_editorial_and_consistency.py (62)
- Evidence: 413 of 611 test files `read_text()` a .qmd/.tex; 2,638 `assert "<phrase>" (not) in <text>` vs 2,771
  numeric approx asserts; e.g.
  ```python
  forbidden_claims = ("no amount of paddling will steer you", "locked into the path", ...)
  for claim in forbidden_claims: assert claim not in article
  ```
- Failure scenario: 8,088 collected tests give a 92 % coverage number that is dominated by file-reading; the
  science kernel's behaviour is covered by ~800 tests. Rewording "locked into the path" to "locked onto the path"
  re-admits the forbidden claim; renaming a section breaks 20 tests that have nothing to do with correctness.
- Why a newer engineer misses this: they *are* regression tests of editorial decisions, which is legitimate, but
  they live in the same suite and the same coverage number as the physics, so the number stops meaning anything.
- Proposed change: move corpus tests under `tests/content/` with the existing `content_lint` marker (already
  defined, pyproject.toml:85), exclude them from `--cov`, and report two numbers: kernel coverage and content-lint
  count. Replace forbidden-phrase lists with a single YAML of banned claims per page.
- Verification: `pytest -m "not content_lint" --cov=src` shows the honest kernel coverage.
- Effort: M

## Draft Pull Request

**Title:** `test(content): separate corpus prose tests from kernel coverage`

### Why This Matters (The Pitch)

The headline coverage number is mostly measuring file reads. 413 of 611 test files read a .qmd or .tex, and the suite holds 2,638 phrase-presence asserts against 2,771 numeric ones. That gives 8,088 collected tests and 92 % coverage, while the physics kernel is covered by about 800 tests. A reviewer or collaborator who sees "92 %" will assume it describes the dynamics code, and it does not. Rewording "locked into the path" to "locked onto the path" re-admits a forbidden claim, and renaming a section breaks twenty unrelated tests. The tests themselves are legitimate editorial regression checks; the problem is that they share a suite and a number with the physics. The `content_lint` marker already exists, so the change is moving files, excluding them from `--cov`, and reporting two figures: kernel coverage and content-lint count. The honest kernel number is the one the manuscript can stand behind.

### Proposed PR Body

## Problem
413 of 611 test files `read_text()` a .qmd/.tex, e.g. `tests/test_control_affine_scientific_trust.py:43-48, 94-102`, `tests/test_dcr_reachability_contract.py:47-73` and `tests/test_secondary_axis_rigor.py:176-178`; the 92 % coverage figure is dominated by file reading, not the kernel.

## Change
- [ ] Move corpus tests under `tests/content/` using the existing `content_lint` marker (`pyproject.toml:85`)
- [ ] Exclude them from `--cov`
- [ ] Report kernel coverage and content-lint count separately
- [ ] Replace forbidden-phrase lists with a single YAML of banned claims per page

## Verification
`pytest -m "not content_lint" --cov=src` shows the honest kernel coverage.

## Risk and Rollback
Mostly file moves and config; a mistake shows up as changed collection counts. Revert the commit to roll back.

## Handoff
Follow-ups: update the test-count baseline (F-AD-017) once the split lands.

Refs: adversarial review 2026-10-16, F-AD-006

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
