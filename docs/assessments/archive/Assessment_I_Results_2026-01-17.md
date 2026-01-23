# Assessment I: Security & Input Validation
**Date:** 2026-01-17
**Repository:** AffineDrift - Quarto Scientific Website
**Assessor:** Security Engineer

---

## Executive Summary

AffineDrift is a static Quarto website with Python tooling for content management. The security assessment reveals **low overall risk** due to the project's nature (static site generation, no user input at runtime, no network operations), but identifies **several input validation gaps** in the build tooling that could lead to local file system vulnerabilities or unexpected behavior.

**Overall Security Grade:** **B (Good)**

**Risk Level:** **LOW-MEDIUM**

**Key Findings:**
- ✅ No hardcoded secrets detected
- ✅ No network operations (no HTTPS/auth concerns)
- ✅ Appropriate `.gitignore` configuration
- ⚠️ Input validation gaps in file path handling
- ⚠️ Dependency security unknown (no automated scanning)
- ⚠️ Potential path traversal vulnerabilities in tooling
- ✅ No command injection vectors detected

---

## Key Metrics

| Metric                     | Target           | Current | Status       |
| -------------------------- | ---------------- | ------- | ------------ |
| Dependency Vulnerabilities | 0 high/critical  | Unknown | 🟡 MAJOR     |
| Input Validation           | 100% user inputs | ~40%    | 🟡 MAJOR     |
| Secrets Exposure           | 0                | 0       | ✅ GOOD      |
| Injection Vulnerabilities  | 0                | 0       | ✅ GOOD      |

---

## Detailed Security Analysis

### A. Dependency Security

**Current State:** 🟡 **UNKNOWN - No Active Scanning**

#### Dependency Inventory

**Python Dependencies (`requirements.txt`):**
```txt
# Test dependencies
numpy>=1.24.0
scipy>=1.10.0
pytest>=7.0.0
pytest-cov>=4.0.0

# Build & Utilities
PyYAML>=6.0.1
types-PyYAML
beautifulsoup4>=4.12.0
matplotlib>=3.7.0
jupyter>=1.0.0
types-requests
streamlit>=1.28.0

# Linting & Quality
pre-commit>=3.0.0
ruff>=0.5.0
black>=24.4.2
isort>=5.13.2
mypy>=1.13.0
```

**Analysis:**
- ✅ Uses minimum version specifiers (`>=`) for flexibility
- ⚠️ No upper bounds - could pull vulnerable versions
- ⚠️ No `pip-audit` or `safety` scan in CI/CD
- ⚠️ Some dependencies (e.g., `jupyter`, `streamlit`) have large attack surfaces

**JavaScript Dependencies (`package.json`):**
```json
{
  "devDependencies": {
    "html-validate": "^8.0.0",
    "prettier": "^3.0.0",
    "stylelint": "^16.0.0"
  }
}
```

**Analysis:**
- ✅ Minimal dependency footprint
- ✅ Only dev dependencies (not deployed)
- ⚠️ No `npm audit` enforcement in CI

#### CI/CD Security Checks

**`.github/workflows/ci-standard.yml`:**
```yaml
# Line 19: Security tools installation
- run: pip install ruff==0.5.0 black==24.4.2 mypy==1.13.0 bandit==1.7.7 pydocstyle==6.3.0
```

**Findings:**
- ✅ **Bandit installed** (security linter for Python)
- ❌ **Bandit not executed** in workflow
- ❌ No `pip-audit` or `safety` checks
- ❌ No `npm audit` enforcement

**Recommendation:**
```yaml
- name: Security Scan - Python Dependencies
  run: |
    pip install pip-audit
    pip-audit --desc --fix-dryrun

- name: Security Scan - Python Code
  run: bandit -r tools/ scripts/ -f json -o bandit-report.json

- name: Security Scan - JavaScript Dependencies
  run: npm audit --audit-level=high
```

---

### B. Input Validation

**Current State:** ⚠️ **INCONSISTENT - Major Gaps**

#### Critical Path Traversal Risk

**`latex_to_qmd.py` - UNVALIDATED FILE PATHS**

```python
# Lines 296-313
def convert_file(self, input_file: str | Path, output_file: str | Path | None = None) -> Path:
    if output_file is None:
        output_file = Path(input_file).with_suffix(".qmd")

    # ⚠️ NO VALIDATION of input_file or output_file paths
    latex_content = self.read_latex_file(input_file)
    qmd_content = self.convert_to_qmd(latex_content)

    # ⚠️ Creates directories without validating path
    output_path = Path(output_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(qmd_content)
```

**Vulnerability:**
```bash
# Attacker could traverse to arbitrary locations
python tools/latex_to_qmd.py ../../../../etc/passwd /tmp/output.qmd
python tools/latex_to_qmd.py input.tex ../../../home/user/.ssh/authorized_keys
```

