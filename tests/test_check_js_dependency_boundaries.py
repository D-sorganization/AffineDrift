"""Tests for JavaScript dependency boundary checks."""

from pathlib import Path

from scripts.check_js_dependency_boundaries import check_rules


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_check_rules_passes_for_allowed_js_imports(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/js_dependency_boundaries.json",
        """
        {
          "rules": [
            {"source_prefix": "src/js/", "forbidden_prefixes": ["src/tools/", "scripts/"]}
          ],
          "exclude_substrings": []
        }
        """,
    )
    _write(
        tmp_path / "src/js/main.js",
        'import { initSearch } from "./modules/search.js";\n',
    )
    _write(tmp_path / "src/js/modules/search.js", "export function initSearch() {}\n")
    assert check_rules(tmp_path) == []


def test_check_rules_flags_forbidden_js_import(tmp_path: Path) -> None:
    _write(
        tmp_path / "config/js_dependency_boundaries.json",
        """
        {
          "rules": [
            {"source_prefix": "src/js/", "forbidden_prefixes": ["src/tools/", "scripts/"]}
          ],
          "exclude_substrings": []
        }
        """,
    )
    _write(
        tmp_path / "src/js/main.js",
        'import { doThing } from "../tools/helper.js";\n',
    )
    _write(tmp_path / "src/tools/helper.js", "export function doThing() {}\n")

    violations = check_rules(tmp_path)
    assert len(violations) == 1
    assert "must not import" in violations[0]
