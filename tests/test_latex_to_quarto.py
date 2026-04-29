"""Tests for the LaTeX-to-Quarto conversion helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.tools.latex_to_quarto import (
    _build_yaml_frontmatter,
    latex_to_quarto_md,
    main,
    prompt_for_files,
)


def test_build_yaml_frontmatter_includes_optional_fields() -> None:
    """YAML frontmatter should include ToC and abstract when requested."""
    yaml = _build_yaml_frontmatter("Test Title", toc=True, abstract="Line one\nLine two")

    assert 'title: "Test Title"' in yaml
    assert "toc: true" in yaml
    assert "abstract: |" in yaml
    assert "  Line one" in yaml


def test_latex_to_quarto_md_converts_sections_and_toc() -> None:
    """LaTeX document structure should map cleanly into Quarto markdown."""
    tex = r"""
    \title{Affine Drift}
    \begin{document}
    \maketitle
    \tableofcontents
    \begin{abstract}
    Short summary.
    \end{abstract}
    \section{Intro}
    Body text.
    \subsection{Detail}
    More text.
    \end{document}
    """

    qmd, original_wc, new_wc = latex_to_quarto_md(tex, "Fallback")

    assert 'title: "Affine Drift"' in qmd
    assert "toc: true" in qmd
    assert "# Intro" in qmd
    assert "## Detail" in qmd
    assert original_wc > 0
    assert new_wc > 0


def test_main_writes_converted_output(tmp_path: Path) -> None:
    """CLI main should convert supplied TeX files into sibling QMD files."""
    tex_path = tmp_path / "article.tex"
    tex_path.write_text(r"\begin{document}\section{Intro}Hello\end{document}", encoding="utf-8")

    with patch("sys.argv", ["latex_to_quarto.py", str(tex_path)]):
        main()

    qmd_path = tex_path.with_suffix(".qmd")
    assert qmd_path.exists()
    assert "# Intro" in qmd_path.read_text(encoding="utf-8")


def test_prompt_for_files_exits_without_tkinter() -> None:
    """GUI fallback should exit cleanly when tkinter is unavailable."""
    import builtins

    original_import = builtins.__import__

    def _raising_import(name, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name == "tkinter":
            raise ImportError("tk unavailable")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=_raising_import):
        with pytest.raises(SystemExit):
            prompt_for_files()


def test_prompt_for_files_returns_selected_paths() -> None:
    """GUI fallback should normalize selected file paths to Path instances."""
    mock_root = MagicMock()
    mock_dialog = MagicMock()
    mock_dialog.askopenfilenames.return_value = ("/tmp/a.tex", "/tmp/b.tex")  # nosec B108
    mock_tk_module = MagicMock()
    mock_tk_module.Tk.return_value = mock_root
    mock_tk_module.filedialog = mock_dialog

    module_overrides = {
        "tkinter": mock_tk_module,
        "tkinter.filedialog": mock_dialog,
    }

    with patch.dict(sys.modules, module_overrides):
        paths = prompt_for_files()

    assert paths == [Path("/tmp/a.tex"), Path("/tmp/b.tex")]  # nosec B108