**Recommended Fix:**
```python
import os.path

def validate_file_path(path: Path, base_dir: Path) -> Path:
    """Validate file path to prevent directory traversal."""
    resolved = path.resolve()
    base_resolved = base_dir.resolve()

    if not resolved.is_relative_to(base_resolved):
        raise ValueError(
            f"Invalid path: {path} is outside base directory {base_dir}"
        )

    return resolved

def convert_file(self, input_file: str | Path, output_file: str | Path | None = None) -> Path:
    base_dir = Path.cwd()

    # Validate input path
    input_path = validate_file_path(Path(input_file), base_dir)

    if output_file is None:
        output_file = input_path.with_suffix(".qmd")

    # Validate output path
    output_path = validate_file_path(Path(output_file), base_dir)

    # Rest of function...
```

#### Regex Injection Risk

**`update_navigation.py` - UNVALIDATED REGEX INPUT**

```python
# Lines 47-50
NAV_LIST_PATTERN = re.compile(
    r'(?P<indent>[ \t]*)<ul class="nav-links">.*?</ul>',
    re.DOTALL,
)
```

**Analysis:**
- ✅ Pattern is hardcoded (not from user input)
- ✅ No dynamic regex compilation
- ✅ **No vulnerability present**

#### HTML/XML Injection Risk

**`check_site_health.py` - BeautifulSoup HTML Parsing**

```python
# Lines 67-73
with full_path.open(encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

for a in soup.find_all("a", href=True):
    href_value = cast("Any", a).get("href")
    href = str(href_value) if href_value is not None else ""
```

**Analysis:**
- ✅ Parsing local files only (not user input)
- ✅ BeautifulSoup handles malformed HTML safely
- ✅ No XSS risk (no HTML generation from parsed content)
- ✅ **No vulnerability present**

#### Command Injection Risk

**Search for dangerous patterns:**
```python
# Searched: subprocess, os.system, eval, exec
# Result: NO INSTANCES FOUND
```

**Analysis:**
- ✅ **No subprocess calls detected**
- ✅ **No os.system() usage**
- ✅ **No eval()/exec() usage**
- ✅ **No command injection vectors**

---

### C. Secrets Management

**Current State:** ✅ **EXCELLENT**

#### `.gitignore` Configuration

```gitignore
# Lines 28-33
env/
venv/
.env
server.log
fetch.log
*.log
```

**Analysis:**
- ✅ Excludes `.env` files
- ✅ Excludes virtual environments
- ✅ Excludes log files
- ✅ Appropriate exclusions

#### Hardcoded Secrets Search

**Search Results:**
```bash
# Searched for: password, secret, api_key, token, credentials
# GitHub Actions workflows use: ${{ secrets.CODECOV_TOKEN }}
# Result: NO HARDCODED SECRETS FOUND
```

**CI/CD Secrets Usage:**
```yaml
# .github/workflows/ci-standard.yml (Lines 102-108)
- uses: codecov/codecov-action@v4
  env:
    CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
  if: env.CODECOV_TOKEN != ''
  with:
    fail_ci_if_error: true
    token: ${{ secrets.CODECOV_TOKEN }}
```

**Analysis:**
- ✅ Uses GitHub Secrets properly
- ✅ Conditional execution if secret not set
- ✅ **No secrets exposed in code**

---

### D. File Handling Security

**Current State:** ⚠️ **MIXED**

#### File Reading Operations

**`generate_search_index.py` - Safe File Reading**
```python
# Lines 106-109
try:
    content = filepath.read_text(encoding="utf-8")
except Exception:
    return None  # ⚠️ Silent failure (not a security issue)
```

**Analysis:**
- ✅ Specifies encoding
- ✅ Exception handling present
- ⚠️ Too broad exception (see Assessment H)
- ✅ **No security vulnerability**

#### File Writing Operations

**`latex_to_qmd.py` - Unsafe File Writing**
```python
# Lines 309-311
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(qmd_content)
```

**Issues:**
- ⚠️ Creates arbitrary directories
- ⚠️ Overwrites existing files without warning
- ⚠️ No file size limits
- ⚠️ No permission checks

**Recommended Improvements:**
```python
import os

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def safe_write_file(path: Path, content: str, max_size: int = MAX_FILE_SIZE) -> None:
    """Safely write file with size and permission checks."""

    # Check content size
    content_bytes = content.encode("utf-8")
    if len(content_bytes) > max_size:
        raise ValueError(f"Content exceeds maximum size of {max_size} bytes")

    # Check parent directory exists and is writable
    parent = path.parent
    if not parent.exists():
        raise ValueError(f"Parent directory does not exist: {parent}")
    if not os.access(parent, os.W_OK):
        raise PermissionError(f"No write permission for directory: {parent}")

    # Warn if overwriting
    if path.exists():
        logger.warning(f"Overwriting existing file: {path}")

    # Write file
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
```

