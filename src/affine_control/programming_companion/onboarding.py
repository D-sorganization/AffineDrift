"""Governed onboarding and verification contracts for Programming Companion (ISSUE-4024).

Provides typed constants and helpers for verified UpstreamDrift installation
and execution entrypoints adhering to DbC, LoD, and DRY design principles.
"""

from __future__ import annotations

from dataclasses import dataclass

CANONICAL_VERIFY_SCRIPT: str = "scripts/ci/verify_installation.py"
CANONICAL_WORKFLOW_ID: str = "installation-verification"


@dataclass(frozen=True)
class OnboardingEntrypoint:
    """A governed onboarding or verification entrypoint."""

    name: str
    command: str
    description: str


def get_verified_onboarding_entrypoints() -> list[OnboardingEntrypoint]:
    """Return the list of verified onboarding and verification entrypoints."""
    return [
        OnboardingEntrypoint(
            name="CI Installation Verification Entrypoint",
            command=f"python {CANONICAL_VERIFY_SCRIPT}",
            description="Base clean-environment installation and dependency verification script.",
        ),
        OnboardingEntrypoint(
            name="Governed Installation Verification Workflow",
            command=(
                "python -m scripts.companion_workflows execute "
                f"--workflow-id {CANONICAL_WORKFLOW_ID}"
            ),
            description="Governed workflow verifying full engine installation and exit code 0.",
        ),
    ]
