---
name: "Content Correction"
about: "Report a technical error, sign error, or missing assumption in the mathematical/physics content"
title: "correction: "
labels: ["content-correction", "needs-verification"]
assignees: []
---

## What is wrong

**Quote the exact text and equation**:
(Please quote the claim exactly as written)

**Location**:

- File and line number (`file:line`):
- Is this in the LaTeX (`.tex`) tree, the Quarto (`.qmd`) tree, or both?

## What it should say

(Provide the corrected derivation, text, or equation here)

## How did you verify this?

A claim is actionable when it is directly observed in the source or reproduced by executing something.
A claim inferred from an _absence_ — a missing file, a missing directory, a missing rendered page — must be checked against `.gitignore`, the CI workflows and the deploy pipeline before it is filed, because generated artifacts are absent from the working tree by design here.

**Method of verification**:
(Did you run a script, recompute the matrix, or derive it by hand? Please provide the steps or script to reproduce your finding)
