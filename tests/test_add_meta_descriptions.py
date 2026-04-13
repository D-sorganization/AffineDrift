from __future__ import annotations

import textwrap
from pathlib import Path

from scripts.add_meta_descriptions import (
    add_description_to_file,
    extract_first_paragraph,
)


def test_extract_first_paragraph_skips_blockquote_epigraph() -> None:
    content = textwrap.dedent("""\
        ---
        title: "Example Chapter"
        ---
        > Opening epigraph that should not become the description.

        This chapter explains how the governing equations are assembled from
        the state, input, and constraint terms that define the local dynamics.
        """)

    description = extract_first_paragraph(content)

    assert description.startswith("This chapter explains how the governing equations")
    assert not description.startswith(">")


def test_add_description_to_file_inserts_after_title(tmp_path: Path) -> None:
    qmd = tmp_path / "chapter.qmd"
    qmd.write_text(
        textwrap.dedent("""\
            ---
            title: "Example Chapter"
            subtitle: "A compact demonstration"
            ---
            This chapter explains the example.
            """),
        encoding="utf-8",
    )

    assert add_description_to_file(qmd, "A compact example chapter description.")

    content = qmd.read_text(encoding="utf-8")
    assert (
        'title: "Example Chapter"\ndescription: "A compact example chapter description."\nsubtitle: "A compact demonstration"'
        in content
    )


def test_add_description_to_file_skips_existing_description(tmp_path: Path) -> None:
    qmd = tmp_path / "chapter.qmd"
    qmd.write_text(
        textwrap.dedent("""\
            ---
            title: "Example Chapter"
            description: "Already present"
            ---
            This chapter explains the example.
            """),
        encoding="utf-8",
    )

    assert not add_description_to_file(qmd, "A replacement description.")
    assert 'description: "Already present"' in qmd.read_text(encoding="utf-8")
