#!/usr/bin/env python3
"""Enforce visual-language discipline on the website source.

Forbidden patterns (per EPIC #3140 / E2):

* ``style="..."`` attributes in QMD pages outside ``articles/**``.
* ``linear-gradient`` / ``radial-gradient`` outside the design-token
  modules under ``css/tokens/``.
* 3- or 6-digit hex color literals outside ``css/tokens/``.

The checker is intentionally small: it walks a configured set of globs,
classifies offenders, and returns structured violations a CI script can
print or a test can assert against.

Run as a CLI from the repo root::

    python3 -m scripts.check_style_discipline
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from src.core.contracts import require

# ─── Regex catalog (single source of truth — DRY) ──────────────────────
_INLINE_STYLE_RE: Final = re.compile(r"""\sstyle\s*=\s*["']""")
_GRADIENT_RE: Final = re.compile(r"""\b(?:linear|radial)-gradient\s*\(""")
_HEX_RE: Final = re.compile(r"""(?<![\w])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b""")

# Color names that look like hex codes but are var() references are
# captured by _HEX_RE; the negative lookbehind on ``[\w]`` prevents
# matches inside identifiers but allows leading ``#`` after whitespace
# or punctuation. CSS variables ``var(--foo)`` contain no ``#`` so they
# are never flagged.


# ─── Violation record ─────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class Violation:
    """A single rule break the checker reports.

    Attributes:
        path: Repo-root-relative POSIX path of the offending file.
        line: 1-indexed line number where the offense begins.
        rule: One of ``"inline-style"``, ``"gradient"``, ``"hardcoded-hex"``.
        snippet: The offending substring (≤80 chars), for human readout.
    """

    path: str
    line: int
    rule: str
    snippet: str

    def format(self) -> str:
        """Human-readable one-liner."""
        return f"{self.path}:{self.line}: {self.rule}: {self.snippet}"


# ─── Configuration ─────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class StyleDisciplineConfig:
    """All knobs the checker exposes.

    The defaults mirror EPIC #3140 scope: top-level QMD pages and all CSS
    except the design-token modules. Tests can construct a narrower
    config against a ``tmp_path`` fixture.
    """

    repo_root: Path
    qmd_globs: tuple[str, ...] = (
        "*.qmd",
        "pages/*.qmd",
        "resources/*.qmd",
        "models/*.qmd",
        "books/*.qmd",
        "repositories/*.qmd",
        "critiques/*.qmd",
    )
    qmd_exclude_globs: tuple[str, ...] = ("articles/**/*.qmd",)
    css_globs: tuple[str, ...] = ("styles.css", "custom.scss", "css/**/*.css")
    hex_allow_globs: tuple[str, ...] = ("css/tokens/**", "site_libs/**")
    gradient_allow_globs: tuple[str, ...] = ("css/tokens/**",)
    # Files that legitimately contain inline ``style=`` such as the splash
    # HTML emitted before stylesheets load.
    inline_style_allow_globs: tuple[str, ...] = field(
        default_factory=lambda: ("_includes/site-head.html",)
    )


DEFAULT_CONFIG: Final = StyleDisciplineConfig(repo_root=Path.cwd())


# ─── Pure helpers (DRY + LOD: no I/O, easy to test) ────────────────────
def _strip_quarto_inline_math(text: str) -> str:
    """Remove ``$...$`` and ``$$...$$`` so ``$#fff`` etc. don't trip the
    hex regex. Math is plentiful in our QMD and never carries CSS hex."""
    # Strip ``$$...$$`` first (greedy not needed; non-greedy + DOTALL).
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.DOTALL)
    text = re.sub(r"\$[^$\n]+\$", " ", text)
    return text


