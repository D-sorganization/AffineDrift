---
title: "Critical: MATLAB Utility Scripts Corrupted"
date: 2026-02-01
labels: ["incomplete-implementation", "critical", "jules:completist"]
---

# Critical: MATLAB Utility Scripts Corrupted

## Description
The completist audit on 2026-02-01 revealed severe corruption in the MATLAB utility scripts located in `src/tools/matlab_utilities/quality/`.

Specifically, the assignment operator `=` has been replaced by `---` throughout the files, rendering them syntactically invalid and unusable.

## Affected Files
1. `src/tools/matlab_utilities/quality/run_quality_checks.m`
2. `src/tools/matlab_utilities/quality/exportCodeIssues.m`

## Impact
All MATLAB quality check and issue export tooling is currently non-functional.

## Action Required
Restore the files from a previous valid state or manually repair the syntax by replacing `---` with `=` where appropriate (and verifying other potential corruptions).
