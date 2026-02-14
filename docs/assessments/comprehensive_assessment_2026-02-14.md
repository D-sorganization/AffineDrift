# AffineDrift — Comprehensive Quality Assessment (2026-02-14)

## Executive Summary

AffineDrift is the organization's documentation and research publication site built with Quarto. It also contains Python tooling for site health, LaTeX conversion, assessment utilities, and an affine-control math library. The codebase is **relatively small** (~8,200 lines of Python in `src/`) but has significant quality gaps in DRY compliance, type safety, and test coverage.

**Overall Score: 6.8/10**

---

## A-O Framework Assessment

| ID | Category | Score | Key Findings |
|----|----------|-------|-------------|
| **A** | Architecture & Implementation | 7.0 | Clean separation: `src/core/`, `src/tools/`, `src/tangent_models/`. Good use of contracts module. `wrist_universal_joint/` is a well-structured sub-application. |
| **B** | Code Quality & Hygiene | 6.5 | 4 `print()` calls in `budget_check_utils.py` (has noqa). Missing return type hints in several utility functions. Ruff/Black configs are solid. |
| **C** | Documentation & Comments | 7.5 | Strong README, CONTRIBUTING.md, and Quarto documentation. Docstrings are present but uneven in `src/tools/utils/`. |
| **D** | User Experience | 7.0 | Quarto site is well-designed. CLI tools have basic argument parsing but lack `--help` consistency. |
| **E** | Performance & Scalability | 7.0 | LaTeX conversion tools could be optimized for batch processing. Current scripts process files sequentially. |
| **F** | Installation & Deployment | 7.5 | Clean `pyproject.toml`. Pre-commit hooks configured. Node dependencies managed via `package.json`. |
| **G** | Testing & Validation | 5.5 | Tests exist for utilities but coverage is estimated at ~45%. No integration tests for the Quarto build pipeline. No property-based tests. |
| **H** | Error Handling & Debugging | 6.0 | `budget_check_utils.py` uses print for output instead of logging. 1 bare `except:` in test code. Error flows in conversion tools are basic. |
| **I** | Security & Input Validation | 7.0 | Path validation in `file_utils.py`. No hardcoded secrets detected. `.env.example` provided. |
| **J** | Extensibility | 6.5 | Tool scripts are standalone — adding new tools requires boilerplate. No plugin/registry pattern for tool discovery. |
| **K** | Reproducibility | 7.0 | `requirements.txt` and `pyproject.toml` lock dependencies. Pre-commit ensures formatting consistency. |
| **L** | Maintainability | 6.0 | `latex_to_html.py` (450 lines) is a candidate for decomposition. Several utils share parsing logic that could be consolidated. |
| **M** | Education | 8.0 | Excellent research articles, book reviews, and educational content. This is the primary purpose of the repo. |
| **N** | Visualization | 7.0 | Quarto handles most visualization. `wrist_universal_joint/plots.py` has good matplotlib integration. |
| **O** | CI/CD | 7.5 | `ci-standard.yml` enforces Ruff, Black, MyPy. Many Jules automation workflows. Deploy pipeline for website. |

**A-O Average: 6.83/10**

---

## Pragmatic Programmer Assessment

### 1. Don't Repeat Yourself (DRY) — 6.0/10

**Issues Identified:**
- **PP-DRY-001**: `latex_to_html.py` and `latex_to_qmd.py` share ~60% of their LaTeX parsing logic. Both files implement independent regex-based conversion pipelines.
- **PP-DRY-002**: `check_links.py` and `check_site_health.py` both implement HTTP request/response validation with overlapping URL parsing logic.
- **PP-DRY-003**: Assessment scripts (`assess_repo.py`, `baseline_assessments.py`) duplicate metric collection patterns that exist in `assessment_utils.py`.
- **PP-DRY-004**: Multiple `check_*` scripts (`check_css_architecture.py`, `check_dependency_boundaries.py`, `check_js_dependency_boundaries.py`) share file-walking and reporting boilerplate.

### 2. Orthogonality & Decoupling — 6.5/10

**Issues Identified:**
- **PP-ORTH-001**: `code_quality_check.py` (317 lines) mixes AST analysis, metric collection, and report generation in a single module.
- **PP-ORTH-002**: `budget_check_utils.py` handles both business logic (budget evaluation) and presentation (print statements) — violates separation of concerns.
- **PP-ORTH-003**: `contracts.py` (351 lines) contains both contract definitions AND validation logic that could be split into `contracts/definitions.py` and `contracts/validators.py`.

### 3. Reversibility & Flexibility — 7.0/10