def find_violations_in_text(text: str, *, suffix: str) -> list[Violation]:
    """Scan a single file's text content. Pure function: no path I/O.

    Args:
        text: The file's full contents.
        suffix: Extension including the dot (``.qmd``, ``.css``, …).
            Controls which rules apply.
    """
    is_qmd = suffix.lower() == ".qmd"
    is_css_like = suffix.lower() in {".css", ".scss"}
    is_html = suffix.lower() == ".html"

    scrubbed = _strip_quarto_inline_math(text) if is_qmd else text
    out: list[Violation] = []

    for lineno, line in enumerate(scrubbed.splitlines(), start=1):
        if (is_qmd or is_html) and _INLINE_STYLE_RE.search(line):
            out.append(Violation("", lineno, "inline-style", line.strip()[:80]))
        if _GRADIENT_RE.search(line):
            out.append(Violation("", lineno, "gradient", line.strip()[:80]))
        for _ in _HEX_RE.finditer(line):
            # The CSS context: we only enforce in CSS / SCSS files; QMD
            # rarely has standalone hex, but flag it if we see one in a
            # non-math, non-fenced context.
            if is_qmd or is_css_like or is_html:
                out.append(Violation("", lineno, "hardcoded-hex", line.strip()[:80]))
                break  # one hex-flag per line is enough signal
    return out


def _matches_any(path: Path, globs: tuple[str, ...], root: Path) -> bool:
    """True if ``path`` (relative to ``root``) matches any glob pattern."""
    rel = path.relative_to(root)
    return any(rel.match(pattern) for pattern in globs)


def _iter_paths(root: Path, globs: tuple[str, ...]) -> list[Path]:
    """Resolve a glob list to existing file paths, sorted, deduped."""
    seen: set[Path] = set()
    for pattern in globs:
        for path in root.glob(pattern):
            if path.is_file():
                seen.add(path)
    return sorted(seen)


# ─── Public API ────────────────────────────────────────────────────────
def check_repository(config: StyleDisciplineConfig) -> list[Violation]:
    """Return every violation under ``config.repo_root``.

    Preconditions:
        ``config.repo_root`` must exist and be a directory.

    Returns:
        Violations with ``path`` set to a POSIX-relative path. Empty
        list if the repository is clean.
    """
    require(
        config.repo_root.is_dir(),
        f"repo_root does not exist or is not a directory: {config.repo_root}",
    )

    violations: list[Violation] = []
    root = config.repo_root

    # ── Scan QMD pages
    for path in _iter_paths(root, config.qmd_globs):
        if _matches_any(path, config.qmd_exclude_globs, root):
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in find_violations_in_text(text, suffix=path.suffix):
            if raw.rule == "inline-style" and _matches_any(
                path, config.inline_style_allow_globs, root
            ):
                continue
            violations.append(Violation(rel, raw.line, raw.rule, raw.snippet))

    # ── Scan CSS / SCSS
    for path in _iter_paths(root, config.css_globs):
        rel = path.relative_to(root).as_posix()
        in_hex_allowlist = _matches_any(path, config.hex_allow_globs, root)
        in_grad_allowlist = _matches_any(path, config.gradient_allow_globs, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in find_violations_in_text(text, suffix=path.suffix):
            if raw.rule == "hardcoded-hex" and in_hex_allowlist:
                continue
            if raw.rule == "gradient" and in_grad_allowlist:
                continue
            violations.append(Violation(rel, raw.line, raw.rule, raw.snippet))

    return violations


def main(argv: list[str] | None = None) -> int:
    """CLI entry. Returns the conventional process exit code.

    Usage::

        python3 -m scripts.check_style_discipline          # scan QMD + CSS
        python3 -m scripts.check_style_discipline --qmd-only
        python3 -m scripts.check_style_discipline --css-only
        python3 -m scripts.check_style_discipline /path/to/repo
    """
    args = list(argv or [])
    scope = "all"
    if "--qmd-only" in args:
        scope = "qmd"
        args.remove("--qmd-only")
    if "--css-only" in args:
        scope = "css"
        args.remove("--css-only")
    repo = Path(args[0]) if args else Path.cwd()
    base = StyleDisciplineConfig(repo_root=repo)
    if scope == "qmd":
        config = StyleDisciplineConfig(repo_root=repo, css_globs=())
    elif scope == "css":
        config = StyleDisciplineConfig(repo_root=repo, qmd_globs=())
    else:
        config = base
    violations = check_repository(config)
    if not violations:
        print("style discipline: OK (0 violations)")
        return 0
    by_rule: dict[str, int] = {}
    for v in violations:
        by_rule[v.rule] = by_rule.get(v.rule, 0) + 1
        print(v.format())
    summary = ", ".join(f"{rule}={count}" for rule, count in sorted(by_rule.items()))
    print(f"\nstyle discipline: {len(violations)} violation(s) ({summary})")
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
