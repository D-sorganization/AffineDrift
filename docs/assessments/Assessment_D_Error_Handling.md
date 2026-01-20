# Assessment D: Error Handling

## Grade: B (8/10)

## Analysis
Error handling is generally present but could be more user-friendly in CLI tools.

### Strengths
*   **Try-Except Blocks:** Used in file processing loops to prevent crashing the whole batch.
*   **Validation:** Input validation exists in some tools.

### Weaknesses
*   **Generic Excepts:** Usage of `except Exception as e:` is common, which can mask bugs.
*   **Silent Failures:** Some `sys.exit(1)` calls are silent or lack context.
*   **Logging:** Reliance on `print` instead of `logging` module in some older scripts makes debugging harder in CI.

## Recommendations
1.  **Specific Exceptions:** Catch specific exceptions (e.g., `FileNotFoundError`, `ValueError`) where possible.
2.  **Standard Logging:** Migrate all `print` error messages to `logging.error`.