- Output format (JSON, Markdown) is mostly hardcoded in scripts rather than configurable.
- LaTeX conversion pipeline is tightly coupled to specific output formats.

### 4. Code Quality & Craftsmanship — 7.0/10

- Naming conventions are consistent (snake_case).
- Some functions exceed 50 lines in conversion tools.
- f-string usage is modern and consistent.

### 5. Error Handling & Robustness — 6.0/10

- **PP-ERR-001**: `print()` used for CI output in `budget_check_utils.py` instead of `logging` module.
- **PP-ERR-002**: Test file `test_assess_repo.py` line 120 contains a bare `except:`.
- **PP-ERR-003**: Conversion tools lack structured error reporting (errors are printed to stdout).

### 6. Testing & Validation — 5.5/10

- **PP-TEST-001**: No property-based tests (no Hypothesis usage).
- **PP-TEST-002**: No integration tests for the Quarto rendering pipeline.
- **PP-TEST-003**: Test coverage for `src/tools/` utility modules is incomplete — `latex_to_html.py`, `publish_manual_article.py` lack test files.

### 7. Documentation & Communication — 7.5/10

- Docstrings present but inconsistent depth across modules.
- `contracts.py` has excellent documentation.

### 8. Automation & Tooling — 8.0/10

- Pre-commit hooks configured.
- CI/CD with comprehensive Jules workflows.
- Automated assessment scripts.

**Pragmatic Programmer Average: 6.69/10**

---

## Code Quality Deep-Dive (DbC, TDD, DRY, Orthogonality, Reversibility)

### Design by Contract (DbC) — 6.5/10

- `src/core/contracts.py` implements a contract system but adoption is limited to `affine_control/` and `core/`.
- **CQ-DBC-001**: Tool scripts in `src/tools/` do not use contracts for input validation.
- **CQ-DBC-002**: No precondition checks on file paths in conversion tools.
- **CQ-DBC-003**: `budget_check_utils.py` functions lack postcondition verification.

### Test-Driven Development (TDD) — 5.0/10

- **CQ-TDD-001**: 6 TODO/FIXME markers remain in source code.
- **CQ-TDD-002**: Several source files lack corresponding test files.
- **CQ-TDD-003**: No mutation testing or property-based testing infrastructure.

### DRY Compliance — 6.0/10

*(See PP-DRY-001 through PP-DRY-004 above)*

### Orthogonality — 6.5/10

*(See PP-ORTH-001 through PP-ORTH-003 above)*

### Reversibility — 7.0/10

- **CQ-REV-001**: Output format for assessment scripts is hardcoded to Markdown — should support JSON/CSV.
- **CQ-REV-002**: LaTeX conversion tools are tightly coupled to specific regex patterns — should use a configurable transformation pipeline.

---

## Issue Summary

| ID | Category | Severity | Description |
|----|----------|----------|-------------|
| PP-DRY-001 | DRY | Major | LaTeX parsing duplication between `latex_to_html.py` and `latex_to_qmd.py` |
| PP-DRY-002 | DRY | Minor | HTTP validation duplication in link/health checkers |
| PP-DRY-003 | DRY | Minor | Assessment metric collection duplication |
| PP-DRY-004 | DRY | Major | File-walking/reporting boilerplate across `check_*` scripts |
| PP-ORTH-001 | Orthogonality | Major | `code_quality_check.py` mixes concerns |
| PP-ORTH-002 | Orthogonality | Minor | `budget_check_utils.py` mixes logic/presentation |
| PP-ORTH-003 | Orthogonality | Minor | `contracts.py` too large — split into sub-modules |
| PP-ERR-001 | Error Handling | Major | Replace print() with logging in production code |
| PP-ERR-002 | Error Handling | Minor | Bare `except:` in test code |
| PP-ERR-003 | Error Handling | Minor | Unstructured error reporting in conversion tools |
| PP-TEST-001 | Testing | Major | No property-based tests |
| PP-TEST-002 | Testing | Major | No Quarto pipeline integration tests |
| PP-TEST-003 | Testing | Minor | Missing test files for several tools |
| CQ-DBC-001 | DbC | Major | Tool scripts lack contract-based validation |
| CQ-DBC-002 | DbC | Minor | No file path preconditions in conversion tools |
| CQ-DBC-003 | DbC | Minor | Missing postconditions in budget utils |
| CQ-REV-001 | Reversibility | Minor | Hardcoded output formats |
| CQ-REV-002 | Reversibility | Minor | Non-configurable LaTeX pipeline |

**Total Issues: 18 (6 Major, 12 Minor)**
