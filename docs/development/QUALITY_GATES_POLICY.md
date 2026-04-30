# Quality Gates Policy

## Purpose
This policy defines the blocking quality gates used to keep code quality from regressing in core tooling and scripts.

## Coverage Gate (Critical Modules)
- Gate script: `scripts/check_critical_module_coverage.py`
- Enforced modules:
  - `src.tools.check_site_health` (>= 85%)
  - `src.tools.check_links` (>= 85%)
  - `src.tools.update_navigation` (>= 80%)
  - `scripts.generate_sitemap` (>= 75%)
- Rule: coverage may not regress below per-module thresholds.

## Module Size and Complexity Gates
- Global budget gate: `scripts/check_module_size_budget.py`
- Changed-file gate: `scripts/check_changed_file_size_budget.py`
- Rule: no net-new changed files may exceed configured size limits.
- Configuration source: `config/module_size_budget.json`

## DRY Adoption Gate
- Gate script: `scripts/check_dry_adoption.py`
- Rule: targeted content-processing scripts must use shared helpers in
  `src/tools/utils/content_utils.py`.

## I/O Boundary Validation Standard
Use shared CLI contracts from `src/tools/utils/cli_contracts.py`:
- `ensure_existing_file(...)`
- `ensure_existing_dir(...)`
- `ensure_writable_output_file(...)`

Rules:
1. Validate input paths at CLI boundaries before processing.
2. Validate output-path parent directories before writing files.
3. Return explicit `ValueError` messages mapped to non-zero CLI exit codes.

## Regression Test Discipline
- Bug fixes must include a regression test in the same PR when technically feasible.
- If omitted, PR must include a rationale and risk statement.
- PR template enforcement lives in `.github/pull_request_template.md`.
