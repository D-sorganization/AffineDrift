"""GAAI project rules fence the core ci-watch-and-fix skill (#5293)."""

from __future__ import annotations

from pathlib import Path

RULES = (
    Path(__file__).resolve().parents[1]
    / ".gaai"
    / "project"
    / "contexts"
    / "rules"
    / "project.rules.md"
)


def test_project_rules_fence_ci_watch_and_fix() -> None:
    # The core skill keeps a session alive for CI; the fleet PR lifecycle
    # ends it at PR open, so the project layer fences it (RM #2567).
    text = RULES.read_text(encoding="utf-8")
    assert "invoke the `ci-watch-and-fix` skill" not in text
    assert "Do not run core skill `delivery/ci-watch-and-fix`" in text
    assert "fleet-pr-lifecycle" in text


def test_ci_watch_section_appears_once() -> None:
    text = RULES.read_text(encoding="utf-8")
    assert text.count("## CI Watch (Post-PR)") == 1
