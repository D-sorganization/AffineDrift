# Editorial QA Checklist

Quality gates for textbook chapters before merge. Every item must pass.

## LaTeX Compilation

- [ ] `pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex` completes without fatal errors
- [ ] No undefined `\ref{}` or `\label{}` warnings in the modified chapters
- [ ] No undefined `\cite{}` keys — every citation resolves to a `.bib` entry

## Bibliography

- [ ] No `[CITE:]` placeholder markers remain
- [ ] No `[citation needed]` markers remain
- [ ] No `[illustrative]` markers remain without justification
- [ ] No duplicate BibTeX keys (case-insensitive)
- [ ] All new entries include author, title, year, and journal/publisher

## Writing Quality

- [ ] No unedited draft material: "Wait", "Actually", "Hmm", "Let me reconsider"
- [ ] No self-congratulatory language: "profound", "elegant", "beautiful", "magnificent" (when describing the book's own content)
- [ ] No unsupported superlatives: "always", "never", "completely", "the only", "proves that" (without qualification)
- [ ] No exclamation marks in formal exposition (permitted in layman's boxes)
- [ ] Numerical claims are cited or qualified with "approximately", "on the order of"

## Notation and Consistency

- [ ] Parameters match the canonical values established in earlier chapters, or differences are noted
- [ ] Custom LaTeX macros (`\state`, `\drift`, `\configvec`, etc.) are defined in the volume's `main.tex`
- [ ] No `\citep{}` or `\citet{}` (use `\cite{}` — natbib is not loaded)
- [ ] No Unicode characters that pdflatex cannot handle (em dashes, infinity symbols, accented characters must use LaTeX escapes)

## TikZ Diagrams

- [ ] All `\node` elements with `\\` line breaks include `align=center`
- [ ] No invalid draw styles (`rounded rectangle`, `arc` as style)
- [ ] `\foreach` not `\for` in loops
- [ ] `every node/.style` includes `align=center` if any nodes use `\\`

## Quarto (.qmd) Files

- [ ] No raw LaTeX boilerplate (`\begin{document}`, `\maketitle`, `\tableofcontents`)
- [ ] No `__DISPLAY_MATH__` placeholders
- [ ] `\textbf{}` converted to `**text**`, `\emph{}` to `*text*`
- [ ] `\cite{}` converted to `[@key]`
- [ ] Lists use markdown syntax, not `\begin{itemize}`
- [ ] New `.qmd` file registered in `_quarto.yml` or parent `.qmd`

## Structure

- [ ] New chapters added to `main.tex` in correct sequence
- [ ] Theorem-like environments use the correct syntax for the volume (check `main.tex` for `\newtheorem` vs `\newtcbtheorem`)
- [ ] Cross-references to other chapters use correct `\label`/`\ref` pairs
