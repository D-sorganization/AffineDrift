"""Offline citation-integrity checks for The Physics of Golf (issue #5600)."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GOLF_BIB = REPO / "articles" / "The_Physics_of_Golf" / "golf_physics.bib"
QUARTO_DIR = REPO / "articles" / "The_Physics_of_Golf" / "quarto"

OBSOLETE_BIB_KEYS = frozenset(
    {
        "haykowsky2003resistance",
        "bo2004pelvic",
        "Sprigings2005",
        "hommel2009theory",
    }
)

REQUIRED_BIB_KEYS = frozenset(
    {
        "Haykowsky1996SAH",
        "Bo2005PelvicFloor",
        "SprigingsNeal2000",
        "Hommel2001TEC",
        "GomiKawato1996",
        "Feldman1986",
        "Scholz1999",
    }
)

KEY_YEAR_EXCEPTIONS: dict[str, int] = {
    # Retain first-edition year in the key; metadata is second edition (1999).
    "Jorgensen1994": 1999,
}

ENTRY_HEAD = re.compile(r"^@\w+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
YEAR_IN_KEY = re.compile(r"(?<!\d)(\d{4})(?!\d)")
_CH28_COR_NUMERIC = re.compile(r"\$e=0\.\d+\$")
_CH28_COR_BIB_KEYS = ("glossaryUSGAEquipment", "club_design_cg")


def _bib_block(text: str, key: str) -> str | None:
    match = re.search(rf"^@\w+\s*\{{\s*{re.escape(key)}\s*,", text, re.MULTILINE)
    if not match:
        return None
    open_brace = text.find("{", match.start())
    depth = 0
    for index in range(open_brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[match.start() : index + 1]
    return None


def _bib_field(body: str, name: str) -> str:
    """Read one BibTeX field, respecting nested braces."""
    brace_match = re.search(rf"\b{name}\s*=\s*\{{", body, re.IGNORECASE)
    if brace_match:
        depth = 1
        index = brace_match.end()
        while index < len(body) and depth:
            if body[index] == "{":
                depth += 1
            elif body[index] == "}":
                depth -= 1
            index += 1
        return body[brace_match.end() : index - 1].strip()
    quoted = re.search(rf'\b{name}\s*=\s*"([^"]*)"', body, re.IGNORECASE)
    if quoted:
        return quoted.group(1).strip()
    bare = re.search(rf"\b{name}\s*=\s*(\d+)", body, re.IGNORECASE)
    return bare.group(1).strip() if bare else ""


def _years_embedded_in_key(key: str) -> list[int]:
    return [int(match) for match in YEAR_IN_KEY.findall(key) if 1900 <= int(match) <= 2030]


def check_obsolete_bib_keys(bib_text: str) -> list[str]:
    """Return violations when legacy misleading keys are still defined."""
    defined = {match.group(1) for match in ENTRY_HEAD.finditer(bib_text)}
    return [f"obsolete bib key: {key}" for key in sorted(OBSOLETE_BIB_KEYS & defined)]


def check_required_bib_keys(bib_text: str) -> list[str]:
    defined = {match.group(1) for match in ENTRY_HEAD.finditer(bib_text)}
    return [f"missing required bib key: {key}" for key in sorted(REQUIRED_BIB_KEYS - defined)]


def check_bib_key_year_alignment(bib_text: str) -> list[str]:
    """Flag renamed #5600 keys whose embedded year disagrees with the year field."""
    violations: list[str] = []
    for key in sorted(REQUIRED_BIB_KEYS):
        block = _bib_block(bib_text, key)
        if block is None:
            continue
        year_field = _bib_field(block, "year")
        if not year_field.isdigit():
            violations.append(f"{key}: missing or non-numeric year field")
            continue
        year = int(year_field)
        embedded = _years_embedded_in_key(key)
        if not embedded:
            continue
        if any(key_year != year for key_year in embedded):
            embedded_str = ", ".join(str(item) for item in embedded)
            violations.append(f"{key}: key embeds {embedded_str} but year field is {year}")

    jorgensen = _bib_block(bib_text, "Jorgensen1994")
    if jorgensen is not None:
        year_field = _bib_field(jorgensen, "year")
        expected = KEY_YEAR_EXCEPTIONS["Jorgensen1994"]
        if year_field.isdigit() and int(year_field) != expected:
            violations.append(
                f"Jorgensen1994: expected year {expected} (key/year exception), found {year_field}"
            )
    return violations


