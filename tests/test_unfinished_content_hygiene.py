"""Content hygiene checks preventing placeholder/unfinished content regression (Issue #3918)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.content_lint

ROOT_DIR = Path(__file__).resolve().parent.parent
QUARTO_CONFIG = ROOT_DIR / "_quarto.yml"


def test_navbar_read_menu_does_not_promote_book_reviews() -> None:
    data = yaml.safe_load(QUARTO_CONFIG.read_text(encoding="utf-8"))
    read_menu = None
    for entry in data["website"]["navbar"]["left"]:
        if entry.get("text") == "Read":
            read_menu = entry.get("menu", [])
            break
    assert read_menu is not None, "Read menu not found in navbar"
    hrefs = [item.get("href") for item in read_menu if isinstance(item, dict)]
    assert "pages/book-reviews.html" not in hrefs


def test_book_reviews_has_no_placeholder_warnings() -> None:
    content = (ROOT_DIR / "pages" / "book-reviews.qmd").read_text(encoding="utf-8")
    assert "No completed reviews are available yet" not in content
    assert "is-queued" not in content
    assert "Review in progress" not in content


def test_research_reviews_family_has_no_stub_or_checklist_markers() -> None:
    review_files = [
        ROOT_DIR / "resources" / "research-reviews.qmd",
        ROOT_DIR / "resources" / "research-review-baseball-pitching.qmd",
        ROOT_DIR / "resources" / "research-review-induced-acceleration-analysis.qmd",
        ROOT_DIR / "resources" / "research-review-interaction-forces.qmd",
        ROOT_DIR / "resources" / "research-review-shaft-flexibility.qmd",
    ]
    for path in review_files:
        text = path.read_text(encoding="utf-8")
        assert "source-collection stub" not in text, f"{path.name} contains stub marker"
        assert "Completion Checklist" not in text, f"{path.name} contains completion checklist"
        assert "Remaining Review Checklist" not in text, f"{path.name} contains checklist marker"


def test_learning_paths_has_no_template_placeholders() -> None:
    content = (ROOT_DIR / "resources" / "learning-paths.qmd").read_text(encoding="utf-8")
    assert "[Continue for 4–8 modules total per path]" not in content
    assert "Chapter X from Volume A" not in content


def test_books_index_does_not_link_nonexistent_volume_chapters() -> None:
    content = (ROOT_DIR / "books" / "index.qmd").read_text(encoding="utf-8")
    assert "#book2-ch1" not in content
    assert "#book3-ch1" not in content
    assert "#book4-ch1" not in content


def test_resources_books_golf_science_not_empty() -> None:
    content = (ROOT_DIR / "resources" / "resources-books.qmd").read_text(encoding="utf-8")
    assert "Books on golf science will be added here in the future" not in content
