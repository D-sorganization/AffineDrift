"""Contract for the Educator Resources page (WEB-14.7, #4609).

Acceptance criteria: at least three teaching modules, each with learning
objectives and exercises with solutions, for instructors in biomechanics,
sport science or control courses. The owner ruling of 2026-10-11 sets the
licence (code MIT; written text and data CC BY 4.0).

Every quantitative answer on the page must be reproducible from a cited page,
widget or ``src/`` function, or be derived in full on the page. The numeric
tests below recompute each answer independently and require the page to state
it, so a later edit cannot leave a stale number behind. The rotation answers
are recomputed from the widget's own engine in ``tests/educator-resources.test.js``.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pytest
import yaml

from src.affine_control.dynamics import double_pendulum_coriolis, double_pendulum_mass_matrix
from src.affine_control.golf_model import GolfModel
from src.affine_control.reachability import constant_additive_drift_interval
from src.core.constants import GRAVITY_M_S2
from src.tangent_models.examples import SimplePendulum
from src.tools.utils.frontmatter import split_frontmatter

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "resources" / "educator-resources.qmd"
PAGE_HREF = "resources/educator-resources.html"
CC_BY_URL = "https://creativecommons.org/licenses/by/4.0/legalcode"
MIN_MODULES = 3
MIN_READING_LINKS = 2
MODULE_HEADING = re.compile(r"^## Module (\d+): .+$", re.MULTILINE)
REQUIRED_SUBSECTIONS = (
    "### Learning Objectives",
    "### Reading Path",
    "### Exercises",
    "### Worked Solutions",
)
LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")


def _text() -> str:
    return PAGE.read_text(encoding="utf-8")


def _flat() -> str:
    """Page text with whitespace collapsed, so wrapped lines still match."""
    return " ".join(_text().split())


def _modules() -> dict[int, str]:
    """Map module number to its section text (up to the next ``## `` heading)."""
    text = _text()
    starts = list(MODULE_HEADING.finditer(text))
    modules: dict[int, str] = {}
    for match in starts:
        rest = text[match.end() :]
        nxt = re.search(r"^## ", rest, re.MULTILINE)
        modules[int(match.group(1))] = rest[: nxt.start()] if nxt else rest
    return modules


def _subsection(module: str, heading: str) -> str:
    start = module.index(heading) + len(heading)
    nxt = re.search(r"^### ", module[start:], re.MULTILINE)
    return module[start : start + nxt.start()] if nxt else module[start:]


def _resolves(target: str) -> bool:
    clean = target.split("#")[0]
    resolved = (PAGE.parent / clean).resolve()
    if resolved.suffix == ".html":
        return resolved.is_file() or resolved.with_suffix(".qmd").is_file()
    return resolved.exists()


def _assert_states(value: float, decimals: int) -> None:
    """Require ``value`` rounded to ``decimals`` places to appear on the page."""
    rendered = f"{value:.{decimals}f}"
    if rendered.startswith("-"):
        rendered = rendered[1:]
    assert rendered in _flat(), f"page does not state {value!r} as {rendered}"


# --- Structure -------------------------------------------------------------


def test_front_matter_meets_page_contracts() -> None:
    front, _ = split_frontmatter(_text())
    assert front["title"] == "Educator Resources"
    assert 70 <= len(str(front["description"])) <= 160
    assert front["categories"] == ["resources"]


def test_page_has_at_least_three_modules() -> None:
    numbers = sorted(_modules())
    assert len(numbers) >= MIN_MODULES, f"only {len(numbers)} modules"
    assert numbers == list(range(1, len(numbers) + 1)), "modules must be numbered 1..N"


@pytest.mark.parametrize("heading", REQUIRED_SUBSECTIONS)
def test_every_module_has_required_subsection(heading: str) -> None:
    for number, module in _modules().items():
        assert heading in module, f"Module {number} lacks {heading!r}"


def test_every_exercise_has_a_worked_solution() -> None:
    for number, module in _modules().items():
        exercises = re.findall(rf"\*\*Exercise ({number}\.\d+)", module)
        solutions = re.findall(rf'title="Solution to Exercise ({number}\.\d+)"', module)
        assert exercises, f"Module {number} has no exercises"
        assert exercises == solutions, f"Module {number}: {exercises} vs solutions {solutions}"


def test_every_module_states_learning_objectives() -> None:
    for number, module in _modules().items():
        objectives = _subsection(module, "### Learning Objectives")
        assert len(re.findall(r"^- ", objectives, re.MULTILINE)) >= 2, number


def test_reading_paths_use_existing_site_pages() -> None:
    for number, module in _modules().items():
        reading = _subsection(module, "### Reading Path")
        targets = [t for t in LINK.findall(reading) if not t.startswith("http")]
        assert len(targets) >= MIN_READING_LINKS, f"Module {number} reading path too short"
        for target in targets:
            assert _resolves(target), f"Module {number}: unresolved link {target}"


def test_all_internal_links_resolve_and_use_relative_html() -> None:
    for target in LINK.findall(_text()):
        if target.startswith(("http", "#", "mailto:")):
            continue
        assert not target.split("#")[0].endswith(".qmd"), target
        assert not target.startswith("/"), target
        assert _resolves(target), f"unresolved link {target}"


def test_licence_notice_follows_owner_ruling() -> None:
    text = _flat()
    assert "## Reuse and Licence" in _text()
    assert "CC BY 4.0" in text
    assert CC_BY_URL in text
    assert "MIT" in text
    assert "COPYRIGHT.md" in text
    assert "figures" in text.lower()


def test_page_is_linked_from_site_navigation() -> None:
    config = yaml.safe_load((ROOT / "_quarto.yml").read_text(encoding="utf-8"))
    footer = config["website"]["page-footer"]["right"]
    links = {item["text"]: item["href"] for item in footer}
    assert links.get("Educator Resources") == PAGE_HREF


# --- Module 2: constraint torques at the wrist ------------------------------


def _rx(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])


