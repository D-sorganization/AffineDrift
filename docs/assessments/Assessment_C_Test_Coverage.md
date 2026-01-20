# Assessment C: Test Coverage

## Grade: 2/10

## Analysis
Test coverage is critically low.

## Strengths
- `pytest` infrastructure is set up.
- `tests/` directory exists.
- Existing tests pass.

## Weaknesses
- **Coverage is only 18%.**
- Most scripts in `tools/` have 0% coverage.
- Critical build scripts like `build-html.py` are untested.

## Recommendations
1. **CRITICAL:** Add unit tests for `build-html.py` and other core tools.
2. Aim for at least 50% coverage in the next sprint.
3. Use `pytest-cov` (already installed) to monitor progress.
