"""Tests for CSS architecture boundary checks."""

from pathlib import Path

from scripts.check_css_architecture import check_rules


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_check_rules_passes_for_valid_modular_imports(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/css_architecture_rules.json",
        """
        {
          "root_stylesheet": "styles.css",
          "required_root_imports": ["css/a.css", "css/b.css"],
          "allowed_root_import_prefixes": ["css/"],
          "feature_css_glob": "css/*.css",
          "exclude_feature_css": []
        }
        """,
    )
    _write(tmp_path / "styles.css", '@import url("css/a.css");\n@import url("css/b.css");\n')
    _write(tmp_path / "css/a.css", ".a { color: red; }\n")
    _write(tmp_path / "css/b.css", ".b { color: blue; }\n")

    assert check_rules(tmp_path) == []


def test_check_rules_flags_missing_required_and_nested_import(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/css_architecture_rules.json",
        """
        {
          "root_stylesheet": "styles.css",
          "required_root_imports": ["css/a.css", "css/b.css"],
          "allowed_root_import_prefixes": ["css/"],
          "feature_css_glob": "css/*.css",
          "exclude_feature_css": []
        }
        """,
    )
    _write(tmp_path / "styles.css", '@import url("css/a.css");\n')
    _write(tmp_path / "css/a.css", '@import url("css/other.css");\n.a { color: red; }\n')

    violations = check_rules(tmp_path)
    assert len(violations) == 2
    assert "missing required import" in "\n".join(violations)
    assert "must not contain @import" in "\n".join(violations)
