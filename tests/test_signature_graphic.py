"""Contract of the WEB-08.2 "Drift Plus Control" signature graphic (#4554).

The figure must be the model, not an illustration of it: the arrows are the
control-affine split of ``SimplePendulum.dynamics`` at a state of a computed
run, drawn head to tail. It must stay accessible, follow both themes and be
embedded where the issue asks.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

from scripts.generate_signature_graphic import (
    ARROW_DT,
    INCLUDE_PATH,
    PENDULUM,
    TORQUE,
    build_scene,
    drift,
    push,
    render_include,
    stale,
    to_view,
)

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "css" / "components" / "drift-plus-control.css"
INCLUDE_LINE = "{{< include ../_includes/generated/drift-plus-control.qmd >}}"


def _svg() -> str:
    """The SVG element of the generated include."""
    text = render_include(build_scene())
    return text[text.index("<svg") : text.index("</svg>") + len("</svg>")]


def _line(svg: str, css: str) -> tuple[float, ...]:
    """Endpoints ``(x1, y1, x2, y2)`` of the line with class ``css``."""
    match = re.search(
        rf'<line class="{css}" x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"', svg
    )
    assert match is not None, css
    return tuple(float(value) for value in match.groups())


@pytest.mark.parametrize("x", [np.array([-2.0, 0.0]), np.array([0.3, 4.0]), np.array([2.9, -6.0])])
def test_split_is_the_control_affine_decomposition_of_the_model(x: np.ndarray) -> None:
    np.testing.assert_allclose(drift(x) + push(x, TORQUE), PENDULUM.dynamics(x, TORQUE))
    np.testing.assert_allclose(push(x, TORQUE), [0.0, TORQUE / (PENDULUM.m * PENDULUM.L**2)])


def test_marked_state_lies_on_the_driven_run_and_differs_from_the_passive_one() -> None:
    scene = build_scene()
    assert any(np.array_equal(scene.mark, state) for state in scene.driven)
    assert not np.allclose(scene.driven[-1], scene.passive[-1])


def test_arrows_are_drawn_head_to_tail_at_model_scale() -> None:
    scene = build_scene()
    svg = _svg()
    start = to_view(*scene.mark)
    drift_head = to_view(*(scene.mark + ARROW_DT * scene.drift))
    push_head = to_view(*(scene.mark + ARROW_DT * (scene.drift + scene.push)))
    expected = {
        "dpc-drift": (*start, *drift_head),
        "dpc-push": (*drift_head, *push_head),
        "dpc-sum": (*start, *push_head),
    }
    for css, coords in expected.items():
        assert _line(svg, css) == pytest.approx(coords, abs=0.051), css


def test_figure_is_accessible() -> None:
    text = render_include(build_scene())
    svg = _svg()
    assert re.match(r'<svg [^>]*role="img" aria-labelledby="dpc-title dpc-desc">', svg)
    assert '<title id="dpc-title">' in svg and '<desc id="dpc-desc">' in svg
    assert 'aria-describedby="dpc-long"' in text
    assert re.search(r'<details id="dpc-long">\s*<summary>Long description</summary>', text)
    assert "not a golfer measurement" in text


def test_colours_come_from_theme_aware_css_only() -> None:
    text = render_include(build_scene())
    assert not re.search(r"#[0-9a-fA-F]{3,6}\b|style=|fill=\"|stroke=\"", text)
    css = CSS.read_text(encoding="utf-8")
    assert '[data-theme="dark"]' in css
    assert ':root:not([data-theme="light"])' in css
    for css_class in ("dpc-drift", "dpc-push", "dpc-sum", "dpc-passive", "dpc-driven", "dpc-field"):
        assert f".{css_class}" in css, css_class
    assert '@import url("css/components/drift-plus-control.css");' in (
        ROOT / "styles.css"
    ).read_text(encoding="utf-8")


@pytest.mark.parametrize("page", ["index.qmd", "articles/theory-part1.qmd"])
def test_graphic_is_embedded(page: str) -> None:
    line = INCLUDE_LINE if "/" in page else INCLUDE_LINE.replace("../", "")
    assert line in (ROOT / page).read_text(encoding="utf-8")


def test_include_is_current() -> None:
    assert (ROOT / INCLUDE_PATH).is_file()
    assert not stale(), "run python -m scripts.generate_signature_graphic"
