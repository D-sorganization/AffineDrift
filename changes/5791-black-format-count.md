---
issue: 5791
summary: "Count actual Black per-file stderr diagnostics and retain read-only checks"
dl_state: "in_review"
next_step: "CI and automated review"
branch: "codex/burn1116-5791-black-count"
paths: "src/tools/utils/shell_utils.py,tests/test_shell_utils.py"
---

Real-Black and fixture regressions reproduce the incorrect zero count; cover timeout and Windows echo fallback paths.
