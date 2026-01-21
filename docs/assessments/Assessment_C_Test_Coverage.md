# Assessment: Test Coverage

## Grade: 3/10

## Analysis
Test coverage is the weakest point. While `pytest` runs and passes 26 tests, they cover specific utilities (`latex_to_qmd`, `wrist_simulator`). Core website logic in `script.js` is untested. Coverage is estimated at ~6%.

### Strengths
- `pytest` infrastructure is set up.
- Critical complex logic (Wrist Simulator) has tests.

### Weaknesses
- No JavaScript unit tests.
- Low overall coverage (~6%).
- `script.js` (core interactivity) is completely untested.

## Recommendations
1. Implement a JavaScript testing framework (Vitest or Jest).
2. Add unit tests for `build-html.py`.
3. Target 50% coverage for core tools.
