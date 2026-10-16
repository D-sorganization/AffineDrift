# F-AD-011

**Wheel-packaging test builds into repo root and reuses a stale wheel forever**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | tests | high | S | proposed |

**Locations:** `tests/test_wheel_packaging.py:22`, `tests/test_wheel_packaging.py:25`

## Finding

- Severity: Medium  - Category: tests
- Confidence: high
- Location: tests/test_wheel_packaging.py:22-37
- Evidence:
  ```python
  def _get_or_build_wheel() -> Path:
      """Return latest wheel in dist/, building one if none exists."""
      wheels = list(dist_dir.glob("affinedrift-*.whl")) if dist_dir.exists() else []
      if not wheels: ... pip wheel ... -w dist .
  ```
  Running the suite created `dist/`, `build/`, `affinedrift.egg-info/` in the checkout (root-hygiene gate then
  reports 3 violations locally).
- Failure scenario: second local run tests yesterday's wheel; a packaging regression (missing `py.typed`, missing
  subpackage) passes locally and fails in CI, or vice-versa.
- Why a newer engineer misses this: "cache the expensive build" is a reasonable instinct; the cache key (none) is the bug.
- Proposed change: build into `tmp_path_factory.mktemp("wheel")` via a session fixture; never glob `dist/`.
- Verification: run twice; `git status --ignored` shows no new dirs.
- Effort: S

## Draft Pull Request

**Title:** `test(packaging): build wheel into tmp dir instead of reusing dist/`

### Why This Matters (The Pitch)

The wheel-packaging test caches its build by globbing `dist/` and never invalidates it, so the second local run tests yesterday's wheel. A packaging regression such as a missing `py.typed` or subpackage can pass locally and fail in CI, or the reverse, which is a miserable class of failure to debug. As a side effect the test litters the checkout with `dist/`, `build/` and an egg-info directory, which then trips the root-hygiene gate with three local violations. The fix is a session fixture that builds into `tmp_path_factory.mktemp("wheel")` and never globs `dist/`. Small, local, and it makes the packaging test mean what it says. A green run then reflects the code being shipped today, not whatever wheel happened to be lying around. Developers stop chasing phantom hygiene failures.

### Proposed PR Body

## Problem
`tests/test_wheel_packaging.py:22-37` returns the latest wheel from `dist/` and builds only if none exists; running the suite creates `dist/`, `build/` and `affinedrift.egg-info/` in the checkout, causing three root-hygiene violations locally.

## Change
- [ ] Build the wheel into `tmp_path_factory.mktemp("wheel")` via a session fixture
- [ ] Stop globbing `dist/`

## Verification
Run the test twice; `git status --ignored` shows no new directories.

## Risk and Rollback
Test-only change; revert the commit to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-011


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
