#!/usr/bin/env python3
"""Advisory readability scoring for reader-facing prose (WEB-12.5).

Computes the Flesch-Kincaid grade level for the three content layers named
by WEB-12.1's readability targets: "lay blocks" (the "In Layman's Terms"
sections embedded in ``articles/**/*.qmd``), the ``summary-plain``
frontmatter field, and hub pages. Math, code, and Quarto/Markdown/HTML
markup are stripped before scoring so syntax cannot inflate a grade level.

Advisory only: the CI step wires this script with ``continue-on-error:
true`` and uploads the JSON report as a build artifact, matching the
existing MATLAB-quality-check pattern in ``ci-standard.yml``.

Run as a CLI from the repo root::

    python3 -m scripts.check_readability
    python3 -m scripts.check_readability --threshold 10 --report readability-report.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from src.core.contracts import require
from src.tools.utils.frontmatter import split_frontmatter

# WEB-12.1: "readability targets per layer (lay block <= grade 10; body
# unconstrained)". WEB-12.4 applies the same grade-10 target to hub pages.
# summary-plain is reader-entry prose like a lay block, so it shares the
# threshold too; override with --threshold if WEB-12.1 lands a different
# number for one layer.
DEFAULT_GRADE_THRESHOLD: Final = 10.0

# WEB-12.4's rewrite scope: home page, Overview, About, Tools, Technology,
# the Resources hub and Learning Paths index, and the Books hub. Pages not
# yet created (e.g. a future "Start Here") are simply absent from the scan;
# override with --hub-page once they exist.
DEFAULT_HUB_PAGES: Final[tuple[str, ...]] = (
    "index.qmd",
    "pages/overview.qmd",
    "pages/about.qmd",
    "pages/tools.qmd",
    "pages/technology.qmd",
    "resources/resources.qmd",
    "resources/learning-paths.qmd",
    "books/index.qmd",
)

# Mirrors SITEMAP_CONTENT_DIRS in scripts/generate_sitemap.py: the full set
# of directories that hold reader-facing QMD content.
DEFAULT_QMD_GLOBS: Final[tuple[str, ...]] = (
    "*.qmd",
    "pages/*.qmd",
    "resources/*.qmd",
    "books/*.qmd",
    "critiques/*.qmd",
    "models/*.qmd",
    "repositories/*.qmd",
    "articles/**/*.qmd",
)

_LAY_SECTION_RE = re.compile(r'<section class="laymans-terms">(.*?)</section>', re.DOTALL)
_LAY_CONTENT_MARKER: Final = 'laymans-terms-content"'
# Shared component form (#4494), rendered by scripts/filters/laymans-terms.lua.
_LAY_COMPONENT_RE = re.compile(
    r"^::: \{\.laymans-terms\}\n```\{=html\}\n(.*?)\n```\n:::$", re.DOTALL | re.MULTILINE
)

_SHORTCODE_RE = re.compile(r"\{\{<.*?>\}\}", re.DOTALL)
_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_DISPLAY_MATH_RE = re.compile(r"\$\$.*?\$\$", re.DOTALL)
_INLINE_MATH_RE = re.compile(r"\$[^$\n]+\$")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s*", re.MULTILINE)
_DIV_FENCE_RE = re.compile(r"^\s*:::.*$", re.MULTILINE)
_ATTR_BRACE_RE = re.compile(r"\{[^}\n]*\}")
_EMPHASIS_RE = re.compile(r"[*_]{1,3}")

_WORD_RE = re.compile(r"[A-Za-z']+")
_SENTENCE_SPLIT_RE = re.compile(r"[.!?]+(?:\s|$)")


# ─── Pure text helpers (no I/O; easy to test) ───────────────────────────
def strip_code_and_math(text: str) -> str:
    """Remove Quarto shortcodes, fenced/inline code, and inline/display math.

    Order matters: code fences may contain ``$`` characters that would
    otherwise look like math delimiters once the fence is gone.
    """
    text = _SHORTCODE_RE.sub(" ", text)
    text = _FENCED_CODE_RE.sub(" ", text)
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _DISPLAY_MATH_RE.sub(" ", text)
    text = _INLINE_MATH_RE.sub(" ", text)
    return text


def strip_markdown_and_html(text: str) -> str:
    """Reduce Markdown/Quarto/HTML furniture to plain prose."""
    text = _HTML_COMMENT_RE.sub(" ", text)
    text = _MD_IMAGE_RE.sub(" ", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _HTML_TAG_RE.sub(" ", text)
    text = _HEADING_RE.sub("", text)
    text = _DIV_FENCE_RE.sub(" ", text)
    text = _ATTR_BRACE_RE.sub(" ", text)
    text = _EMPHASIS_RE.sub("", text)
    return text


def count_syllables(word: str) -> int:
    """Heuristic vowel-group syllable count (standard FK-grade approximation)."""
    word = word.lower()
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and not word.endswith("le") and count > 1:
        count -= 1
    return max(count, 1)


@dataclass(frozen=True, slots=True)
class ReadabilityScore:
    """A single passage's Flesch-Kincaid grade level and word count."""

    grade: float
    word_count: int


