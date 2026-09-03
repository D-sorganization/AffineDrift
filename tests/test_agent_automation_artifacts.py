from scripts.check_agent_automation_artifacts import find_forbidden_agent_artifacts


def test_find_forbidden_agent_artifacts_flags_generated_delivery_wrappers():
    paths = [
        ".gaai/project/contexts/backlog/.delivery-locks/GH1633_run.sh",
        ".gaai/project/contexts/backlog/.delivery-locks/GH1633.lock",
        ".gaai/project/contexts/backlog/.delivery-logs/GH1633.log",
        ".claude/settings.local.json",
        ".gaai/core/scripts/delivery-daemon.sh",
    ]

    assert find_forbidden_agent_artifacts(paths) == paths[:4]


def test_find_forbidden_agent_artifacts_allows_static_agent_docs():
    paths = [
        ".claude/skills/lint/SKILL.md",
        ".claude/commands/gaai-status.md",
        ".gaai/core/scripts/delivery-daemon.sh",
    ]

    assert find_forbidden_agent_artifacts(paths) == []


def test_find_forbidden_agent_artifacts_flags_duplicate_agent_and_gaai_artefacts():
    paths = [
        ".agent/skills/lint/SKILL.md",
        ".gaai/project/contexts/artefacts/plans/GH1602.execution-plan.md",
        ".claude/skills/lint/SKILL.md",
    ]

    assert find_forbidden_agent_artifacts(paths) == paths[:2]
