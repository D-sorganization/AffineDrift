# Assessment H Results: Error Handling & Debugging

## Executive Summary

- **Error Handling**: Scripts use standard Python exceptions. `tools/scientific_auditor.py` catches exceptions to prevent crashes during audit.
- **Clarity**: `build-html.py` prints clear warnings.
- **Recovery**: `build-html.py` continues processing other files if one fails (mostly).

## Top Reliability Risks

1.  **Silent Failures (Severity: LOW)**: Some scripts might just print "Warning" and exit 0, potentially hiding issues in CI if not checked strictly.
2.  **No Verbose Mode (Severity: LOW)**: CLI tools don't seem to have `--verbose` flags.

## Scorecard

| Category                 | Score | Evidence                                                                 | Remediation                               |
| ------------------------ | ----- | ------------------------------------------------------------------------ | ----------------------------------------- |
| Actionable Error Rate    | 8/10  | Errors are generally readable.                                           | N/A                                       |
| Time to Understand Error | 9/10  | Simple scripts, simple errors.                                           | N/A                                       |
| Recovery Path Documented | 7/10  | Not explicitly documented, but code recovers.                            | N/A                                       |

**Weighted Score: 8.0/10**

## Refactoring Plan

**Quick Wins**
1.  **Exit Codes**: Ensure all scripts return non-zero exit codes on critical failures (e.g. `check_links.py` does `sys.exit(1)`).

**Strategic Fixes**
1.  **Logging**: Switch `print` to `logging` everywhere (like `check_links.py` does).
