import importlib.util
import sys
from pathlib import Path

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load build-html.py
repo_root = Path(__file__).parents[1]
build_html = load_module_from_path("build_html", repo_root / "build-html.py")

def test_extract_html_from_qmd(tmp_path):
    qmd_content = """---
title: "Test Title"
description: "Test Description"
---

```{=html}
<div>Test Content</div>
```
"""
    f = tmp_path / "test.qmd"
    f.write_text(qmd_content)

    title, desc, html_content = build_html.extract_html_from_qmd(f)
    assert title == "Test Title"
    assert desc == "Test Description"
    assert "Test Content" in html_content

def test_extract_html_no_frontmatter(tmp_path):
    qmd_content = "Just some text"
    f = tmp_path / "test_no_fm.qmd"
    f.write_text(qmd_content)

    title, desc, html_content = build_html.extract_html_from_qmd(f)
    assert title is None
    assert desc is None
    assert html_content is None