def _ry(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])


def test_wrist_reciprocal_direction_answers() -> None:
    phi, psi = math.radians(30.0), math.radians(20.0)
    rotation = _rx(phi) @ _ry(psi)
    a = np.array([1.0, 0.0, 0.0])
    b = _rx(phi) @ np.array([0.0, 1.0, 0.0])
    n_forearm = np.cross(a, b)
    n_hand = rotation.T @ n_forearm
    assert abs(n_forearm @ a) < 1e-12 and abs(n_forearm @ b) < 1e-12
    for value in (*n_forearm[1:], n_hand[0], n_hand[2]):
        _assert_states(float(value), 6)


def test_wrist_reaction_depends_on_input() -> None:
    mass = np.array([[2.0, 0.0, 0.5], [0.0, 2.0, 0.0], [0.5, 0.0, 2.0]])
    constraint = np.array([[0.0, 0.0, 1.0]])
    inputs = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    m_inv = np.linalg.inv(mass)
    gain = -np.linalg.solve(constraint @ m_inv @ constraint.T, constraint @ m_inv @ inputs)
    assert gain[0, 0] == pytest.approx(0.25)
    assert gain[0, 1] == pytest.approx(0.0)
    text = _flat()
    assert "\\lambda=u/4" in text.replace(" ", "")
    for value in (2 / 3.75, 0.5 / 3.75):
        _assert_states(value, 4)


def test_widget_transverse_inertia_answer() -> None:
    inertia = 0.200 * 0.85**2 + (1.0 / 3.0) * 0.100 * 1.0**2
    _assert_states(inertia, 6)
    _assert_states(inertia, 4)


def test_cardan_widget_ratio_answers() -> None:
    delta = math.radians(30.0)
    for phase_deg in (0.0, 60.0):
        denominator = 1.0 - math.sin(delta) ** 2 * math.sin(math.radians(phase_deg)) ** 2
        omega_ratio = math.cos(delta) / denominator
        _assert_states(omega_ratio, 4)
        _assert_states(1.0 / omega_ratio, 4)
    _assert_states(1.0 - 0.25 * 0.75, 4)


