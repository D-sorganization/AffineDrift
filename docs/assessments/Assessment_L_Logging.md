# Assessment L: Logging

## Score: 5/10

## Analysis
Logging is inconsistent.
- **Methods**: Mix of `print()` and `logging` module.
- **Consistency**: Some scripts log verbosely, others are silent.

## Findings
- **Strengths**: Critical errors are usually printed.
- **Weaknesses**: Reliance on `print()` makes automated parsing/monitoring harder.

## Recommendations
- Standardize on Python's `logging` module for all scripts in `tools/`.
- Configure log levels (INFO/DEBUG) consistently.
