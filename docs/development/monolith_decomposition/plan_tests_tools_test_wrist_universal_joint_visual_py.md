# Decomposition Plan: tests\tools\test_wrist_universal_joint_visual.py

## Metrics
- **Current LOC**: 681 lines
- **Target**: < 300 lines per file, functions < 40 lines

## Strategy
1. Identify logical sections (parsing, business logic, output)
2. Extract each section into focused module
3. Replace inline logic with function calls
4. Write unit tests for each extracted module
5. Delete original once all callers updated

## Proposed Structure
```
tests\tools\test_wrist_universal_joint_visual/
  __init__.py  - re-exports public API
  parser.py    - input parsing / validation
  core.py      - core business logic
  output.py    - formatting / output
  cli.py       - CLI entry point (if applicable)
```

## Status
- [ ] Section identification complete
- [ ] Modules created
- [ ] Tests written
- [ ] Original file decomposed
