"""Reference integrity guardrails for Tangent-Space Methods bibliography."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "articles" / "The_Geometry_of_Motion" / "geometry_of_motion.bib"
KNOWN_LEGACY_IDENTIFIER_GAPS = {
    "Albus1971",
    "Alexander1991",
    "Caruthers2016",
    "Challis2011",
    "Clark2013",
    "Cohen1980",
    "Cohen2005",
    "dAvellaBizzi2005",
    "Friston2010",
    "Friston2016",
    "Georgopoulos1986",
    "Gershman2017",
    "Greenwald1970",
    "Grillner1975",
    "Halder2000",
    "HansenOstermeier2001",
    "HerculanoHouzel2010",
    "Hill1950",
    "Hirashima2007control",
    "Hirashima2008kinetic",
    "HirashimaOhtsuki2008",
    "Hommel2001",
    "Kawato1987",
    "Kepple1997",
    "Lephart2007",
    "Marr1969",
    "Matsuoka1985",
    "McGeer1990",
    "Mountcastle1997",
    "Neptune2001",
    "OConnor1989",
    "Putnam1993",
    "RileyKerrigan1999",
    "Schmidt1975",
    "Schultz1997",
    "Schutte1993",
    "Shadmehr1994",
    "Solis2005",
    "StornPrice1997",
    "TingMacpherson2005",
    "Tresch2006",
    "Winters1984",
    "WolpertKawato1998",
    "Wretenberg1995",
    "Zajac2002",
    "Zajac2003",
    "ZajacGordon1989",
}


@dataclass(frozen=True)
class BibEntry:
    kind: str
    key: str
    fields: dict[str, str]


def _parse_bib_entries(text: str) -> list[BibEntry]:
    pattern = re.compile(r"@(\w+)\{([^,]+),(.*?)\n\}", re.DOTALL)
    entries: list[BibEntry] = []
    for kind, key, body in pattern.findall(text):
        fields: dict[str, str] = {}
        for field, value in re.findall(r"\n\s*([A-Za-z]+)\s*=\s*\{([^}]*)\}", body):
            fields[field.lower()] = value.strip()
        entries.append(BibEntry(kind.lower(), key.strip(), fields))
    return entries


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def test_article_and_proceedings_entries_have_identifier() -> None:
    """Each article/proceedings entry should include a DOI or URL."""
    entries = _parse_bib_entries(BIB_PATH.read_text(encoding="utf-8"))
    missing_ids = [
        entry.key
        for entry in entries
        if entry.kind in {"article", "inproceedings"}
        and "doi" not in entry.fields
        and "url" not in entry.fields
    ]
    unexpected = sorted(set(missing_ids) - KNOWN_LEGACY_IDENTIFIER_GAPS)
    assert not unexpected, f"Missing DOI/URL for: {unexpected}"


def test_known_high_risk_attributions_are_correct() -> None:
    """Known concerns from issue #1287 should be explicitly validated."""
    entries = {
        entry.key: entry for entry in _parse_bib_entries(BIB_PATH.read_text(encoding="utf-8"))
    }
    andrieu_entry = entries["AndreuPraly2009"]
    assert "Andrieu" in andrieu_entry.fields["author"]
    assert andrieu_entry.fields["doi"] == "10.1016/j.automatica.2008.07.015"

    pham_entry = entries["PhamTabuadaSlotine2009"]
    assert pham_entry.fields["doi"] == "10.1109/TAC.2008.2009619"


def test_duplicate_titles_require_legacy_note() -> None:
    """Duplicate citation records must be marked as a compatibility alias."""
    entries = _parse_bib_entries(BIB_PATH.read_text(encoding="utf-8"))
    by_signature: dict[tuple[str, str], list[BibEntry]] = defaultdict(list)
    for entry in entries:
        title = entry.fields.get("title", "")
        year = entry.fields.get("year", "")
        by_signature[(_norm(title), year)].append(entry)

    duplicates = [group for group in by_signature.values() if len(group) > 1]
    for group in duplicates:
        notes = [entry.fields.get("note", "") for entry in group]
        assert any("Legacy duplicate key retained" in note for note in notes)
