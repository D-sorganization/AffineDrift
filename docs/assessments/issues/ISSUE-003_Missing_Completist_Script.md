---
title: Missing Completist Script
date: 2026-02-01
labels: ["jules:code-quality", "critical"]
---

# Issue Description

The script `scripts/generate_completist_data.py` is missing from the repository, likely deleted or lost during the recent massive commit. This script is essential for Stage 1 of the assessment pipeline (Data Generation). Without it, the "Completist" workflow cannot generate fresh data files (e.g., `todo_markers.txt`) for analysis.

# Remediation Plan
1.  Restore `scripts/generate_completist_data.py` from a previous commit or backup.
2.  Verify that it correctly scans the codebase and generates the required data files in `.jules/completist_data/`.
3.  Ensure the script handles binary file filtering to prevent corruption, as noted in project guidelines.
