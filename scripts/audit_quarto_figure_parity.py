#!/usr/bin/env python3
"""Audit figure parity between LaTeX textbook sources and their Quarto mirrors.

Analyzes all chapters in the LaTeX textbook source tree (`articles/*/chapters/`)
and compares them with their corresponding Quarto markdown mirrors (`articles/*/quarto/`),
counting figure environments, TikZ diagrams, includegraphics macros, figure labels,
and cross-references.

Generates structured JSON, Markdown inventory reports, and documentation artifacts.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from scripts.cli_output import write_stderr, write_stdout
except ModuleNotFoundError:
    from cli_output import write_stderr, write_stdout  # type: ignore[import-not-found]

LOGGER = logging.getLogger(__name__)

# Known book directory mappings (LaTeX chapter dir, Quarto mirror dir, optional prefix)
BOOK_CONFIGS: dict[str, tuple[str, str, str]] = {
    "The_Physics_of_Golf": (
        "articles/The_Physics_of_Golf/chapters",
        "articles/The_Physics_of_Golf/quarto",
        "",
    ),
    "The_Geometry_of_Motion_Vol0": (
        "articles/The_Geometry_of_Motion/Volume_0/chapters",
        "articles/The_Geometry_of_Motion/quarto",
        "vol0_",
    ),
    "The_Geometry_of_Motion_VolI": (
        "articles/The_Geometry_of_Motion/Volume_I/chapters",
        "articles/The_Geometry_of_Motion/quarto",
        "",
    ),
}

# Non-chapter stems that are front/back matter or structural
NON_CHAPTER_STEMS = frozenset(
    {
        "main",
        "nomenclature",
        "further_reading",
        "index",
        "glossary",
        "volume0",
        "volume1",
        "volume2",
        "volume2_content",
        "textbook-main",
    }
)

RE_LATEX_FIGURE_ENV = re.compile(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", re.DOTALL)
RE_LATEX_TIKZ_ENV = re.compile(r"\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}", re.DOTALL)
RE_LATEX_INCLUDEGRAPHICS = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
RE_LATEX_LABEL = re.compile(r"\\label\{([^}]+)\}")
RE_LATEX_CAPTION = re.compile(r"\\caption(?:\[[^\]]*\])?\{([^}]+)\}")
RE_LATEX_FIG_REF = re.compile(r"\\(?:auto|c|page)?ref\{(fig:[^}]+)\}")
RE_LATEX_CHAPTER_TITLE = re.compile(r"\\chapter\{([^}]+)\}")

RE_QUARTO_MD_IMAGE = re.compile(r"!\[(.*?)\]\((.*?)\)(?:\{([^}]*)\})?")
RE_QUARTO_FIG_DIV = re.compile(r":::+\s*\{#fig-([^}\s]+)[^}]*\}")
RE_QUARTO_CODE_CELL = re.compile(r"```+\s*\{([a-zA-Z0-9_-]+)\}")
RE_QUARTO_CELL_LABEL = re.compile(r"#\|\s*label:\s*(fig-[a-zA-Z0-9_-]+)")
RE_QUARTO_FIG_REF = re.compile(r"(?<![\w`])@(fig-[A-Za-z0-9_:.-]+)")
RE_QUARTO_RAW_TEX_FIG_REF = re.compile(r"\\(?:auto|c|page)?ref\{(fig:[^}]+)\}")
RE_QUARTO_TITLE = re.compile(r"^title:\s*[\"']?([^\"'\n]+)[\"']?", re.MULTILINE)
RE_PROSE_FIGURE_MENTION = re.compile(r"\b(?:[Ff]igures?|[Ff]igs?\.)(?:\s|$|[0-9])")


@dataclass(frozen=True)
class FigureDetail:
    """Detailed record of an individual figure in a chapter."""

    figure_index: int
    label: str
    caption: str
    has_tikzpicture: bool
    has_includegraphics: bool
    graphics_target: str | None
    tikz_line_count: int


@dataclass(frozen=True)
class ChapterFigureAudit:
    """Audit record for a single chapter's figure parity."""

    chapter_stem: str
    chapter_title: str
    tex_path: str
    qmd_path: str | None
    latex_figure_count: int
    latex_tikz_count: int
    latex_includegraphics_count: int
    latex_fig_labels: list[str]
    latex_fig_refs: list[str]
    quarto_figure_count: int
    quarto_md_images: int
    quarto_fig_divs: int
    quarto_code_cells_with_fig: int
    quarto_fig_refs: list[str]
    quarto_raw_tex_fig_refs: list[str]
    quarto_prose_mentions: list[str]
    figures: list[FigureDetail]

    @property
    def parity_delta(self) -> int:
        """Difference between Quarto figure count and LaTeX figure count."""
        return self.quarto_figure_count - self.latex_figure_count

    @property
    def is_in_parity(self) -> bool:
        """Return whether Quarto and LaTeX figure counts match."""
        return self.quarto_figure_count == self.latex_figure_count


