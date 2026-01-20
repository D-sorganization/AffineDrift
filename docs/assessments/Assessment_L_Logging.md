# Assessment L: Logging

## Grade: 5/10

## Analysis
Logging is the weakest part of the operational code.

## Strengths
- `logging` module is used in some newer scripts.

## Weaknesses
- Many scripts rely on `print()` for debugging and status.
- No centralized logging configuration.

## Recommendations
- Standardize on `logging` module for all scripts.
- Create a shared logging config in `tools/__init__.py` or similar.
