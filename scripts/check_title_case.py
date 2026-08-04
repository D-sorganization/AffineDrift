"""Enforce title case in rendered AffineDrift website sources.

The check covers page metadata, Markdown headings, Quarto navigation labels,
figure captions, and literal chart titles. Prose is intentionally out of scope.
Run with ``--fix`` to apply deterministic capitalization corrections.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

MINOR_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "but",
    "by",
    "for",
    "in",
    "nor",
    "of",
    "on",
    "or",
    "per",
    "so",
    "the",
    "to",
    "via",
    "vs",
    "yet",
}

LOWERCASE_TERMS = {"cm", "kg", "km", "m", "mm", "ms", "nm", "rad", "s"}
LOWERCASE_PARTICLES = {"da", "de", "der", "di", "la", "le", "van", "von"}

WORD = re.compile(r"[^\W\d_][^\W_]*(?:['’][^\W_]+)?", re.UNICODE)
PROTECTED = re.compile(
    r"`[^`]+`|\$[^$]+\$|<[^>]+>|https?://\S+|\b[A-Z]\([^)]*\)|"
    r"\([^\s()]*(?:/|\.html)[^\s()]*\)|@[\w:.-]+|\\[A-Za-z]+|"
    r"\\['\"`^~=.uvHtcdbkr]\{?[A-Za-z]\}?|"
    r"\b[\w.-]+\.(?i:qmd|md|py|js|html|css|yml|yaml|bib|pdf|docx|xlsx|pptx)\b"
)
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
YAML_VALUE = re.compile(
    r"^(?P<prefix>\s*(?:title|subtitle|fig-cap|fig-subcap)\s*:\s*)"
    r"(?P<quote>['\"]?)(?P<value>.*?)(?P=quote)\s*$"
)
NAV_VALUE = re.compile(
    r"^(?P<prefix>\s*-?\s*(?:text|section|title)\s*:\s*)"
    r"(?P<quote>['\"]?)(?P<value>.*?)(?P=quote)\s*$"
)
CHART_CALL = re.compile(
    r"\b(?:set_title|suptitle|(?:plt|pyplot)\.title)\s*\(\s*"
    r"(?:[fFrRuUbB]{0,2})?(?P<quote>['\"])(?P<value>.+?)(?P=quote)"
)
CHART_PROPERTY = re.compile(
    r"\btitle\s*(?:=|:)\s*(?:[fFrRuUbB]{0,2})?(?P<quote>['\"])(?P<value>.+?)(?P=quote)"
)
FIGURE_ATTRIBUTE = re.compile(
    r"\bfig-(?:cap|subcap)\s*=\s*(?P<quote>['\"])(?P<value>.+?)(?P=quote)"
)
MARKDOWN_FIGURE = re.compile(r"!\[(?P<value>[^]]+)]\([^)]*\)\s*\{[^}]*#fig-[^}]*}")
TRAILING_ATTRIBUTES = re.compile(r"\s*\{[^{}]*}\s*$")

EXCLUDED_PARTS = {
    ".git",
    ".quarto",
    "docs",
    "legacy-pages",
    "node_modules",
    "Drafts_Original_Articles",
    "tangent-hyperplane-contraction",
}
SOURCE_DIRECTORIES = (
    "articles",
    "books",
    "critiques",
    "models",
    "pages",
    "repositories",
    "resources",
)
PYTHON_SOURCE_DIRECTORIES = ("content", "src")

CANONICAL_LITERALS = {
    "@Sec-": "@sec-",
    r"\Quad": r"\quad",
    r"Poincar\'E": r"Poincar\'e",
    "FréChet": "Fréchet",
    "GâTeaux": "Gâteaux",
    "GrüBler": "Grübler",
    "NaïVe": "Naïve",
    "SchöLlhorn": "Schöllhorn",
    "Van Der Pol": "van der Pol",
    "δX": "δx",
    "1 Km to 10 M": "1 km to 10 m",
    "50--100 Ms": "50--100 ms",
}


@dataclass(frozen=True)
class Finding:
    """One title whose capitalization differs from the project standard."""

    path: Path
    line: int
    kind: str
    actual: str
    expected: str


def _protected_spans(value: str) -> list[tuple[int, int]]:
    """Return spans containing code, math, tags, or link destinations."""
    return [(match.start(), match.end()) for match in PROTECTED.finditer(value)]


def _is_protected(start: int, spans: list[tuple[int, int]]) -> bool:
    """Whether a word begins inside a protected span."""
    return any(span_start <= start < span_end for span_start, span_end in spans)


def _capitalize_word(word: str) -> str:
    """Capitalize a normal word while preserving acronyms and product names."""
    if word.isupper() or (any(char.isupper() for char in word[1:]) and not word.istitle()):
        return word
    return word[:1].upper() + word[1:]


def _replacement_for_word(word: str, *, boundary: bool, compound_edge: bool) -> str:
    """Apply title rules to one word with enough context for edge cases."""
    lowered = word.lower()
    if len(word) > 1 and word.isupper():
        return word
    if not word[0].isascii() and word[1:].isascii():
        return word
    if word.islower() and (lowered in LOWERCASE_PARTICLES or lowered in LOWERCASE_TERMS):
        return word
    if len(word) == 1 and word.islower() and lowered != "a":
        return word
    if lowered in MINOR_WORDS and not boundary and not compound_edge:
        return lowered
    return _capitalize_word(word)


def _canonicalize_literals(value: str) -> str:
    """Restore case-sensitive names, notation, commands, cross-references, and units."""
    for actual, canonical in CANONICAL_LITERALS.items():
        value = value.replace(actual, canonical)
    value = re.sub(r"\bso(?=\(\d+\))", "SO", value)
    return re.sub(
        r"\.(Qmd|Md|Py|Js|Html|Css|Yml|Yaml|Bib|Pdf|Docx|Xlsx|Pptx)\b",
        lambda match: match.group().lower(),
        value,
    )


def expected_title(value: str) -> str:
    """Return ``value`` in APA-style title capitalization."""
    value = _canonicalize_literals(value)
    spans = _protected_spans(value)
    matches = [match for match in WORD.finditer(value) if not _is_protected(match.start(), spans)]
    if not matches:
        return value

    pieces: list[str] = []
    cursor = 0
    previous_end = 0
    for index, match in enumerate(matches):
        pieces.append(value[cursor : match.start()])
        word = match.group()
        separator = value[previous_end : match.start()]
        protected_after = any(span_start >= match.end() for span_start, _ in spans)
        is_last = index == len(matches) - 1 and not protected_after
        punctuation_boundary = bool(re.search(r"(?:[:!?—–]|-{2,}|[([{])\s*$", separator))
        if separator.lstrip().startswith(".") and matches[index - 1].group().lower() != "vs":
            punctuation_boundary = True
        boundary = index == 0 or is_last or punctuation_boundary
        hyphens = "-‐‑"
        compound_edge = (match.start() > 0 and value[match.start() - 1] in hyphens) != (
            match.end() < len(value) and value[match.end()] in hyphens
        )
        replacement = _replacement_for_word(word, boundary=boundary, compound_edge=compound_edge)
        pieces.append(replacement)
        cursor = match.end()
        previous_end = match.end()
    pieces.append(value[cursor:])
    return "".join(pieces)


def _finding(path: Path, line_number: int, kind: str, value: str) -> Finding | None:
    """Build a finding when a nonempty literal title needs correction."""
    clean = value.strip()
    if not clean or clean in {"---", "—"} or "{{" in clean:
        return None
    expected = expected_title(clean)
    if expected == clean:
        return None
    return Finding(path, line_number, kind, clean, expected)


def _append_match(
    findings: list[Finding], path: Path, line_number: int, kind: str, match: re.Match[str] | None
) -> None:
    """Append a regex match as a finding when it violates title case."""
    if match is None:
        return
    finding = _finding(path, line_number, kind, match.group("value"))
    if finding is not None and finding not in findings:
        findings.append(finding)


def findings_for_text(path: Path, text: str) -> list[Finding]:
    """Find title-case violations in one Quarto source or configuration file."""
    if path.suffix == ".py":
        return _python_chart_findings(path, text)

    findings: list[Finding] = []
    in_fence = False
    is_config = path.name == "_quarto.yml"
    in_frontmatter = False

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if line_number == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and stripped == "---":
            in_frontmatter = False
            continue
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue

        if is_config:
            _append_match(findings, path, line_number, "navigation label", NAV_VALUE.match(line))
            continue

        if in_frontmatter:
            match = YAML_VALUE.match(line)
            if match is not None:
                kind = "page title" if "title" in match.group("prefix") else "figure caption"
                _append_match(findings, path, line_number, kind, match)
            continue

        if not in_fence:
            heading = HEADING.match(line)
            if heading is not None:
                value = TRAILING_ATTRIBUTES.sub("", heading.group(2)).strip()
                finding = _finding(path, line_number, "heading", value)
                if finding is not None:
                    findings.append(finding)
            figure_attribute = FIGURE_ATTRIBUTE.search(line)
            _append_match(findings, path, line_number, "figure caption", figure_attribute)
            if figure_attribute is None:
                _append_match(
                    findings, path, line_number, "figure caption", MARKDOWN_FIGURE.search(line)
                )
        else:
            yaml_match = YAML_VALUE.match(line.removeprefix("#| "))
            if yaml_match is not None and "fig-" in yaml_match.group("prefix"):
                _append_match(findings, path, line_number, "figure caption", yaml_match)
            _append_match(findings, path, line_number, "chart title", CHART_CALL.search(line))
            _append_match(findings, path, line_number, "chart title", CHART_PROPERTY.search(line))

    return findings


def _chart_call_name(node: ast.Call) -> str | None:
    """Return the plotting title method name for a Python call, if applicable."""
    function = node.func
    if not isinstance(function, ast.Attribute):
        return None
    if function.attr in {"set_title", "suptitle"}:
        return function.attr
    if function.attr == "title" and isinstance(function.value, ast.Name):
        if function.value.id in {"plt", "pyplot"}:
            return function.attr
    return None


def _string_segments(node: ast.AST) -> list[tuple[int, str]]:
    """Return literal string segments and source lines from a chart-title expression."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [(node.lineno, node.value)]
    if isinstance(node, ast.JoinedStr):
        segments: list[tuple[int, str]] = []
        for value in node.values:
            segments.extend(_string_segments(value))
        return segments
    return []


