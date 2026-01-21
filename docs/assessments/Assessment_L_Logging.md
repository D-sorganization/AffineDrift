# Assessment: Logging (Category L)

**Score: 8/10**

## Findings
Logging practices are good in Python scripts.
- `logging` module is used.
- JS code avoids `console.log` in production.

## Strengths
- Configurable log levels.
- Clean output for CI pipelines.

## Weaknesses
- Some older scripts might still use `print` for status updates.

## Recommendations
1. Migrate any remaining `print` statements to `logger.info` or `logger.debug`.
