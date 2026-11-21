---
issue: 5797
summary: "Honor include_root=False in Quarto discovery without duplicate root entries"
dl_state: "in_review"
next_step: "CI and automated review"
branch: "codex/burn1116-5797-qmd-root"
paths: "src/tools/utils/file_utils.py,tests/test_file_utils.py"
---

Four regressions failed before the fix; 75 related tests pass, 100% statements and 97.3% combined coverage.
