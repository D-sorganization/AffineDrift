"""Coverage checks for repository inventory and component README docs."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.content_lint

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_DOC = ROOT / "docs" / "development" / "repository_inventory.md"
REQUIRED_READMES = (
    ROOT / "src" / "README.md",
    ROOT / "src" / "affine_control" / "README.md",
    ROOT / "src" / "tangent_models" / "README.md",
    ROOT / ".github" / "workflows" / "README.md",
    ROOT / "articles" / "The_Geometry_of_Motion" / "README.md",
    ROOT / "books" / "README.md",
)


def test_repository_inventory_doc_exists_with_status_and_gaps() -> None:
    """Inventory doc must document implementation status and known gaps."""
    assert INVENTORY_DOC.exists()
    text = INVENTORY_DOC.read_text(encoding="utf-8")
    assert "## Inventory Map" in text
    assert "Implementation Status" in text
    assert "Known Gaps" in text
    assert "Maintenance Note" in text


def test_primary_components_have_readme_coverage() -> None:
    """Primary components should expose README status documents."""
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_READMES if not path.exists()]
    assert missing == []
