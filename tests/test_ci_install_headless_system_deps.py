"""Contract tests for the shared CI apt bootstrap used by static-checks and E2E."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "ci" / "install_headless_system_deps.sh"

REQUIRED_SNIPPETS = (
    "DPkg::Lock::Timeout",
    "dl.google.com",
    "libasound2t64",
    "libasound2",
    "libgl1",
    "APT_INSTALL_OK",
)


def test_install_headless_system_deps_script_exists() -> None:
    assert SCRIPT.is_file(), f"missing CI bootstrap script: {SCRIPT}"


def test_install_headless_system_deps_script_contract() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for snippet in REQUIRED_SNIPPETS:
        assert snippet in text, f"bootstrap script must mention {snippet!r}"


def test_ci_standard_invokes_shared_bootstrap() -> None:
    workflow = REPO_ROOT / ".github" / "workflows" / "ci-standard.yml"
    text = workflow.read_text(encoding="utf-8")
    assert text.count("bash scripts/ci/install_headless_system_deps.sh") >= 2