#### Pickle/Untrusted Data Parsing

**Search Results:**
```bash
# Searched for: pickle.load, yaml.load (unsafe), json.loads
# Result: NO UNSAFE DESERIALIZATION FOUND
```

**`generate_search_index.py` uses safe JSON:**
```python
# Lines 192-200
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        {
            "generated": datetime.now().isoformat(),
            "count": len(index),
            "entries": index,
        },
        f,
        indent=2,
    )
```

**Analysis:**
- ✅ Uses `json.dump()` (write only, safe)
- ✅ No `json.loads()` or `pickle.load()` usage
- ✅ **No deserialization vulnerabilities**

#### Temporary File Cleanup

**Search Results:**
```bash
# Searched for: tempfile, mkstemp, NamedTemporaryFile
# Result: NO TEMPORARY FILE USAGE FOUND
```

**Analysis:**
- ✅ No temporary file handling
- ✅ **No cleanup issues**

---

### E. Network Security

**Current State:** N/A - **No Network Operations**

**Analysis:**
- ✅ Static site - no server-side code
- ✅ No HTTP requests in build tools
- ✅ No authentication/authorization needed
- ✅ **No network security concerns**

**Note:** The deployed site uses GitHub Pages HTTPS by default.

---

## Vulnerability Report

| ID    | Type                  | Severity | Location                     | Fix                          |
| ----- | --------------------- | -------- | ---------------------------- | ---------------------------- |
| I-001 | Dependency Scanning   | MEDIUM   | CI/CD pipeline               | Add `pip-audit` to workflow  |
| I-002 | Path Traversal        | MEDIUM   | `latex_to_qmd.py:296-313`    | Add path validation          |
| I-003 | File Size Limits      | LOW      | `latex_to_qmd.py:311`        | Add max file size check      |
| I-004 | Input Validation      | MEDIUM   | Multiple files               | Add argparse validation      |
| I-005 | Bandit Not Executed   | LOW      | CI/CD pipeline               | Run bandit security scan     |
| I-006 | Unsafe File Overwrite | LOW      | `latex_to_qmd.py:311`        | Add overwrite warning        |

---

## Security Best Practices Assessment

### ✅ Implemented

1. **Secrets Management**
   - GitHub Secrets for tokens
   - `.env` files excluded from git
   - No hardcoded credentials

2. **Code Quality**
   - Pre-commit hooks configured
   - Type hints used (MyPy)
   - Linting with Ruff

3. **Dependency Pinning (Partial)**
   - Some tools have exact versions in CI
   - Requirements use minimum versions

### ⚠️ Partially Implemented

4. **Input Validation**
   - Some tools validate, many don't
   - No centralized validation utilities
   - Path traversal risks exist

5. **Error Handling**
   - Some exception handling
   - Often too broad (`except Exception`)
   - See Assessment H for details

### ❌ Missing

6. **Automated Security Scanning**
   - No `pip-audit` in CI
   - Bandit installed but not run
   - No `npm audit` enforcement

7. **Security Documentation**
   - No SECURITY.md
   - No vulnerability reporting process
   - No security release process

8. **Content Security Policy**
   - No CSP headers (GitHub Pages limitation)
   - No SRI for external resources

---

## Remediation Roadmap

### 48 Hours: Critical Vulnerabilities

**Priority: HIGH**

1. **Add dependency vulnerability scanning**
   ```yaml
   # Add to .github/workflows/ci-standard.yml
   - name: Scan Python Dependencies
     run: |
       pip install pip-audit
       pip-audit --desc --fix-dryrun --format=json --output=audit-report.json

   - name: Security Scan Code
     run: bandit -r tools/ scripts/ -ll
   ```

2. **Add path validation to `latex_to_qmd.py`**
   - Implement `validate_file_path()` function
   - Prevent directory traversal
   - Estimated time: 1-2 hours

### 2 Weeks: Input Validation Coverage

**Priority: MEDIUM**

3. **Implement centralized validation utilities**
   ```python
   # tools/validation.py
   from pathlib import Path

   def validate_input_path(path: str | Path, must_exist: bool = True) -> Path:
       """Validate input file path."""
       p = Path(path).resolve()
       if must_exist and not p.exists():
           raise FileNotFoundError(f"Input file not found: {path}")
       return p

   def validate_output_path(path: str | Path, base_dir: Path) -> Path:
       """Validate output file path against base directory."""
       p = Path(path).resolve()
       if not p.is_relative_to(base_dir.resolve()):
           raise ValueError(f"Output path outside base directory: {path}")
       return p
   ```

4. **Add argparse to all tools**
   - Proper argument validation
   - Help messages
   - Type checking

5. **Add file size limits**
   - Prevent resource exhaustion
   - Add to all file write operations

