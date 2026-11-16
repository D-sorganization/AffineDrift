"""Validate Geometry of Motion book landing pages against manuscript chapter metadata."""

from __future__ import annotations

import re
from pathlib import Path

_VOLUME0_FORBIDDEN = ("geodesic metrics",)
_VOLUME0_REQUIRED = ("geodesics/shortest rotation paths", "SLERP")
_VOLUME1_DENY = "No Volume I chapter has its own web page yet"
_VOLUME1_CHAPTER_HTML = (
    "ch01_foundations.html",
    "ch02_variational.html",
    "ch03_superposition.html",
    "ch03b_induced_acceleration_biomechanics.html",
    "ch04_contraction.html",
    "ch05_optimal_control.html",
    "ch06_duality.html",
    "ch07_counterfactuals.html",
    "ch08_applications.html",
    "ch09_parallel_mechanisms_constrained_dynamics.html",
)
_STALE_AUDIT_FILES = (
    "AUDIT_INDEX.md",
    "QUICK_REFERENCE.md",
    "BIBLIOGRAPHY_AUDIT_REPORT.md",
    "PR_INSTRUCTIONS.md",
)
_VOL2_CHAPTER_HEADING = re.compile(r"^## (.+?) \{(#[-a-z0-9]+)\}", re.MULTILINE)
_BOOK2_CHAPTER = re.compile(
    r"^## Chapter \d+: (.+?)(?: \{#book2-ch\d+\})?$",
    re.MULTILINE,
)
_BOOK2_WEB_LINK = re.compile(
    r"\[Read this chapter on the web\]\(\.\./articles/The_Geometry_of_Motion/quarto/volume2\.html#([^)]+)\)"
)


def _rel(repo_root: Path, path: Path) -> str:
    """Display a repository-relative path consistently across operating systems."""
    return str(path.relative_to(repo_root)).replace("\\", "/")


def _read(path: Path) -> str:
    """Read a manuscript source using the repository's UTF-8 encoding."""
    return path.read_text(encoding="utf-8")


def _volume0_violations(repo_root: Path) -> list[str]:
    """Check that the introductory blurb names the supported rotation topics."""
    path = repo_root / "articles/The_Geometry_of_Motion/quarto/volume0.qmd"
    text = _read(path)
    violations: list[str] = []
    for phrase in _VOLUME0_FORBIDDEN:
        if phrase in text:
            violations.append(f"{_rel(repo_root, path)}: must not contain {phrase!r}")
    for phrase in _VOLUME0_REQUIRED:
        if phrase not in text:
            violations.append(f"{_rel(repo_root, path)}: missing required blurb token {phrase!r}")
    return violations


def _volume1_violations(repo_root: Path) -> list[str]:
    """Require the landing page to link every published Volume I chapter."""
    path = repo_root / "books/tangent-space-methods.qmd"
    text = _read(path)
    violations: list[str] = []
    if _VOLUME1_DENY in text:
        violations.append(f"{_rel(repo_root, path)}: stale denial that chapter HTML exists")
    for chapter_html in _VOLUME1_CHAPTER_HTML:
        if chapter_html not in text:
            violations.append(f"{_rel(repo_root, path)}: missing link to {chapter_html}")
    return violations


def _normalize_chapter_title(title: str) -> str:
    """Strip Quarto escapes so landing headings compare to manuscript titles."""
    return title.replace(r"\&", "&").replace("  ", " ").strip()


def _volume2_chapter_sections(repo_root: Path) -> list[tuple[str, str]]:
    """Return manuscript (title, section_id) pairs in chapter order."""
    content_path = repo_root / "articles/The_Geometry_of_Motion/quarto/volume2_content.qmd"
    pairs = _VOL2_CHAPTER_HEADING.findall(_read(content_path))
    if len(pairs) != 11:
        raise ValueError(
            f"Expected 11 Volume II chapters in {content_path.name}, found {len(pairs)}"
        )
    return [(_normalize_chapter_title(title), anchor.lstrip("#")) for title, anchor in pairs]


def _volume2_violations(repo_root: Path) -> list[str]:
    """Compare Volume II landing titles and links with manuscript sections."""
    landing_path = repo_root / "books/control-is-motion.qmd"
    text = _read(landing_path)
    violations: list[str] = []
    if "volume2.html" not in text:
        violations.append(f"{_rel(repo_root, landing_path)}: missing volume2.html monograph link")
    if "Throwing Away the Target" in text:
        violations.append(
            f"{_rel(repo_root, landing_path)}: stale chapter title 'Throwing Away the Target'"
        )

    manuscript = _volume2_chapter_sections(repo_root)
    landing_titles = _BOOK2_CHAPTER.findall(text)
    if len(landing_titles) != len(manuscript):
        violations.append(
            f"{_rel(repo_root, landing_path)}: expected {len(manuscript)} chapter headings, "
            f"found {len(landing_titles)}"
        )
    else:
        for index, ((ms_title, _), landing_title) in enumerate(
            zip(manuscript, landing_titles, strict=True), 1
        ):
            if ms_title != _normalize_chapter_title(landing_title):
                violations.append(
                    f"{_rel(repo_root, landing_path)}: chapter {index} title "
                    f"{landing_title!r} != manuscript {ms_title!r}"
                )

    fragment_ids = _BOOK2_WEB_LINK.findall(text)
    expected_ids = [section_id for _, section_id in manuscript]
    if fragment_ids != expected_ids:
        violations.append(
            f"{_rel(repo_root, landing_path)}: chapter web fragments {fragment_ids!r} "
            f"!= manuscript section ids {expected_ids!r}"
        )
    return violations


def _stale_audit_violations(repo_root: Path) -> list[str]:
    """Keep archived audit instructions out of the published manuscript tree."""
    gom_root = repo_root / "articles/The_Geometry_of_Motion"
    violations: list[str] = []
    for name in _STALE_AUDIT_FILES:
        stale = gom_root / name
        if stale.exists():
            violations.append(
                f"{_rel(repo_root, stale)}: sandbox audit file must be archived, not in manuscript tree"
            )
    return violations


def collect_violations(repo_root: Path) -> list[str]:
    """Return human-readable violations when landing pages drift from the manuscript."""
    violations: list[str] = []
    violations.extend(_volume0_violations(repo_root))
    violations.extend(_volume1_violations(repo_root))
    violations.extend(_volume2_violations(repo_root))
    violations.extend(_stale_audit_violations(repo_root))
    return violations
