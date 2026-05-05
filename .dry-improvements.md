# DRY Improvements — AffineDrift Issue #1698

## Executive Summary

Addressed DRY violations in repeated code blocks across scripts and utilities:
- Created `src/tools/utils/budget_check_utils.py` to consolidate 12+ instances of common code
- Refactored `check_*_budget.py` and `check_*_boundaries.py` scripts to use shared utilities
- Established pattern for future script consolidation

## Evidence of Consolidation

### Problem Statement
Assessment #1698 identified repeated 6-line blocks appearing 12 times across:
- `scripts/check_css_architecture.py`
- `scripts/check_js_dependency_boundaries.py`
- `scripts/check_styles_budget.py`
- `scripts/check_tech_debt_budget.py`

### Solution
Created `src/tools/utils/budget_check_utils.py` with:

1. **`load_config()`** - Load JSON configs from `config/` directory
2. **`is_included()`** - Path inclusion/exclusion logic
3. **`collect_matching_files()`** - Walk and filter files by rules
4. **`read_text_safe()`** - Safe file reading with error handling
5. **`report_results()`** - Standardized exit-code reporting

### Refactored Scripts

All four scripts now use the shared utilities:

```python
# Before: ~40 lines of duplicated file walking
# After:
from src.tools.utils.budget_check_utils import load_config, report_results

files = collect_matching_files(repo_root, ...)
return report_results("Check name", len(files), details, errors)
```

## Impact

- **Eliminated ~48 lines of duplicated code**
- **Standardized error reporting across all budget checks**
- **Single source of truth for file filtering rules**
- **Easier to maintain and extend**

## Architecture Pattern

All `scripts/check_*.py` now follow this pattern:

```python
def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    config = load_config(repo_root, "config_name.json")
    # ... specific logic ...
    return report_results(check_name, files_scanned, details, errors)

if __name__ == "__main__":
    sys.exit(main())
```

## Recommendations

1. Continue extracting common patterns into `src/tools/utils/`
2. Document shared utilities in module docstrings
3. Add contract-based validation using `src.core.contracts`
4. Maintain alphabetical organization of utility modules
