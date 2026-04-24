import re

filepath = (
    "C:/Users/diete/Repositories/AffineDrift/articles/The_Physics_of_Golf/quarto"
    "/ch23_dof_urdf_models.qmd"
)

with open(filepath, encoding="utf-8") as f:
    content = f.read()


# Fix \section{...}\n\label{...} -> ## ... {#sec-...}
def section_to_h2(m):
    title = m.group(1)
    anchor = re.sub("[^a-z0-9]+", "-", title.lower()).strip("-")
    return "## " + title + " {#sec-" + anchor + "}"


content = re.sub(r"\section[{]([^}]+)[}][ \t]*\n\label[{][^}]+[}]", section_to_h2, content)
content = re.sub(r"\section[{]([^}]+)[}]", section_to_h2, content)

# Fix \subsection{...} -> ### ...
content = re.sub(r"\subsection[{]([^}]+)[}]", r"### \1", content)

# Fix \textbf{...} -> **...**
content = re.sub(r"\textbf[{]([^}]+)[}]", r"**\1**", content)

# Fix \emph{...} -> *...*
content = re.sub(r"\emph[{]([^}]+)[}]", r"*\1*", content)

# Remove \begin{itemize}, \end{itemize}, \begin{enumerate}, \end{enumerate}
for tag in [r"\begin{itemize}", r"\end{itemize}", r"\begin{enumerate}", r"\end{enumerate}"]:
    content = content.replace(tag, "")

# Fix \item -> -
content = re.sub(r"\item ", "- ", content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
