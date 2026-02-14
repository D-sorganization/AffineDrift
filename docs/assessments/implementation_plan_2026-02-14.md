# AffineDrift — Implementation Plan (2026-02-14)

> **Reference Assessment**: `docs/assessments/comprehensive_assessment_2026-02-14.md`
> **Principles**: TDD, DbC, DRY, Orthogonality, Reversibility, Decoupled Code

---

## Phase 1: Error Handling & Type Safety (Quick Wins)

**Target Issues**: PP-ERR-001, PP-ERR-002, PP-ERR-003

### 1.1 Replace print() with logging in production code

**Files to modify:**
- `src/tools/utils/budget_check_utils.py` — Replace all `print()` with `logging.info()` / `logging.error()`. Remove `noqa: T201` comments.

**Pattern:**
```python
import logging
logger = logging.getLogger(__name__)

# Before:
print(check_name)  # noqa: T201 — CI script output
# After:
logger.info(check_name)
```

### 1.2 Fix bare except in test code

**Files to modify:**
- `tests/test_assess_repo.py` line 120 — Replace bare `except:` with `except Exception:`.

### 1.3 Add return type hints to all public functions

**Files to scan:** All files in `src/` where `def` lines lack `->`.

**DbC Pattern to apply:**
```python
def check_budget(files: list[Path], max_lines: int) -> BudgetResult:
    """Check if files exceed line budget.
    
    Preconditions:
        - files is non-empty
        - max_lines > 0
    Postconditions:
        - result.files_scanned == len(files)
    """
    assert files, "files list must be non-empty"
    assert max_lines > 0, "max_lines must be positive"
    # ...implementation...
    assert result.files_scanned == len(files)
    return result
```

### 1.4 Resolve TODO/FIXME markers

Review and resolve the 6 TODO/FIXME markers in source code.

---

## Phase 2: DRY Consolidation

**Target Issues**: PP-DRY-001, PP-DRY-002, PP-DRY-004

### 2.1 Extract shared LaTeX parsing library

**Create:** `src/tools/utils/latex_parser.py`

Extract common LaTeX parsing logic from:
- `src/tools/latex_to_html.py`
- `src/tools/latex_to_qmd.py`

**Shared operations to extract:**
- LaTeX environment detection and parsing
- Math mode extraction (`$...$`, `$$...$$`, `\[...\]`)
- Reference/citation handling
- Figure/table environment parsing

**TDD requirement:** Write `tests/test_latex_parser.py` FIRST with tests for each extraction function, then extract.

### 2.2 Extract shared HTTP validation library

**Create:** `src/tools/utils/http_utils.py`

Extract common HTTP validation from:
- `src/tools/check_links.py`
- `src/tools/check_site_health.py`

### 2.3 Create shared check-script base

**Create:** `src/tools/utils/check_base.py`

Extract common file-walking and reporting patterns from all `check_*` scripts:
- File discovery (glob patterns)
- Progress reporting
- Result aggregation
- Exit code determination

**Pattern (DbC-compliant):**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CheckResult:
    """Result of a check operation."""
    check_name: str
    files_scanned: int
    violations: list[str]
    passed: bool

class BaseChecker(ABC):
    """Base class for all check scripts.
    
    Invariant: checkers must be idempotent and side-effect free.
    """
    
    @abstractmethod
    def check_file(self, path: Path) -> list[str]:
        """Check a single file. Returns list of violation messages."""
        ...
    
    def run(self, root: Path, glob: str = "**/*.py") -> CheckResult:
        """Run check across all matching files."""
        assert root.is_dir(), f"root must be a directory: {root}"
        files = list(root.glob(glob))
        violations = []
        for f in files:
            violations.extend(self.check_file(f))
        return CheckResult(
            check_name=self.__class__.__name__,
            files_scanned=len(files),
            violations=violations,
            passed=len(violations) == 0,
        )
```

---

## Phase 3: Orthogonality & Decomposition

**Target Issues**: PP-ORTH-001, PP-ORTH-002, PP-ORTH-003

### 3.1 Decompose `code_quality_check.py` (317 lines)

Split into:
- `src/tools/code_quality/ast_analyzer.py` — AST-based metric collection
- `src/tools/code_quality/report_generator.py` — Report formatting
- `src/tools/code_quality/check.py` — Orchestrator

### 3.2 Separate concerns in `budget_check_utils.py`

Split into:
- Business logic: `budget_check_utils.py` (keep, remove print calls)
- CLI presentation: Move to `scripts/` entry points

### 3.3 Split `contracts.py` (351 lines)

Split into:
- `src/core/contracts/definitions.py` — Contract type definitions
- `src/core/contracts/validators.py` — Validation functions
- `src/core/contracts/__init__.py` — Re-exports for backward compatibility

---

## Phase 4: Testing & DbC Uplift

**Target Issues**: PP-TEST-001, PP-TEST-002, PP-TEST-003, CQ-DBC-001, CQ-DBC-002

### 4.1 Add property-based tests

**Create:** `tests/test_properties.py` using Hypothesis for:
- LaTeX parsing functions (roundtrip properties)
- Contract validation (invariant properties)
- Budget calculation (monotonicity properties)

### 4.2 Add integration tests for Quarto pipeline

**Create:** `tests/integration/test_quarto_pipeline.py`
- Test that sample `.qmd` files render without errors
- Verify link integrity post-render

### 4.3 Fill missing test coverage

Create test files for:
- `tests/test_latex_to_html.py`
- `tests/test_publish_manual_article.py`
- `tests/test_fix_html_validation.py`

### 4.4 Add DbC contracts to tool scripts

Add precondition/postcondition assertions to all public functions in `src/tools/`.

---

## Phase 5: Reversibility & Polish

**Target Issues**: CQ-REV-001, CQ-REV-002

### 5.1 Make output format configurable

Add `--format {json,markdown,csv}` flag to assessment scripts.

### 5.2 Create configurable LaTeX transformation pipeline

Replace hardcoded regex in conversion tools with a configurable pipeline:
```python
@dataclass
class TransformRule:
    pattern: str
    replacement: str
    description: str

class ConversionPipeline:
    rules: list[TransformRule]
    
    @classmethod
    def from_config(cls, config_path: Path) -> "ConversionPipeline": ...
```

---

## Cross-Repository Dependencies

- **Tools**: AffineDrift's `src/tools/utils/assessment_utils.py` standardizes assessment principles used fleet-wide. Any changes here must be coordinated with Tools repo's `scripts/pragmatic_programmer_review.py`.
- **UpstreamDrift**: The `BaseChecker` pattern (Phase 2.3) should be consistent with UpstreamDrift's quality gate scripts.

---

## Success Criteria

After all phases:
- [ ] 0 print() calls in production code (excluding noqa-annotated debug utils)
- [ ] 0 bare `except:` blocks
- [ ] All public functions have return type hints
- [ ] 0 TODO/FIXME markers
- [ ] Test coverage ≥ 60%
- [ ] No file exceeds 400 lines
- [ ] All check scripts inherit from `BaseChecker`
- [ ] CI/CD passes on all changes
