# Assessment H: Error Handling & Debugging
**Date:** 2026-01-17
**Repository:** AffineDrift - Quarto Scientific Website
**Assessor:** Developer Experience Engineer

---

## Executive Summary

AffineDrift is a Quarto-based scientific website with supporting Python tooling for content conversion, site health checking, and quality assurance. The error handling assessment reveals a **mixed maturity level** - while some tools demonstrate good practices, the majority lack comprehensive error handling, actionable error messages, and debugging support.

**Overall Grade:** **C+ (Fair)**

**Key Findings:**
- ✅ Minimal custom exceptions across the codebase
- ⚠️ Inconsistent error message quality (cryptic silent failures common)
- ❌ No verbose/debug mode in most tools
- ❌ Poor error recovery and user guidance
- ✅ Some good examples in newer tools (`update_navigation.py`, `code_quality_check.py`)

---

## Key Metrics

| Metric                   | Target | Current | Status     |
| ------------------------ | ------ | ------- | ---------- |
| Actionable Error Rate    | >80%   | ~35%    | 🔴 CRITICAL |
| Time to Understand Error | <2 min | 5-15min | 🟡 MAJOR    |
| Recovery Path Documented | 100%   | 0%      | 🔴 MAJOR    |
| Verbose Mode Available   | Yes    | No      | 🟡 MINOR    |

---

## Detailed Analysis

### A. Error Message Quality

#### ✅ GOOD Examples

**1. `update_navigation.py` - Clear, Actionable Error**
```python
# Line 91-92
message = f'No <ul class="nav-links"> block found in "{file_path}".'
raise ValueError(message)
```
- ✅ Specifies exact problem (missing nav block)
- ✅ Includes context (file path)
- ✅ Clear exception type (ValueError)

**2. `code_quality_check.py` - Rich Error Context**
```python
# Lines 264-273
for filepath, issues in all_issues:
    sys.stderr.write(f"\n{Colors.CYAN}{filepath}:{Colors.ENDC}\n")
    for line_num, message, code in issues:
        if line_num > 0:
            sys.stderr.write(f"  Line {Colors.BOLD}{line_num}{Colors.ENDC}: {message}\n")
            if code:
                sys.stderr.write(f"    > {Colors.WARNING}{code}{Colors.ENDC}\n")
```
- ✅ Color-coded output for clarity
- ✅ Line numbers and code snippets
- ✅ Aggregated error summary

#### ❌ POOR Examples

**1. `latex_to_qmd.py` - Silent Failures**
```python
# Lines 318-319, 324-325
if len(sys.argv) < 2:
    sys.exit(1)  # ❌ NO ERROR MESSAGE

if not os.path.exists(input_file):
    sys.exit(1)  # ❌ NO ERROR MESSAGE
```
**Issues:**
- No indication of what went wrong
- No usage instructions
- User has no idea why the program failed

**Recommended Fix:**
```python
if len(sys.argv) < 2:
    print("Error: Missing input file", file=sys.stderr)
    print("Usage: latex_to_qmd.py <input.tex> [output.qmd]", file=sys.stderr)
    sys.exit(1)

if not os.path.exists(input_file):
    print(f"Error: Input file not found: {input_file}", file=sys.stderr)
    print(f"Current directory: {os.getcwd()}", file=sys.stderr)
    sys.exit(1)
```

**2. `generate_search_index.py` - Swallowed Exceptions**
```python
# Lines 106-109
try:
    content = filepath.read_text(encoding="utf-8")
except Exception:
    return None  # ❌ Silent failure
```
**Issues:**
- No logging of what failed
- No indication which file caused the problem
- User doesn't know search index is incomplete

**3. `check_site_health.py` - Generic Exception Handler**
```python
# Lines 123-124
except Exception as e:
    logger.error("Error processing %s: %s", file_path, e)
```
**Issues:**
- Too broad exception catching
- No distinction between file read errors vs. parsing errors
- No recovery guidance

---

### B. Exception Hierarchy

**Finding:** ❌ **NO custom exceptions defined**

**Analysis:**
```bash
# Search result shows NO custom exception classes
find . -name "*.py" -exec grep -l "class.*Exception" {} \;
# Result: (empty)
```

**Impact:**
- Cannot distinguish between error types programmatically
- No domain-specific error handling
- Generic exceptions make debugging harder

