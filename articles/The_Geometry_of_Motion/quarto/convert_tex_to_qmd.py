import os
import re


def convert_tex_to_qmd(input_file, output_file):
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


base_dir = r"c:\Users\diete\Repositories\AffineDrift\articles\The_Geometry_of_Motion"

vol0_chapters = []
vol0_dir = os.path.join(base_dir, "Volume_0", "chapters")
for chap in sorted(os.listdir(vol0_dir)):
    if chap.endswith(".tex"):
        qmd_chap = chap.replace(".tex", ".qmd")
        # Rename to avoid conflicts with Vol 1
        qmd_chap = "vol0_" + qmd_chap
        convert_tex_to_qmd(os.path.join(vol0_dir, chap), os.path.join(base_dir, "quarto", qmd_chap))
        vol0_chapters.append(qmd_chap)

with open(os.path.join(base_dir, "quarto", "volume0.qmd"), "w") as f:
    f.write("# Volume 0: The Mathematical Primer\n\n")
    for q in vol0_chapters:
        f.write(f"{{{{< include {q} >}}}}\n")

vol1_chapters = []
vol1_dir = os.path.join(base_dir, "Volume_I", "chapters")
for chap in sorted(os.listdir(vol1_dir)):
    if chap.endswith(".tex"):
        qmd_chap = chap.replace(".tex", ".qmd")
        convert_tex_to_qmd(os.path.join(vol1_dir, chap), os.path.join(base_dir, "quarto", qmd_chap))
        vol1_chapters.append(qmd_chap)

with open(os.path.join(base_dir, "quarto", "volume1.qmd"), "w") as f:
    f.write("# Volume I: Foundations of Exact Linearization and Contraction\n\n")
    for q in vol1_chapters:
        f.write(f"{{{{< include {q} >}}}}\n")

convert_tex_to_qmd(
    os.path.join(base_dir, "Volume_II", "main.tex"),
    os.path.join(base_dir, "quarto", "volume2_content.qmd"),
)

with open(os.path.join(base_dir, "quarto", "volume2.qmd"), "w") as f:
    f.write("# Volume II: Transverse Control and The Architecture of Trajectories\n\n")
    f.write("{{< include volume2_content.qmd >}}\n")

print("Conversion complete!")
