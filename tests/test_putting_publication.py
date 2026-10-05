"""Keep the reviewed putting chapter reachable in both book editions."""

from pathlib import Path

import yaml


def test_putting_is_in_both_book_editions() -> None:
    """An on-disk chapter must also appear in the PDF and HTML book navigation."""
    root = Path(__file__).resolve().parents[1] / "articles/The_Physics_of_Golf"
    latex = (root / "main.tex").read_text(encoding="utf-8")
    config = yaml.safe_load((root / "quarto/_quarto.yml").read_text(encoding="utf-8"))
    parts = [part for part in config["book"]["chapters"] if isinstance(part, dict)]
    chapters = [chapter for part in parts for chapter in part["chapters"]]
    assert "\\include{chapters/ch32_putting}" in latex
    assert chapters.count("ch32_putting.qmd") == 1
    assert (root / "chapters/ch32_putting.tex").is_file()
    assert (root / "quarto/ch32_putting.qmd").is_file()
