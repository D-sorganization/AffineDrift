#!/usr/bin/env python3
"""Cross-tree audit of LaTeX boxed items vs. Quarto callout blocks and prose.

Audits textbook chapters (default: The Physics of Golf) to detect boxed item
parity, measuring n-gram word containment of every LaTeX box against its Quarto
counterpart, and identifying absent or abridged material.

Usage:
    python scripts/audit_quarto_boxed_items.py
    python scripts/audit_quarto_boxed_items.py --json
    python scripts/audit_quarto_boxed_items.py --markdown
    python scripts/audit_quarto_boxed_items.py --write-doc
    python scripts/audit_quarto_boxed_items.py --check
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from scripts.cli_output import write_stderr, write_stdout
except ImportError:
    try:
        from cli_output import write_stderr, write_stdout
    except ImportError:

        def write_stdout(text: str) -> None:
            sys.stdout.write(text + "\n")
            sys.stdout.flush()

        def write_stderr(text: str) -> None:
            sys.stderr.write(text + "\n")
            sys.stderr.flush()


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Supported LaTeX boxed item environments defined in textbook preambles
BOX_ENVIRONMENTS: tuple[str, ...] = (
    "principle",
    "laymansbox",
    "example",
    "definition",
    "theorem",
    "exercises",
    "algorithm",
    "driftcontrol",
    "mythreality",
    "constraintbox",
    "reference",
    "explanation",
    "infobox",
    "warningbox",
    "takeawaybox",
    "tcolorbox",
)

RE_LATEX_COMMAND = re.compile(r"\\[a-zA-Z]+(?:\*|\+)?(?:\[[^\]]*\])?(?:\{[^\}]*\})*")
RE_CALLOUT_START = re.compile(r"^:::\s*\{\.callout-([a-zA-Z]+)\}", re.MULTILINE)
RE_BOLD_LABEL_START = re.compile(
    r"^\*\*(?:Example|Definition|Key Principle|In Plain Language|Theorem|Exercise|Myth vs\. Reality|Constraint Insight|Takeaway)[^:]*:\s*([^*]+)\*\*",
    re.MULTILINE,
)


@dataclass
class BoxedItem:
    """Represents a single boxed item in LaTeX source."""

    environment: str
    title: str
    label: str
    body_preview: str
    word_count: int
    containment_ratio: float
    status: str  # 'present', 'partial', 'absent'


@dataclass
class ChapterBoxAudit:
    """Audit results for one chapter pair."""

    stem: str
    tex_path: str
    qmd_path: str | None
    tex_lines: int
    qmd_lines: int
    total_boxes: int
    substantive_boxes: int
    present_boxes: int
    partial_boxes: int
    absent_boxes: int
    quarto_callouts_count: int
    quarto_bold_labels_count: int
    boxes: list[BoxedItem]


@dataclass
class BookBoxAudit:
    """Audit results across an entire book."""

    book_title: str
    total_chapters_audited: int
    total_boxes: int
    total_substantive_boxes: int
    total_present_boxes: int
    total_partial_boxes: int
    total_absent_boxes: int
    total_quarto_callouts: int
    chapters: list[ChapterBoxAudit]


def strip_latex_comments(content: str) -> str:
    """Remove LaTeX comments preserving escaped percentage signs."""
    lines: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        line = re.sub(r"(?<!\\)%.*$", "", line)
        lines.append(line)
    return "\n".join(lines)


def tokenize_words(text: str) -> list[str]:
    """Tokenize plain text or markup into lowercase alphanumeric word tokens."""
    # Remove LaTeX commands and inline math / markdown delimiters
    cleaned = RE_LATEX_COMMAND.sub(" ", text)
    cleaned = re.sub(r"[{}\\_^$#&~@`*|#><\[\]\(\)\"\':;=]", " ", cleaned)
    words = re.findall(r"[a-z0-9]+", cleaned.lower())
    return words


def compute_ngrams(words: list[str], n: int = 5) -> set[tuple[str, ...]]:
    """Compute n-grams of words."""
    if not words:
        return set()
    if len(words) < n:
        return {tuple(words)}
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def parse_balanced_latex_arg(text: str, start_index: int) -> tuple[str, int]:
    """Parse a single balanced {...} LaTeX argument starting at start_index."""
    while start_index < len(text) and text[start_index].isspace():
        start_index += 1
    if start_index >= len(text) or text[start_index] != "{":
        return "", start_index

    depth = 0
    pos = start_index
    while pos < len(text):
        char = text[pos]
        if char == "{" and (pos == 0 or text[pos - 1] != "\\"):
            depth += 1
        elif char == "}" and (pos == 0 or text[pos - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start_index + 1 : pos], pos + 1
        pos += 1
    return text[start_index + 1 :], len(text)


def parse_boxed_items_from_tex(tex_content: str) -> list[dict[str, Any]]:
    """Extract boxed item environments with title, label, and body."""
    clean_tex = strip_latex_comments(tex_content)
    pattern_begin = re.compile(r"\\begin\{(" + "|".join(BOX_ENVIRONMENTS) + r")\}")

    results: list[dict[str, Any]] = []
    pos = 0

    while pos < len(clean_tex):
        match = pattern_begin.search(clean_tex, pos)
        if not match:
            break

        env_name = match.group(1)
        after_begin = match.end()

        # Check for optional bracket arguments: [options]
        opt_match = re.match(r"\s*\[(.*?)\]", clean_tex[after_begin:], re.DOTALL)
        opt_arg = ""
        cursor = after_begin
        if opt_match:
            opt_arg = opt_match.group(1)
            cursor = after_begin + opt_match.end()

        # Parse mandatory curly-brace arguments
        arg1, next_cursor = parse_balanced_latex_arg(clean_tex, cursor)
        arg2, next_cursor2 = parse_balanced_latex_arg(clean_tex, next_cursor)

        body_start = next_cursor2
        end_tag = f"\\end{{{env_name}}}"
        end_idx = clean_tex.find(end_tag, body_start)

        if end_idx == -1:
            body = clean_tex[body_start:]
            pos = len(clean_tex)
        else:
            body = clean_tex[body_start:end_idx]
            pos = end_idx + len(end_tag)

        title = arg1 if arg1 else opt_arg
        label = arg2

        results.append(
            {
                "env": env_name,
                "title": title.strip(),
                "label": label.strip(),
                "body": body.strip(),
            }
        )

    return results


def count_quarto_callouts(qmd_content: str) -> int:
    """Count Quarto callout blocks."""
    return len(RE_CALLOUT_START.findall(qmd_content))


def count_quarto_bold_labels(qmd_content: str) -> int:
    """Count standalone bold label paragraphs mimicking boxes."""
    return len(RE_BOLD_LABEL_START.findall(qmd_content))


def audit_chapter_boxed_items(
    tex_path: Path,
    qmd_path: Path | None,
    ngram_size: int = 5,
) -> ChapterBoxAudit:
    """Audit boxed items for a single LaTeX/Quarto chapter pair."""
    stem = tex_path.stem
    tex_content = tex_path.read_text(encoding="utf-8")
    tex_lines = len(tex_content.splitlines())

    qmd_content = ""
    qmd_lines = 0
    if qmd_path and qmd_path.exists():
        qmd_content = qmd_path.read_text(encoding="utf-8")
        qmd_lines = len(qmd_content.splitlines())

    qmd_words = tokenize_words(qmd_content)
    qmd_ngrams = compute_ngrams(qmd_words, n=ngram_size)

    quarto_callouts = count_quarto_callouts(qmd_content)
    quarto_bold_labels = count_quarto_bold_labels(qmd_content)

    raw_boxes = parse_boxed_items_from_tex(tex_content)
    boxed_items: list[BoxedItem] = []

    present_cnt = 0
    partial_cnt = 0
    absent_cnt = 0
    substantive_cnt = 0

    for b in raw_boxes:
        body = b["body"]
        b_words = tokenize_words(body)
        w_count = len(b_words)

        # Boxes with < 5 words are deemed trivial/empty
        if w_count < 5:
            continue

        substantive_cnt += 1
        b_ngrams = compute_ngrams(b_words, n=ngram_size)

        if not b_ngrams or not qmd_ngrams:
            ratio = 0.0
        else:
            overlap = len(b_ngrams.intersection(qmd_ngrams))
            ratio = overlap / len(b_ngrams)

        if ratio >= 0.50:
            status = "present"
            present_cnt += 1
        elif ratio >= 0.10:
            status = "partial"
            partial_cnt += 1
        else:
            status = "absent"
            absent_cnt += 1

        preview = re.sub(r"\s+", " ", body)[:140]
        boxed_items.append(
            BoxedItem(
                environment=b["env"],
                title=b["title"],
                label=b["label"],
                body_preview=preview,
                word_count=w_count,
                containment_ratio=round(ratio, 4),
                status=status,
            )
        )

    return ChapterBoxAudit(
        stem=stem,
        tex_path=str(tex_path),
        qmd_path=str(qmd_path) if qmd_path else None,
        tex_lines=tex_lines,
        qmd_lines=qmd_lines,
        total_boxes=len(raw_boxes),
        substantive_boxes=substantive_cnt,
        present_boxes=present_cnt,
        partial_boxes=partial_cnt,
        absent_boxes=absent_cnt,
        quarto_callouts_count=quarto_callouts,
        quarto_bold_labels_count=quarto_bold_labels,
        boxes=boxed_items,
    )


def audit_book_boxed_items(
    book_dir: Path,
    book_title: str = "The_Physics_of_Golf",
    ngram_size: int = 5,
) -> BookBoxAudit:
    """Audit all chapter pairs for a given book directory."""
    tex_dir = book_dir / "chapters"
    qmd_dir = book_dir / "quarto"

    tex_files = sorted(tex_dir.glob("ch*.tex"))

    chapters: list[ChapterBoxAudit] = []
    tot_boxes = 0
    tot_substantive = 0
    tot_present = 0
    tot_partial = 0
    tot_absent = 0
    tot_callouts = 0

    for tex_path in tex_files:
        stem = tex_path.stem
        qmd_path = qmd_dir / f"{stem}.qmd"
        ch_audit = audit_chapter_boxed_items(
            tex_path=tex_path,
            qmd_path=qmd_path if qmd_path.exists() else None,
            ngram_size=ngram_size,
        )
        chapters.append(ch_audit)

        tot_boxes += ch_audit.total_boxes
        tot_substantive += ch_audit.substantive_boxes
        tot_present += ch_audit.present_boxes
        tot_partial += ch_audit.partial_boxes
        tot_absent += ch_audit.absent_boxes
        tot_callouts += ch_audit.quarto_callouts_count

    return BookBoxAudit(
        book_title=book_title,
        total_chapters_audited=len(chapters),
        total_boxes=tot_boxes,
        total_substantive_boxes=tot_substantive,
        total_present_boxes=tot_present,
        total_partial_boxes=tot_partial,
        total_absent_boxes=tot_absent,
        total_quarto_callouts=tot_callouts,
        chapters=chapters,
    )


def format_markdown_report(audit: BookBoxAudit) -> str:
    """Format full audit result as Markdown report."""
    md: list[str] = [
        f"# Boxed Items Parity Audit: {audit.book_title.replace('_', ' ')}",
        "",
        "## Summary Metrics",
        "",
        f"- **Total Chapters Audited**: {audit.total_chapters_audited}",
        f"- **Total LaTeX Boxed Items**: {audit.total_boxes} (Substantive: {audit.total_substantive_boxes})",
        f"- **Present in Quarto (>=50% 5-gram containment)**: {audit.total_present_boxes}",
        f"- **Partially Present in Quarto (10-50% containment)**: {audit.total_partial_boxes}",
        f"- **Absent from Quarto (<10% containment)**: {audit.total_absent_boxes}",
        f"- **Total Quarto Callouts Rendered**: {audit.total_quarto_callouts}",
        "",
        "## Chapter Breakdown",
        "",
        "| Chapter Stem | LaTeX Boxes | Substantive | Present (>=50%) | Partial (10-50%) | Absent (<10%) | Quarto Callouts | TeX / Qmd Lines |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for ch in audit.chapters:
        md.append(
            f"| `{ch.stem}` | {ch.total_boxes} | {ch.substantive_boxes} | {ch.present_boxes} | {ch.partial_boxes} | {ch.absent_boxes} | {ch.quarto_callouts_count} | {ch.tex_lines} / {ch.qmd_lines} |"
        )

    md.extend(
        [
            "",
            "## Absent & Partial Boxed Items Inventory",
            "",
            "| Chapter | Env | Title | Status | Containment | Words | Preview |",
            "| :--- | :--- | :--- | :---: | :---: | :---: | :--- |",
        ]
    )

    for ch in audit.chapters:
        for b in ch.boxes:
            if b.status in ("absent", "partial"):
                title = b.title.replace("|", "\\|") if b.title else "*(Untitled)*"
                preview = b.body_preview.replace("|", "\\|")
                md.append(
                    f"| `{ch.stem}` | `{b.environment}` | {title} | **{b.status.upper()}** | {b.containment_ratio:.1%} | {b.word_count} | {preview} |"
                )

    return "\n".join(md) + "\n"


def format_terminal_summary(audit: BookBoxAudit) -> str:
    """Format concise summary for CLI output."""
    lines: list[str] = [
        f"=== Boxed Items Parity Audit: {audit.book_title} ===",
        f"Total Chapters Audited: {audit.total_chapters_audited}",
        f"Total LaTeX Boxes: {audit.total_boxes} (Substantive: {audit.total_substantive_boxes})",
        f"Present (>=50%): {audit.total_present_boxes}",
        f"Partial (10-50%): {audit.total_partial_boxes}",
        f"Absent (<10%): {audit.total_absent_boxes}",
        f"Total Quarto Callouts: {audit.total_quarto_callouts}",
        "",
        f"{'Chapter Stem':<32} | {'Total':<6} | {'Present':<8} | {'Partial':<8} | {'Absent':<7} | {'Callouts':<8} | {'Lines (Tex/Qmd)':<15}",
        "-" * 95,
    ]
    for ch in audit.chapters:
        lines.append(
            f"{ch.stem:<32} | {ch.total_boxes:<6} | {ch.present_boxes:<8} | {ch.partial_boxes:<8} | {ch.absent_boxes:<7} | {ch.quarto_callouts_count:<8} | {ch.tex_lines}/{ch.qmd_lines:<15}"
        )
    return "\n".join(lines)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Audit boxed items across LaTeX and Quarto mirrors."
    )
    parser.add_argument(
        "--book",
        type=str,
        default="The_Physics_of_Golf",
        help="Book folder name under articles/ (default: The_Physics_of_Golf)",
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Path to repository root",
    )
    parser.add_argument(
        "--chapter",
        type=str,
        default=None,
        help="Audit a single chapter stem (e.g. ch18_inverse_dynamics_parallel)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON format",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Output Markdown report format",
    )
    parser.add_argument(
        "--write-doc",
        action="store_true",
        help="Generate and write docs/THE_PHYSICS_OF_GOLF_BOXED_ITEMS_INVENTORY.md",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path",
    )
    parser.add_argument(
        "--check",
        "--fail-on-discrepancy",
        action="store_true",
        help="Exit with code 1 if absent boxed items exceed allowed threshold",
    )
    parser.add_argument(
        "--threshold-absent",
        type=int,
        default=0,
        help="Maximum allowed absent boxes before --check returns failure (default: 0)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress terminal summary output",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Main CLI entrypoint."""
    parsed_args = parse_args(args)

    if parsed_args.repo_root:
        repo_root = Path(parsed_args.repo_root).resolve()
    else:
        repo_root = Path(__file__).resolve().parents[1]

    book_dir = repo_root / "articles" / parsed_args.book
    if not book_dir.exists():
        write_stderr(f"Error: Book directory not found: {book_dir}")
        return 1

    if parsed_args.chapter:
        tex_path = book_dir / "chapters" / f"{parsed_args.chapter}.tex"
        qmd_path = book_dir / "quarto" / f"{parsed_args.chapter}.qmd"
        if not tex_path.exists():
            write_stderr(f"Error: LaTeX chapter not found: {tex_path}")
            return 1
        ch_audit = audit_chapter_boxed_items(
            tex_path=tex_path,
            qmd_path=qmd_path if qmd_path.exists() else None,
        )
        if parsed_args.json:
            write_stdout(json.dumps(asdict(ch_audit), indent=2))
        elif parsed_args.markdown:
            write_stdout(
                f"## {ch_audit.stem}\n- Total: {ch_audit.total_boxes}\n- Present: {ch_audit.present_boxes}"
            )
        else:
            write_stdout(
                f"Chapter: {ch_audit.stem} | Total Boxes: {ch_audit.total_boxes} | Present: {ch_audit.present_boxes} | Partial: {ch_audit.partial_boxes} | Absent: {ch_audit.absent_boxes}"
            )
        return 0

    book_audit = audit_book_boxed_items(book_dir)

    if parsed_args.write_doc:
        doc_path = repo_root / "docs" / "THE_PHYSICS_OF_GOLF_BOXED_ITEMS_INVENTORY.md"
        doc_content = format_markdown_report(book_audit)
        doc_path.write_text(doc_content, encoding="utf-8")
        logger.info(f"Generated boxed items inventory at {doc_path}")
        if not parsed_args.quiet:
            write_stdout(f"Boxed items documentation written to {doc_path}")

    if parsed_args.json:
        out_str = json.dumps(asdict(book_audit), indent=2)
        if parsed_args.output:
            Path(parsed_args.output).write_text(out_str, encoding="utf-8")
        else:
            write_stdout(out_str)
    elif parsed_args.markdown:
        out_str = format_markdown_report(book_audit)
        if parsed_args.output:
            Path(parsed_args.output).write_text(out_str, encoding="utf-8")
        else:
            write_stdout(out_str)
    elif not parsed_args.quiet:
        write_stdout(format_terminal_summary(book_audit))

    if parsed_args.check:
        if book_audit.total_absent_boxes > parsed_args.threshold_absent:
            write_stderr(
                f"FAILURE: Absent boxed items ({book_audit.total_absent_boxes}) exceed threshold ({parsed_args.threshold_absent})"
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
