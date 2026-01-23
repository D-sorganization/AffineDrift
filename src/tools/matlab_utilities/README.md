# MATLAB Utilities

This directory contains various MATLAB-related utilities for code quality, data conversion, and scientific modeling.

## Tools

### matlab_quality_check.py
A unified Python wrapper for running comprehensive MATLAB code quality checks.

## Usage
```bash
python tools/matlab_utilities/scripts/matlab_quality_check.py --strict
```

## Standards
All MATLAB code should follow the project's `.cursorrules.md` and include:
- Function docstrings
- Arguments validation blocks
- Proper encapsulation (no `eval`, `assignin`, etc.)
- No magic numbers
