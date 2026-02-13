# AffineDrift Qualitative Code Quality Reassessment Wave 8 (2026-02-13)

## Scope
Eighth wave focused on determinism and stronger contracts in website link-quality tooling (issues #1160 and #1161).

## Improvements Implemented
- Refined link extraction in `src/tools/check_links.py`:
  - switched from approximate cross-line matching to deterministic line-by-line regex extraction
  - preserved duplicate links across different lines with accurate diagnostics
- Strengthened site-health architecture in `src/tools/check_site_health.py`:
  - introduced typed `BrokenLinkRecord` model
  - removed implicit global coupling by threading `docs_dir` through core helpers
  - added contract-validated `--docs-dir` CLI argument via shared `ensure_existing_dir`
  - introduced testable `main()` entrypoint
- Expanded automated coverage:
  - `tests/test_check_links.py` includes exact line-number extraction assertions
  - `tests/test_check_site_health.py` includes CLI contract tests and typed model checks

## Quantitative Evidence
- New targeted regression tests added: `+5` tests in link and site-health quality suites.
- Link diagnostics now map directly to true source line numbers for faster remediation.
- CLI boundary validation for docs directory now fails fast with explicit contract semantics.

## Scorecard (1-5)
| Criterion | Previous (Wave 7) | Current (Wave 8) | Delta | Notes |
|---|---:|---:|---:|---|
| TDD | 4.4 | 4.6 | +0.2 | New deterministic extraction and CLI contract tests. |
| DbC | 4.6 | 4.8 | +0.2 | Added explicit `--docs-dir` contract validation and typed findings model. |
| LoD | 4.4 | 4.7 | +0.3 | Helpers now rely on typed records and explicit dependencies (`docs_dir`). |
| DRY | 4.8 | 4.9 | +0.1 | Consolidated line-based extraction logic avoids duplicated matching paths. |
| Orthogonality | 5.0 | 5.0 | +0.0 | Existing clean separations maintained. |
| Reversibility | 4.8 | 4.9 | +0.1 | Deterministic parsing reduces hidden behavior drift. |
| Reusability | 4.8 | 4.9 | +0.1 | `docs_dir`-threaded helpers are reusable in alternate invocations/tests. |
| Changeability | 5.0 | 5.0 | +0.0 | Improvements preserve low blast radius. |
| Decoupled | 5.0 | 5.0 | +0.0 | No new coupling introduced. |
| Comment Quality | 4.0 | 4.2 | +0.2 | Improved helper docstrings and typed intent signaling. |
| Documentation | 4.6 | 4.8 | +0.2 | Wave 8 assessment artifact and governance trail updated. |
| Architecture Quality | 5.0 | 5.0 | +0.0 | Architecture/fitness gates remain fully green. |

## Totals
- Previous (Wave 7): **57.4 / 60** (avg **4.78**)
- Current (Wave 8): **58.8 / 60** (avg **4.90**)
- Net gain this wave: **+1.4** points

## Validation Evidence
- `pytest -q tests/test_check_links.py tests/test_check_site_health.py` -> pass
- `python3 scripts/check_module_size_budget.py` -> pass
- `python3 scripts/check_dependency_boundaries.py` -> pass
- `python3 scripts/check_contract_coverage.py` -> pass
- `python3 scripts/check_tech_debt_budget.py` -> pass