def score_prose(raw_text: str) -> ReadabilityScore | None:
    """Flesch-Kincaid Grade Level for ``raw_text`` after stripping non-prose.

    Returns:
        A score, or ``None`` if no scorable prose remains (e.g. the passage
        was entirely code or math).
    """
    prose = strip_markdown_and_html(strip_code_and_math(raw_text))
    words = _WORD_RE.findall(prose)
    if not words:
        return None
    sentences = [s for s in _SENTENCE_SPLIT_RE.split(prose) if s.strip()]
    sentence_count = max(len(sentences), 1)
    syllable_count = sum(count_syllables(w) for w in words)
    grade = 0.39 * (len(words) / sentence_count) + 11.8 * (syllable_count / len(words)) - 15.59
    return ReadabilityScore(grade=max(grade, 0.0), word_count=len(words))


# ─── Layer extraction ────────────────────────────────────────────────────
def extract_lay_blocks(content: str) -> list[str]:
    """Return the raw HTML of each "In Layman's Terms" block in ``content``.

    Recognises both the legacy inline ``<section>`` and the shared
    ``::: {.laymans-terms}`` component, whose raw-HTML fence lines are dropped.
    """
    blocks = []
    for section in _LAY_SECTION_RE.findall(content):
        marker = section.find(_LAY_CONTENT_MARKER)
        blocks.append(section[marker:] if marker != -1 else section)
    blocks.extend(_LAY_COMPONENT_RE.findall(content))
    return blocks


def extract_summary_plain(content: str) -> str | None:
    """Return the ``summary-plain`` frontmatter field, or ``None`` if absent."""
    fm, _ = split_frontmatter(content)
    value = fm.get("summary-plain")
    if value is None:
        return None
    text = str(value).strip()
    return text or None


# ─── Finding record ──────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class ReadabilityFinding:
    """A single scored passage.

    Attributes:
        path: Repo-root-relative POSIX path of the source file.
        layer: One of ``"lay-block"``, ``"summary-plain"``, ``"hub-page"``.
        grade: The computed Flesch-Kincaid grade level.
        threshold: The grade-level threshold this passage was checked against.
        word_count: Number of scorable words in the passage.
    """

    path: str
    layer: str
    grade: float
    threshold: float
    word_count: int

    @property
    def over_threshold(self) -> bool:
        return self.grade > self.threshold

    def format(self) -> str:
        flag = "OVER" if self.over_threshold else "ok"
        return (
            f"{self.path} [{self.layer}]: grade {self.grade:.1f} "
            f"({flag}, threshold {self.threshold:.0f}, {self.word_count} words)"
        )


# ─── Configuration ───────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class ReadabilityConfig:
    """All knobs the checker exposes.

    Defaults mirror WEB-12.5 scope: lay blocks and ``summary-plain`` across
    all reader-facing QMD content, plus the WEB-12.4 hub-page list.
    """

    repo_root: Path
    qmd_globs: tuple[str, ...] = DEFAULT_QMD_GLOBS
    hub_pages: tuple[str, ...] = DEFAULT_HUB_PAGES
    threshold: float = DEFAULT_GRADE_THRESHOLD


