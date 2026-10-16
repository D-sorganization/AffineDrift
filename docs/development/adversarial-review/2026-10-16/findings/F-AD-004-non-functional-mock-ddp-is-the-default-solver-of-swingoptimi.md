# F-AD-004

**Non-functional mock DDP is the default solver of SwingOptimizer while a real iLQR with the same signature is unused**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟧 High | architecture | high | M | proposed |

**Locations:** `src/affine_control/ddp.py:7`, `src/affine_control/ddp.py:55`, `src/affine_control/ddp.py:162`, `src/affine_control/swing_optimizer.py:119`, `src/affine_control/swing_optimizer.py:384`, `src/core/optimizers/optimizer_factory.py:22`

## Finding

- Severity: High  - Category: architecture / correctness
- Confidence: high
- Location: src/affine_control/ddp.py:7-10, 53-60, 162-212; src/affine_control/swing_optimizer.py:1-15, 119-139, 384; src/core/optimizers/optimizer_factory.py:16-18, 22-32; tests/test_affine_control/test_swing_optimizer.py (53 tests), tests/test_medium_wave2.py (28), tests/test_critical_physics_fixes.py:74-160
- Evidence:
  ```python
  # ddp.py:7
  WARNING: The DDP implementation in this module is a non-functional mock. The backward pass and Riccati
  equation solving are not implemented. Results are not mathematically meaningful.
  # ddp.py:55  — production code sniffing for pytest
  return "PYTEST_CURRENT_TEST" in os.environ or "pytest" in os.environ.get("PYTHONPATH", "")
  # optimizer_factory.py:22  — a real solver with the mock's exact signature, wired to nothing
  def ilqr_solver_wrapper(f, x0, xf, u_init, eps_residual=1e-3, max_iters=50, compute_hessian_bound_func=None, dt=0.01)
  ```
  `swing_optimizer.py:1-7` still says it "find[s] optimal joint torque trajectories that maximize clubhead velocity".
- Failure scenario: ~100 tests assert properties of a solver that does nothing (resamples controls, re-simulates);
  "coverage" of `swing_optimizer` is on the critical-coverage list (check_critical_module_coverage.py:66-73).
  The referenced issue document `docs/assessments/issues/ISSUE_Completist_Critical_DDPMock_2026-01-30.md` does
  not exist. Since 2026-01-30.
- Why a newer engineer misses this: the mock was wrapped in so much DbC scaffolding (env-var gates, warnings,
  `allow_mock_solver`) that it reads as a deliberate safety feature rather than dead weight.
- Proposed change: delete `ddp.py`; make `SwingOptimizer.__init__` default to `ilqr_solver_wrapper`; drop
  `allow_mock_solver`, `_is_running_under_pytest`, and the 5-iteration outer loop (`max_iters=min(5, …)` at
  swing_optimizer.py:384 re-runs the solver cold instead of warm-starting). Keep `_rk4_step`/`_resample_controls`
  only if something uses them.
- Verification: `pytest tests/test_affine_control/test_swing_optimizer.py` after rewriting its mock-specific tests;
  an integration test that the double-integrator reaches the target velocity within tolerance.
- Effort: M

## Draft Pull Request

**Title:** `refactor(optimizer): drop mock DDP, default SwingOptimizer to iLQR`

### Why This Matters (The Pitch)

The default solver behind the 727-LOC SwingOptimizer describes itself as a "non-functional mock" whose results are "not mathematically meaningful", and it has been that way since 2026-01-30. Around 100 tests assert properties of a solver that resamples controls and re-simulates, the module sits on the critical-coverage list, and the issue document the mock points to does not exist. Meanwhile a real iLQR with the identical signature, `ilqr_solver_wrapper`, is wired to nothing. For a paper that may cite optimal swing results, an optimizer that does not optimize is a credibility trap, and the scaffolding around it (environment-variable gates, pytest sniffing in production code, `allow_mock_solver`) makes it read as a safety feature. The change is mostly deletion: remove ddp.py and its flags, switch the default, and rewrite the mock-specific tests into a test that the double-integrator actually reaches its target. Less to lint, less to clone, and an optimizer reviewers can trust.

### Proposed PR Body

## Problem
`src/affine_control/ddp.py:7-10` declares the DDP a non-functional mock (backward pass and Riccati solve not implemented), `ddp.py:55` sniffs `PYTEST_CURRENT_TEST` in production code, and `src/affine_control/swing_optimizer.py:119-139, 384` uses it by default, while `src/core/optimizers/optimizer_factory.py:22-32` offers an unused `ilqr_solver_wrapper` with the same signature.

## Change
- [ ] Delete `src/affine_control/ddp.py`
- [ ] Make `SwingOptimizer.__init__` default to `ilqr_solver_wrapper`
- [ ] Drop `allow_mock_solver`, `_is_running_under_pytest`, and the 5-iteration outer loop (`max_iters=min(5, ...)` at `swing_optimizer.py:384`)
- [ ] Keep `_rk4_step`/`_resample_controls` only if something uses them
- [ ] Rewrite mock-specific tests (`tests/test_affine_control/test_swing_optimizer.py`, `tests/test_medium_wave2.py`, `tests/test_critical_physics_fixes.py:74-160`)

## Verification
`pytest tests/test_affine_control/test_swing_optimizer.py` after rewrite, plus an integration test that the double-integrator reaches the target velocity within tolerance.

## Risk and Rollback
Optimizer results will change since the previous ones were not meaningful; revert the commit to restore the mock.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-004


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
