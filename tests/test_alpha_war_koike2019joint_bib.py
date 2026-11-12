"""Contract: Alpha War `koike2019joint` bibliography entry (#5466).

The full v1 draft lives on branch ``research/alpha-war-thesis``; this test locks the
corrected CrossRef metadata after [#5367](https://github.com/D-sorganization/AffineDrift/issues/5367).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "research" / "alpha-war" / "references.bib"


def test_koike2019joint_entry_matches_doi_record() -> None:
    """``koike2019joint`` matches DOI 10.1016/j.jbiomech.2019.01.032 (rugby place kick)."""
    text = BIB_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"@article\{koike2019joint,(.*?)^\}",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, "koike2019joint entry missing from research/alpha-war/references.bib"
    block = match.group(1)
    assert "Sekiya Koike" in block
    assert "Tatsuya Ishikawa" in block
    assert "Alexander P. Willmott" in block
    assert "Neil E. Bezodis" in block
    assert "swinging motion" in block
    assert "golf" not in block.lower()
    assert "10.1016/j.jbiomech.2019.01.032" in block
    assert "Journal of Biomechanics" in block
