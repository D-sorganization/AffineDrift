# A-N Assessment - AffineDrift - 2026-04-17

Run time: 2026-04-17T08:01:19.6221680Z UTC
Sync status: blocked
Sync notes: stash failed: Saved working directory and index state On codex/an-assessment-2026-04-14: automation-sync-2026-04-17
warning: could not open directory '.pytest-tmp/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-build-tracker-1s9yp_td/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-ephem-wheel-cache-u9f2sc10/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-install-h4zf7946/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-target-4iq0mphj/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-unpack-dx9541mg/': Permission denied
warning: could not open directory '.pytest-tmp/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-build-tracker-1s9yp_td/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-ephem-wheel-cache-u9f2sc10/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-install-h4zf7946/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-target-4iq0mphj/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-unpack-dx9541mg/': Permission denied
warning: could not open directory '.pytest-tmp/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-build-tracker-1s9yp_td/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-ephem-wheel-cache-u9f2sc10/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-install-h4zf7946/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-target-4iq0mphj/': Permission denied
warning: could not open directory '.tmp_validation_tmp/pip-unpack-dx9541mg/': Permission denied
warning: failed to remove .pytest-tmp/: Directory not empty
warning: failed to remove .tmp_validation_tmp/pip-build-tracker-1s9yp_td: Directory not empty
warning: failed to remove .tmp_validation_tmp/pip-ephem-wheel-cache-u9f2sc10: Directory not empty
warning: failed to remove .tmp_validation_tmp/pip-install-h4zf7946: Directory not empty
warning: failed to remove .tmp_validation_tmp/pip-target-4iq0mphj: Directory not empty
warning: failed to remove .tmp_validation_tmp/pip-unpack-dx9541mg: Directory not empty

Overall grade: C (76/100)

## Coverage Notes
- Reviewed tracked first-party files from git ls-files, excluding cache, build, vendor, virtualenv, temp, and generated output directories.
- Reviewed 1578 tracked files, including 453 code files, 187 test files, 56 CI files, 6 config/build files, and 522 docs/onboarding files.
- This is a read-only static assessment of committed files. TDD history and confirmed Law of Demeter semantics require commit-history review and deeper call-graph analysis; this report distinguishes those limits from confirmed file evidence.

## Category Grades
### A. Architecture and Boundaries: B (82/100)
Assesses source organization and boundary clarity from tracked first-party layout.
- Evidence: `1578 tracked first-party files`
- Evidence: `249 files under source-like directories`

### B. Build and Dependency Management: B (84/100)
Assesses committed build, dependency, and tool configuration.
- Evidence: `Makefile`
- Evidence: `package-lock.json`
- Evidence: `package.json`
- Evidence: `pyproject.toml`
- Evidence: `requirements.txt`
- Evidence: `src/tools/wrist_universal_joint/requirements.txt`

### C. Configuration and Environment Hygiene: C (78/100)
Checks whether runtime and developer configuration is explicit.
- Evidence: `Makefile`
- Evidence: `package-lock.json`
- Evidence: `package.json`
- Evidence: `pyproject.toml`
- Evidence: `requirements.txt`
- Evidence: `src/tools/wrist_universal_joint/requirements.txt`

### D. Contracts, Types, and Domain Modeling: B (82/100)
Design by Contract evidence includes validation, assertions, typed models, explicit raised errors, and invariants.
- Evidence: `.gaai/core/scripts/backlog-scheduler.sh`
- Evidence: `articles/motion-control/compile_book.py`
- Evidence: `fix_html.py`
- Evidence: `js/rotation-converter.js`
- Evidence: `scripts/analyze_completist_data.py`
- Evidence: `scripts/assess_repo.py`
- Evidence: `scripts/check_bibliography_quality.py`
- Evidence: `scripts/check_citation_resolution.py`
- Evidence: `scripts/check_coverage_gates.py`
- Evidence: `scripts/check_js_dependency_boundaries.py`

### E. Reliability and Error Handling: C (76/100)
Reliability is graded from test presence plus explicit validation/error-handling signals.
- Evidence: `.agent/skills/tests/SKILL.md`
- Evidence: `.claude/skills/tests/SKILL.md`
- Evidence: `docs/assessments/Assessment_C_Test_Coverage.md`
- Evidence: `test_notes.html`
- Evidence: `tests/README.md`
- Evidence: `.gaai/core/scripts/backlog-scheduler.sh`
- Evidence: `articles/motion-control/compile_book.py`
- Evidence: `fix_html.py`
- Evidence: `js/rotation-converter.js`
- Evidence: `scripts/analyze_completist_data.py`

