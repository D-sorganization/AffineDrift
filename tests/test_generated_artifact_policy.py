from __future__ import annotations

from pathlib import Path

from scripts.check_generated_artifact_policy import (
    GeneratedArtifactPolicy,
    load_policy,
    validate_policy,
)


def test_generated_site_artifacts_are_documented_and_ignored() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    policy = load_policy(repo_root)
    assert "site_libs/" in policy.generated_roots
    assert "/site_libs/" in (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert validate_policy(repo_root, policy) == []


def test_policy_rejects_generated_root_in_source_quality_budget() -> None:
    policy = GeneratedArtifactPolicy(
        generated_roots=("site_libs/",),
        source_quality_include_roots=("src", "site_libs"),
    )

    errors = validate_policy(Path.cwd(), policy)

    assert errors == ["generated root site_libs/ must not be in source-quality include roots"]
