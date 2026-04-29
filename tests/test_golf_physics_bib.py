import re
from collections import Counter
from pathlib import Path


def test_golf_physics_bib_has_unique_keys():
    bib_path = (
        Path(__file__).resolve().parents[1]
        / "articles"
        / "The_Physics_of_Golf"
        / "golf_physics.bib"
    )
    text = bib_path.read_text(encoding="utf-8")

    keys = [
        match.group(1).casefold() for match in re.finditer(r"^@\w+\{([^,]+),", text, re.MULTILINE)
    ]
    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)

    assert duplicates == [], f"Duplicate BibTeX keys found in {bib_path}: {duplicates}"
