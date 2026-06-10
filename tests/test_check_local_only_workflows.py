"""Tests for the hosted-runner routing CI gate (issue #3230).

Guards scripts/check_local_only_workflows.py — itself a CI enforcement layer
that was previously unverified.
"""

from scripts.check_local_only_workflows import BANNED, scan_workflow_text


class TestScanWorkflowText:
    def test_clean_workflow_has_no_findings(self):
        text = "jobs:\n  build:\n    runs-on: d-sorg-fleet\n"
        assert scan_workflow_text("wf.yml", text) == []

    def test_detects_ubuntu_latest(self):
        text = "jobs:\n  build:\n    runs-on: ubuntu-latest\n"
        findings = scan_workflow_text("wf.yml", text)
        assert len(findings) == 1
        assert "ubuntu-latest" in findings[0]
        assert "wf.yml:3" in findings[0]

    def test_reports_each_banned_token(self):
        text = "runs-on: windows-latest\nlabel: macos-latest\n"
        findings = scan_workflow_text("wf.yml", text)
        assert len(findings) == 2

    def test_every_banned_token_is_detectable(self):
        # Boundary/coverage: each configured token must trigger a finding.
        for token in BANNED:
            findings = scan_workflow_text("wf.yml", f"x: {token}\n")
            assert findings, f"token not detected: {token}"

    def test_empty_text_is_no_op(self):
        assert scan_workflow_text("wf.yml", "") == []
