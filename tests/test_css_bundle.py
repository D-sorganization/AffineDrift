"""Tests for the CSS bundler (scripts/bundle_css.py) — issue #3219."""

from pathlib import Path

from scripts.bundle_css import build_bundle, bundle

REPO_ROOT = Path(__file__).resolve().parent.parent


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class TestBundleSynthetic:
    def test_inlines_nested_imports(self, tmp_path):
        _write(tmp_path, "styles.css", '@import "css/a.css";\nbody { color: red; }\n')
        _write(tmp_path, "css/a.css", '@import url("tokens/b.css");\n.a { color: blue; }\n')
        _write(tmp_path, "css/tokens/b.css", ":root { --x: 1px; }\n")

        out = bundle(tmp_path / "styles.css", tmp_path)

        assert "@import" not in out
        assert "--x: 1px;" in out
        assert ".a { color: blue; }" in out
        assert "body { color: red; }" in out

    def test_handles_both_import_syntaxes(self, tmp_path):
        _write(
            tmp_path,
            "styles.css",
            '@import "css/a.css";\n@import url("css/c.css");\n',
        )
        _write(tmp_path, "css/a.css", ".a {}\n")
        _write(tmp_path, "css/c.css", ".c {}\n")

        out = bundle(tmp_path / "styles.css", tmp_path)
        assert ".a {}" in out and ".c {}" in out
        assert "@import" not in out

    def test_remote_import_kept_verbatim(self, tmp_path):
        _write(
            tmp_path,
            "styles.css",
            '@import url("https://fonts.example/x.css");\n.local {}\n',
        )
        out = bundle(tmp_path / "styles.css", tmp_path)
        # Remote imports cannot be inlined and must survive.
        assert "https://fonts.example/x.css" in out

    def test_cycle_does_not_recurse_forever(self, tmp_path):
        _write(tmp_path, "styles.css", '@import "css/a.css";\n')
        _write(tmp_path, "css/a.css", '@import "../styles.css";\n.a {}\n')

        out = bundle(tmp_path / "styles.css", tmp_path)
        assert ".a {}" in out  # terminates


class TestBundleRealStyles:
    def test_repo_bundle_has_no_imports_and_defines_token(self):
        # Acceptance criterion: flattened bundle has zero @import and still
        # defines a token-system variable pulled in transitively.
        out = build_bundle(REPO_ROOT, "styles.css")
        assert "@import" not in out
        assert "--color-primary-dark" in out