### F. Function, Module Size, and SRP: F (55/100)
Evaluates function size, script/module size, and single responsibility using static size signals.
- Evidence: `.gaai/core/scripts/backlog-scheduler.sh (509 lines)`
- Evidence: `.gaai/core/scripts/delivery-daemon.sh (1190 lines)`
- Evidence: `articles/motion-control/chapter2_artifact.jsx (504 lines)`
- Evidence: `articles/motion-control/chapter3_artifact.jsx (539 lines)`
- Evidence: `articles/motion-control/chapter4_artifact.jsx (625 lines)`
- Evidence: `js/rotation-converter.js (579 lines)`
- Evidence: `js/ui-components.js (546 lines)`
- Evidence: `.gaai/core/scripts/backlog-scheduler.sh (coarse avg 170 lines/definition)`
- Evidence: `.gaai/core/scripts/delivery-metrics.sh (coarse avg 215 lines/definition)`
- Evidence: `articles/motion-control/compile_book.py (coarse avg 100 lines/definition)`

### G. Testing and TDD Posture: B (82/100)
TDD history cannot be confirmed statically; grade reflects committed automated test posture.
- Evidence: `.agent/skills/tests/SKILL.md`
- Evidence: `.claude/skills/tests/SKILL.md`
- Evidence: `docs/assessments/Assessment_C_Test_Coverage.md`
- Evidence: `test_notes.html`
- Evidence: `tests/README.md`
- Evidence: `tests/__init__.py`
- Evidence: `tests/bibliography.test.js`
- Evidence: `tests/conftest.py`
- Evidence: `tests/e2e/README.md`
- Evidence: `tests/e2e/accessibility.spec.js`
- Evidence: `tests/e2e/article.spec.js`
- Evidence: `tests/e2e/bibliography.spec.js`

### H. CI/CD and Automation: C (78/100)
Checks for tracked CI/CD workflow files.
- Evidence: `.github/workflows/Bot-CI-Trigger.yml`
- Evidence: `.github/workflows/Code-Metrics.yml`
- Evidence: `.github/workflows/Comment-to-Issue-Converter.yml`
- Evidence: `.github/workflows/Jules-Archivist.yml`
- Evidence: `.github/workflows/Jules-Assessment-AutoFix.yml`
- Evidence: `.github/workflows/Jules-Assessment-Generator.yml`
- Evidence: `.github/workflows/Jules-Assessment-Remediator.yml`
- Evidence: `.github/workflows/Jules-Auto-Assign-Issues.yml`
- Evidence: `.github/workflows/Jules-Auto-Rebase.yml`
- Evidence: `.github/workflows/Jules-Auto-Refactor.yml`

### I. Security and Secret Hygiene: B (82/100)
Secret scan is regex-based; findings require manual confirmation.
- Evidence: No direct tracked-file evidence found for this category.

### J. Documentation and Onboarding: B (82/100)
Checks docs, README, onboarding, and release documents.
- Evidence: `.Jules/palette.md`
- Evidence: `.agent/skills/issues-10-sequential/SKILL.md`
- Evidence: `.agent/skills/issues-5-combined/SKILL.md`
- Evidence: `.agent/skills/lint/SKILL.md`
- Evidence: `.agent/skills/tests/SKILL.md`
- Evidence: `.agent/skills/update-issues/SKILL.md`
- Evidence: `.agent/workflows/issues-10-sequential.md`
- Evidence: `.agent/workflows/issues-5-combined.md`
- Evidence: `.agent/workflows/lint.md`
- Evidence: `.agent/workflows/tests.md`
- Evidence: `.agent/workflows/update-issues.md`
- Evidence: `.claude/commands/gaai-bootstrap.md`

### K. Maintainability, DRY, and Duplication: B (80/100)
DRY is assessed through duplicate filename clusters and TODO/FIXME density as static heuristics.
- Evidence: `scripts/analyze_completist_data.py`
- Evidence: `scripts/check_tech_debt_budget.py`
- Evidence: `scripts/generate_completist_data.py`
- Evidence: `scripts/pragmatic_programmer_review.py`
- Evidence: `scripts/setup_hooks.py`
- Evidence: `service-worker.js`
- Evidence: `src/tools/matlab_utilities/scripts/line_checks.py`
- Evidence: `tests/test_cli_boundary_validation.py`

