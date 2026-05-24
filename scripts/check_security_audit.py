"""Security input sanitization audit for AffineDrift source code.

Implements SEC-001: Input Sanitization Audit.

Checks for common security anti-patterns in Python source and scripts:
- `shell=True` in subprocess calls (command injection risk)
- `eval()` usage (code injection risk)
- Hardcoded credentials patterns
- Unsafe XML parsing without defusedxml
- `verify=False` in requests (SSL verification disabled)
- `os.system()` calls (prefer subprocess)

Exit codes:
  0: All checks passed
  1: Security issues found (blocking)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout

# Directories to scan for Python files
SCAN_DIRS = ["src", "scripts"]

# Directories to ignore completely
IGNORE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    ".venv",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    ".mypy_cache",
}

# Security patterns that indicate a potential vulnerability
# Each entry: (pattern, severity, description, exception_marker)
SECURITY_PATTERNS: list[tuple[re.Pattern[str], str, str, str | None]] = [
    (
        re.compile(
            r"(?<![.\w])\bsubprocess\.(run|call|Popen|check_output|check_call)\b.*shell\s*=\s*True"
        ),
        "HIGH",
        "shell=True in subprocess call — command injection risk if args contain user input",
        "# nosec",
    ),
    (
        re.compile(r"\bos\.system\s*\("),
        "MEDIUM",
        "os.system() — prefer subprocess.run() with shell=False for security and portability",
        "# nosec",
    ),
    (
        # Match Python built-in eval() — not method calls like evaluator.eval() or obj.eval()
        re.compile(r"(?<![.\w])\beval\s*\("),
        "HIGH",
        "eval() usage — code injection risk if input is user-controlled",
        "# nosec",
    ),
    (
        # Match Python built-in exec() — not method calls like app.exec() or dialog.exec()
        re.compile(r"(?<![.\w])\bexec\s*\("),
        "HIGH",
        "exec() usage — code injection risk if input is user-controlled",
        "# nosec",
    ),
    (
        re.compile(r"verify\s*=\s*False"),
        "HIGH",
        "SSL verification disabled (verify=False) — MITM attack risk",
        "# nosec",
    ),
    (
        re.compile(r"\bpickle\.load[s]?\s*\("),
        "MEDIUM",
        "pickle.load() — deserialization of untrusted data is a security risk",
        "# nosec",
    ),
    (
        re.compile(r"\bET\.fromstring\s*\(|ElementTree\.fromstring\s*\("),
        "LOW",
        "xml.etree.ElementTree.fromstring() — use defusedxml for untrusted XML input",
        "# noqa: S314 -- reason: false positive pattern definition in audit script",
    ),
]

# Patterns for hardcoded credential detection
CREDENTIAL_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{4,}['\"]"), "Hardcoded password"),
    (re.compile(r"(?i)(api_key|apikey|api-key)\s*=\s*['\"][^'\"]{8,}['\"]"), "Hardcoded API key"),
    (re.compile(r"(?i)(secret|token)\s*=\s*['\"][^'\"]{8,}['\"]"), "Hardcoded secret/token"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "GitHub Personal Access Token"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "OpenAI API key"),
]

# Files explicitly exempted from specific checks (relative path patterns)
EXEMPTIONS: dict[str, list[str]] = {
    # link-checker.py uses urlopen for link validation — trusted URLs only
    "scripts/link-checker.py": ["SSL verification disabled"],
    # line_checks.py contains eval() only in string literals describing MATLAB anti-patterns,
    # not as actual Python eval() usage
    "src/tools/matlab_utilities/scripts/line_checks.py": ["eval() usage"],
    # check_security_audit.py itself contains the pattern strings
    "scripts/check_security_audit.py": [],
}


def find_python_files(scan_dirs: list[str]) -> list[Path]:
    """Find all Python files in scan directories, excluding ignored dirs."""
    files: list[Path] = []
    root = Path(".")
    for dir_name in scan_dirs:
        scan_path = root / dir_name
        if not scan_path.is_dir():
            continue
        for path in scan_path.rglob("*.py"):
            if not any(part in IGNORE_DIRS for part in path.parts):
                files.append(path)
    return sorted(files)


def is_exempt(file_path: Path, description: str) -> bool:
    """Check if a finding is explicitly exempted."""
    rel_path = str(file_path).replace("\\", "/")
    for exempt_path, exempt_descriptions in EXEMPTIONS.items():
        if rel_path.endswith(exempt_path):
            if not exempt_descriptions:  # empty list means exempt from all checks
                return True
            return any(desc in description for desc in exempt_descriptions)
    return False


def _check_security_patterns(file_path: Path, line_num: int, line: str) -> list[dict[str, str]]:
    """Check a single line for security anti-patterns."""
    findings: list[dict[str, str]] = []
    for pattern, severity, description, exception_marker in SECURITY_PATTERNS:
        if not pattern.search(line):
            continue
        if exception_marker and exception_marker in line:
            continue
        if is_exempt(file_path, description):
            continue
        findings.append(
            {
                "file": str(file_path),
                "line": str(line_num),
                "severity": severity,
                "description": description,
                "code": line.strip()[:120],
            }
        )
    return findings


def _check_credential_patterns(
    file_path: Path, line_num: int, line: str, stripped: str
) -> list[dict[str, str]]:
    """Check a single line for hardcoded credentials."""
    findings: list[dict[str, str]] = []
    if "test_" in file_path.name:
        return findings
    for cred_pattern, cred_description in CREDENTIAL_PATTERNS:
        if not cred_pattern.search(line):
            continue
        if stripped.startswith(("#", '"""', "'''")):
            continue
        if any(
            kw in line.lower()
            for kw in ["example", "placeholder", "dummy", "fake", "mock", "redacted"]
        ):
            continue
        findings.append(
            {
                "file": str(file_path),
                "line": str(line_num),
                "severity": "CRITICAL",
                "description": cred_description,
                "code": "[REDACTED]",  # don't echo credential values
            }
        )
    return findings


