---
issue: 5618
summary: "Reconcile learning-path weekly schedules and module hour totals with 16-week path budgets."
branch: "gemini-ct/5618-learning-paths"
---

- Replace inconsistent `hours/day` blocks in `resources/learning-path-control-theory.qmd` and `resources/learning-path-biomechanics.qmd` with `## Recommended Weekly Schedule` blocks spanning all 8 two-week modules (`Weeks 1–2` through `Weeks 15–16`).
- Align module two-week hour ranges and weekly totals with each page's declared `Total Time` (`120–160 hours` and `100–140 hours`).
- Add regression schedule/citation contract tests in `tests/test_learning_paths.py`.
