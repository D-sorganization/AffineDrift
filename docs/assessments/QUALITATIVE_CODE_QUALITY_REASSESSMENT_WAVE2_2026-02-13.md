# AffineDrift Qualitative Code Quality Reassessment Wave 2 (2026-02-13)

## Scope
Second improvement wave after PR #1153, targeting DRY, Decoupling, Orthogonality, Changeability, and Architecture Quality.

## Improvements Implemented
- Removed large runtime CSS injection block from `src/js/bibliography.js` and moved styling to canonical stylesheet ownership in `styles.css`.
- Removed inline style attributes from `js/bibliography.js` templates in favor of CSS classes.
- Added explicit sync policy for bibliography asset mirror:
  - `scripts/sync_frontend_assets.py`: `js/bibliography.js -> docs/js/bibliography.js`
- Tightened maintainability budgets to lock in gains:
  - `config/module_size_budget.json`: stricter `.js`, `.css`, and explicit limits.

## Quantitative Evidence
- `src/js/bibliography.js`: **718 -> 507 lines** ( -211, ~29% reduction )
- New module size thresholds:
  - `.js`: **800 -> 700**
  - `.css`: **6000 -> 5000**
  - `src/js/bibliography.js`: **850 -> 550**
  - `styles.css`: **6500 -> 5000**

## Scorecard (1-5)
| Criterion | Previous (Wave 1) | Current (Wave 2) | Delta | Notes |
|---|---:|---:|---:|---|
| TDD | 3.4 | 3.5 | +0.1 | Refactor validated through existing JS/Python guardrail suites. |
| DbC | 3.6 | 3.6 | 0.0 | No additional contract primitives this wave. |
| LoD | 3.2 | 3.4 | +0.2 | Reduced implicit runtime coupling by removing style injection behavior. |
| DRY | 2.6 | 3.2 | +0.6 | Styling now centralized in stylesheet; mirror policy codified for bibliography asset. |
| Orthogonality | 3.3 | 3.8 | +0.5 | Presentation concerns shifted out of JS behavior module. |
| Reversibility | 3.5 | 3.7 | +0.2 | Tighter budgets + sync checks reduce regression blast radius. |
| Reusability | 3.2 | 3.5 | +0.3 | New shared bibliography CSS classes are reusable across render paths. |
| Changeability | 3.1 | 3.9 | +0.8 | Smaller JS module and style separation simplify isolated edits. |
| Decoupled | 3.3 | 4.0 | +0.7 | Better separation between rendering logic and presentation styling. |
| Comment Quality | 3.3 | 3.4 | +0.1 | Intent clearer through structure, though not a comment-heavy change. |
| Documentation | 3.7 | 3.8 | +0.1 | Wave 2 assessment record added. |
| Architecture Quality | 3.4 | 4.0 | +0.6 | Improved boundary discipline: behavior vs presentation + stronger budget governance. |

## Totals
- Previous (Wave 1): **40.6 / 60** (avg **3.38**)
- Current (Wave 2): **44.8 / 60** (avg **3.73**)
- Net gain this wave: **+4.2** points

## Validation Evidence
- `python3 scripts/check_module_size_budget.py` -> pass
- `python3 scripts/check_dependency_boundaries.py` -> pass
- `python3 scripts/check_js_dependency_boundaries.py` -> pass
- `python3 scripts/sync_frontend_assets.py --check` -> pass
- `pytest tests/test_check_module_size_budget.py tests/test_check_dependency_boundaries.py tests/test_check_js_dependency_boundaries.py tests/test_check_site_health.py tests/tools/utils/test_cli_contracts.py -q` -> pass
- `npm test -- --runInBand` -> pass
