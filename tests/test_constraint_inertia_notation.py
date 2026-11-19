"""Keep constraint-space inertia and its inverse distinct in the reference."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_constraint_gram_matrix_is_inverse_inertia() -> None:
    """The Jacobian/mass Gram matrix has inverse-inertia units."""
    text = (ROOT / "NOTATION.md").read_text(encoding="utf-8")
    rows = (
        [cell.strip() for cell in line.split("|")]
        for line in text.splitlines()
        if line.startswith("|")
    )
    row = next(cells for cells in rows if cells[1] == "$K_c$")
    assert "inverse inertia" in row[3].lower()
    assert r"$K_c^{-1}$" in text
    assert r"$K_c=0.75$ kg$^{-1}$" in text
    assert r"$\Lambda_c=4/3$ kg" in text