### 6 Weeks: Full Security Audit

**Priority: MEDIUM-LOW**

6. **Create SECURITY.md**
   ```markdown
   # Security Policy

   ## Reporting a Vulnerability

   Please report security vulnerabilities to: [email]

   ## Supported Versions

   | Version | Supported |
   | ------- | --------- |
   | Latest  | ✅        |

   ## Security Update Process

   1. Vulnerabilities are triaged within 48 hours
   2. Fixes released within 7 days for critical issues
   3. Security advisories published on GitHub
   ```

7. **Implement security testing**
   - Add security-focused unit tests
   - Path traversal test cases
   - Malicious input test cases

8. **Add pre-commit security hooks**
   ```yaml
   # .pre-commit-config.yaml
   - repo: https://github.com/PyCQA/bandit
     rev: 1.7.7
     hooks:
       - id: bandit
         args: ["-ll"]
   ```

---

## Risk Assessment Matrix

| Threat                 | Likelihood | Impact | Risk Level | Mitigation Priority |
| ---------------------- | ---------- | ------ | ---------- | ------------------- |
| Path Traversal         | Medium     | Medium | **MEDIUM** | HIGH                |
| Dependency Vuln        | Medium     | High   | **MEDIUM** | HIGH                |
| Resource Exhaustion    | Low        | Low    | **LOW**    | MEDIUM              |
| Code Injection         | Very Low   | High   | **LOW**    | LOW                 |
| Secrets Exposure       | Very Low   | High   | **LOW**    | LOW (Already Good)  |
| XSS (Static Site)      | Very Low   | Medium | **LOW**    | LOW                 |

---

## Compliance & Standards

### OWASP Top 10 (2021) Applicability

| Category                      | Applicable? | Status | Notes                           |
| ----------------------------- | ----------- | ------ | ------------------------------- |
| A01: Broken Access Control    | ⚠️          | N/A    | Local tools only                |
| A02: Cryptographic Failures   | ❌          | N/A    | No sensitive data handling      |
| A03: Injection                | ✅          | ✅     | No injection vectors found      |
| A04: Insecure Design          | ⚠️          | ⚠️     | Some missing validations        |
| A05: Security Misconfiguration| ✅          | ⚠️     | Bandit installed but not run    |
| A06: Vulnerable Components    | ✅          | ⚠️     | No automated scanning           |
| A07: Auth Failures            | ❌          | N/A    | No authentication               |
| A08: Data Integrity Failures  | ⚠️          | ✅     | No deserialization              |
| A09: Logging Failures         | ⚠️          | ⚠️     | See Assessment H                |
| A10: Server-Side Request Forge| ❌          | N/A    | No network operations           |

---

## Recommendations Summary

### Critical (Implement Immediately)

1. **Add `pip-audit` to CI/CD pipeline**
   - Impact: Detect vulnerable dependencies
   - Effort: Low (30 minutes)

2. **Fix path traversal in `latex_to_qmd.py`**
   - Impact: Prevent arbitrary file system access
   - Effort: Low (1-2 hours)

### High Priority (This Week)

3. **Run Bandit security linter in CI**
   - Impact: Catch security anti-patterns
   - Effort: Low (30 minutes)

4. **Add file size limits to file operations**
   - Impact: Prevent resource exhaustion
   - Effort: Low (1-2 hours)

### Medium Priority (This Month)

5. **Create centralized validation utilities**
   - Impact: Consistent input validation
   - Effort: Medium (4-6 hours)

6. **Create SECURITY.md**
   - Impact: Clear vulnerability reporting process
   - Effort: Low (1 hour)

7. **Add security-focused tests**
   - Impact: Prevent security regressions
   - Effort: Medium (6-8 hours)

---

## Conclusion

AffineDrift has **good baseline security** due to its nature as a static site generator with no runtime user input or network operations. However, the **build tooling has input validation gaps** that could be exploited in development or CI/CD environments.

**Strengths:**
- ✅ No hardcoded secrets
- ✅ No command injection vectors
- ✅ No unsafe deserialization
- ✅ Appropriate `.gitignore` configuration

**Weaknesses:**
- ⚠️ No automated dependency vulnerability scanning
- ⚠️ Path traversal risks in file path handling
- ⚠️ Inconsistent input validation
- ⚠️ Bandit installed but not executed

**Overall:** The security risks are **manageable** and mostly limited to development/build environments. Implementing the recommended fixes would elevate the security posture from **B (Good)** to **A (Excellent)**.

**Next Steps:**
1. Implement dependency scanning (48 hours)
2. Fix path traversal vulnerabilities (48 hours)
3. Add comprehensive input validation (2 weeks)
4. Create security documentation (6 weeks)

---

**Assessment I Complete**
*Cross-reference: See Assessment F for deployment security, Assessment B for code quality*
