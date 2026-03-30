import re
from pathlib import Path

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


base_dir = Path(r"c:\Users\diete\Repositories\AffineDrift\articles\The_Geometry_of_Motion")
quarto_dir = base_dir / "quarto"

vol0_chapters = []
vol0_dir = base_dir / "Volume_0" / "chapters"
if vol0_dir.exists():
    for f_path in vol0_dir.iterdir():
        if f_path.name.endswith(".tex"):
            qmd_chap = f_path.name.replace(".tex", ".qmd")
            # Rename to avoid conflicts with Vol 1
            qmd_chap = "vol0_" + qmd_chap
            convert_tex_to_qmd(f_path, quarto_dir / qmd_chap)
            vol0_chapters.append(qmd_chap)

with open(quarto_dir / "volume0.qmd", "w") as f_out:
    f_out.write("# Volume 0: The Mathematical Primer\n\n")
    for q in sorted(vol0_chapters):
        f_out.write(f"{{{{< include {q} >}}}}\n")

vol1_chapters = []
vol1_dir = base_dir / "Volume_I" / "chapters"
if vol1_dir.exists():
    for f_path in vol1_dir.iterdir():
        if f_path.name.endswith(".tex"):
            qmd_chap = f_path.name.replace(".tex", ".qmd")
            convert_tex_to_qmd(f_path, quarto_dir / qmd_chap)
            vol1_chapters.append(qmd_chap)

with open(quarto_dir / "volume1.qmd", "w") as f_out:
    f_out.write("# Volume I: Foundations of Exact Linearization and Contraction\n\n")
    for q in sorted(vol1_chapters):
        f_out.write(f"{{{{< include {q} >}}}}\n")

vol2_main = base_dir / "Volume_II" / "main.tex"
if vol2_main.exists():
    convert_tex_to_qmd(vol2_main, quarto_dir / "volume2_content.qmd")

with open(quarto_dir / "volume2.qmd", "w") as f_out:
    f_out.write("# Volume II: Transverse Control and The Architecture of Trajectories\n\n")
    f_out.write("{{< include volume2_content.qmd >}}\n")

print("Conversion complete!")
