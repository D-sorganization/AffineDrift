"""Licensing terms consistency (WEB-14.7 #4609).

Owner ruling (2026-10-11): code is MIT; written text and data are CC BY 4.0.
Enforces that the licence files, package metadata and README agree with that ruling.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = ROOT / "package.json"
LICENSE_MIT = ROOT / "LICENSE"
LICENSE_CONTENT = ROOT / "LICENSE-CONTENT"
README = ROOT / "README.md"
COPYRIGHT = ROOT / "COPYRIGHT.md"
CC_BY_URL = "https://creativecommons.org/licenses/by/4.0/legalcode"


def test_package_metadata_declares_mit_for_code() -> None:
    package = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    assert package["license"] == "MIT"


def test_mit_licence_file_names_copyright_holder() -> None:
    text = LICENSE_MIT.read_text(encoding="utf-8")
    assert text.startswith("MIT License")
    assert "Copyright (c) 2026 D-Sorganization" in text


def test_content_licence_file_states_cc_by_4_with_legalcode_url() -> None:
    text = LICENSE_CONTENT.read_text(encoding="utf-8")
    assert "Creative Commons Attribution 4.0" in text
    assert CC_BY_URL in text


def test_readme_licensing_section_matches_ruling() -> None:
    text = README.read_text(encoding="utf-8")
    licensing = text.split("## Licensing", 1)[1].split("\n## ", 1)[0]
    assert "MIT" in licensing
    assert "CC BY 4.0" in licensing
    assert "LICENSE-CONTENT" in licensing


def test_copyright_page_does_not_reserve_written_content() -> None:
    text = COPYRIGHT.read_text(encoding="utf-8")
    assert "all rights reserved" not in text.lower()
    assert "CC BY 4.0" in text
