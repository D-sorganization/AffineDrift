"""Tests for the hosted-runner routing CI gate (issue #3230).

Guards scripts/check_local_only_workflows.py — itself a CI enforcement layer
that was previously unverified.
"""

from scripts.check_local_only_workflows import (
    BANNED,
    hosted_runners_are_metered,
    scan_workflow_text,
)


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


class TestHostedRunnersAreMetered:
    """Hosted runners are free on public repos, so the ban must not apply there."""

    def test_public_is_not_metered(self):
        assert hosted_runners_are_metered("public") is False

    def test_private_and_internal_are_metered(self):
        assert hosted_runners_are_metered("private") is True
        assert hosted_runners_are_metered("internal") is True

    def test_visibility_is_case_and_whitespace_insensitive(self):
        assert hosted_runners_are_metered("  PUBLIC \n") is False

    def test_unknown_visibility_fails_closed(self):
        # A false failure costs a re-run; a false pass costs a billed month.
        assert hosted_runners_are_metered("") is True
        assert hosted_runners_are_metered("something-else") is True

    def test_reads_environment_by_default(self, monkeypatch):
        monkeypatch.setenv("REPO_VISIBILITY", "public")
        assert hosted_runners_are_metered() is False
        monkeypatch.setenv("REPO_VISIBILITY", "private")
        assert hosted_runners_are_metered() is True
        monkeypatch.delenv("REPO_VISIBILITY")
        assert hosted_runners_are_metered() is True
