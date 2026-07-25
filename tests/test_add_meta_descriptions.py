from __future__ import annotations

import textwrap
from pathlib import Path

from scripts.add_meta_descriptions import (
    add_description_to_file,
    build_critique_description,
    extract_first_paragraph,
    extract_title,
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


def test_extract_title_reads_first_markdown_h1_without_frontmatter() -> None:
    content = textwrap.dedent("""\
        # Critique: Input-Dependent Boundary Conditions

        The critique examines how grip stiffness can alter the effective plant.
        """)

    assert extract_title(content) == "Critique: Input-Dependent Boundary Conditions"


def test_add_description_to_file_creates_frontmatter_for_markdown(tmp_path: Path) -> None:
    md = tmp_path / "critique.md"
    md.write_text(
        textwrap.dedent("""\
            # Critique: Input-Dependent Boundary Conditions

            The critique examines how grip stiffness can alter the effective plant.
            """),
        encoding="utf-8",
    )

    assert add_description_to_file(md, "Critique of grip stiffness effects in AffineDrift.")

    content = md.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert 'title: "Critique: Input-Dependent Boundary Conditions"' in content
    assert 'description: "Critique of grip stiffness effects in AffineDrift."' in content
    assert "# Critique: Input-Dependent Boundary Conditions" in content


def test_build_critique_description_uses_title_topic() -> None:
    content = "# Critique: Input-Dependent Boundary Conditions\n\nThe math includes $f(x)$."

    description = build_critique_description(content)

    assert description == (
        "Critique and response context for Input-Dependent Boundary Conditions "
        "in AffineDrift's control-affine golf-swing framework."
    )


def test_build_critique_description_handles_bibliographic_analysis() -> None:
    content = "# Bibliographic Analysis: The Effective Plant Fallacy\n\n- Source notes"

    description = build_critique_description(content)

    assert description == (
        "Bibliographic analysis supporting the AffineDrift critique of "
        "The Effective Plant Fallacy."
    )
