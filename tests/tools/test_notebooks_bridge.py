"""Tests for notebooks_bridge.py"""
from pathlib import Path
from src.tools.notebooks_bridge import (
    ChapterRef,
    _slug,
    _notebook_rel_path,
    _build_notebook,
    extract_chapters_from_text,
    _has_tutorial_title,
    _parse_source_ref,
)

def test_slug_generation():
    assert _slug("Hello World!") == "hello_world"
    assert _slug("  Some--Text  ") == "some_text"
    assert _slug("!@#$") == "chapter" # fallback if empty

def test_notebook_rel_path():
    ref = ChapterRef(
        volume=1,
        chapter=4,
        anchor="book1-ch4",
        title="My Chapter",
        source_file=Path("dummy.qmd")
    )
    path = _notebook_rel_path(ref)
    assert path == Path("notebooks/geometry_of_motion/vol1_ch4_my_chapter.ipynb")

def test_build_notebook():
    ref = ChapterRef(
        volume=1,
        chapter=4,
        anchor="book1-ch4",
        title="My Chapter",
        source_file=Path("dummy.qmd")
    )
    nb = _build_notebook(ref)
    assert nb["nbformat"] == 4
    assert len(nb["cells"]) == 2
    
    # Check tutorial title
    assert _has_tutorial_title(nb) is True

def test_extract_chapters_from_text():
    text = \"\"\"Some intro text.
## Chapter 1: Introduction {#book1-ch1}
Content here.
## Chapter 2: Foundations {#book1-ch2}
\"\"\"
    chapters = extract_chapters_from_text(text, source_file=Path("dummy.qmd"))
    assert len(chapters) == 2
    assert chapters[0].volume == 1
    assert chapters[0].chapter == 1
    assert chapters[0].anchor == "book1-ch1"
    assert chapters[0].title == "Introduction"
    assert chapters[1].chapter == 2

def test_parse_source_ref():
    path, anchor = _parse_source_ref("file.qmd#anchor")
    assert path == Path("file.qmd")
    assert anchor == "anchor"
    
    path, anchor = _parse_source_ref("file.qmd")
    assert path == Path("file.qmd")
    assert anchor is None

def test_has_tutorial_title_invalid():
    assert _has_tutorial_title({}) is False
    assert _has_tutorial_title({"cells": []}) is False
    assert _has_tutorial_title({"cells": [{"cell_type": "code"}]}) is False