### L. API Surface and Law of Demeter: F (58/100)
Law of Demeter is approximated with deep member-chain hints; confirmed violations require semantic review.
- Evidence: `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py`
- Evidence: `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py`
- Evidence: `docs/js/bibliography.js`
- Evidence: `docs/js/notes-workspace.js`
- Evidence: `docs/js/startup-launcher.js`
- Evidence: `fix_html.py`
- Evidence: `js/accessibility.js`
- Evidence: `js/bibliography.js`
- Evidence: `js/forms.js`
- Evidence: `js/home.js`

### M. Observability and Operability: C (74/100)
Checks for logging, metrics, monitoring, and operational artifacts.
- Evidence: `.gaai/core/scripts/delivery-metrics.sh`
- Evidence: `.gaai/core/skills/cross/success-metrics-evaluation/SKILL.md`
- Evidence: `.github/workflows/Code-Metrics.yml`
- Evidence: `css/search-metrics.css`
- Evidence: `docs/assessments/Assessment_L_Logging.md`
- Evidence: `docs/assessments/issues/Issue_2042_Incomplete_Placeholder_in_search_metrics_css_432.md`
- Evidence: `docs/css/search-metrics.css`
- Evidence: `docs/js/metrics.js`
- Evidence: `js/metrics.js`
- Evidence: `src/tools/utils/logging_utils.py`

### N. Governance, Licensing, and Release Hygiene: C (74/100)
Checks ownership, release, contribution, security, and license metadata.
- Evidence: `.gaai/core/skills/cross/security-audit/SKILL.md`
- Evidence: `.github/CODEOWNERS`
- Evidence: `CHANGELOG.md`
- Evidence: `CONTRIBUTING.md`
- Evidence: `LICENSE`
- Evidence: `SECURITY.md`
- Evidence: `docs/assessments/Assessment_F_Security.md`
- Evidence: `security_issues/ISSUE-001.md`

## Explicit Engineering Practice Review
- TDD: Automated tests are present, but red-green-refactor history is not confirmable from static files.
- DRY: No repeated filename clusters met the static threshold.
- Design by Contract: Validation/contract signals were found in tracked code.
- Law of Demeter: Deep member-chain hints were found and should be semantically reviewed.
- Function size and SRP: Large modules or coarse long-definition signals were found.

## Key Risks
- Large modules/scripts reduce maintainability and SRP clarity.
- Deep member-chain usage may indicate Law of Demeter pressure points.

## Prioritized Remediation Recommendations
1. Split the largest modules by responsibility and add characterization tests before refactoring.
2. Review deep member chains and introduce boundary methods where object graph traversal leaks across modules.

## Actionable Issue Candidates
### Split oversized modules by responsibility
- Severity: medium
- Problem: Oversized files found: .gaai/core/scripts/backlog-scheduler.sh (509 lines); .gaai/core/scripts/delivery-daemon.sh (1190 lines); articles/motion-control/chapter2_artifact.jsx (504 lines); articles/motion-control/chapter3_artifact.jsx (539 lines); articles/motion-control/chapter4_artifact.jsx (625 lines); js/rotation-converter.js (579 lines); js/ui-components.js (546 lines); script.js (1758 lines); scripts/analyze_completist_data.py (545 lines); scripts/assess_repo.py (688 lines); src/affine_control/swing_optimizer.py (509 lines); tests/test_affine_control/test_swing_optimizer.py (570 lines); tests/tools/test_rl_funnel_benchmark.py (535 lines); tests/tools/test_wrist_universal_joint_visual.py (682 lines)
- Evidence: Category F lists files over 500 lines or coarse long-definition signals.
- Impact: Large modules obscure ownership, complicate review, and weaken SRP.
- Proposed fix: Add characterization tests, then split cohesive responsibilities into smaller modules.
- Acceptance criteria: Largest files are reduced or justified; extracted modules have focused tests.
- Expectations: SRP, function size, module size, maintainability

### Review deep object traversal hotspots
- Severity: medium
- Problem: Deep member-chain hints found in: content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py; docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py; docs/js/bibliography.js; docs/js/notes-workspace.js; docs/js/startup-launcher.js; fix_html.py; js/accessibility.js; js/bibliography.js
- Evidence: Category L found repeated chains with three or more member hops.
- Impact: Law of Demeter pressure can make APIs brittle and increase coupling.
- Proposed fix: Review hotspots and introduce boundary methods or DTOs where callers traverse object graphs.
- Acceptance criteria: Hotspots are documented, simplified, or justified; tests cover any API boundary changes.
- Expectations: Law of Demeter, SRP, maintainability