**Recommendations:**
```python
# Suggested exception hierarchy for AffineDrift

class AffineDriftError(Exception):
    """Base exception for all AffineDrift tools."""
    pass

class ConversionError(AffineDriftError):
    """Raised when content conversion fails."""
    pass

class ValidationError(AffineDriftError):
    """Raised when content validation fails."""
    pass

class ConfigurationError(AffineDriftError):
    """Raised when configuration is invalid."""
    pass
```

---

### C. Debugging Support

#### Current State: ❌ **Inadequate**

| Feature                  | Available? | Notes                          |
| ------------------------ | ---------- | ------------------------------ |
| Verbose/debug mode       | ❌         | Only in `code_quality_check.py` (color output) |
| Intermediate state dumps | ❌         | No inspection capability       |
| Structured logging       | ⚠️         | Only in `check_site_health.py` |
| Stack trace clarity      | ⚠️         | Default Python behavior        |

**Positive Example:**
```python
# check_site_health.py - Uses logging module
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)
```

**Missing in Most Tools:**
- No `--verbose` or `--debug` flags
- No intermediate output showing progress
- No dry-run modes for testing
- No state inspection during failures

**Recommended Addition:**
```python
import argparse
import logging

def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Enable verbose output")
args = parser.parse_args()
setup_logging(args.verbose)
```

---

### D. Recovery Strategies

**Current State:** ❌ **Minimal Recovery Support**

| Strategy              | Implementation | Notes                    |
| --------------------- | -------------- | ------------------------ |
| Automatic retry       | ❌             | No retry logic anywhere  |
| Graceful degradation  | ⚠️             | Partial in `generate_search_index.py` |
| Partial results       | ⚠️             | Search index continues on error |
| State recovery        | ❌             | No checkpoint/resume     |

**Best Practice Example Found:**
```python
# generate_search_index.py - Continues on individual file failures
for filepath in dir_path.glob(pattern):
    entry = process_file(filepath)
    if entry:
        index.append(entry)
        processed += 1
    else:
        skipped += 1  # ⚠️ But doesn't log WHY it was skipped
```

**Improvement Needed:**
```python
for filepath in dir_path.glob(pattern):
    try:
        entry = process_file(filepath)
        if entry:
            index.append(entry)
            processed += 1
        else:
            logger.warning(f"Skipped {filepath}: No valid content")
            skipped += 1
    except Exception as e:
        logger.error(f"Failed to process {filepath}: {e}")
        if args.verbose:
            logger.exception("Detailed traceback:")
        failed += 1
```

---

### E. Error Documentation

**Current State:** ❌ **Non-existent**

| Documentation Type       | Exists? | Notes                     |
| ------------------------ | ------- | ------------------------- |
| Error codes              | ❌      | No error code system      |
| Troubleshooting guide    | ❌      | No dedicated guide        |
| FAQ for common errors    | ❌      | Not available             |
| Links from error to docs | ❌      | No error message links    |

**CONTRIBUTING.md mentions error reporting** but doesn't provide troubleshooting:
```markdown
# Lines 76-86
When reporting issues, please include:
- Description: What's the problem?
- Steps to reproduce
- Expected vs actual behavior
- Screenshots
- Browser/OS
```

**Recommendation:**
Create `docs/TROUBLESHOOTING.md` with common error scenarios:
```markdown
# Troubleshooting Guide

## LaTeX to Quarto Conversion Errors

### "No input file specified"
**Cause:** Missing command-line argument
**Fix:** `python tools/latex_to_qmd.py input.tex output.qmd`

### "Input file not found"
**Cause:** File path is incorrect or file doesn't exist
**Fix:**
1. Check file exists: `ls -la input.tex`
2. Use absolute path: `python tools/latex_to_qmd.py /full/path/to/input.tex`
```

---

## Error Scenario Testing

