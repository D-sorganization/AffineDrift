# Assessment G: Dependencies

## Grade: 9/10

## Analysis
Dependency management is excellent.

## Strengths
- Single `requirements.txt` makes management easy.
- Versions are pinned (mostly `>=` but some specific).
- `package.json` manages frontend tools.

## Weaknesses
- Mixing runtime and dev dependencies in one file can be slightly messy, but acceptable here.
- `types-*` packages need to be kept in sync.

## Recommendations
1. Consider splitting `requirements.txt` into `requirements.txt` and `requirements-dev.txt` if the list grows too long.
