"""Reader-facing Contributor and Reviewer Guide (issue #4607).

Verifies the guide page exists, routes each of the four contribution paths
(correction, critique, dataset, chapter review) to its GitHub issue
template, and is linked from the Collaborate page as required by the
issue's acceptance criteria.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDE_PATH = REPO_ROOT / "pages" / "contributor-guide.qmd"
COLLABORATE_PATH = REPO_ROOT / "pages" / "collaborate.qmd"


def test_guide_page_exists() -> None:
    assert GUIDE_PATH.is_file(), f"Expected reader-facing guide at {GUIDE_PATH}"


def test_guide_links_to_content_correction_template() -> None:
    text = GUIDE_PATH.read_text(encoding="utf-8")
    assert "issues/new?template=content-correction.md" in text


def test_guide_links_to_critique_response_template() -> None:
    text = GUIDE_PATH.read_text(encoding="utf-8")
    assert "issues/new?template=critique-response.md" in text
    assert "critiques/index.html" in text


def test_guide_links_to_dataset_contribution_path() -> None:
    text = GUIDE_PATH.read_text(encoding="utf-8")
    assert "issues/new?template=resource-addition.md" in text
    assert "resources-datasets.html" in text


def test_guide_links_to_textbook_improvement_template() -> None:
    text = GUIDE_PATH.read_text(encoding="utf-8")
    assert "issues/new?template=textbook-improvement.md" in text


def test_guide_referenced_templates_exist_in_repo() -> None:
    template_dir = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
    for name in (
        "content-correction.md",
        "critique-response.md",
        "resource-addition.md",
        "textbook-improvement.md",
    ):
        assert (template_dir / name).is_file(), f"Missing issue template: {name}"


def test_collaborate_page_links_to_guide() -> None:
    text = COLLABORATE_PATH.read_text(encoding="utf-8")
    assert "contributor-guide.html" in text
