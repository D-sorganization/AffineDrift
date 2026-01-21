# Assessment: Logging

## Grade: 7/10

## Analysis
Logging practices are mixed.
- **Good Examples**: `tools/update_navigation.py` uses the standard `logging` library with configurable levels.
- **Bad Examples**: `tools/latex_to_qmd.py` has no logging, silently exiting on error.
- **Frontend**: `AGENTS.md` restricts `console.log` in production JS, which is good.

## Strengths
- `AGENTS.md` explicitly sets a standard ("USE the logging module").
- Some tools follow this standard well.

## Weaknesses
- Inconsistency: Several tools rely on silent failures or simple `sys.exit()` without user feedback.
- Lack of centralized logging configuration (e.g., a shared `logging.conf` or setup module).

## Recommendations
1. Refactor `tools/latex_to_qmd.py` and other scripts to use `logging`.
2. Create a shared `tools/utils/logger.py` to standardize logging formats (timestamps, colors) across all CLI tools.
