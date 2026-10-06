"""Protect the WEB-11.6 symbol hover references (#4584).

1. NOTATION.md's marked equation-symbol table is the single source; the
   generated ``data/symbol_references.json`` stays current with it.
2. The parser fails closed on malformed tables (Design by Contract).
3. Every ``\\symref{key}{tex}`` used in site sources names a registered symbol.
4. Opt-in per page: ``symbol-hover: true`` in front matter, and only opted-in
   pages use ``\\symref``.
5. Rendered through Quarto, opted-in pages get MathJax ``\\class`` hooks plus a
   native ``<details>`` symbol list outside the aria-hidden math, and pages that
   do not opt in get the plain TeX (skipped when Quarto is not installed).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from src.tools.symbol_references import (
    REGISTRY_PATH,
    SymbolReference,
    parse_symbol_table,
    render_registry,
)

ROOT = Path(__file__).resolve().parents[1]
NOTATION = ROOT / "NOTATION.md"
FILTER = ROOT / "scripts" / "filters" / "symbol-hover.lua"
SCRIPT = ROOT / "js" / "symbol-hover.js"
STYLE = ROOT / "css" / "components" / "symbol-hover.css"
ADOPTER = ROOT / "articles" / "theory-part1.qmd"
#: The symbols named by the issue, plus gravity and the actuation matrix that
#: appear in the same theory Part 1 force balance.
REQUIRED_KEYS = {"x", "f", "G", "u", "M", "C", "g", "B"}
SYMREF_RE = re.compile(r"\\symref\{([^{}]*)\}")
_EXCLUDED_DIRS = {"node_modules", "_site", ".quarto", ".git", "docs"}
_TABLE = (
    "<!-- SYMBOL-REFERENCES:START -->\n\n"
    "| Key | Symbol | Name | Definition |\n"
    "| --- | --- | --- | --- |\n"
    "{rows}\n\n"
    "<!-- SYMBOL-REFERENCES:END -->\n"
)


def _table(*rows: str) -> str:
    return _TABLE.format(rows="\n".join(rows))


def _quarto() -> str | None:
    found = shutil.which("quarto")
    if found:
        return found
    bundled = (
        Path(os.environ.get("ProgramFiles", "")) / "Positron/resources/app/quarto/bin/quarto.exe"
    )
    return str(bundled) if bundled.is_file() else None


def _site_sources() -> list[Path]:
    return [
        path
        for suffix in ("*.qmd", "*.md")
        for path in ROOT.rglob(suffix)
        if not _EXCLUDED_DIRS.intersection(path.relative_to(ROOT).parts)
    ]


def _front_matter(text: str) -> dict[str, object]:
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    loaded = yaml.safe_load(block)
    return loaded if isinstance(loaded, dict) else {}


def test_parse_reads_key_tex_name_and_definition() -> None:
    refs = parse_symbol_table(
        _table(
            "| `f` | $f(x)$ | Drift f(x) | Complete autonomous drift. |",
            "| `C` | $C(q,\\dot q)$ | Coriolis matrix C(q, q-dot) | Velocity-product loads. |",
        )
    )
    assert refs == (
        SymbolReference("f", "f(x)", "Drift f(x)", "Complete autonomous drift."),
        SymbolReference(
            "C", "C(q,\\dot q)", "Coriolis matrix C(q, q-dot)", "Velocity-product loads."
        ),
    )


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("no markers here", "markers"),
        (_table(), "no symbol rows"),
        (_table("| `f` | $f$ | Drift |"), "four cells"),
        (_table("| `f` | $f$ | Drift | One. |", "| `f` | $f$ | Drift | Two. |"), "duplicate"),
        (_table("| `f-1` | $f$ | Drift | One. |"), "key"),
        (_table("| `f` | f | Drift | One. |"), "TeX"),
        (_table("| `f` | $f$ |  | One. |"), "empty"),
    ],
)
def test_parse_fails_closed_on_malformed_tables(text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_symbol_table(text)


def test_notation_table_defines_the_required_symbols() -> None:
    refs = parse_symbol_table(NOTATION.read_text(encoding="utf-8"))
    assert REQUIRED_KEYS <= {ref.key for ref in refs}


def test_registry_is_current() -> None:
    expected = render_registry(parse_symbol_table(NOTATION.read_text(encoding="utf-8")))
    assert (
        REGISTRY_PATH.read_text(encoding="utf-8") == expected
    ), "run: python -m scripts.generate_symbol_references"


def test_registry_links_to_the_rendered_notation_section() -> None:
    assert '"anchor": "/pages/notation.html#equation-symbol-definitions"' in render_registry(())
    assert "### Equation Symbol Definitions" in NOTATION.read_text(encoding="utf-8")


def test_every_symref_names_a_registered_symbol() -> None:
    keys = {ref.key for ref in parse_symbol_table(NOTATION.read_text(encoding="utf-8"))}
    unknown = [
        (path.relative_to(ROOT).as_posix(), key)
        for path in _site_sources()
        for key in SYMREF_RE.findall(path.read_text(encoding="utf-8", errors="ignore"))
        if key not in keys and key != "key"
    ]
    assert unknown == []


def test_only_opted_in_pages_use_symref() -> None:
    offenders = []
    for path in _site_sources():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix == ".qmd" and SYMREF_RE.search(text):
            if _front_matter(text).get("symbol-hover") is not True:
                offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == [], "add `symbol-hover: true` to the front matter"


def test_theory_part_one_adopts_symbol_hover() -> None:
    text = ADOPTER.read_text(encoding="utf-8")
    assert _front_matter(text).get("symbol-hover") is True
    assert REQUIRED_KEYS <= set(SYMREF_RE.findall(text))


def test_filter_is_registered_and_assets_are_self_hosted() -> None:
    config = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
    assert "- scripts/filters/symbol-hover.lua" in config
    assert '@import url("css/components/symbol-hover.css");' in (ROOT / "styles.css").read_text(
        encoding="utf-8"
    )
    for path in (FILTER, SCRIPT, STYLE):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"https?://", text), f"{path.name} references a remote URL"
    # A few kilobytes at most: the feature must not move the MathJax budget.
    assert SCRIPT.stat().st_size + STYLE.stat().st_size <= 8 * 1024


def _render(tmp_path: Path, front_matter: str, body: str) -> str:
    quarto = _quarto()
    if quarto is None:
        pytest.skip("Quarto is required for the symbol-hover filter integration check")
    qmd = tmp_path / "page.qmd"
    qmd.write_text(
        f"---\ntitle: Symbols\nformat: html\nfilters:\n  - {FILTER.as_posix()}\n"
        f"{front_matter}---\n\n{body}\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [quarto, "render", str(qmd), "--to", "html"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return qmd.with_suffix(".html").read_text(encoding="utf-8")


BODY = "$$\\dot x=\\symref{f}{f(x)}+\\symref{G}{G(x)}\\,\\symref{u}{u}$$\n"


@pytest.mark.integration
def test_opted_in_page_gets_class_hooks_and_an_accessible_symbol_list(tmp_path: Path) -> None:
    html = _render(tmp_path, "symbol-hover: true\n", BODY)
    assert "\\class{symref symref--f}{f(x)}" in html
    assert "\\class{symref symref--G}{G(x)}" in html
    assert "\\symref" not in html
    details = re.search(r'<details class="symbol-refs">.*?</details>', html, re.S)
    assert details is not None
    block = details.group(0)
    assert "<summary>Symbols in this equation</summary>" in block
    assert (
        block.index('data-symref="f"')
        < block.index('data-symref="G"')
        < block.index('data-symref="u"')
    )
    assert "/pages/notation.html#equation-symbol-definitions" in block
    assert len(re.findall(r'<script src="/js/symbol-hover\.js" defer(="")?>', html)) == 1


@pytest.mark.integration
def test_page_without_opt_in_renders_plain_tex(tmp_path: Path) -> None:
    html = _render(tmp_path, "", BODY)
    # The group braces keep a superscript on the whole symbol, as \class does.
    assert "\\dot x={f(x)}+{G(x)}\\,{u}" in html
    assert "symref" not in html
    assert "symbol-hover.js" not in html
