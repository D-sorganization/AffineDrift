---
issue: 5116
summary: "Filter CI Render Cache Inputs Without Reducing Validation"
dl_state: "in_progress"
next_step: "Validate the source fix, merge through protected checks, then observe normal runs for seven days and at least ten eligible completions."
branch: "fix/ci-render-cache-5116"
paths: ".github/workflows/ci-standard.yml, scripts/quarto_cache_key.py, tests/test_quarto_cache_key.py, tests/test_deployment_integrity.py, docs/development/ci-profiles/render-cache-inputs-5116.md"
---

## CI Render Cache Inputs

- Exclude root `SPEC.md` and `changes/` authoring records from the exact E2E
  render cache fingerprint while retaining tracked render inputs and full
  rendering on a miss (#5116).
- Validate Git index records and document a seven-day observation window,
  required-check evidence, dependency maintenance, and protected rollback.
- Correct existing workflow shell quoting and diagnostic findings without
  changing retry counts, test-count thresholds, or required checks.
