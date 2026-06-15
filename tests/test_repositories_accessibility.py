"""Accessibility regression tests for the repositories page."""

from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODELS_PAGE = REPO_ROOT / "models" / "models.qmd"
REPOSITORIES_PAGE = REPO_ROOT / "repositories" / "repositories.qmd"


class AccordionIconParser(HTMLParser):
    """Collect decorative accordion icon spans from Quarto content."""

    def __init__(self) -> None:
        super().__init__()
        self.icons: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record spans whose class list includes accordion-icon."""
        if tag != "span":
            return

        attributes = dict(attrs)
        classes = attributes.get("class", "")
        if classes is not None and "accordion-icon" in classes.split():
            self.icons.append(attributes)


def test_repositories_accordion_icons_are_hidden_from_screen_readers() -> None:
    """Decorative accordion icons must not be announced as button text."""
    parser = AccordionIconParser()
    parser.feed(REPOSITORIES_PAGE.read_text(encoding="utf-8"))

    assert parser.icons
    assert all(icon.get("aria-hidden") == "true" for icon in parser.icons)

def test_models_accordion_icons_are_hidden_from_screen_readers() -> None:
    """Decorative accordion icons must not be announced as button text."""
    parser = AccordionIconParser()
    parser.feed(MODELS_PAGE.read_text(encoding="utf-8"))

    assert parser.icons
    assert all(icon.get("aria-hidden") == "true" for icon in parser.icons)
