"""Tests for contract coverage checks."""

from pathlib import Path

from scripts.check_contract_coverage import check_rules


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_check_rules_passes_when_required_tokens_present(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/contract_coverage_rules.json",
        """
        {
          "rules": [
            {"path": "scripts/a.py", "required_tokens": ["ensure_existing_file("]}
          ]
        }
        """,
    )
    _write(tmp_path / "scripts/a.py", "from x import ensure_existing_file\nensure_existing_file('a')\n")

    assert check_rules(tmp_path) == []


def test_check_rules_flags_missing_token(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/contract_coverage_rules.json",
        """
        {
          "rules": [
            {"path": "scripts/a.py", "required_tokens": ["ensure_existing_file("]}
          ]
        }
        """,
    )
    _write(tmp_path / "scripts/a.py", "print('no contract')\n")

    violations = check_rules(tmp_path)
    assert len(violations) == 1
    assert "missing contract token" in violations[0]
