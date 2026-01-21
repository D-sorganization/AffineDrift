# Assessment: Dependencies

## Grade: 8/10

## Analysis
Dependencies are well-managed via `requirements.txt` and `package.json`. Versions are pinned. However, the list is long and mixes build, test, and runtime dependencies in a single `requirements.txt`.

### Strengths
- Pinned versions.
- Modern packages.

### Weaknesses
- Single `requirements.txt` for everything (dev/test/prod).
- Potential bloat if not pruned.

## Recommendations
1. Split `requirements.txt` into `requirements.in` (base) and `requirements-dev.txt`.
2. Audit unused dependencies.
