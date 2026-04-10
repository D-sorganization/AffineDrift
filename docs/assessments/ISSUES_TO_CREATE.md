# Issues to Create

## Replace or quarantine the mock DDP implementation

**Problem statement**  
`src/affine_control/ddp.py` explicitly documents that the DDP implementation is a non-functional mock and warns that the backward pass and Riccati solving are not implemented. That makes optimization behavior easy to misunderstand and weakens reliability claims.

**Evidence**
- `src/affine_control/ddp.py`

**Impact**  
Optimization-related tests and documentation can imply more mathematical validity than the implementation actually provides.

**Proposed fix**  
Either implement the missing backward-pass logic or move the mock behind an unmistakably non-production interface and update callers/tests accordingly.

**Acceptance criteria**
- Production-facing code paths no longer depend on the mock as if it were real DDP.
- Tests clearly separate placeholder behavior from validated optimization behavior.
- Documentation matches the runtime contract.

**Expectations**  
Relevant to TDD, DbC, and reliability expectations.

---

## Refactor the wrist model monolith into tested components

**Problem statement**  
`content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` is 1,512 LOC, with `initUI` at 484 LOC and `update_diagram` at 333 LOC. This is a confirmed SRP and function-size violation.

**Evidence**
- `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py`

**Impact**  
UI and plotting changes are difficult to review, test, and safely evolve.

**Proposed fix**  
Split the module into domain math, plotting, and UI composition helpers, with tests for each nontrivial component.

**Acceptance criteria**
- The largest functions are reduced to orchestration only.
- Plotting/state update logic is moved into reusable helpers.
- New tests cover the extracted behavior.

**Expectations**  
Directly addresses DRY, LoD, SRP, and maintainability.

---

## Raise coverage enforcement for critical scientific modules

**Problem statement**  
The repo has a strong test suite, but CI still allows `fail_under = 50` in `pyproject.toml`, which is too low for a contract-heavy scientific/editorial codebase.

**Evidence**
- `pyproject.toml`
- `tests/`

**Impact**  
Important regressions can slip through even though the repo already has the discipline to support stronger guarantees.

**Proposed fix**  
Raise the coverage floor in stages and enforce higher coverage for the most critical numerical and editorial infrastructure modules.

**Acceptance criteria**
- The global threshold is increased above 50%.
- Critical modules have explicit coverage expectations.
- CI fails when those thresholds regress.

**Expectations**  
Directly improves TDD and long-term maintainability.
