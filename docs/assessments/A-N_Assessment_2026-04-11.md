# A-N Codebase Assessment - 2026-04-11

**Repository**: `AffineDrift-textbook-review`  
**Date**: 2026-04-11  
**Reviewer**: Automated comprehensive review and issue generation task  
**Mode**: Local filesystem assessment. GitHub sync/publication was attempted separately and blocked by local credential/safe-directory issues.

## Executive Summary

Overall grade: **B-**

This assessment reviewed first-party source, tests, configuration, CI metadata, and documentation visible under `C:\Users\diete\Repositories\AffineDrift-textbook-review`. Generated/cache/vendor/build directories were excluded unless they were already part of first-party source layout. Findings below are evidence-backed from local files; where process evidence such as TDD practice cannot be proven from files, the assessment says so explicitly.

## Coverage Notes

Reviewed file counts:

- First-party code files: 592
- First-party code LOC: 147659
- Test/spec files: 162
- Documentation files: 690
- Config/dependency files: 6
- CI workflow files: 53

Skipped/inaccessible paths:

- .NET enumeration used IgnoreInaccessible=true; excluded cache/build/vendor/generated directories were intentionally omitted.

## Language / LOC Inventory

| Extension | LOC |
|---|---:|
| `.qmd` | 83896 |
| `.py` | 47307 |
| `.js` | 10108 |
| `.m` | 1928 |
| `.jsx` | 1665 |
| `.ipynb` | 1600 |
| `.rs` | 1155 |

## A-N Grades

| Category | Grade |
|---|---|
| A_Code_Structure | C |
| B_Documentation | B |
| C_Test_Coverage_TDD | B |
| D_Error_Handling_DbC | B- |
| E_Performance | C |
| F_Security | B- |
| G_Dependencies | B |
| H_CI_CD | B |
| I_Code_Style | B- |
| J_API_Design_LoD | C |
| K_Data_Handling | B- |
| L_Logging | B- |
| M_Configuration | B |
| N_Scalability_Maintainability | C |

## Evidence and Findings

### TDD and Testability

Discoverable tests: 162. File evidence can show whether tests exist and whether CI appears wired, but it cannot confirm that implementation was written test-first. TDD maturity is therefore graded from test presence, proximity to source, and CI evidence rather than assumed workflow.

### DRY and Module Structure

Large modules are used as a proxy for duplicated responsibilities and weak module boundaries. Confirmed oversized modules:

- `articles\The_Geometry_of_Motion\quarto\volume2_content.qmd` - 3806 LOC
- `articles\Tangent Hyperplane Articles\Tangent_Hyperplanes_Unified_Thesis.qmd` - 3105 LOC
- `articles\affine-nature-golf-swing.qmd` - 2746 LOC
- `articles\Tangent Hyperplane Articles\Advanced\Hybrid_Tangent_Spaces.qmd` - 2223 LOC
- `articles\The_Geometry_of_Motion\quarto\ch08_applications.qmd` - 1853 LOC
- `articles\Tangent Hyperplane Articles\Advanced\Contraction_Tangent_Unification.qmd` - 1808 LOC
- `script.js` - 1753 LOC
- `docs\content\Wrist as Universal Joint\Universal_Joint_Model_Enhanced.py` - 1710 LOC
- `articles\Tangent Hyperplane Articles\Advanced\Residual-Aware_Control.qmd` - 1664 LOC
- `articles\superposition.qmd` - 1582 LOC
- `articles\The_Geometry_of_Motion\quarto\ch03_superposition.qmd` - 1577 LOC
- `articles\Tangent Hyperplane Articles\Advanced\Contraction_Tangent_CRITIC.qmd` - 1438 LOC

### Design by Contract and Error Handling

Contract/error-handling signal files sampled: contract-like checks in 221 files; explicit error-handling signals in 178 files. This confirms some boundary validation when counts are nonzero, but it does not prove complete DbC coverage across all public APIs.

### Law of Demeter, API Design, and SRP

Law of Demeter cannot be fully proven from metrics alone. This pass uses oversized functions/modules and API-boundary contract signals as evidence of where object navigation and responsibility boundaries need manual review.

Confirmed oversized Python functions:

- `docs\content\Wrist as Universal Joint\Universal_Joint_Model_Enhanced.py` `initUI` - 485 lines
- `docs\content\Wrist as Universal Joint\Universal_Joint_Model_Enhanced.py` `update_diagram` - 334 lines
- `articles\motion-control\compile_book.py` `extract_chapter_content` - 184 lines
- `articles\motion-control\compile_book.py` `compile_pdf` - 141 lines
- `src\tools\wrist_universal_joint\qt_ui_sections.py` `_build_plot_controls_group` - 118 lines
- `src\tools\wrist_universal_joint\qt_ui_sections.py` `_build_parameter_group` - 99 lines
- `docs\content\Wrist as Universal Joint\Universal_Joint_Model_Enhanced.py` `_plot_transmission_sweep` - 89 lines
- `docs\content\Wrist as Universal Joint\Universal_Joint_Model_Enhanced.py` `generate_sample_torque` - 88 lines
- `scripts\check_textbook_claims.py` `_merge_base` - 81 lines
- `scripts\analyze_completist_data.py` `_compile_report_body` - 80 lines
- `scripts\validate_accessibility.py` `check_alt_text_in_qmd` - 79 lines
- `scripts\generate_assessment_summary.py` `_build_markdown_summary` - 77 lines

### Function Size, Single Responsibility, Script/Module Size

Functions above 40 LOC and modules above 300 LOC are treated as maintainability risks unless they are generated code or have documented justification. Generated/cache/build directories were excluded from this check.

### Security, Dependencies, Configuration, CI/CD

- Dependency/config manifests found: 6
- CI workflow files found: 53
- .env committed: False
- Logging/observability signal files sampled: 137
- TODO/FIXME/HACK signal files sampled: 37

## Prioritized Remediation Recommendations

### Split oversized functions by responsibility

- Severity: medium
- Problem statement: One or more Python functions exceed 40 LOC.
- Evidence: current assessment metrics for `AffineDrift-textbook-review`; see large function/module tables and CI/test inventory above.
- Impact: Large functions weaken SRP, reviewability, and targeted TDD.
- Proposed fix: Extract pure helpers and add tests around extracted behavior.
- Acceptance criteria: No priority function remains above 40 LOC without documented justification.
- Expectations: preserve TDD, DRY, Design by Contract, Law of Demeter, small functions, SRP, and bounded module size.

### Decompose monolithic modules and scripts

- Severity: medium
- Problem statement: One or more modules exceed 300 LOC.
- Evidence: current assessment metrics for `AffineDrift-textbook-review`; see large function/module tables and CI/test inventory above.
- Impact: Long modules concentrate unrelated responsibilities and increase maintenance risk.
- Proposed fix: Move orchestration, I/O, and domain logic into focused modules.
- Acceptance criteria: Top oversized modules have clear boundaries and regression tests.
- Expectations: preserve TDD, DRY, Design by Contract, Law of Demeter, small functions, SRP, and bounded module size.


## GitHub Issue Creation Status

GitHub issue creation was **blocked** in this environment: `gh auth status` cannot read `C:\Users\diete\AppData\Roaming\GitHub CLI\config.yml` due access denial, and `git fetch` over HTTPS fails with `SEC_E_NO_CREDENTIALS`. The issue candidates above are ready to file once credentials are available.
