# Assessment K Results: Reproducibility & Provenance

## Executive Summary

- **Determinism**: Python models (Streamlit) use `np.random.default_rng(SEED)`, which is excellent. JS models use `Math.random()`, which is not reproducible.
- **Version Tracking**: `requirements.txt` tracks dependencies but versions are loose.
- **Provenance**: No explicit experiment tracking (e.g. MLflow), but appropriate for this project type.

## Top Reproducibility Risks

1.  **JS Randomness (Severity: MEDIUM)**: JavaScript simulations use `Math.random()` which cannot be seeded, making visual regression testing impossible.
2.  **Loose Python Deps (Severity: LOW)**: `requirements.txt` allows newer versions which might break math (unlikely for `numpy` but possible).

## Scorecard

| Category              | Score | Evidence                                                                 | Remediation                               |
| --------------------- | ----- | ------------------------------------------------------------------------ | ----------------------------------------- |
| Deterministic Exec    | 8/10  | Python good, JS bad.                                                     | Use seeded RNG in JS.                     |
| Version Tracking      | 7/10  | `requirements.txt` present but loose.                                    | Pin versions.                             |
| Random Seed Handling  | 9/10  | Python explicitly handles it.                                            | N/A                                       |
| Result Reproduction   | 8/10  | Code is available.                                                       | N/A                                       |

**Weighted Score: 8.0/10**

## Refactoring Plan

**Quick Wins**
1.  **Pin Dependencies**: Tighten `requirements.txt`.

**Strategic Fixes**
1.  **Seeded JS RNG**: Implement a simple Linear Congruential Generator (LCG) in JS for simulations.
