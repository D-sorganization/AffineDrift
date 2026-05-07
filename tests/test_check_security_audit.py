"""Tests for the security input sanitization audit script.

Verifies that the audit script correctly detects security anti-patterns
and avoids false positives for known-safe patterns.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure scripts package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.check_security_audit import (
    _check_credential_patterns,
    _check_security_patterns,
    audit_file,
    is_exempt,
)


class TestSecurityPatternDetection:
    """Tests for security anti-pattern detection."""

    def _check_line(self, line: str, file_name: str = "test_module.py") -> list[dict]:
        """Helper to check a single line against security patterns."""
        path = Path(file_name)
        return _check_security_patterns(path, 1, line)

    def test_shell_true_detected(self) -> None:
        findings = self._check_line('subprocess.run(["ls"], shell=True)', "test_module.py")
        assert len(findings) == 1
        assert findings[0]["severity"] == "HIGH"
        assert "shell=True" in findings[0]["description"]

    def test_shell_false_not_detected(self) -> None:
        findings = self._check_line('subprocess.run(["ls"], shell=False)', "test_module.py")
        assert findings == []

    def test_eval_builtin_detected(self) -> None:
        findings = self._check_line("result = eval(user_input)", "test_module.py")
        assert len(findings) == 1
        assert "eval()" in findings[0]["description"]

    def test_method_eval_not_detected(self) -> None:
        """evaluator.eval() is a method call, not Python built-in eval()."""
        findings = self._check_line("result = evaluator.eval(expression)", "test_module.py")
        assert findings == []

    def test_exec_builtin_detected(self) -> None:
        findings = self._check_line("exec(code_string)", "test_module.py")
        assert len(findings) == 1
        assert "exec()" in findings[0]["description"]

    def test_qt_exec_not_detected(self) -> None:
        """QDialog.exec() and app.exec() are Qt methods, not Python built-in exec()."""
        assert _check_security_patterns(Path("qt_window.py"), 1, "return app.exec()") == []
        assert _check_security_patterns(Path("qt_window.py"), 1, "dialog.exec()") == []

    def test_ssl_verify_false_detected(self) -> None:
        findings = self._check_line("requests.get(url, verify=False)", "test_module.py")
        assert len(findings) == 1
        assert "SSL" in findings[0]["description"]

    def test_nosec_suppresses_finding(self) -> None:
        findings = self._check_line("subprocess.run(cmd, shell=True)  # nosec", "test_module.py")
        assert findings == []

    def test_os_system_detected(self) -> None:
        findings = self._check_line('os.system("ls -la")', "test_module.py")
        assert len(findings) == 1
        assert findings[0]["severity"] == "MEDIUM"

    def test_pickle_load_detected(self) -> None:
        findings = self._check_line("data = pickle.load(f)", "test_module.py")
        assert len(findings) == 1
        assert findings[0]["severity"] == "MEDIUM"

    def test_comment_line_skipped(self) -> None:
        """Lines starting with # should not be checked."""
        # We test this through audit_file which skips comment lines
        tmp = Path("_test_sec_tmp.py")
        tmp.write_text("# subprocess.run(cmd, shell=True)\n")
        try:
            findings = audit_file(tmp)
            assert findings == []
        finally:
            tmp.unlink(missing_ok=True)


class TestCredentialPatternDetection:
    """Tests for hardcoded credential detection."""

    def _check_cred_line(self, line: str, file_name: str = "module.py") -> list[dict]:
        stripped = line.strip()
        return _check_credential_patterns(Path(file_name), 1, line, stripped)

    def test_hardcoded_password_detected(self) -> None:
        findings = self._check_cred_line('password = "s3cr3tP@ss"')
        assert len(findings) == 1
        assert findings[0]["severity"] == "CRITICAL"
        assert findings[0]["code"] == "[REDACTED]"

    def test_hardcoded_github_token_detected(self) -> None:
        token = "ghp_" + "A" * 36
        findings = self._check_cred_line(f'token = "{token}"')
        assert len(findings) >= 1

    def test_example_keyword_skips_finding(self) -> None:
        findings = self._check_cred_line('password = "example_password_here"')
        assert findings == []

    def test_test_files_skipped(self) -> None:
        """Credential patterns should not be checked in test files."""
        findings = self._check_cred_line('password = "test_password"', file_name="test_auth.py")
        assert findings == []

    def test_comment_line_not_flagged(self) -> None:
        findings = self._check_cred_line('# password = "secret123"')
        assert findings == []


class TestExemptions:
    """Tests for exemption handling."""

    def test_link_checker_exempt_from_ssl(self) -> None:
        path = Path("scripts/link-checker.py")
        assert is_exempt(path, "SSL verification disabled") is True

    def test_link_checker_not_exempt_from_other(self) -> None:
        path = Path("scripts/link-checker.py")
        assert is_exempt(path, "shell=True in subprocess") is False

    def test_security_audit_itself_exempt(self) -> None:
        path = Path("scripts/check_security_audit.py")
        assert is_exempt(path, "any description") is True

    def test_unknown_file_not_exempt(self) -> None:
        path = Path("src/my_module.py")
        assert is_exempt(path, "SSL verification disabled") is False


class TestAuditIntegration:
    """Integration tests using temporary files."""

    def test_clean_file_passes(self, tmp_path: Path) -> None:
        f = tmp_path / "clean.py"
        f.write_text("import subprocess\n" 'result = subprocess.run(["ls"], capture_output=True)\n')
        findings = audit_file(f)
        assert findings == []

    def test_unreadable_file_returns_error(self, tmp_path: Path) -> None:
        f = tmp_path / "nonexistent.py"
        findings = audit_file(f)
        assert len(findings) == 1
        assert findings[0]["severity"] == "ERROR"
