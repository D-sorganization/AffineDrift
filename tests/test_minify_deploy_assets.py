"""Tests for deploy-only CSS and JavaScript minification."""

from __future__ import annotations

from pathlib import Path

from scripts.minify_deploy_assets import minify_css, minify_deploy_assets, minify_js


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


def test_minify_deploy_assets_touches_only_docs_assets(tmp_path: Path) -> None:
    (tmp_path / "docs" / "js").mkdir(parents=True)
    (tmp_path / "js").mkdir()
    (tmp_path / "docs" / "styles.css").write_text(".x { color: red; }\n", encoding="utf-8")
    (tmp_path / "docs" / "js" / "app.js").write_text("const value = 1; // x\n", encoding="utf-8")
    (tmp_path / "js" / "app.js").write_text("const value = 1; // x\n", encoding="utf-8")

    touched = minify_deploy_assets(tmp_path)

    assert {path.relative_to(tmp_path).as_posix() for path in touched} == {
        "docs/styles.css",
        "docs/js/app.js",
    }
    assert (tmp_path / "docs" / "styles.css").read_text(encoding="utf-8") == ".x{color:red}\n"
    assert (tmp_path / "docs" / "js" / "app.js").read_text(encoding="utf-8") == "const value=1;\n"
    assert (tmp_path / "js" / "app.js").read_text(encoding="utf-8") == "const value = 1; // x\n"
