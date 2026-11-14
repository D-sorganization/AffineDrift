from scripts.check_agent_automation_artifacts import find_forbidden_agent_artifacts


def test_find_forbidden_agent_artifacts_flags_local_settings():
    paths = [
        ".claude/settings.local.json",
        ".claude/skills/lint/SKILL.md",
    ]

    assert find_forbidden_agent_artifacts(paths) == paths[:1]


def test_find_forbidden_agent_artifacts_allows_static_agent_docs():
    paths = [
        ".claude/skills/lint/SKILL.md",
        ".claude/settings.json",
    ]

    assert find_forbidden_agent_artifacts(paths) == []


def test_find_forbidden_agent_artifacts_flags_duplicate_agent_directory():
    paths = [
        ".agent/skills/lint/SKILL.md",
        ".claude/skills/lint/SKILL.md",
    ]

    assert find_forbidden_agent_artifacts(paths) == paths[:1]
