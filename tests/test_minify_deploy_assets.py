"""Tests for deploy-only CSS and JavaScript minification."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from scripts.minify_deploy_assets import minify_css, minify_deploy_assets, minify_js
from scripts.sync_frontend_assets import CANONICAL_JS_NAMES


def test_minify_css_removes_comments_and_extra_whitespace() -> None:
    css = """
    /* comment */
    .card   {
      color :  red ;
      margin : 0 ;
    }
    """

    assert minify_css(css) == ".card{color:red;margin:0}\n"


def test_minify_css_preserves_descendant_space_before_pseudo_class() -> None:
    css = "#quarto-document-content :not(pre) > code { white-space: normal; }"

    assert minify_css(css) == ("#quarto-document-content :not(pre) > code{white-space:normal}\n")


def test_minify_css_preserves_media_ranges_and_calc_operator_spacing() -> None:
    css = """
    @media (width >= 1440px) {
      .grid > .item { width: calc(50% + 1rem); }
    }
    """

    assert minify_css(css) == ("@media (width >= 1440px){.grid > .item{width:calc(50% + 1rem)}}\n")


def test_minify_js_preserves_strings_while_removing_comments() -> None:
    js = """
    const url = "https://example.test/a//b"; // trailing comment
    const label = 'hello world';
    function run () {
      return `${label} /* kept */`;
    }
    """

    minified = minify_js(js)

    assert "trailing comment" not in minified
    assert '"https://example.test/a//b"' in minified
    assert "`" in minified
    assert "const url" in minified
    assert "function run" in minified


def test_minify_deploy_assets_touches_only_site_assets(tmp_path: Path) -> None:
    (tmp_path / "_site" / "js").mkdir(parents=True)
    (tmp_path / "js").mkdir()
    (tmp_path / "_site" / "styles.css").write_text(".x { color: red; }\n", encoding="utf-8")
    (tmp_path / "_site" / "js" / "app.js").write_text("const value = 1; // x\n", encoding="utf-8")
    (tmp_path / "js" / "app.js").write_text("const value = 1; // x\n", encoding="utf-8")

    touched = minify_deploy_assets(tmp_path)

    assert {path.relative_to(tmp_path).as_posix() for path in touched} == {
        "_site/styles.css",
        "_site/js/app.js",
    }
    assert (tmp_path / "_site" / "styles.css").read_text(encoding="utf-8") == ".x{color:red}\n"
    assert (tmp_path / "_site" / "js" / "app.js").read_text(encoding="utf-8") == "const value=1;\n"
    assert (tmp_path / "js" / "app.js").read_text(encoding="utf-8") == "const value = 1; // x\n"


def test_minify_js_preserves_asi_and_newline_semantics() -> None:
    js = """
    const api = factory(root)
    root.item = api
    """
    minified = minify_js(js)
    assert "factory(root)\nroot.item" in minified


def test_minify_js_all_canonical_assets_produce_valid_syntax() -> None:
    node_bin = shutil.which("node")
    assert node_bin is not None, "node executable required for syntax check"

    repo_root = Path(__file__).resolve().parent.parent
    for name in CANONICAL_JS_NAMES:
        src_path = repo_root / "js" / name
        if not src_path.is_file():
            continue
        minified = minify_js(src_path.read_text(encoding="utf-8"))
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tmp:
            tmp.write(minified)
            tmp_path = tmp.name
        try:
            p = subprocess.run([node_bin, "--check", tmp_path], capture_output=True, text=True)
            if p.returncode != 0:
                with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as tmp_mjs:
                    tmp_mjs.write(minified)
                    tmp_mjs_path = tmp_mjs.name
                p2 = subprocess.run(
                    [node_bin, "--check", tmp_mjs_path], capture_output=True, text=True
                )
                Path(tmp_mjs_path).unlink()
                assert p2.returncode == 0, f"{name} minification failed syntax check: {p2.stderr}"
        finally:
            Path(tmp_path).unlink()
