# Assessment C: Test Coverage

## Grade: C- (4/10)

## Analysis
Test coverage is the weakest area of the repository. While the structure for testing exists (`pytest`), the actual coverage is very low (~18%).

### Strengths
*   **Test Infrastructure:** `pytest` and `pytest-cov` are configured and working.
*   **Critical Paths Tested:** `tests/test_wrist_simulator.py` and `tests/test_latex_to_qmd.py` show that complex logic is being targeted.

### Weaknesses
*   **Low Overall Coverage:** 18% is significantly below industry standards (usually 80%+).
*   **Untested Tools:** Many scripts in `tools/` have 0% coverage (`verify_images.py`, `check_site_health.py`, etc.).
*   **No Integration Tests:** Tests appear to be unit-focused; end-to-end site build tests are minimal.

## Recommendations
1.  **Mandate Tests for New Code:** Enforce a rule that any new script or feature must have accompanying tests.
2.  **Backfill Tests:** Prioritize writing tests for high-impact tools like `convert_all_to_quarto.py` and `check_site_health.py`.
3.  **Mock File I/O:** Use `pytest-mock` or `tmp_path` fixture to test file manipulation scripts without risking the actual filesystem.