def _iter_qmd_files(root: Path, globs: tuple[str, ...]) -> list[Path]:
    """Resolve a glob list to existing file paths under ``root``, sorted, deduped."""
    seen: set[Path] = set()
    for pattern in globs:
        for path in root.glob(pattern):
            if path.is_file():
                seen.add(path)
    return sorted(seen)


def _findings_for_file(
    path: Path, rel: str, hub_page_paths: set[Path], threshold: float
) -> list[ReadabilityFinding]:
    content = path.read_text(encoding="utf-8", errors="replace")
    findings: list[ReadabilityFinding] = []

    for block in extract_lay_blocks(content):
        score = score_prose(block)
        if score is not None:
            findings.append(
                ReadabilityFinding(rel, "lay-block", score.grade, threshold, score.word_count)
            )

    summary_plain = extract_summary_plain(content)
    if summary_plain is not None:
        score = score_prose(summary_plain)
        if score is not None:
            findings.append(
                ReadabilityFinding(rel, "summary-plain", score.grade, threshold, score.word_count)
            )

    if path.resolve() in hub_page_paths:
        _, body = split_frontmatter(content)
        score = score_prose(body)
        if score is not None:
            findings.append(
                ReadabilityFinding(rel, "hub-page", score.grade, threshold, score.word_count)
            )

    return findings


# ─── Public API ───────────────────────────────────────────────────────────
def check_repository(config: ReadabilityConfig) -> list[ReadabilityFinding]:
    """Return every readability finding under ``config.repo_root``.

    Preconditions:
        ``config.repo_root`` must exist and be a directory.
        ``config.threshold`` must be positive.

    Returns:
        Findings for every scorable lay block, ``summary-plain`` field, and
        hub page found. Empty list if none were found.
    """
    require(
        config.repo_root.is_dir(),
        f"repo_root does not exist or is not a directory: {config.repo_root}",
    )
    require(config.threshold > 0, "threshold must be positive")

    root = config.repo_root
    hub_page_paths = {(root / p).resolve() for p in config.hub_pages}

    findings: list[ReadabilityFinding] = []
    for path in _iter_qmd_files(root, config.qmd_globs):
        rel = path.relative_to(root).as_posix()
        findings.extend(_findings_for_file(path, rel, hub_page_paths, config.threshold))
    return findings


def write_json_report(
    findings: list[ReadabilityFinding], report_path: Path, threshold: float
) -> None:
    """Write the full finding set to a JSON report artifact."""
    payload = {
        "threshold": threshold,
        "scored": len(findings),
        "over_threshold": sum(1 for f in findings if f.over_threshold),
        "findings": [
            {
                "path": f.path,
                "layer": f.layer,
                "grade": round(f.grade, 2),
                "threshold": f.threshold,
                "word_count": f.word_count,
                "over_threshold": f.over_threshold,
            }
            for f in findings
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """CLI entry. Returns the conventional process exit code.

    Advisory: CI wires this with ``continue-on-error: true``, so a non-zero
    return here does not fail the build; it only signals that the printed
    findings and JSON report contain over-threshold passages.
    """
    parser = argparse.ArgumentParser(description="Advisory readability scoring (WEB-12.5).")
    parser.add_argument(
        "repo_root", nargs="?", default=".", type=Path, help="Repository root to scan."
    )
    parser.add_argument("--threshold", type=float, default=DEFAULT_GRADE_THRESHOLD)
    parser.add_argument("--report", type=Path, default=Path("readability-report.json"))
    args = parser.parse_args(argv)

    config = ReadabilityConfig(repo_root=args.repo_root.resolve(), threshold=args.threshold)
    findings = check_repository(config)
    write_json_report(findings, args.report, config.threshold)

    over = [f for f in findings if f.over_threshold]
    if not over:
        print(
            f"readability: OK — {len(findings)} block(s) at or under grade {config.threshold:.0f}"
        )
    else:
        for f in over:
            print(f.format())
        print(
            f"\nreadability: {len(over)}/{len(findings)} block(s) over grade {config.threshold:.0f}"
        )
    print(f"report written to {args.report}")
    return 1 if over else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
