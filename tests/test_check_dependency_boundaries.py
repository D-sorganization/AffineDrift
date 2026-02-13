"""Tests for dependency boundary checks."""

from pathlib import Path

from scripts.check_dependency_boundaries import check_rules


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_check_rules_passes_for_allowed_imports(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/dependency_boundaries.json",
        """
        {
          "python_root": "src",
          "rules": [{"source_prefix": "src.core", "forbidden_prefixes": ["src.tools"]}],
          "exclude_substrings": []
        }
        """,
    )
    _write(tmp_path / "src/core/example.py", "from src.affine_control.ddp import DDPSolver\n")
    assert check_rules(tmp_path) == []


def test_check_rules_flags_forbidden_import(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/dependency_boundaries.json",
        """
        {
          "python_root": "src",
          "rules": [{"source_prefix": "src.core", "forbidden_prefixes": ["src.tools"]}],
          "exclude_substrings": []
        }
        """,
    )
    _write(
        tmp_path / "src/core/example.py",
        "from src.tools.update_navigation import update_navigation\n",
    )

    violations = check_rules(tmp_path)
    assert len(violations) == 1
    assert "must not import" in violations[0]
