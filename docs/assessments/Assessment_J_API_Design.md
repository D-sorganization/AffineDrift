# Assessment: API Design

## Grade: 7/10

## Analysis
This is primarily a static site, so "API Design" refers to internal tool interfaces. Functions in `build-html.py` and `tools/` have clear signatures and type hints.

### Strengths
- Type hints used.
- Clear function names.

### Weaknesses
- Internal APIs are ad-hoc; no formal contract for tool interaction.

## Recommendations
1. Standardize CLI arguments for all tools using `argparse` or `typer`.
