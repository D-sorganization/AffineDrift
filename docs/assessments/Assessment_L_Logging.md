# Assessment L: Logging

## Grade: B- (7/10)

## Analysis
Logging is mixed between `print` and `logging`.

### Strengths
*   **Logging Config:** `logging.getLogger(__name__)` is used in some newer tools.

### Weaknesses
*   **Print Usage:** Many scripts still use `print()` for status updates and errors, which doesn't integrate well with structured logging systems or log levels.
*   **Inconsistent Formats:** No standard log format defined across tools.

## Recommendations
1.  **Unified Logger:** Create a `tools.logger` module to provide a standard logger configuration.
2.  **Migrate Prints:** Systematically replace `print()` with `logger.info()`, `logger.warning()`, etc.