def check_jorgensen_entry(bib_text: str) -> list[str]:
    block = _bib_block(bib_text, "Jorgensen1994")
    if block is None:
        return ["missing bib key: Jorgensen1994"]
    violations: list[str] = []
    if "edition = {2nd}" not in block:
        violations.append("Jorgensen1994: edition must be 2nd")
    if _bib_field(block, "year") != "1999":
        violations.append("Jorgensen1994: year must be 1999 for the cited second edition")
    publisher = _bib_field(block, "publisher")
    if publisher not in {"Springer-Verlag", "Springer"}:
        violations.append("Jorgensen1994: publisher must be Springer (2nd edition)")
    return violations


def _ch28_paragraphs_lacking_cor_source(ch28: str) -> list[str]:
    lacking: list[str] = []
    for para in re.split(r"\n\s*\n", ch28):
        if not _CH28_COR_NUMERIC.search(para):
            continue
        if "illustrative $e=0.83$" in para:
            lacking.append("ch28 still labels COR as illustrative without conformance cite")
            continue
        if not any(key in para for key in _CH28_COR_BIB_KEYS):
            lacking.append(para.strip()[:120])
    return lacking


def check_ch28_impact_sourcing(ch28_text: str) -> list[str]:
    violations: list[str] = []
    if "glossaryUSGAEquipment" not in ch28_text and "club_design_cg" not in ch28_text:
        violations.append("ch28: missing equipment-rules citation for conformance limits")
    if "Cochran1968" not in ch28_text and "Penner2003" not in ch28_text:
        violations.append("ch28: missing contact-duration literature citation")
    violations.extend(
        f"ch28: unsourced COR paragraph: {snippet!r}"
        for snippet in _ch28_paragraphs_lacking_cor_source(ch28_text)
    )
    return violations


def check_ch25_ucm(ch25_text: str) -> list[str]:
    violations: list[str] = []
    if "Scholz1999" not in ch25_text:
        violations.append("ch25: missing Scholz1999 UCM citation")
    if (
        "uncontrolled-manifold" not in ch25_text.lower()
        and "uncontrolled manifold" not in ch25_text.lower()
    ):
        violations.append("ch25: uncontrolled-manifold method not named")
    return violations


def check_ch27_equilibrium_point(ch27_text: str) -> list[str]:
    violations: list[str] = []
    lowered = ch27_text.lower()
    if "equilibrium-point" not in lowered and "equilibrium point" not in lowered:
        violations.append("ch27: equilibrium-point hypothesis not named")
    if "Feldman1986" not in ch27_text:
        violations.append("ch27: missing Feldman1986 citation")
    if "GomiKawato1996" not in ch27_text:
        violations.append("ch27: missing GomiKawato1996 critique citation")
    return violations


def find_violations(
    *,
    repo_root: Path | None = None,
    bib_path: Path | None = None,
    quarto_dir: Path | None = None,
) -> list[str]:
    """Collect every #5600 citation-integrity violation under the repo."""
    root = repo_root or REPO
    bib = bib_path or (root / "articles" / "The_Physics_of_Golf" / "golf_physics.bib")
    quarto = quarto_dir or (root / "articles" / "The_Physics_of_Golf" / "quarto")
    if not bib.is_file():
        return [f"missing bibliography: {bib.relative_to(root)}"]

    bib_text = bib.read_text(encoding="utf-8")
    violations: list[str] = []
    violations.extend(check_obsolete_bib_keys(bib_text))
    violations.extend(check_required_bib_keys(bib_text))
    violations.extend(check_bib_key_year_alignment(bib_text))
    violations.extend(check_jorgensen_entry(bib_text))

    ch28 = quarto / "ch28_impact_collision.qmd"
    if ch28.is_file():
        violations.extend(check_ch28_impact_sourcing(ch28.read_text(encoding="utf-8")))
    else:
        violations.append(f"missing chapter: {ch28.relative_to(root)}")

    ch25 = quarto / "ch25_motor_learning.qmd"
    if ch25.is_file():
        violations.extend(check_ch25_ucm(ch25.read_text(encoding="utf-8")))

    ch27 = quarto / "ch27_passive_distributed_control.qmd"
    if ch27.is_file():
        violations.extend(check_ch27_equilibrium_point(ch27.read_text(encoding="utf-8")))

    return violations
