import re
from pathlib import Path

from scripts.cli_output import write_stdout
from src.core.contracts import require


def convert_tex_to_qmd(input_file: str | Path, output_file: str | Path) -> None:
    """Convert a LaTeX .tex file to a Quarto .qmd file.

    Performs basic structural conversion: chapter/section headers to
    markdown headings, theorem environments to callout blocks, and
    lstlisting blocks to fenced code blocks.

    Parameters
    ----------
    input_file : str | Path
        Path to the input .tex file.
    output_file : str | Path
        Path to the output .qmd file.
    """
    require(bool(input_file), "input_file must not be empty")
    require(bool(output_file), "output_file must not be empty")

    with open(input_file, encoding="utf-8") as f:
        content = f.read()

    # Find the start of the content
    doc_start = content.find(r"\begin{document}")
    if doc_start != -1:
        content = content[doc_start:]

    # Remove \end{document}
    content = content.replace(r"\end{document}", "")

    # Simple Headers
    lines = content.split("\n")
    out_lines = []

    for line in lines:
        if line.startswith(r"\chapter{"):
            title = line.replace(r"\chapter{", "").rstrip("}")
            out_lines.append(f"\n# {title}\n")
        elif line.startswith(r"\section{"):
            title = line.replace(r"\section{", "").rstrip("}")
            out_lines.append(f"\n## {title}\n")
        elif line.startswith(r"\subsection{"):
            title = line.replace(r"\subsection{", "").rstrip("}")
            out_lines.append(f"\n### {title}\n")
        elif (
            line.startswith(r"\begin{principle}")
            or line.startswith(r"\begin{definition}")
            or line.startswith(r"\begin{keyidea}")
            or line.startswith(r"\begin{laymansbox}")
        ):
            out_lines.append("\n::: {.callout-note}\n")
        elif (
            line.startswith(r"\end{principle}")
            or line.startswith(r"\end{definition}")
            or line.startswith(r"\end{keyidea}")
            or line.startswith(r"\end{laymansbox}")
        ):
            out_lines.append("\n:::\n")
        elif line.startswith(r"\begin{lstlisting}"):
            out_lines.append("\n```python\n")
        elif line.startswith(r"\end{lstlisting}"):
            out_lines.append("\n```\n")
        else:
            out_lines.append(line)

    content = "\n".join(out_lines)

    # Convert bold and italics (non-greedy)
    content = re.sub(r"\\textbf\{(.*?)\}", r"**\1**", content)
    content = re.sub(r"\\emph\{(.*?)\}", r"*\1*", content)
    content = re.sub(r"\\textit\{(.*?)\}", r"*\1*", content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)


def _collect_volume_chapters(volume_dir: Path, quarto_dir: Path, prefix: str = "") -> list[str]:
    """Convert a volume's chapter .tex files and return the generated QMD names."""
    chapters: list[str] = []
    if not volume_dir.exists():
        return chapters

    for f_path in volume_dir.iterdir():
        if f_path.name.endswith(".tex"):
            qmd_chap = f_path.name.replace(".tex", ".qmd")
            if prefix:
                qmd_chap = f"{prefix}{qmd_chap}"
            convert_tex_to_qmd(f_path, quarto_dir / qmd_chap)
            chapters.append(qmd_chap)
    return chapters


def _write_volume_index(quarto_dir: Path, filename: str, title: str, chapters: list[str]) -> None:
    """Write a Quarto include file for a volume."""
    with open(quarto_dir / filename, "w", encoding="utf-8") as f_out:
        f_out.write(f"# {title}\n\n")
        for q in sorted(chapters):
            f_out.write(f"{{{{< include {q} >}}}}\n")


def main(repo_root: Path | None = None) -> int:
    """Convert the Geometry of Motion LaTeX volumes to Quarto includes."""
    repo_root = repo_root or Path(__file__).resolve().parents[3]
    base_dir = repo_root / "articles" / "The_Geometry_of_Motion"
    quarto_dir = base_dir / "quarto"
    quarto_dir.mkdir(parents=True, exist_ok=True)

    vol0_chapters = _collect_volume_chapters(
        base_dir / "Volume_0" / "chapters",
        quarto_dir,
        "vol0_",
    )
    _write_volume_index(
        quarto_dir,
        "volume0.qmd",
        "Volume 0: The Mathematical Primer",
        vol0_chapters,
    )

    vol1_chapters = _collect_volume_chapters(base_dir / "Volume_I" / "chapters", quarto_dir)
    _write_volume_index(
        quarto_dir,
        "volume1.qmd",
        "Volume I: Foundations of Exact Linearization and Contraction",
        vol1_chapters,
    )

    vol2_main = base_dir / "Volume_II" / "main.tex"
    if vol2_main.exists():
        convert_tex_to_qmd(vol2_main, quarto_dir / "volume2_content.qmd")

    with open(quarto_dir / "volume2.qmd", "w", encoding="utf-8") as f_out:
        f_out.write("# Volume II: Transverse Control and The Architecture of Trajectories\n\n")
        f_out.write("{{< include volume2_content.qmd >}}\n")

    write_stdout("Conversion complete!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
