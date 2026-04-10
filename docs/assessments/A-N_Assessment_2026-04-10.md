# A-N Codebase Assessment — 2026-04-10 Refresh

**Date**: 2026-04-10  
**Baseline**: `A-N_Assessment_2026-04-04.md`  
**Scope**: First-party website, textbooks, Python tooling, tests, JavaScript, CI, and supporting scripts under `src/`, `scripts/`, `tests/`, `js/`, `docs/content/`, and `.github/workflows/`. Generated artifacts and caches were excluded.  
**Reviewer**: Automated scheduled comprehensive review

## 1. Executive Summary

**Overall Grade: B-**

The repository retains strong contract usage, dense automated tests, and broad CI coverage, but several previously important weaknesses remain: the DDP optimizer is still a documented mock, the root `script.js` is now a 1,525 LOC frontend monolith, the coverage gate is still only 50%, and the wrist-model code path remains oversized. This repo is productive, but its highest-risk modules are still larger and less isolated than they should be.

## 2. Fresh Metrics (2026-04-10)

| Metric | Value |
|---|---:|
| First-party Python files | 152 |
| First-party Python LOC | 21,804 |
| Test files | 141 |
| Test LOC | 16,208 |
| JavaScript files | 43 |
| JavaScript LOC | 8,698 |
| GitHub workflow files | 53 |
| `print(` call sites | 14 |
| Contract/helper hits | 1,046 |
| Oversized files (>500 LOC) | 5 sampled |

### Largest confirmed files

- `script.js` — 1,525 LOC
- `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` — 1,505 LOC
- `scripts/mypy_autofix_agent.py` — 624 LOC
- `scripts/assess_repo.py` — 572 LOC
- `js/rotation-converter.js` — 511 LOC

### Largest confirmed functions

- `Universal_Joint_Model_Enhanced.py::initUI` — 484 LOC
- `Universal_Joint_Model_Enhanced.py::update_diagram` — 333 LOC
- `src/tools/wrist_universal_joint/qt_ui_sections.py::_build_plot_controls_group` — 116 LOC
- `src/tools/wrist_universal_joint/qt_ui_sections.py::_build_parameter_group` — 97 LOC
- `src/affine_control/residuals.py::update` — 66 LOC
- `src/golf_simulation/terrain.py::compute_bounce` — 65 LOC

## 3. Grades A–N

| Category | Grade | Evidence |
|---|---|---|
| A. Code Structure | B- | Strong layout, but key frontend and wrist-model files are still too large. |
| B. Documentation | A- | Editorial and architecture docs are extensive and well maintained. |
| C. Test Coverage | B | Test density is strong, but the enforced floor is still only 50%. |
| D. Error Handling | B+ | Contract-heavy patterns remain a standout strength. |
| E. Performance | B- | Numerical code is structured, but large UI/JS modules hinder focused optimization. |
| F. Security | B | CI includes dependency audit and broad checks; no obvious secret-handling issue was confirmed. |
| G. Dependencies | B | Tooling is broad but purposeful; boundary checks are enforced in CI. |
| H. CI/CD | A- | 53 workflows and explicit quality budgets provide substantial safety nets. |
| I. Code Style | B | Tooling is strict, but monolithic JS/Python files remain. |
| J. API Design | B | Reusable contracts and structured modules exist, though some script-heavy surfaces remain. |
| K. Data Handling | B+ | Contract checks and numerical validation are strong. |
| L. Logging | B- | Fewer `print(` calls than the editorial sibling, but there is still room to standardize. |
| M. Configuration | B+ | Config and CI remain explicit and consistent. |
| N. Scalability | B- | Good for current scope, but the frontend and wrist-model monoliths will slow future changes. |

## 4. TDD / DRY / DbC / LoD / SRP Evaluation

### TDD
- Positive evidence: 141 test files for 152 first-party Python files is strong.
- Confirmed issue: `pyproject.toml` still permits `fail_under = 50`, which is low for a repo with this much guardrail infrastructure.

### DRY
- Positive evidence: contract helpers and dedicated architecture/budget scripts are reused widely.
- Confirmed issue: the wrist-model logic exists both in a giant docs/content script and in smaller tool modules, which increases drift risk.

### Design by Contract
- Strongest aspect of the repo.
- Contract/helper hits are high and `src/core/contracts/validators.py` continues to back numerical assertions with `require`.

### Law of Demeter
- No major chain-call abuse was confirmed in sampled core Python modules.
- The real maintainability problem is not deep chaining so much as oversized UI/state management routines.

### Function Size / Single Responsibility / Script Size
- `script.js` at 1,525 LOC is the clearest current monolith.
- `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` still contains 484 LOC and 333 LOC functions.
- `src/tools/wrist_universal_joint/qt_ui_sections.py` is cleaner than the legacy script, but still contains very large builder functions.

## 5. Key Risks

1. The DDP implementation remains a documented mock in a repo that presents scientific/optimization content.
2. `script.js` is now a frontend monolith and likely the most important maintainability hotspot in the repo.
3. Coverage enforcement still undershoots the repo’s quality intent.
4. Wrist-model code remains split across giant legacy/doc paths and newer tool modules.

## 6. Prioritized Remediation Recommendations

1. Replace or isolate the mock DDP implementation from production-style narratives and usage.
2. Break `script.js` into feature modules with explicit ownership and tests.
3. Raise coverage thresholds for critical modules beyond 50%.
4. Continue migrating wrist-model behavior out of the giant legacy/doc script into smaller maintained modules.
5. Reduce the largest UI builder functions in `src/tools/wrist_universal_joint/qt_ui_sections.py`.

## 7. Coverage Notes

Reviewed explicitly:
- `README.md`
- `pyproject.toml`
- `.github/workflows/ci-standard.yml`
- `src/core/contracts/validators.py`
- `src/affine_control/ddp.py`
- `src/tools/wrist_universal_joint/qt_ui_sections.py`
- `script.js`
- `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py`
- `tests/`

Not fully assessed:
- Every Quarto/book chapter for content accuracy
- Binary PDFs and media assets
- Generated caches and temporary files

Assumptions avoided:
- No claim of current green CI state.
- No claim that legacy wrist-model code and maintained tool code are behaviorally equivalent.
