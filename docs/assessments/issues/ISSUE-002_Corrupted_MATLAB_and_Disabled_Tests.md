---
title: Corrupted MATLAB Code and Disabled Tests
date: 2026-02-01
labels: ["jules:code-quality", "critical"]
---

# Issue Description

A recent massive commit introduced critical syntax errors in MATLAB utility files. Specifically, the assignment operator `=` has been replaced by `---` in:
*   `src/tools/matlab_utilities/quality/run_quality_checks.m`
*   `src/tools/matlab_utilities/quality/exportCodeIssues.m`

This renders the MATLAB quality tools non-functional.

Additionally, the `matlab-tests` job in `.github/workflows/ci-standard.yml` has been disabled with `if: false`. This "CI gaming" prevents the pipeline from catching these syntax errors.

# Remediation Plan
1.  Fix the syntax in the affected MATLAB files (replace `---` with `=`).
2.  Re-enable the `matlab-tests` job in `.github/workflows/ci-standard.yml`.
3.  Remove `continue-on-error: true` from critical quality checks where appropriate.
