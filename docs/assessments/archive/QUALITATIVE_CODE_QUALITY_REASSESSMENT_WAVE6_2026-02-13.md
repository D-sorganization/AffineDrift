# AffineDrift Qualitative Code Quality Reassessment Wave 6 (2026-02-13)

## Scope
Sixth wave focused on elevating DbC/TDD/architecture rigor with enforceable contract coverage and broader CLI boundary validation.

## Improvements Implemented
- Expanded shared CLI contracts:
  - `src/tools/utils/cli_contracts.py` adds `ensure_existing_dir`
- Applied contract validation to additional tool boundary:
  - `src/tools/fix_html_validation.py` now validates `--docs-dir` and uses it as actual search root
- Added contract coverage fitness function:
  - `config/contract_coverage_rules.json`
  - `scripts/check_contract_coverage.py`
  - `tests/test_check_contract_coverage.py`
- Added CLI behavior tests for `fix_html_validation` contracts:
  - `tests/test_fix_html_validation_cli.py`
- Enforced contract coverage in CI and deploy workflows:
  - `.github/workflows/ci-standard.yml`
  - `.github/workflows/deploy-website.yml`

## Quantitative Evidence
- Contract coverage gate now checks core boundary scripts for required contract tokens.
- Expanded automated test coverage by +14 tests in focused contract/CLI suites (`27 -> 41` in targeted run).
- All quality gates pass with contract coverage enabled.

## Scorecard (1-5)
| Criterion | Previous (Wave 5) | Current (Wave 6) | Delta | Notes |
|---|---:|---:|---:|---|
| TDD | 3.9 | 4.2 | +0.3 | New dedicated tests for contract-coverage and CLI boundary behavior. |
| DbC | 3.8 | 4.4 | +0.6 | Contract helpers expanded + enforced across more CLI entrypoints via CI gate. |
| LoD | 3.9 | 4.0 | +0.1 | Less implicit path handling and clearer boundary lookup paths. |
| DRY | 4.6 | 4.7 | +0.1 | Contract rules centralized in config/checker vs scattered manual checks. |
| Orthogonality | 4.7 | 4.8 | +0.1 | Boundary validation responsibilities now explicit and modular. |
| Reversibility | 4.4 | 4.6 | +0.2 | Contract regressions fail fast in CI/deploy. |
| Reusability | 4.3 | 4.5 | +0.2 | Reusable directory/file contract primitives now shared across tools. |
| Changeability | 4.8 | 4.9 | +0.1 | Stronger boundary contracts reduce uncertainty when changing tool CLIs. |
| Decoupled | 4.8 | 4.9 | +0.1 | Contract enforcement decoupled from script internals via rules/checker. |
| Comment Quality | 3.7 | 3.8 | +0.1 | New checks/helpers are clearly documented and narrowly scoped. |
| Documentation | 4.2 | 4.4 | +0.2 | Wave 6 governance/assessment artifacts added. |
| Architecture Quality | 4.9 | 5.0 | +0.1 | Multi-layer fitness functions now include Python, JS, CSS, and contract coverage. |

## Totals
- Previous (Wave 5): **55.0 / 60** (avg **4.58**)
- Current (Wave 6): **56.2 / 60** (avg **4.68**)
- Net gain this wave: **+1.2** points

## Validation Evidence
- `python3 scripts/check_contract_coverage.py` -> pass
- `python3 scripts/check_css_architecture.py` -> pass
- `python3 scripts/check_module_size_budget.py` -> pass
- `python3 scripts/check_dependency_boundaries.py` -> pass
- `python3 scripts/check_js_dependency_boundaries.py` -> pass
- `python3 scripts/check_ui_ux_budget.py` -> pass
- `python3 scripts/sync_frontend_assets.py --check` -> pass
- `pytest tests/test_check_contract_coverage.py tests/test_fix_html_validation_cli.py tests/tools/utils/test_cli_contracts.py tests/test_check_css_architecture.py tests/test_check_module_size_budget.py tests/test_check_dependency_boundaries.py tests/test_check_js_dependency_boundaries.py tests/test_check_site_health.py tests/test_fix_html_validation.py -q` -> pass
- `npm test -- --runInBand` -> pass
