# Logging Standard for AffineDrift

## Source Code (src/) - STRICT LOGGING ONLY

All code in `src/` must use Python's `logging` module exclusively:

```python
import logging
logger = logging.getLogger(__name__)

# Usage:
logger.debug("Detailed diagnostic info")
logger.info("Confirmation of correct operation")
logger.warning("Something unexpected")
logger.error("A serious problem")
```

**Print is strictly forbidden in src/**.

## Scripts and Tools (scripts/, tools/) - LOGGING + INTENTIONAL CLI

Scripts may use `print()` ONLY for:
- User-facing CLI output (intentional UX)
- Progress indicators
- Final results

For diagnostics and errors, use `logging` with `file=sys.stderr` for error output.

## Test Files (tests/)

Use `logging` for diagnostic output. Print is acceptable for test output formatting.

## Implementation Guidelines

1. **Initialization**: Always add at the module top:
   ```python
   logger = logging.getLogger(__name__)
   ```

2. **No print() in src/** - enforced by CI

3. **Script print() allowed** - but use logging for errors/warnings

4. **Structured logging**: Include context in messages:
   ```python
   logger.info(f"Processing file: {filename} (size: {size} bytes)")
   ```

## Enforcement

- CI fails `ruff check` if `print()` appears in src/
- Script files must demonstrate intent when using print
- All new code requires logging for diagnostics
