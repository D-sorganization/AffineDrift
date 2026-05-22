"""Contract for the design-system primitives (EPIC #3140, B3).

The repo's visual language must funnel through a small, audited set of
classes: ``.site-card``, ``.site-button``, ``.section-stack``,
``.page-sidebar``, ``.entry-list``, ``.provenance-note``, ``.home-hero``.
These tests verify the primitive files exist and conform to the design
contract (no gradients, no hardcoded hex, only token-driven values, modest
border-radius).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.check_style_discipline import find_violations_in_text

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPONENTS_DIR = REPO_ROOT / "css" / "components"

PRIMITIVE_FILES = {
    "site-card": COMPONENTS_DIR / "site-card.css",
    "site-button": COMPONENTS_DIR / "site-button.css",
    "section-stack": COMPONENTS_DIR / "section-stack.css",
    "page-sidebar": COMPONENTS_DIR / "page-sidebar.css",
    "entry-list": COMPONENTS_DIR / "entry-list.css",
    "provenance-note": COMPONENTS_DIR / "provenance-note.css",
    "home-hero": COMPONENTS_DIR / "home-hero.css",
}


@pytest.fixture(params=sorted(PRIMITIVE_FILES.keys()))
def primitive(request: pytest.FixtureRequest) -> tuple[str, Path]:
    name = request.param
    return name, PRIMITIVE_FILES[name]


class TestPrimitivesExist:
    def test_file_exists(self, primitive: tuple[str, Path]) -> None:
        name, path = primitive
        assert path.is_file(), f"Missing primitive CSS module: {name} ({path})"

    def test_file_declares_its_own_class(self, primitive: tuple[str, Path]) -> None:
        name, path = primitive
        text = path.read_text(encoding="utf-8")
        # The class name maps 1:1 to the file name (LOD: a reader of the
        # filename can predict the selector without opening the file).
        assert f".{name}" in text


class TestPrimitivesObeyDesignContract:
    def test_no_gradient_or_hex(self, primitive: tuple[str, Path]) -> None:
        _, path = primitive
        violations = find_violations_in_text(path.read_text(encoding="utf-8"), suffix=".css")
        offenders = [v for v in violations if v.rule in {"gradient", "hardcoded-hex"}]
        assert offenders == [], f"{path.name} contains forbidden visual patterns: " + ", ".join(
            f"L{v.line} {v.rule}" for v in offenders
        )

    def test_uses_design_tokens(self, primitive: tuple[str, Path]) -> None:
        _, path = primitive
        text = path.read_text(encoding="utf-8")
        # Every primitive should reference at least one design token. This
        # guards against accidental hardcoded values being introduced via
        # named CSS colors or numeric literals masquerading as tokens.
        assert "var(--" in text, f"{path.name} doesn't reference any design token"

    def test_border_radius_within_budget(self, primitive: tuple[str, Path]) -> None:
        _, path = primitive
        text = path.read_text(encoding="utf-8")
        # No literal border-radius above 8px. Token-driven radii are fine.
        for match in re.finditer(r"border-radius:\s*([0-9.]+)px", text):
            value = float(match.group(1))
            assert value <= 8.0, f"{path.name}: border-radius {value}px exceeds 8px design budget"

    def test_no_hover_lift_transform(self, primitive: tuple[str, Path]) -> None:
        _, path = primitive
        text = path.read_text(encoding="utf-8")
        # Playful translate hovers are out per the design contract.
        assert (
            "translateY" not in text
        ), f"{path.name}: hover-lift transform translateY is forbidden"


class TestPrimitivesAreImported:
    """B1 wiring: styles.css must @import every primitive."""

    def test_styles_imports_primitives(self) -> None:
        styles = (REPO_ROOT / "styles.css").read_text(encoding="utf-8")
        for name in PRIMITIVE_FILES:
            assert (
                f"css/components/{name}.css" in styles
            ), f"styles.css does not @import css/components/{name}.css"