@dataclass(frozen=True)
class BookAuditResult:
    """Aggregated audit result across all chapters in a textbook."""

    book_name: str
    total_chapters: int
    chapters_with_latex_figures: int
    total_latex_figures: int
    total_latex_tikz: int
    total_latex_includegraphics: int
    total_latex_fig_labels: int
    total_latex_fig_refs: int
    total_quarto_figures: int
    total_quarto_md_images: int
    total_quarto_fig_divs: int
    total_quarto_code_cells_with_fig: int
    total_quarto_fig_refs: int
    total_quarto_raw_tex_fig_refs: int
    total_quarto_prose_mentions: int
    missing_figures_count: int
    chapters: list[ChapterFigureAudit]

    @property
    def is_in_full_parity(self) -> bool:
        """Return whether all chapters in the book are in figure parity."""
        return self.missing_figures_count == 0 and all(ch.is_in_parity for ch in self.chapters)


def strip_latex_comments(content: str) -> str:
    """Remove comments from LaTeX content while preserving escaped percent signs."""
    lines: list[str] = []
    for line in content.splitlines():
        # Match % that is not preceded by backslash
        cleaned = re.sub(r"(?<!\\)%.*$", "", line)
        lines.append(cleaned)
    return "\n".join(lines)


def extract_balanced_latex_arg(text: str, command: str) -> str | None:
    """Extract argument from a LaTeX macro with balanced braces."""
    pattern = rf"\\{command}(?:\[[^\]]*\])?\{{"
    match = re.search(pattern, text)
    if not match:
        return None
    start = match.end()
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        char = text[i]
        prev = text[i - 1] if i > 0 else ""
        if char == "{" and prev != "\\":
            depth += 1
        elif char == "}" and prev != "\\":
            depth -= 1
        i += 1
    if depth == 0:
        return text[start : i - 1]
    return None


def extract_chapter_title_from_tex(tex_content: str, default: str) -> str:
    """Extract chapter title from \\chapter{...} macro."""
    clean = strip_latex_comments(tex_content)
    arg = extract_balanced_latex_arg(clean, "chapter")
    if arg:
        return arg.strip()
    return default.replace("_", " ").title()


