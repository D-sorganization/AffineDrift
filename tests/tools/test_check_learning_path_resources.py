"""Tests for learning-path and resources regression contracts (#5618)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.check_learning_path_resources import (
    ContractRule,
    Violation,
    check_contract,
    load_contract,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_load_contract_reads_repo_config() -> None:
    contract = load_contract(REPO_ROOT / "config" / "learning_path_resource_contract.yml")
    assert contract.file_rules
    assert contract.global_rules


def test_check_contract_reports_missing_required_substring(tmp_path: Path) -> None:
    target = tmp_path / "resources" / "resources-websites.qmd"
    target.parent.mkdir(parents=True)
    target.write_text("No pinocchio link here.\n", encoding="utf-8")
    rule = ContractRule(
        path=Path("resources/resources-websites.qmd"),
        forbidden=(),
        required=("stack-of-tasks.github.io/pinocchio",),
    )
    violations = check_contract(tmp_path, [rule], global_rules=())
    assert any(v.kind == "missing_required" for v in violations)


def test_check_contract_reports_forbidden_substring(tmp_path: Path) -> None:
    target = tmp_path / "resources" / "resources-websites.qmd"
    target.parent.mkdir(parents=True)
    target.write_text(
        "https://www.pinocchio.org/\nhttps://stack-of-tasks.github.io/pinocchio/\n",
        encoding="utf-8",
    )
    rule = ContractRule(
        path=Path("resources/resources-websites.qmd"),
        forbidden=("pinocchio.org",),
        required=(),
    )
    violations = check_contract(tmp_path, [rule], global_rules=())
    assert violations == [
        Violation(
            path=rule.path,
            kind="forbidden",
            detail="forbidden substring 'pinocchio.org'",
        )
    ]


def test_repository_passes_learning_path_resource_contract() -> None:
    violations = check_contract(
        REPO_ROOT,
        load_contract(REPO_ROOT / "config" / "learning_path_resource_contract.yml").file_rules,
        load_contract(REPO_ROOT / "config" / "learning_path_resource_contract.yml").global_rules,
    )
    assert violations == [], "\n".join(f"{v.path}: {v.kind} — {v.detail}" for v in violations)


def test_main_exits_zero_when_contract_clean() -> None:
    assert main([str(REPO_ROOT)]) == 0


def test_main_exits_nonzero_on_forbidden_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "contract.yml"
    bad = tmp_path / "resources" / "bad.qmd"
    bad.parent.mkdir(parents=True)
    bad.write_text("https://www.pinocchio.org/\n", encoding="utf-8")
    config.write_text(
        yaml.safe_dump(
            {
                "global_rules": [
                    {
                        "globs": ["resources/**/*.qmd"],
                        "forbidden": ["pinocchio.org"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert main(["--config", str(config), str(tmp_path)]) == 1