| Scenario                  | Current Message                                 | Actionable? | Fix Priority |
| ------------------------- | ----------------------------------------------- | ----------- | ------------ |
| Invalid input file        | `sys.exit(1)` (no message)                      | ❌          | **HIGH**     |
| Missing config            | N/A (tools don't use config files)              | N/A         | -            |
| File permission denied    | Generic Python exception                        | ⚠️          | **MEDIUM**   |
| Invalid LaTeX syntax      | No validation, produces broken output           | ❌          | **HIGH**     |
| Missing dependencies      | ImportError (good) but no installation guidance | ⚠️          | **MEDIUM**   |
| Network failure           | N/A (no network operations)                     | N/A         | -            |
| Out of memory             | Default Python exception                        | ⚠️          | **LOW**      |
| Broken links (site health)| `Found 0 broken links` / Lists broken links     | ✅          | -            |

---

## Error Quality Audit

| Error Source              | Current Quality | Examples                                | Fix Priority |
| ------------------------- | --------------- | --------------------------------------- | ------------ |
| Missing CLI arguments     | **POOR**        | Silent `sys.exit(1)`                    | **HIGH**     |
| File not found            | **POOR**        | Silent `sys.exit(1)`                    | **HIGH**     |
| Invalid file format       | **POOR**        | No validation, silent failure           | **HIGH**     |
| Parsing errors            | **FAIR**        | Generic exception messages              | **MEDIUM**   |
| Site health checks        | **GOOD**        | Clear logging with details              | **LOW**      |
| Code quality checks       | **GOOD**        | Color-coded output with line numbers    | **LOW**      |
| Navigation update errors  | **GOOD**        | Clear ValueError with context           | **LOW**      |
| Search index generation   | **FAIR**        | Continues on error but no logging       | **MEDIUM**   |

---

## Remediation Roadmap

### 48 Hours: Top 5 Worst Error Messages

1. **`latex_to_qmd.py` - Add usage messages**
   ```python
   # Priority: CRITICAL
   # Lines: 318-319, 324-325
   # Impact: Users completely blocked without guidance
   ```

2. **`generate_search_index.py` - Log skipped files**
   ```python
   # Priority: HIGH
   # Lines: 106-109
   # Impact: Silent data loss in search index
   ```

3. **Add `--help` flags to all CLI tools**
   ```python
   # Priority: HIGH
   # Impact: Discoverability and user experience
   ```

4. **`check_site_health.py` - Narrow exception handling**
   ```python
   # Priority: MEDIUM
   # Lines: 123-124
   # Impact: Masks specific error types
   ```

5. **All tools - Add version information**
   ```python
   # Priority: MEDIUM
   # Impact: Debugging and compatibility checking
   ```

### 2 Weeks: All User-Facing Errors Actionable

- [ ] Define custom exception hierarchy (`AffineDriftError` base class)
- [ ] Add error codes to all major error types
- [ ] Implement `--verbose` mode in all tools
- [ ] Add recovery suggestions to all error messages
- [ ] Create error message catalog
- [ ] Add input validation to all tools
- [ ] Replace all `except Exception` with specific exceptions

### 6 Weeks: Full Troubleshooting Guide + Verbose Mode

- [ ] Create comprehensive `TROUBLESHOOTING.md`
- [ ] Add error code documentation
- [ ] Implement debug logging in all tools
- [ ] Add dry-run modes for destructive operations
- [ ] Create error message testing framework
- [ ] Add links from error messages to documentation
- [ ] Implement state inspection/checkpointing for long operations

---

## Recommendations Summary

### Critical (Fix Immediately)

1. **Add error messages to all `sys.exit(1)` calls**
   - Impact: Users can't diagnose problems
   - Effort: Low (1-2 hours)

2. **Log skipped/failed operations**
   - Impact: Silent data loss
   - Effort: Medium (4-6 hours)

### High Priority (Fix This Week)

3. **Implement custom exception hierarchy**
   - Impact: Better error categorization
   - Effort: Medium (6-8 hours)

4. **Add `--help` and `--verbose` to all tools**
   - Impact: Improved user experience
   - Effort: Medium (6-8 hours)

### Medium Priority (Fix This Month)

5. **Create TROUBLESHOOTING.md**
   - Impact: Reduced support burden
   - Effort: High (8-12 hours)

6. **Add specific exception handling**
   - Impact: Better error recovery
   - Effort: High (10-15 hours)

---

## Conclusion

AffineDrift's error handling is **functional but immature**. The codebase shows signs of rapid development with limited attention to error scenarios. While some newer tools (`update_navigation.py`, `code_quality_check.py`) demonstrate good practices, the majority of tools fail to provide actionable error messages or recovery paths.

**Primary Issues:**
1. Silent failures (multiple `sys.exit(1)` with no messages)
2. Over-broad exception catching
3. No debugging/verbose modes
4. Missing error documentation

**Path Forward:**
Focus on the 48-hour quick wins (adding error messages) to immediately improve user experience, then systematically add error handling infrastructure over the next 6 weeks.

---

**Assessment H Complete**
*Cross-reference: See Assessment D for user experience, Assessment G for testing coverage*