def _python_chart_findings(path: Path, text: str) -> list[Finding]:
    """Find literal Matplotlib chart titles in Python modules using the AST."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _chart_call_name(node) is None or not node.args:
            continue
        for line_number, value in _string_segments(node.args[0]):
            finding = _finding(path, line_number, "chart title", value)
            if finding is not None:
                findings.append(finding)
    return findings


def source_files(root: Path) -> list[Path]:
    """Return source files that Quarto can publish for the website."""
    paths = [path for path in root.glob("*.qmd") if path.is_file()]
    for directory in SOURCE_DIRECTORIES:
        source_root = root / directory
        if source_root.exists():
            paths.extend(source_root.rglob("*.qmd"))
    for directory in PYTHON_SOURCE_DIRECTORIES:
        source_root = root / directory
        if source_root.exists():
            paths.extend(source_root.rglob("*.py"))
    paths.extend(root.rglob("_quarto.yml"))
    return sorted(
        {
            path
            for path in paths
            if not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
            and path.name not in {"CRITICS_CORNER.qmd", "INLINE_SUGGESTIONS.md"}
        }
    )


def apply_fixes(text: str, findings: list[Finding]) -> str:
    """Apply findings by line so identical prose elsewhere remains untouched."""
    lines = text.splitlines(keepends=True)
    for finding in findings:
        index = finding.line - 1
        lines[index] = lines[index].replace(finding.actual, finding.expected, 1)
    return "".join(lines)


def main() -> int:
    """Check all publishable sources, optionally applying safe corrections."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--fix", action="store_true")
    args = parser.parse_args()

    all_findings: list[Finding] = []
    checked = source_files(args.root)
    for path in checked:
        with path.open(encoding="utf-8", errors="replace", newline="") as handle:
            text = handle.read()
        findings = findings_for_text(path.relative_to(args.root), text)
        all_findings.extend(findings)
        if args.fix and findings:
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(apply_fixes(text, findings))

    if args.fix:
        print(f"  corrected {len(all_findings)} title(s) in {len(checked)} source file(s)")
        return 0
    for finding in all_findings:
        print(
            f"  {finding.path.as_posix()}:{finding.line}: {finding.kind} "
            f"'{finding.actual}' -> '{finding.expected}'"
        )
    if all_findings:
        print(f"\n  {len(all_findings)} title-case violation(s)")
        return 1
    print(f"  {len(checked)} source file(s) checked, all titles use title case")
    return 0


if __name__ == "__main__":
    sys.exit(main())