def test_torque_noise_integration_answers() -> None:
    sigma_tau, horizon = 0.15, 0.010
    for inertia, expected in ((0.005, 0.0015), (0.00015, 0.0500)):
        sigma_theta = horizon**2 * sigma_tau / (2.0 * inertia)
        assert sigma_theta == pytest.approx(expected)
        _assert_states(sigma_theta, 4)
    _assert_states(0.005 / 0.00015, 3)


# --- Module 3: proximal-distal energy accounting ----------------------------


def test_kinetic_energy_mismatch_answers() -> None:
    m2, mc, length, omega = 3.0, 1.0, 1.0, 2.0
    tip = 0.5 * (m2 + mc) * length**2 * omega**2
    rod = 0.5 * (m2 / 3.0 + mc) * length**2 * omega**2
    assert (tip, rod) == (pytest.approx(8.0), pytest.approx(4.0))
    text = _flat()
    for joules in (tip, rod):
        assert re.search(rf"={joules:g}\$? J", text), f"page does not state {joules:g} J"


def test_two_hand_couple_answer() -> None:
    f_right, f_left = np.array([10.0, 0.0, 0.0]), np.array([-10.0, 0.0, 0.0])
    separation = np.array([0.0, 0.0, 0.1])
    moment = np.cross(separation / 2.0, f_right - f_left)
    assert np.allclose(f_right + f_left, 0.0)
    assert np.allclose(moment, [0.0, 1.0, 0.0])
    assert "(0,1,0)" in _flat().replace(" ", "").replace("\\,", "")


# --- Module 4: control-affine dynamics and counterfactuals ------------------


def test_reachable_interval_answers() -> None:
    low0, high0 = constant_additive_drift_interval(
        initial_state=0.0, drift=0.0, control_bound=1.0, horizon=1.0
    )
    low1, high1 = constant_additive_drift_interval(
        initial_state=0.0, drift=100.0, control_bound=1.0, horizon=1.0
    )
    assert high0 - low0 == pytest.approx(high1 - low1) == pytest.approx(2.0)
    flat = _flat().replace(" ", "")
    assert f"[{low0:g},{high0:g}]" in flat and f"[{low1:g},{high1:g}]" in flat


def test_pendulum_drift_and_linearization_answers() -> None:
    pendulum = SimplePendulum(m=1.0, L=1.0, g=GRAVITY_M_S2)
    state, control = np.array([0.5, 0.0]), np.array([0.0])
    drift = pendulum.dynamics(x=state, u=control)
    a_matrix, _ = pendulum.linearize(x=state, u=control)
    _assert_states(float(drift[1]), 4)
    _assert_states(float(a_matrix[1, 0]), 4)
    _assert_states(math.sin(0.5), 6)
    _assert_states(math.cos(0.5), 6)


def test_ztcf_pointwise_sample_answer() -> None:
    sample = GolfModel().drift_acceleration(np.zeros(3), np.zeros(3))
    for value in sample:
        _assert_states(float(value), 2)


def test_superposition_increment_answer() -> None:
    q, qd = np.array([0.5, -0.3]), np.array([1.0, 0.5])
    mass = double_pendulum_mass_matrix(q, 1.0, 1.0, 1.0, 1.0)
    bias = double_pendulum_coriolis(q, qd, 1.0, 1.0, 1.0) @ qd

    def response(torque: np.ndarray) -> np.ndarray:
        return np.linalg.solve(mass, torque - bias)

    zero = response(np.zeros(2))
    first, second = response(np.array([2.0, 0.0])), response(np.array([0.0, 1.0]))
    combined = first + second - zero
    assert np.allclose(combined, response(np.array([2.0, 1.0])))
    for value in (*zero, *first, *second, *combined):
        _assert_states(float(value), 4)
