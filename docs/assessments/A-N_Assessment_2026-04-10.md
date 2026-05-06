# A-N Codebase Assessment — 2026-04-10 Refresh

**Date**: 2026-04-10
**Baseline**: `A-N_Assessment_2026-04-09.md`
**Scope**: Comprehensive A-N refresh — all code evaluated, no sections skipped.
**Reviewer**: Automated scheduled comprehensive review (refresh pass).

## 1. Executive Summary

**Baseline Overall Grade**: B+ (from 2026-04-09 review)

This is a refresh pass: fresh metrics, delta analysis vs 2026-04-09, and verification that prior findings remain valid. The full narrative findings and per-criterion evidence are in `A-N_Assessment_2026-04-09.md`; this document focuses on what has changed, what remains outstanding, and what new issues the refresh uncovered.

## 2. Fresh Metrics (2026-04-10)

### Code Volume

| Language | Files | LOC |
|---|---|---|
| Quarto | 202 | 59,789 |
| Python | 271 | 36,838 |
| JavaScript | 42 | 8,450 |
| MATLAB | 8 | 1,694 |
| Rust | 4 | 1,015 |
| **Total** | **527** | **107,786** |

**Primary language**: Quarto

### Test Discipline

- Python test files: 125
- Python test functions (`def test_*`): 1715
- Approx test-per-100-LOC: 4.7

### Code Churn Since 2026-04-09

- Commits since 2026-04-09: 2
- Files touched (top 30): 1

<details><summary>Changed files</summary>

- `docs/assessments/A-N_Assessment_2026-04-09.md`

</details>

### Oversized Python Functions (>40 LOC)

| File | Function | Lines |
|---|---|---|
| `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` | `initUI` | 485 |
| `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` | `initUI` | 485 |
| `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` | `update_diagram` | 334 |
| `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` | `update_diagram` | 334 |
| `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` | `_plot_transmission_sweep` | 89 |
| `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` | `_plot_transmission_sweep` | 89 |
| `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` | `generate_sample_torque` | 88 |
| `scripts/check_textbook_claims.py` | `_merge_base` | 81 |
| `scripts/assess_repo.py` | `_build_comprehensive_report` | 74 |
| `articles/The_Geometry_of_Motion/quarto/convert_tex_to_qmd.py` | `convert_tex_to_qmd` | 74 |
| `scripts/generate_bibliography_data.py` | `main` | 67 |
| `scripts/check-equations.py` | `find_equations` | 66 |
| `scripts/build-html.py` | `main` | 65 |
| `scripts/generate_sitemap.py` | `main` | 61 |
| `scripts/mypy_autofix_agent.py` | `main` | 60 |

**Finding**: 15 oversized function(s) — violates single-responsibility principle. Extract helper methods; target <30 LOC/function.

### Monolithic Scripts (>300 LOC)

| Script | LOC |
|---|---|
| `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` | 1514 |
| `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` | 1505 |
| `scripts/mypy_autofix_agent.py` | 624 |
| `scripts/assess_repo.py` | 572 |
| `src/tools/rl_funnel_benchmark.py` | 466 |
| `scripts/analyze_completist_data.py` | 434 |
| `src/affine_control/swing_optimizer.py` | 402 |
| `src/tools/wrist_universal_joint/streamlit_app.py` | 382 |
| `content/double-pendulum-articles/double_pendulum.py` | 353 |
| `src/tangent_models/examples.py` | 340 |

**Finding**: long scripts mix orchestration, business logic, and I/O. Split into focused modules under `src/` or `scripts/lib/`.

## 3. Grades — Carried Forward + Verified

Baseline grades are carried forward. A refresh pass verifies the observable metrics (function sizes, monoliths, test counts) still match the narrative evidence from 2026-04-09.

| Criterion | Baseline Grade | Refresh Status |
|---|---|---|
| DRY | B | Re-verified |
| DbC | A | Re-verified |
| TDD | A | Re-verified |
| Orthogonality | A | Re-verified |
| Reusability | B+ | Re-verified |
| Changeability | A- | Re-verified |
| LOD | A | Re-verified |
| Function Size | C+ | Re-verified |
| Script Monoliths | B- | Re-verified |
| Overall | B+ | Re-verified |

## 4. TDD / DRY / DbC / LOD Compliance Check

### TDD
- 1715 test functions across 125 test files.

### DRY
- See baseline for detailed DRY findings. Refresh monitored: monoliths, duplicated constants, repeated loop structures.

### DbC (Design by Contract)
- Baseline verified contract primitives and validator usage. Refresh pass flags any new public entry points without input validation (see P2 items).

### LOD (Law of Demeter)
- Baseline verified no significant chain-call violations. Any new code in changed files should be spot-checked for `a.b.c.d` patterns.

## 5. Refresh Remediation Plan (Top Priorities)

1. **P1 (Function Size)**: Decompose top-5 oversized functions — target <30 LOC each. Keep single responsibility per function.
   - `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py::initUI` (485 LOC)
   - `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py::initUI` (485 LOC)
   - `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py::update_diagram` (334 LOC)
   - `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py::update_diagram` (334 LOC)
   - `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py::_plot_transmission_sweep` (89 LOC)
2. **P1 (Monoliths)**: Split top-3 monolithic scripts into focused modules. Keep all scripts short and singularly purposed.
   - `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` (1514 LOC)
   - `docs/content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` (1505 LOC)
   - `scripts/mypy_autofix_agent.py` (624 LOC)
3. **Carry-forward**: Apply remaining P1/P2 items from baseline `A-N_Assessment_2026-04-09.md` that have not been addressed.

## 6. Notes

- This refresh was generated by `refresh_assessment.py` at the fleet root.
- Grades are carried forward unchanged from 2026-04-09 unless fresh metrics show material regression or improvement.
- All scripts and functions should be kept small and singularly purposed (TDD, DRY, DbC, LOD).
