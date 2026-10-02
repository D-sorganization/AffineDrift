"""Tests for controlled category vocabulary enforcement (WEB-02.7, #4501).

Validates that:
1. `config/categories.yml` loads as a non-empty mapping of category slugs to descriptions.
2. Every rendered content page scanned via `find_content_pages` uses only categories
   defined in `config/categories.yml`.
3. Categories outside the controlled vocabulary are rejected.
4. The Drifter Manifesto pages are categorized as `opinion` (not `critique`).
5. `resources/articles.qmd` configures a Quarto listing driven by categories and filter UI.
"""

from __future__ import annotations

from pathlib import Path

from src.tools.site_link_gate import check_categories, is_book_chapter, load_vocabulary
from src.tools.site_page_scan import find_content_pages, parse_front_matter

REPO_ROOT = Path(__file__).resolve().parent.parent
VOCABULARY_PATH = REPO_ROOT / "config" / "categories.yml"


def test_load_category_vocabulary() -> None:
    """Category vocabulary exists and contains valid category mappings."""
    vocab = load_vocabulary(REPO_ROOT)
    assert isinstance(vocab, dict)
    assert len(vocab) > 0

    # Key categories must be defined
    assert "theory-core" in vocab
    assert "opinion" in vocab
    assert "critique" in vocab
    assert "resources" in vocab
    assert "books" in vocab

    for category, description in vocab.items():
        assert isinstance(category, str) and category.strip()
        assert isinstance(description, str) and description.strip()


def test_all_rendered_content_pages_use_vocabulary_categories() -> None:
    """All rendered content pages must declare categories from config/categories.yml."""
    vocab = load_vocabulary(REPO_ROOT)
    pages = find_content_pages(REPO_ROOT)
    assert len(pages) >= 200, f"Expected 200+ content pages, got {len(pages)}"

    unknown_categories: list[str] = []
    missing_categories: list[str] = []

    for page in pages:
        rel = page.relative_to(REPO_ROOT).as_posix()
        if is_book_chapter(rel):
            continue
        text = page.read_text(encoding="utf-8", errors="ignore")
        front = parse_front_matter(text)
        categories = front.get("categories")

        if categories is None or categories == []:
            missing_categories.append(rel)
            continue

        if isinstance(categories, list):
            for cat in categories:
                if str(cat) not in vocab:
                    unknown_categories.append(f"{rel}: unknown category '{cat}'")
        else:
            unknown_categories.append(f"{rel}: categories is not a list ({type(categories)})")

    assert not missing_categories, f"Pages missing categories: {missing_categories}"
    assert not unknown_categories, f"Pages with unknown categories: {unknown_categories}"


def test_unknown_categories_are_rejected(tmp_path: Path) -> None:
    """Categories outside the vocabulary must be rejected by check_categories."""
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "categories.yml").write_text(
        VOCABULARY_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    test_page = tmp_path / "articles" / "test_unknown.qmd"
    test_page.parent.mkdir(parents=True, exist_ok=True)
    test_page.write_text(
        "---\ntitle: Test Unknown\ncategories:\n  - bogus-category-xyz\n---\n\nBody content\n",
        encoding="utf-8",
    )

    errors = check_categories(tmp_path, [test_page])
    assert any("unknown category 'bogus-category-xyz'" in err for err in errors)


def test_manifesto_categorised_as_opinion() -> None:
    """Manifesto pages must be categorized as 'opinion' (or 'theory-core'), not 'critique'."""
    manifesto_pages = [
        REPO_ROOT / "pages" / "drifter-manifesto.qmd",
        REPO_ROOT / "articles" / "drifter-manifesto.qmd",
    ]
    for page in manifesto_pages:
        assert page.is_file(), f"{page} must exist"
        fm = parse_front_matter(page.read_text(encoding="utf-8"))
        categories = fm.get("categories", [])
        assert "opinion" in categories or "theory-core" in categories
        assert "critique" not in categories


def test_article_index_listing_configured() -> None:
    """resources/articles.qmd must configure a Quarto listing with categories and filter-ui."""
    articles_index = REPO_ROOT / "resources" / "articles.qmd"
    assert articles_index.is_file(), "resources/articles.qmd must exist"

    fm = parse_front_matter(articles_index.read_text(encoding="utf-8"))
    assert "listing" in fm, "resources/articles.qmd must declare a listing in front matter"

    listing = fm["listing"]
    assert isinstance(listing, dict), "listing must be a dict"
    assert "contents" in listing, "listing must specify contents"
    assert listing.get("categories") is True, "listing must enable categories: true"
    assert listing.get("filter-ui") is True, "listing must enable filter-ui: true"
    assert listing.get("type") == "default"
