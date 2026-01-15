# Assessment K Results: Reproducibility & Provenance

## Executive Summary

Reproducibility is hindered by the `requirements.txt` issues (`numpy` failure). While the code *exists* to reproduce the site, the *environment* is not perfectly specified. The scientific models in `tools/` should ideally have their own `requirements.txt` or environment definition to ensure results (e.g., wrist simulation) are reproducible.

## Top Risks

1.  **Environment Ambiguity (Severity: HIGH)**: `requirements.txt` seems insufficient for the test suite in a fresh environment.
2.  **Scientific Reproducibility (Severity: MEDIUM)**: Models in `tools/` need strict versioning of `numpy`/`scipy` to guarantee numerical identicality.

## Scorecard

| Category               | Score | Evidence                                           | Remediation                               |
| ---------------------- | ----- | -------------------------------------------------- | ----------------------------------------- |
| Build Reproducibility  | 8/10  | CI builds consistently.                            | N/A                                       |
| Local Reproducibility  | 6/10  | Local setup failed.                                | Fix requirements.                         |
| Scientific Provenance  | 7/10  | Code available, but env specs loose.               | Pin versions exactly.                     |

**Weighted Score: 7/10**

## Refactoring Plan

**Quick Wins**
1.  **Fix Requirements**: Add missing deps.
2.  **Version Info**: Add a step in the build to log `pip freeze` to artifacts for debugging.

**Strategic Fixes**
1.  **Docker**: Provide a `Dockerfile` that builds the exact environment, guaranteeing reproducibility forever.
