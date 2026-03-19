# Project Rules — AffineDrift (GAAI Fleet)

## Safety
1. All AI work on `staging` branch. Never commit directly to `main`.
2. PRs target `staging`. No auto-merge. Human approval required.
3. No destructive git history operations.
4. No secret commits (.env, API keys, credentials).

## Quality Gates (CI)
5. `ruff check` must pass on modified Python files before PR creation.
6. `black --check` must pass (this repo uses Black, NOT ruff format). Line length: 100 characters.
7. No new `print()` calls in `src/` (use logging).
8. Minimum test coverage: 50%. Coverage must not decrease.
9. Quarto documentation builds must succeed (`quarto render` must not fail).
10. No TODO/FIXME comments unless a tracked GitHub issue exists.

## Escalation
11. If a story requires modifying CI pipelines in a breaking way — escalate.
12. If a story touches shared/core modules affecting multiple subsystems — escalate.
13. If a story affects Quarto build output or published docs — verify render before PR.

---

## Coding Principles (Mandatory — enforced in QA)

### TDD (Test-Driven Development)
- Write tests BEFORE implementation code.
- Every new public function/method must have at least one test.
- Test file must exist before or in the same commit as the implementation.
- If modifying existing code, add tests for the modified behavior first.

### DRY (Don't Repeat Yourself)
- No duplicated logic blocks >5 lines. Extract shared logic into helpers.
- Before writing new utility code, search for existing implementations.
- If you find yourself copying code, refactor into a shared function.

### DbC (Design by Contract)
- Public functions must validate preconditions (raise ValueError/TypeError on invalid input).
- Document postconditions in docstrings for non-trivial functions.
- Use assert statements for invariants in non-hot-path code.

### LOD (Law of Demeter)
- No method chains >2 levels (e.g., `a.b.c.d()` violates LOD).
- Functions should only call methods on: self, parameters, objects they create, direct attributes.
- If you need deep access, add a delegating method to the intermediate object.
