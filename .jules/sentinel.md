# Sentinel's Journal

## 2024-05-23 - Unsanitized HTML Injection in Custom Build Script
**Vulnerability:** The `build-html.py` script injected `title` and `description` from `.qmd` YAML frontmatter directly into the HTML template without escaping. This allowed Cross-Site Scripting (XSS) via malicious metadata in source files.
**Learning:** Custom build scripts for static sites often lack the automatic sanitization features present in mature frameworks like Quarto or Jekyll. Input from source files (even "trusted" ones) should still be sanitized to prevent accidental markup breakage or injection.
**Prevention:** Always use `html.escape()` when injecting strings into HTML templates, even for build-time tools. Added strict typing and linting checks to the script.

## 2026-01-20 - Security Audit

**Scan Results:**
- Dependencies: 0 vulnerabilities (H/M/L)
- Code Analysis: 1 issue (Medium), 12 issues (Low) - Excluding test asserts
- Pattern Scan: Skipped (Tool installation failure)

**Issues Created:** #1
**Deferred:**
- `tools/verify_images.py`: S310 finding matches policy exception for verification tools, but flagged for manual verification.

**Low Severity Findings:**
- Subprocess usage detected (B404, B603, B607) in multiple build/utility scripts:
    - `build-html.py`
    - `scripts/create_issues_from_assessment.py`
    - `scripts/generate_sitemap.py`
    - `tools/matlab_utilities/scripts/matlab_quality_check.py`
- Action: Review to ensure inputs are trusted.

## 2026-01-21 - Security Audit

**Scan Results:**
- Dependencies: 0 vulnerabilities (H/M/L)
- Code Analysis: 1 issue (Medium), 12 issues (Low) - Excluding test asserts
- Pattern Scan: N/A (Report missing)

**Issues Created:** .jules/security_issues/ISSUE_S310_verify_images.md
**Deferred:** None

**Low Severity Findings:**
- Subprocess usage detected (B404, B603, B607) in multiple build/utility scripts:
    - `build-html.py`
    - `scripts/create_issues_from_assessment.py`
    - `scripts/generate_sitemap.py`
    - `tools/matlab_utilities/scripts/matlab_quality_check.py`
- Action: Review to ensure inputs are trusted.
