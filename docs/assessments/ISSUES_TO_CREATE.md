# Issues to Create

## Break up the root script.js monolith

**Problem statement**  
The repository’s root `script.js` is 1,525 LOC, which is well beyond a reasonable module-size budget for a site with multiple feature areas.

**Evidence**
- `script.js`

**Impact**  
Frontend changes become harder to review, test, and reason about, and unrelated behaviors are likely coupled.

**Proposed fix**  
Split `script.js` by feature area into smaller modules with explicit imports and direct tests for nontrivial behavior.

**Acceptance criteria**
- The root module becomes a small bootstrap/orchestration file.
- Feature logic moves into named modules.
- JS tests cover extracted behavior.

**Expectations**  
Directly improves DRY, SRP, and maintainability.

---

## Replace or quarantine the mock DDP implementation

**Problem statement**  
`src/affine_control/ddp.py` still documents that the DDP implementation is a non-functional mock, which weakens reliability for optimization-oriented code and documentation.

**Evidence**
- `src/affine_control/ddp.py`

**Impact**  
Readers and callers can over-trust optimization behavior that is explicitly incomplete.

**Proposed fix**  
Implement the missing optimization logic or move the mock behind an unmistakably placeholder interface with updated tests and docs.

**Acceptance criteria**
- Production-style paths do not depend on the mock as if it were validated DDP.
- Tests distinguish placeholder behavior from validated optimization.
- Documentation reflects the actual runtime contract.

**Expectations**  
Relevant to TDD, DbC, and reliability expectations.

---

## Raise coverage enforcement for critical modules

**Problem statement**  
The repo has a large test suite but still allows `fail_under = 50` in `pyproject.toml`, which is too permissive for a contract-heavy scientific/editorial codebase.

**Evidence**
- `pyproject.toml`
- `tests/`

**Impact**  
The CI quality bar does not match the repository’s stated engineering expectations.

**Proposed fix**  
Increase the global threshold and add stricter expectations for critical numerical and frontend modules.

**Acceptance criteria**
- Global coverage threshold is raised above 50%.
- Critical-module thresholds are defined and enforced.
- CI fails on regression below those thresholds.

**Expectations**  
Directly improves TDD and maintainability.
