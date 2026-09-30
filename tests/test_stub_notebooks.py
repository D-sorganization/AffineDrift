"""Tests for Jupyter notebook completeness and Colab button governance.

Enforces acceptance criteria for WEB-06.7:
1. No Colab button links to a notebook with fewer than 5 code cells.
2. Filled priority notebooks execute top to bottom without error via nbclient.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = REPO_ROOT / "notebooks/geometry_of_motion"
BOOKS_DIR = REPO_ROOT / "books"

PRIORITY_NOTEBOOKS = [
    NOTEBOOKS_DIR / "vol1_ch3_superposition_in_control_affine_systems.ipynb",
    NOTEBOOKS_DIR / "vol1_ch7_counterfactual_analysis.ipynb",
    NOTEBOOKS_DIR / "vol2_ch5_underactuation_and_passive_dynamics.ipynb",
]

COLAB_PATTERN = re.compile(
    r"\[Open Notebook in Colab\]\(https://colab\.research\.google\.com/github/[^/]+/[^/]+/blob/[^/]+/(.+?)\)"
)


def _get_code_cell_count(notebook_path: Path) -> int:
    """Return the number of code cells in a notebook."""
    data = json.loads(notebook_path.read_text(encoding="utf-8"))
    return sum(1 for cell in data.get("cells", []) if cell.get("cell_type") == "code")


def test_no_colab_button_links_to_stub_notebook() -> None:
    """No Colab button across books/*.qmd may link to a notebook with < 5 code cells."""
    colab_links: list[tuple[Path, str, Path]] = []

    for qmd_path in sorted(BOOKS_DIR.glob("*.qmd")):
        text = qmd_path.read_text(encoding="utf-8")
        for match in COLAB_PATTERN.finditer(text):
            rel_notebook_path = match.group(1)
            target_notebook = REPO_ROOT / rel_notebook_path
            colab_links.append((qmd_path, rel_notebook_path, target_notebook))

    assert colab_links, "Expected at least one Colab link for the priority notebooks."

    for qmd_path, rel_nb, target_nb in colab_links:
        assert (
            target_nb.is_file()
        ), f"Colab button in {qmd_path.name} links to missing notebook: {rel_nb}"
        code_count = _get_code_cell_count(target_nb)
        assert (
            code_count >= 5
        ), f"Colab button in {qmd_path.name} links to stub notebook {rel_nb} with only {code_count} code cells (< 5)."


@pytest.mark.parametrize("notebook_path", PRIORITY_NOTEBOOKS)
def test_priority_notebooks_have_at_least_five_code_cells(notebook_path: Path) -> None:
    """Each filled priority notebook must have >= 5 code cells."""
    assert notebook_path.is_file(), f"Missing priority notebook: {notebook_path}"
    code_count = _get_code_cell_count(notebook_path)
    assert (
        code_count >= 5
    ), f"Priority notebook {notebook_path.name} has only {code_count} code cells; expected >= 5."


@pytest.mark.parametrize("notebook_path", PRIORITY_NOTEBOOKS)
def test_priority_notebooks_execute_top_to_bottom(notebook_path: Path) -> None:
    """Each filled priority notebook must execute top-to-bottom without error via nbclient."""
    assert notebook_path.is_file(), f"Missing priority notebook: {notebook_path}"
    nb = nbformat.read(str(notebook_path), as_version=4)  # type: ignore[no-untyped-call]
    client = NotebookClient(nb, timeout=60, kernel_name="python3")
    # Execute should run all code cells without raising CellExecutionError
    client.execute()
