# Assessment K Results: Reproducibility & Provenance

## Executive Summary

*   **Code Reproducibility**: High. Git history is preserved.
*   **Environment Reproducibility**: Medium/Low. Lack of lockfile means environment can drift.
*   **Data Provenance**: `data/` directory exists (`bibliography.yaml`). Source of data is version controlled.
*   **Scientific Reproducibility**: Physics models in `tools/` are deterministic code.

## Scorecard

| Category              | Score | Evidence                                           | Remediation                     |
| --------------------- | ----- | -------------------------------------------------- | ------------------------------- |
| Version Control       | 10/10 | Git used effectively.                              | N/A                             |
| Environment           | 5/10  | No lockfile.                                       | Add `requirements.lock`.        |
| Data Management       | 8/10  | YAML data files are clean.                         | N/A                             |
| **Overall Score**     | **7.6/10** | **Good, needs lockfile.**                    |                                 |

## Remediation

1.  **Add Lockfile**: (Repeated recommendation).
