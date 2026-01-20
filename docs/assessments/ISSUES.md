# Issues Requiring Attention

The following areas have scored below 5/10 and require immediate remediation:

## [Assessment C: Test Coverage](docs/assessments/Assessment_C_Test_Coverage.md) (Grade: 4/10)

**Problem:** Test coverage is critically low (~18%). Most utility scripts in `tools/` have 0% coverage.

**Action Plan:**
1.  **Mandate Tests:** Update `CONTRIBUTING.md` to require tests for all new PRs.
2.  **Backfill:** create a "Test Sprint" to write basic unit tests for the top 5 most used scripts:
    - `tools/check_site_health.py`
    - `tools/code_quality_check.py`
    - `tools/convert_all_to_quarto.py`
    - `tools/update_navigation.py`
    - `tools/verify_images.py`
3.  **Integration Tests:** Add a simple "smoke test" that builds the site and checks for critical files in `docs/`.
