# LaTeX to HTML Conversion Guide for AffineDrift

This directory contains tools for converting LaTeX article files to HTML with proper MathJax equation rendering.

## Tools

### `latex_to_html.py`

Single-file LaTeX to HTML converter

**Usage:**

```bash
python3 tools/latex_to_html.py <input.tex> [output.html]
```

**Example:**

```bash
python3 tools/latex_to_html.py "content/Wrist as Universal Joint/Wrist_Universal_Claude.tex"
```

### `convert_all_latex.py`

Batch converter for all LaTeX files in the repository

**Usage:**

```bash
# Dry run (preview without making changes)
python3 tools/convert_all_latex.py --dry-run

# Actual conversion
python3 tools/convert_all_latex.py
```

## Features

The converter handles:

- **Equations**: Preserves LaTeX equations for MathJax rendering
  - Display equations: `\begin{equation}...\end{equation}`, `\[...\]`
  - Inline equations: `$...$`, `\(...\)`
  - Align environments: `\begin{align}...\end{align}`

- **Sections**: Converts to HTML headings
  - `\section{}` → `<h2>`
  - `\subsection{}` → `<h3>`
  - `\subsubsection{}` → `<h4>`

- **Text Formatting**:
  - `\textbf{}` → `<strong>`
  - `\textit{}`, `\emph{}` → `<em>`
  - `\texttt{}` → `<code>`

- **Lists**:
  - `\begin{itemize}` → `<ul>`
  - `\begin{enumerate}` → `<ol>`

- **Special Environments**:
  - `\begin{abstract}` → Styled abstract section
  - `\begin{keypoint}` → Blue highlighted box
  - `\begin{limitation}` → Red highlighted box

- **Links**:
  - `\url{}` → `<a href="...">`
  - `\href{}{}` → `<a href="...">`

- **Figures**: Removed (TikZ/PGFPlots not supported in HTML)
  - Displays `[Figure: See PDF version]` placeholder

## LaTeX to HTML Conversion Mapping

| LaTeX Feature   | HTML Output                  | Notes                  |
| --------------- | ---------------------------- | ---------------------- |
| Equations       | MathJax rendering            | Preserves LaTeX syntax |
| Sections        | `<h2>`, `<h3>`, `<h4>`       | Hierarchical headings  |
| Abstract        | Styled `<div>`               | Blue background box    |
| Lists           | `<ul>`, `<ol>`               | Standard HTML lists    |
| Text formatting | `<strong>`, `<em>`, `<code>` | Semantic HTML          |
| Custom boxes    | Styled `<div>`               | Color-coded by type    |
| Figures/TikZ    | Placeholder text             | Not converted          |

## Adding New Conversions

To add a new LaTeX file to the batch converter:

1. Edit `tools/convert_all_latex.py`
2. Add an entry to the `CONVERSIONS` list:

```python
{
    "source": "content/path/to/article.tex",
    "target": "content/path/to/article.html",
    "root_page": None  # or path to root-level page if applicable
}
```

## Template Structure

The converter uses the standard AffineDrift template with:

- MathJax 3 for equation rendering
- Responsive CSS styling
- Sidebar navigation
- Styled equation boxes
- Styled abstract and special environment boxes

## Equation Rendering

MathJax is configured to process:

- Inline math: `$...$` and `\(...\)`
- Display math: `$$...$$` and `\[...\]`
- LaTeX environments: `equation`, `align`, etc.

**Important:** Equations are preserved in LaTeX syntax and rendered client-side by MathJax.

## Troubleshooting

### Equations not rendering

- Check MathJax script is loading (network tab in browser dev tools)
- Verify equation delimiters: `$...$` for inline, `\[...\]` for display
- Check for LaTeX syntax errors

### Broken formatting

- Review the LaTeX source for unsupported commands
- Check the converter's `clean_latex_commands()` method
- Add custom handling for new LaTeX commands if needed

### Missing content

- TikZ figures are intentionally not converted
- Some LaTeX environments may be removed if not handled
- Check the console for conversion warnings

## Development

To modify the converter:

1. Edit `tools/latex_to_html.py`
2. Test on a single file first
3. Run batch converter in dry-run mode
4. Review converted HTML in browser
5. Check equation rendering with MathJax

## Future Enhancements

Potential improvements:

- Convert TikZ figures to SVG using `tikz2svg`
- Handle more LaTeX packages (listings, algorithm, etc.)
- Generate table of contents from sections
- Add bibliography support
- Create automated deployment workflow
- Add Quarto support for more advanced conversions

## Related Documentation

- [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) - General website development
- [WEBSITE_MANAGEMENT.md](../WEBSITE_MANAGEMENT.md) - Content management
- [README.md](README.md) - Tools directory overview