def extract_chapter_title_from_qmd(qmd_content: str, default: str) -> str:
    """Extract chapter title from frontmatter title field or top heading."""
    match = RE_QUARTO_TITLE.search(qmd_content)
    if match:
        return match.group(1).strip()
    heading_match = re.search(r"^#\s+(.+)$", qmd_content, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()
    return default.replace("_", " ").title()


def extract_latex_figures(tex_content: str) -> list[FigureDetail]:
    """Parse figure environments from LaTeX content and return detailed records."""
    clean = strip_latex_comments(tex_content)
    figures: list[FigureDetail] = []

    for index, match in enumerate(RE_LATEX_FIGURE_ENV.finditer(clean), start=1):
        block = match.group(1)

        raw_label = extract_balanced_latex_arg(block, "label")
        label = raw_label.strip() if raw_label else f"unlabeled_fig_{index}"

        raw_caption = extract_balanced_latex_arg(block, "caption")
        if raw_caption:
            # Remove any nested label inside caption
            clean_caption = re.sub(r"\\label\{[^}]+\}", "", raw_caption).strip()
            # Normalize whitespace
            caption = " ".join(clean_caption.split())
        else:
            caption = ""

        tikz_match = RE_LATEX_TIKZ_ENV.search(block)
        has_tikz = bool(tikz_match)
        tikz_line_count = len(tikz_match.group(1).splitlines()) if tikz_match else 0

        ig_match = RE_LATEX_INCLUDEGRAPHICS.search(block)
        has_ig = bool(ig_match)
        graphics_target = ig_match.group(1) if ig_match else None

        figures.append(
            FigureDetail(
                figure_index=index,
                label=label,
                caption=caption,
                has_tikzpicture=has_tikz,
                has_includegraphics=has_ig,
                graphics_target=graphics_target,
                tikz_line_count=tikz_line_count,
            )
        )

    return figures


def extract_quarto_figures_count(qmd_content: str) -> tuple[int, int, int, int]:
    """Count Quarto figure elements: (total_figures, md_images, fig_divs, code_cells)."""
    md_images = len(RE_QUARTO_MD_IMAGE.findall(qmd_content))
    fig_divs = len(RE_QUARTO_FIG_DIV.findall(qmd_content))

    # Check executable code cells with #| label: fig-...
    cells_with_fig = 0
    for cell in re.finditer(r"```+\s*\{[a-zA-Z0-9_-]+\}(.*?)```+", qmd_content, re.DOTALL):
        if RE_QUARTO_CELL_LABEL.search(cell.group(1)):
            cells_with_fig += 1

    total = md_images + fig_divs + cells_with_fig
    return total, md_images, fig_divs, cells_with_fig


def extract_quarto_prose_mentions(qmd_content: str) -> list[str]:
    """Extract sentences or lines in Quarto that refer to figures in prose."""
    mentions: list[str] = []
    for line in qmd_content.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("<!--") or trimmed.startswith("#"):
            continue
        if RE_PROSE_FIGURE_MENTION.search(trimmed):
            mentions.append(trimmed)
    return mentions


def audit_chapter_pair(
    tex_path: Path | None,
    qmd_path: Path | None,
    chapter_stem: str,
    repo_root: Path,
) -> ChapterFigureAudit:
    """Perform a figure parity audit on a single chapter pair."""
    tex_content = tex_path.read_text(encoding="utf-8") if tex_path and tex_path.exists() else ""
    qmd_content = qmd_path.read_text(encoding="utf-8") if qmd_path and qmd_path.exists() else ""

    tex_rel = tex_path.relative_to(repo_root).as_posix() if tex_path else ""
    qmd_rel = qmd_path.relative_to(repo_root).as_posix() if qmd_path else None

    title = (
        extract_chapter_title_from_tex(tex_content, chapter_stem)
        if tex_content
        else extract_chapter_title_from_qmd(qmd_content, chapter_stem)
    )

    # LaTeX figure extraction
    figures = extract_latex_figures(tex_content) if tex_content else []
    clean_tex = strip_latex_comments(tex_content) if tex_content else ""

    latex_tikz_count = sum(1 for f in figures if f.has_tikzpicture)
    latex_ig_count = sum(1 for f in figures if f.has_includegraphics)
    latex_labels = [f.label for f in figures]
    latex_refs = RE_LATEX_FIG_REF.findall(clean_tex)

    # Quarto figure extraction
    q_total, q_images, q_divs, q_cells = (
        extract_quarto_figures_count(qmd_content) if qmd_content else (0, 0, 0, 0)
    )
    q_fig_refs = RE_QUARTO_FIG_REF.findall(qmd_content) if qmd_content else []
    q_raw_refs = RE_QUARTO_RAW_TEX_FIG_REF.findall(qmd_content) if qmd_content else []
    q_prose_mentions = extract_quarto_prose_mentions(qmd_content) if qmd_content else []

    return ChapterFigureAudit(
        chapter_stem=chapter_stem,
        chapter_title=title,
        tex_path=tex_rel,
        qmd_path=qmd_rel,
        latex_figure_count=len(figures),
        latex_tikz_count=latex_tikz_count,
        latex_includegraphics_count=latex_ig_count,
        latex_fig_labels=latex_labels,
        latex_fig_refs=latex_refs,
        quarto_figure_count=q_total,
        quarto_md_images=q_images,
        quarto_fig_divs=q_divs,
        quarto_code_cells_with_fig=q_cells,
        quarto_fig_refs=q_fig_refs,
        quarto_raw_tex_fig_refs=q_raw_refs,
        quarto_prose_mentions=q_prose_mentions,
        figures=figures,
    )


def audit_book(
    repo_root: Path,
    book_key: str = "The_Physics_of_Golf",
) -> BookAuditResult:
    """Audit figure parity across all chapters in a specified book."""
    if book_key not in BOOK_CONFIGS:
        raise ValueError(f"Unknown book key '{book_key}'. Choose from: {list(BOOK_CONFIGS.keys())}")

    tex_rel_dir, qmd_rel_dir, qmd_prefix = BOOK_CONFIGS[book_key]
    tex_dir = repo_root / tex_rel_dir
    qmd_dir = repo_root / qmd_rel_dir

    if not tex_dir.exists():
        raise FileNotFoundError(f"LaTeX directory not found: {tex_dir}")

    # Discover all LaTeX chapter files
    chapter_audits: list[ChapterFigureAudit] = []

    tex_files = sorted(tex_dir.glob("*.tex"))
    for tf in tex_files:
        stem = tf.stem
        if stem in NON_CHAPTER_STEMS:
            continue

        qmd_filename = f"{qmd_prefix}{stem}.qmd"
        qmd_path = qmd_dir / qmd_filename
        qmd_target = qmd_path if qmd_path.exists() else None

        audit = audit_chapter_pair(tf, qmd_target, stem, repo_root)
        chapter_audits.append(audit)

    total_chapters = len(chapter_audits)
    chapters_with_figs = sum(1 for c in chapter_audits if c.latex_figure_count > 0)
    total_latex_figs = sum(c.latex_figure_count for c in chapter_audits)
    total_latex_tikz = sum(c.latex_tikz_count for c in chapter_audits)
    total_latex_ig = sum(c.latex_includegraphics_count for c in chapter_audits)
    total_latex_labels = sum(len(c.latex_fig_labels) for c in chapter_audits)
    total_latex_refs = sum(len(c.latex_fig_refs) for c in chapter_audits)

    total_q_figs = sum(c.quarto_figure_count for c in chapter_audits)
    total_q_imgs = sum(c.quarto_md_images for c in chapter_audits)
    total_q_divs = sum(c.quarto_fig_divs for c in chapter_audits)
    total_q_cells = sum(c.quarto_code_cells_with_fig for c in chapter_audits)
    total_q_refs = sum(len(c.quarto_fig_refs) for c in chapter_audits)
    total_q_raw_refs = sum(len(c.quarto_raw_tex_fig_refs) for c in chapter_audits)
    total_q_prose = sum(len(c.quarto_prose_mentions) for c in chapter_audits)

    missing_count = total_latex_figs - total_q_figs

    return BookAuditResult(
        book_name=book_key,
        total_chapters=total_chapters,
        chapters_with_latex_figures=chapters_with_figs,
        total_latex_figures=total_latex_figs,
        total_latex_tikz=total_latex_tikz,
        total_latex_includegraphics=total_latex_ig,
        total_latex_fig_labels=total_latex_labels,
        total_latex_fig_refs=total_latex_refs,
        total_quarto_figures=total_q_figs,
        total_quarto_md_images=total_q_imgs,
        total_quarto_fig_divs=total_q_divs,
        total_quarto_code_cells_with_fig=total_q_cells,
        total_quarto_fig_refs=total_q_refs,
        total_quarto_raw_tex_fig_refs=total_q_raw_refs,
        total_quarto_prose_mentions=total_q_prose,
        missing_figures_count=missing_count,
        chapters=chapter_audits,
    )


def format_text_summary(result: BookAuditResult) -> str:
    """Format human-readable CLI summary table."""
    lines: list[str] = [
        f"=== Figure Parity Audit: {result.book_name} ===",
        f"Total Chapters Audited: {result.total_chapters}",
        f"Chapters with LaTeX Figures: {result.chapters_with_latex_figures}",
        f"Total LaTeX Figures: {result.total_latex_figures} (TikZ: {result.total_latex_tikz}, includegraphics: {result.total_latex_includegraphics})",
        f"Total LaTeX \\ref References: {result.total_latex_fig_refs}",
        f"Total Quarto Figures: {result.total_quarto_figures} (Markdown: {result.total_quarto_md_images}, Divs: {result.total_quarto_fig_divs}, Cells: {result.total_quarto_code_cells_with_fig})",
        f"Total Quarto @fig References: {result.total_quarto_fig_refs}",
        f"Quarto Figure Prose Mentions: {result.total_quarto_prose_mentions}",
        f"Parity Gap (Missing Figures): {result.missing_figures_count}",
        "",
        f"{'Chapter Stem':<32} | {'Title':<30} | {'LaTeX':<6} | {'TikZ':<5} | {'Quarto':<6} | {'Delta':<6}",
        "-" * 95,
    ]

    for ch in result.chapters:
        short_title = (
            ch.chapter_title[:27] + "..." if len(ch.chapter_title) > 30 else ch.chapter_title
        )
        lines.append(
            f"{ch.chapter_stem:<32} | {short_title:<30} | {ch.latex_figure_count:<6} | {ch.latex_tikz_count:<5} | {ch.quarto_figure_count:<6} | {ch.parity_delta:<6}"
        )

    return "\n".join(lines)


def format_markdown_report(result: BookAuditResult) -> str:
    """Generate comprehensive Markdown report and inventory document."""
    lines: list[str] = [
        f"# Figures Inventory and Parity Audit: {result.book_name.replace('_', ' ')}",
        "",
        "This document provides the formal audit and inventory of all figures across the LaTeX book sources and their Quarto website mirrors, tracking figure types, labels, captions, and parity gaps.",
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **Total Chapters Audited** | {result.total_chapters} |",
        f"| **Chapters with Figures** | {result.chapters_with_latex_figures} |",
        f"| **Total LaTeX Figures** | {result.total_latex_figures} |",
        f"| **TikZ Figures** | {result.total_latex_tikz} |",
        f"| **Raster / Includegraphics Figures** | {result.total_latex_includegraphics} |",
        f"| **LaTeX Figure Labels** | {result.total_latex_fig_labels} |",
        f"| **LaTeX Prose Figure Refs** | {result.total_latex_fig_refs} |",
        f"| **Total Quarto Figures** | {result.total_quarto_figures} |",
        f"| **Quarto Figure Defs (Divs / Imgs / Cells)** | {result.total_quarto_md_images + result.total_quarto_fig_divs + result.total_quarto_code_cells_with_fig} |",
        f"| **Quarto Prose Figure Mentions** | {result.total_quarto_prose_mentions} |",
        f"| **Missing Figures in Quarto** | **{result.missing_figures_count}** |",
        "",
        "## Chapter Parity Matrix",
        "",
        "| Chapter Stem | Title | LaTeX Figs | TikZ | Quarto Figs | Parity Status |",
        "|---|---|---|---|---|---|",
    ]

    for ch in result.chapters:
        status = "✅ Parity" if ch.is_in_parity else f"❌ Missing {abs(ch.parity_delta)}"
        lines.append(
            f"| `{ch.chapter_stem}` | {ch.chapter_title} | {ch.latex_figure_count} | {ch.latex_tikz_count} | {ch.quarto_figure_count} | {status} |"
        )

    lines.extend(
        [
            "",
            "## Complete Figures Inventory",
            "",
            "| Chapter | Fig # | Label | Type | Caption Summary |",
            "|---|---|---|---|---|",
        ]
    )

    for ch in result.chapters:
        if not ch.figures:
            continue
        for f in ch.figures:
            fig_type = (
                "TikZ Diagram"
                if f.has_tikzpicture
                else "Includegraphics" if f.has_includegraphics else "Other"
            )
            clean_cap = f.caption.replace("|", "\\|").replace("\n", " ")
            short_cap = clean_cap[:90] + "..." if len(clean_cap) > 90 else clean_cap
            lines.append(
                f"| `{ch.chapter_stem}` | {f.figure_index} | `{f.label}` | {fig_type} | {short_cap} |"
            )

    lines.extend(
        [
            "",
            "## Strategic Recommendations for Quarto Figure Rendering",
            "",
            "1. **TikZ to SVG Build-Time Pipeline**: Because all 31 figures are `tikzpicture` environments, an automated offline pipeline (e.g. `pdflatex` + `dvisvgm` or `standalone` LaTeX compiler) can render high-fidelity SVGs into `articles/The_Physics_of_Golf/quarto/figures/` without introducing runtime browser dependencies.",
            "2. **Executable Matplotlib / OJS Option**: Select conceptual plots (e.g. `ch06` ZTCF comparison, `ch11` shaft bending, `ch29` mass-spring-damper) can optionally be upgraded to interactive executable cells in future enhancements.",
            "3. **Cross-Reference Hygiene**: Update Quarto cross-references to use `@fig-<label>` matching LaTeX `fig:<label>` identifiers.",
            "",
        ]
    )

    return "\n".join(lines)


def generate_inventory_doc(
    repo_root: Path,
    output_path: Path | None = None,
) -> Path:
    """Generate and write the formal documentation file in docs/."""
    result = audit_book(repo_root, "The_Physics_of_Golf")
    doc_content = format_markdown_report(result)

    target = output_path or (repo_root / "docs/THE_PHYSICS_OF_GOLF_FIGURES_INVENTORY.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc_content, encoding="utf-8")
    LOGGER.info("Generated figures inventory documentation at %s", target)
    return target


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for figure parity audit."""
    parser = argparse.ArgumentParser(
        description="Audit figure parity between LaTeX textbook sources and Quarto mirrors."
    )
    parser.add_argument(
        "--book",
        choices=list(BOOK_CONFIGS.keys()) + ["all"],
        default="The_Physics_of_Golf",
        help="Target book to audit (default: The_Physics_of_Golf)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Path to repository root (default: current working directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON data",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Output formatted Markdown report",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Write output to specified file path",
    )
    parser.add_argument(
        "--write-doc",
        action="store_true",
        help="Generate and write docs/THE_PHYSICS_OF_GOLF_FIGURES_INVENTORY.md",
    )
    parser.add_argument(
        "--check",
        "--fail-on-discrepancy",
        action="store_true",
        dest="check_mode",
        help="Exit with non-zero status if figure parity discrepancy is detected",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress human-readable summary output",
    )

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    repo_root = args.repo_root.resolve()

    if args.write_doc:
        doc_path = generate_inventory_doc(repo_root)
        write_stdout(f"Inventory documentation written to {doc_path}")

    books_to_audit = list(BOOK_CONFIGS.keys()) if args.book == "all" else [args.book]
    results: list[BookAuditResult] = []

    for b in books_to_audit:
        try:
            res = audit_book(repo_root, b)
            results.append(res)
        except Exception as exc:
            write_stderr(f"Error auditing book '{b}': {exc}")
            LOGGER.exception("Failed to audit %s", b)
            return 2

    # Formatting output
    if args.json:
        payload = [asdict(r) for r in results] if len(results) > 1 else asdict(results[0])
        json_str = json.dumps(payload, indent=2)
        if args.output:
            args.output.write_text(json_str, encoding="utf-8")
        else:
            write_stdout(json_str)
    elif args.markdown:
        md_reports = [format_markdown_report(r) for r in results]
        combined_md = "\n\n---\n\n".join(md_reports)
        if args.output:
            args.output.write_text(combined_md, encoding="utf-8")
        else:
            write_stdout(combined_md)
    elif not args.quiet:
        summary_text = "\n\n".join(format_text_summary(r) for r in results)
        if args.output:
            args.output.write_text(summary_text, encoding="utf-8")
        else:
            write_stdout(summary_text)

    if args.check_mode:
        has_discrepancy = any(not r.is_in_full_parity for r in results)
        if has_discrepancy:
            total_missing = sum(r.missing_figures_count for r in results)
            write_stderr(
                f"Figure parity check FAILED: {total_missing} missing figures detected across {len(results)} book(s)."
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
