# A-N Codebase Assessment — 2026-04-10

**Date**: 2026-04-10  
**Scope**: First-party website, research, tooling, tests, CI, and supporting scripts under `src/`, `scripts/`, `tests/`, `js/`, `content/`, and `.github/workflows/`. Caches and generated artifacts were excluded.  
**Reviewer**: Automated scheduled comprehensive review

## 1. Executive Summary

**Overall Grade: B**

AffineDrift-editorial is well-instrumented and unusually deliberate about contracts, test automation, and content-quality gates. The main confirmed weaknesses are a non-functional mock DDP implementation, one extremely large wrist-model module, a modest 50% coverage gate for a codebase with critical scientific claims, and some remaining print-based/logging hygiene issues.

## 2. Fresh Metrics

| Metric | Value |
|---|---:|
| First-party Python files | 128 |
| First-party Python LOC | 19,427 |
| Test files | 133 |
| Test LOC | 16,245 |
| JavaScript files | 42 |
| JavaScript LOC | 7,128 |
| GitHub workflow files | 52 |
| `print(` call sites | 26 |
| Contract/helper hits | 952 |
| Oversized files (>500 LOC) | 4 sampled |

### Largest confirmed files

- `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` — 1,512 LOC
- `scripts/mypy_autofix_agent.py` — 624 LOC
- `scripts/assess_repo.py` — 553 LOC
- `js/rotation-converter.js` — 511 LOC

### Largest confirmed functions

- `Universal_Joint_Model_Enhanced.py::initUI` — 484 LOC
- `Universal_Joint_Model_Enhanced.py::update_diagram` — 333 LOC
- `articles/motion-control/compile_book.py::create_complete_book` — 187 LOC
- `articles/motion-control/compile_book.py::create_summary` — 113 LOC

## 3. Grades A–N

| Category | Grade | Evidence |
|---|---|---|
| A. Code Structure | B | Clear domain layout across `src/`, `scripts/`, content, and tests, but the wrist-model module is too large. |
| B. Documentation | A- | `README.md`, `CONTENT_ARCHITECTURE.md`, `CONTRIBUTING.md`, and rich in-repo docs are strong. |
| C. Test Coverage | B | Test volume is strong, but CI’s coverage gate remains only 50% in `pyproject.toml`. |
| D. Error Handling | B+ | Contract-heavy validation and explicit checks are common across core modules. |
| E. Performance | B- | Scientific code uses structured helpers, but giant UI/plot routines will be harder to optimize. |
| F. Security | B- | No obvious secret exposure; however current CI standard does not show a Python dependency audit step. |
| G. Dependencies | B | Dependency boundaries are actively checked in CI and package setup is disciplined. |
| H. CI/CD | A- | 52 workflows and budget checks create strong guardrails, though complexity is high. |
| I. Code Style | B | Ruff/Black/mypy are enforced, but 26 `print(` sites and long files remain. |
| J. API Design | B | Contracts and reusable helpers are good, though some tooling modules remain script-heavy. |
| K. Data Handling | B+ | Strong use of validators and explicit contracts for numerical work. |
| L. Logging | C+ | Logging exists, but 26 `print(` occurrences are still present in first-party Python. |
| M. Configuration | B+ | `pyproject.toml`, Quarto config, and workflow policy are coherent and explicit. |
| N. Scalability | B- | Good automation coverage for a research site, but large single-file tools will constrain future growth. |

## 4. TDD / DRY / DbC / LoD / SRP Evaluation

### TDD
- Positive evidence: 133 test files for 128 first-party Python files is unusually strong.
- Confirmed gap: the repo still enforces only `fail_under = 50` in `pyproject.toml`, which is too low for critical scientific and editorial logic.
- Conclusion: TDD discipline is present, but the minimum quality bar in CI understates the repo’s ambitions.

### DRY
- Positive evidence: reusable contracts and boundary-check scripts are widespread.
- Confirmed risk: the wrist model’s very large UI/diagram functions centralize a lot of behavior that should be decomposed into shared helpers.

### Design by Contract
- Strongest aspect of the repo.
- `src/core/contracts/validators.py` provides reusable `require`-backed finite/shape/range checks, and contract-helper hits are high.

### Law of Demeter
- No major cross-object chain abuse was confirmed in sampled core modules.
- Residual risk is mainly inside giant UI update routines where too much state is touched in one place.

### Function Size / Single Responsibility / Script Size
- `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` is the clearest confirmed hotspot.
- `initUI` at 484 LOC and `update_diagram` at 333 LOC clearly violate SRP and small-function expectations.

## 5. Key Risks

1. `src/affine_control/ddp.py` is explicitly documented as a non-functional mock, which undermines trust in optimization-related tests.
2. The wrist-model Python module is too large and too stateful to change safely.
3. A 50% coverage floor is too permissive for scientific/editorial code with strong contract discipline.
4. Security scanning appears incomplete in the current CI standard.

## 6. Prioritized Remediation Recommendations

1. Replace or quarantine the mock DDP implementation so optimization paths cannot be mistaken for production-capable logic.
2. Decompose `Universal_Joint_Model_Enhanced.py` into view, plotting, and domain helpers with direct tests.
3. Raise the Python coverage floor above 50% for critical modules.
4. Add explicit Python dependency audit and, if desired, bandit-style security scanning to the standard CI path.
5. Replace remaining `print(` calls with structured logging where output is operational rather than instructional.

## 7. Coverage Notes

Reviewed explicitly:
- `README.md`
- `pyproject.toml`
- `.github/workflows/ci-standard.yml`
- `src/core/contracts/validators.py`
- `src/affine_control/ddp.py`
- `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py`
- `scripts/`
- `tests/`
- `js/`

Not fully assessed:
- Full content correctness of all `.qmd`/book chapters
- Binary and media assets
- Generated caches and build outputs

Assumptions avoided:
- No claim that Quarto, JS, or E2E suites pass today.
- No claim that the mock DDP code is acceptable just because it is documented as a mock.
