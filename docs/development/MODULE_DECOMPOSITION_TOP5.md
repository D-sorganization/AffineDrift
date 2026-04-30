# Module Decomposition Backlog (Top 5)

## Goal
Reduce blast radius by decomposing the largest mixed-responsibility modules first.

## Selection Criteria
- High line count
- High churn/risk surface
- Critical-path relevance

## Priority Queue
1. `content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py`
2. `scripts/mypy_autofix_agent.py`
3. `src/tools/wrist_universal_joint/visualization.py`
4. `src/tools/matlab_utilities/scripts/matlab_quality_check.py`
5. `scripts/assess_repo.py`

## Decomposition Pattern
For each target module:
1. Add characterization tests for current behavior.
2. Split into:
   - pure domain logic
   - orchestration/service layer
   - I/O or CLI boundary layer
3. Introduce stable module interfaces.
4. Keep each new module under configured size budgets where practical.

## Exit Criteria
- No behavior regressions.
- Test coverage retained or improved for extracted logic.
- Reduced per-file size and lower change blast radius.