def audit_file(file_path: Path) -> list[dict[str, str]]:
    """Audit a single Python file for security issues."""
    findings: list[dict[str, str]] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        findings.append(
            {
                "file": str(file_path),
                "line": "?",
                "severity": "ERROR",
                "description": f"Cannot read file: {e}",
            }
        )
        return findings

    for line_num, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        findings.extend(_check_security_patterns(file_path, line_num, line))
        findings.extend(_check_credential_patterns(file_path, line_num, line, stripped))

    return findings


def main() -> int:
    """Run the security input sanitization audit."""
    files = find_python_files(SCAN_DIRS)
    if not files:
        write_stdout("No Python files found to audit.\n")
        return 0

    all_findings: list[dict[str, str]] = []
    for file_path in files:
        all_findings.extend(audit_file(file_path))

    # Separate by severity
    critical = [f for f in all_findings if f["severity"] == "CRITICAL"]
    high = [f for f in all_findings if f["severity"] == "HIGH"]
    medium = [f for f in all_findings if f["severity"] == "MEDIUM"]
    low = [f for f in all_findings if f["severity"] == "LOW"]

    # Report findings
    if all_findings:
        for finding in all_findings:
            severity = finding["severity"]
            file_loc = f"{finding['file']}:{finding['line']}"
            desc = finding["description"]
            code = finding.get("code", "")
            write_stdout(f"[{severity}] {file_loc}: {desc}\n")
            if code:
                write_stdout(f"       {code}\n")

    # Summary
    total = len(all_findings)
    blocking = len(critical) + len(high)
    write_stdout(
        f"\nSecurity audit: {len(files)} files scanned, "
        f"{total} findings ({len(critical)} CRITICAL, {len(high)} HIGH, "
        f"{len(medium)} MEDIUM, {len(low)} LOW)\n"
    )

    if critical:
        write_stderr("CRITICAL findings must be resolved before merging.\n")
        return 1

    if high:
        write_stderr(
            f"{len(high)} HIGH severity findings detected. "
            "Review each and add '# nosec' with justification if accepted.\n"
        )
        return 1

    if medium or low:
        write_stderr(
            f"{len(medium)} MEDIUM, {len(low)} LOW severity findings (non-blocking).\n"
            "Review and address in the next sprint.\n"
        )
        # Non-blocking for medium/low

    if blocking == 0:
        write_stdout("Security audit passed.\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
