#!/usr/bin/env python3
"""Cross-tree audit of citations between LaTeX book and Quarto website mirrors.

Audits textbook chapters (default: The Physics of Golf) to detect citation parity,
sentence alignment, mechanical restoration candidates, and citation drift between
LaTeX (.tex) and Quarto (.qmd) mirrors.

Usage:
    python scripts/audit_book_citations.py
    python scripts/audit_book_citations.py --json
    python scripts/audit_book_citations.py --markdown
    python scripts/audit_book_citations.py --write-doc
    python scripts/audit_book_citations.py --check
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path

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

# LaTeX citation regex matching \cite, \citep, \citet, \citeauthor, \citeyear, \citealt, \citealp
RE_LATEX_CITE = re.compile(
    r"\\(?:cite[ptalyp]*|citeauthor|citeyear|citealt|citealp)\*?(?:\[[^\]]*\])*\{([^}]+)\}"
)

# Quarto citation regex matching @key or [@key]
RE_QUARTO_CITE = re.compile(r"(?<![\w/])@([A-Za-z0-9][A-Za-z0-9:._/-]*)")

# Non-citation cross-reference prefixes in Quarto
NON_CITATION_PREFIXES: tuple[str, ...] = (
    "fig-",
    "sec-",
    "tbl-",
    "tab-",
    "eq-",
    "app-",
    "ch-",
    "q-",
    "fig:",
    "sec:",
    "tbl:",
    "tab:",
    "eq:",
    "app:",
    "ch:",
    "q:",
)


@dataclass
class CitationOccurrence:
    """Represents a citation instance in LaTeX with its host sentence."""

    keys: list[str]
    tex_sentence: str
    best_qmd_sentence: str
    similarity: float
    missing_in_qmd_chapter: list[str]
    classification: str  # 'exact_match', 'near_match', 'rewritten', 'dropped'


@dataclass
class ChapterCitationAudit:
    """Audit results for one chapter pair."""

    stem: str
    tex_path: str
    qmd_path: str | None
    tex_unique_keys: list[str]
    qmd_unique_keys: list[str]
    shared_keys: list[str]
    book_only_keys: list[str]
    mirror_only_keys: list[str]
    total_tex_citations: int
    total_qmd_citations: int
    mechanical_restoration_candidates: int
    occurrences: list[CitationOccurrence]


@dataclass
class BookCitationAudit:
    """Audit results across an entire book."""

    book_title: str
    total_chapters_audited: int
    all_tex_unique_keys_count: int
    all_qmd_unique_keys_count: int
    shared_keys_count: int
    book_only_keys_count: int
    mirror_only_keys_count: int
    all_book_only_keys: list[str]
    all_mirror_only_keys: list[str]
    total_mechanical_candidates: int
    chapters: list[ChapterCitationAudit]


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


def normalize_words(text: str) -> str:
    """Extract and normalize plain word sequence for robust sentence comparison."""
    # Remove LaTeX commands and inline math/formatting
    cleaned = re.sub(r"\\[a-zA-Z]+(?:\*|\+)?(?:\[[^\]]*\])?(?:\{[^\}]*\})*", " ", text)
    cleaned = re.sub(r"[{}\\_^$#&~@`*|#><\[\]\(\)\"\':;=]", " ", cleaned)
    words = re.findall(r"[a-z0-9]+", cleaned.lower())
    return " ".join(words)


def extract_sentences(text: str) -> list[str]:
    """Split text into sentence blocks based on terminal punctuation."""
    normalized = re.sub(r"\s+", " ", text)
    raw_sentences = re.split(r"(?<=[.!?])\s+", normalized)
    return [s.strip() for s in raw_sentences if len(s.strip()) > 5]


def parse_latex_citations(tex_content: str) -> tuple[set[str], list[tuple[list[str], str]]]:
    """Extract unique citation keys and all citation occurrences with host sentences."""
    clean_tex = strip_latex_comments(tex_content)
    unique_keys: set[str] = set()
    occurrences: list[tuple[list[str], str]] = []

    sentences = extract_sentences(clean_tex)
    for sent in sentences:
        matches = list(RE_LATEX_CITE.finditer(sent))
        if not matches:
            continue
        sent_keys: list[str] = []
        for m in matches:
            raw_keys = [k.strip() for k in m.group(1).split(",") if k.strip()]
            for k in raw_keys:
                unique_keys.add(k)
                sent_keys.append(k)
        if sent_keys:
            occurrences.append((sent_keys, sent))

    return unique_keys, occurrences


def parse_quarto_citations(qmd_content: str) -> set[str]:
    """Extract unique bibliography keys cited in Quarto document."""
    unique_keys: set[str] = set()
    for m in RE_QUARTO_CITE.finditer(qmd_content):
        key = m.group(1)
        if any(key.startswith(p) for p in NON_CITATION_PREFIXES):
            continue
        unique_keys.add(key)
    return unique_keys


def audit_chapter_citations(
    tex_path: Path,
    qmd_path: Path | None,
    similarity_threshold: float = 0.85,
) -> ChapterCitationAudit:
    """Audit citations for a single LaTeX / Quarto chapter pair."""
    stem = tex_path.stem
    tex_content = tex_path.read_text(encoding="utf-8")

    qmd_content = ""
    if qmd_path and qmd_path.exists():
        qmd_content = qmd_path.read_text(encoding="utf-8")

    tex_keys, tex_occurrences = parse_latex_citations(tex_content)
    qmd_keys = parse_quarto_citations(qmd_content)

    qmd_sentences = extract_sentences(qmd_content)
    qmd_sentences_norm = [
        (s, normalize_words(s), set(normalize_words(s).split())) for s in qmd_sentences
    ]

    shared_keys = tex_keys.intersection(qmd_keys)
    book_only_keys = tex_keys - qmd_keys
    mirror_only_keys = qmd_keys - tex_keys

    occurrences_data: list[CitationOccurrence] = []
    mechanical_candidates = 0

    for keys, sent_tex in tex_occurrences:
        sent_tex_norm = normalize_words(sent_tex)
        sent_tex_words = set(sent_tex_norm.split())
        len_tex = len(sent_tex_norm)
        best_sim = 0.0
        best_qmd = ""

        for raw_q, norm_q, q_words in qmd_sentences_norm:
            if not norm_q:
                continue
            len_q = len(norm_q)
            if len_tex > 0 and (len_q > 3 * len_tex or len_tex > 3 * len_q):
                continue
            if len_tex > 30 and len(sent_tex_words & q_words) < 2:
                continue
            sim = SequenceMatcher(None, sent_tex_norm, norm_q).ratio()
            if sim > best_sim:
                best_sim = sim
                best_qmd = raw_q

        missing_in_ch = [k for k in keys if k not in qmd_keys]

        if best_sim >= 0.95:
            classification = "exact_match"
        elif best_sim >= similarity_threshold:
            classification = "near_match"
        elif best_sim >= 0.40:
            classification = "rewritten"
        else:
            classification = "dropped"

        if missing_in_ch and best_sim >= similarity_threshold:
            mechanical_candidates += 1

        occurrences_data.append(
            CitationOccurrence(
                keys=keys,
                tex_sentence=sent_tex[:180],
                best_qmd_sentence=best_qmd[:180] if best_qmd else "",
                similarity=round(best_sim, 4),
                missing_in_qmd_chapter=missing_in_ch,
                classification=classification,
            )
        )

    return ChapterCitationAudit(
        stem=stem,
        tex_path=str(tex_path),
        qmd_path=str(qmd_path) if qmd_path else None,
        tex_unique_keys=sorted(tex_keys),
        qmd_unique_keys=sorted(qmd_keys),
        shared_keys=sorted(shared_keys),
        book_only_keys=sorted(book_only_keys),
        mirror_only_keys=sorted(mirror_only_keys),
        total_tex_citations=len(tex_occurrences),
        total_qmd_citations=len(re.findall(RE_QUARTO_CITE, qmd_content)),
        mechanical_restoration_candidates=mechanical_candidates,
        occurrences=occurrences_data,
    )


def audit_book_citations(
    book_dir: Path,
    book_title: str = "The_Physics_of_Golf",
    similarity_threshold: float = 0.85,
) -> BookCitationAudit:
    """Audit citations across all chapters of a book directory."""
    tex_dir = book_dir / "chapters"
    qmd_dir = book_dir / "quarto"

    tex_files = sorted(tex_dir.glob("ch*.tex"))

    chapters: list[ChapterCitationAudit] = []
    all_tex_keys: set[str] = set()
    all_qmd_keys: set[str] = set()
    total_candidates = 0

    for tex_path in tex_files:
        stem = tex_path.stem
        qmd_path = qmd_dir / f"{stem}.qmd"
        ch_audit = audit_chapter_citations(
            tex_path=tex_path,
            qmd_path=qmd_path if qmd_path.exists() else None,
            similarity_threshold=similarity_threshold,
        )
        chapters.append(ch_audit)
        all_tex_keys.update(ch_audit.tex_unique_keys)
        all_qmd_keys.update(ch_audit.qmd_unique_keys)
        total_candidates += ch_audit.mechanical_restoration_candidates

    shared = all_tex_keys.intersection(all_qmd_keys)
    book_only = all_tex_keys - all_qmd_keys
    mirror_only = all_qmd_keys - all_tex_keys

    return BookCitationAudit(
        book_title=book_title,
        total_chapters_audited=len(chapters),
        all_tex_unique_keys_count=len(all_tex_keys),
        all_qmd_unique_keys_count=len(all_qmd_keys),
        shared_keys_count=len(shared),
        book_only_keys_count=len(book_only),
        mirror_only_keys_count=len(mirror_only),
        all_book_only_keys=sorted(book_only),
        all_mirror_only_keys=sorted(mirror_only),
        total_mechanical_candidates=total_candidates,
        chapters=chapters,
    )


def format_markdown_report(audit: BookCitationAudit) -> str:
    """Format full citation audit as Markdown report."""
    md: list[str] = [
        f"# Citations Parity Audit: {audit.book_title.replace('_', ' ')}",
        "",
        "## Summary Metrics",
        "",
        f"- **Total Chapters Audited**: {audit.total_chapters_audited}",
        f"- **Total Unique Keys in LaTeX Book**: {audit.all_tex_unique_keys_count}",
        f"- **Total Unique Keys in Quarto Mirror**: {audit.all_qmd_unique_keys_count}",
        f"- **Shared Unique Keys**: {audit.shared_keys_count}",
        f"- **Book-Only Unique Keys (Global)**: {audit.book_only_keys_count}",
        f"- **Mirror-Only Unique Keys (Global)**: {audit.mirror_only_keys_count}",
        f"- **Mechanical Restoration Candidates (Similarity >= 0.85)**: {audit.total_mechanical_candidates}",
        "",
        "## Chapter Citation Parity Matrix",
        "",
        "| Chapter Stem | LaTeX Keys | Quarto Keys | Shared | Book-Only | Mirror-Only | Mech Candidates |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for ch in audit.chapters:
        b_only = len(ch.book_only_keys)
        m_only = len(ch.mirror_only_keys)
        md.append(
            f"| `{ch.stem}` | {len(ch.tex_unique_keys)} | {len(ch.qmd_unique_keys)} | {len(ch.shared_keys)} | {b_only} | {m_only} | {ch.mechanical_restoration_candidates} |"
        )

    md.extend(
        [
            "",
            "## Chapter Divergence Details",
            "",
        ]
    )

    for ch in audit.chapters:
        if ch.book_only_keys or ch.mirror_only_keys:
            md.append(f"### `{ch.stem}`")
            if ch.book_only_keys:
                md.append(
                    f"- **Book-Only Keys**: {', '.join([f'`{k}`' for k in ch.book_only_keys])}"
                )
            if ch.mirror_only_keys:
                md.append(
                    f"- **Mirror-Only Keys**: {', '.join([f'`{k}`' for k in ch.mirror_only_keys])}"
                )
            md.append("")

    return "\n".join(md) + "\n"


def format_terminal_summary(audit: BookCitationAudit) -> str:
    """Format concise summary for CLI output."""
    lines: list[str] = [
        f"=== Citation Parity Audit: {audit.book_title} ===",
        f"Total Chapters Audited: {audit.total_chapters_audited}",
        f"Total Unique Keys in LaTeX: {audit.all_tex_unique_keys_count}",
        f"Total Unique Keys in Quarto: {audit.all_qmd_unique_keys_count}",
        f"Shared Keys: {audit.shared_keys_count}",
        f"Book-Only Keys: {audit.book_only_keys_count}",
        f"Mirror-Only Keys: {audit.mirror_only_keys_count}",
        f"Mechanical Restoration Candidates: {audit.total_mechanical_candidates}",
        "",
        f"{'Chapter Stem':<32} | {'LaTeX':<6} | {'Quarto':<7} | {'Shared':<7} | {'Book-Only':<10} | {'Mirror-Only':<12}",
        "-" * 85,
    ]
    for ch in audit.chapters:
        lines.append(
            f"{ch.stem:<32} | {len(ch.tex_unique_keys):<6} | {len(ch.qmd_unique_keys):<7} | {len(ch.shared_keys):<7} | {len(ch.book_only_keys):<10} | {len(ch.mirror_only_keys):<12}"
        )
    return "\n".join(lines)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Audit citation parity between LaTeX and Quarto mirrors."
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
        help="Audit a single chapter stem (e.g. ch05_affine_structure)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Sentence similarity threshold for mechanical match (default: 0.85)",
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
        help="Generate and write docs/THE_PHYSICS_OF_GOLF_CITATIONS_AUDIT.md",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check citation parity and report status",
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
        ch_audit = audit_chapter_citations(
            tex_path=tex_path,
            qmd_path=qmd_path if qmd_path.exists() else None,
            similarity_threshold=parsed_args.threshold,
        )
        book_audit = BookCitationAudit(
            book_title=book_dir.name,
            total_chapters_audited=1,
            all_tex_unique_keys_count=len(ch_audit.tex_unique_keys),
            all_qmd_unique_keys_count=len(ch_audit.qmd_unique_keys),
            shared_keys_count=len(ch_audit.shared_keys),
            book_only_keys_count=len(ch_audit.book_only_keys),
            mirror_only_keys_count=len(ch_audit.mirror_only_keys),
            all_book_only_keys=ch_audit.book_only_keys,
            all_mirror_only_keys=ch_audit.mirror_only_keys,
            total_mechanical_candidates=ch_audit.mechanical_restoration_candidates,
            chapters=[ch_audit],
        )
    else:
        book_audit = audit_book_citations(
            book_dir,
            book_title=book_dir.name,
            similarity_threshold=parsed_args.threshold,
        )

    markdown_output = format_markdown_report(book_audit)
    json_output = json.dumps(asdict(book_audit), indent=2)

    if parsed_args.write_doc:
        doc_path = repo_root / "docs" / f"{parsed_args.book.upper()}_CITATIONS_AUDIT.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(markdown_output, encoding="utf-8")
        logger.info("Generated citations audit at %s", doc_path)
        write_stdout(f"Citations documentation written to {doc_path}")

    if parsed_args.output:
        out_path = Path(parsed_args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if parsed_args.json:
            out_path.write_text(json_output, encoding="utf-8")
        else:
            out_path.write_text(markdown_output, encoding="utf-8")
        write_stdout(f"Report written to {out_path}")

    if parsed_args.json:
        write_stdout(json_output)
    elif parsed_args.markdown:
        write_stdout(markdown_output)
    elif not parsed_args.quiet:
        write_stdout(format_terminal_summary(book_audit))

    return 0


if __name__ == "__main__":
    sys.exit(main())
