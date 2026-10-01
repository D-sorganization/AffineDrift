"""Tests for Chapter 3 Hill-type muscle model contracts."""

import ast
import inspect
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

TEX_PATH = (
    Path(__file__).resolve().parents[1]
    / "articles/The_Geometry_of_Motion/Volume_III/chapters/ch03_muscle_models.tex"
)


@pytest.fixture(scope="module")
def muscle_mod() -> Any:
    content = TEX_PATH.read_text(encoding="utf-8")
    pattern = r"\\begin\{lstlisting\}(?:\[.*?\])?\s*\n(.*?)\\end\{lstlisting\}"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        pytest.fail("Python listing not found in TeX source.")
    tree = ast.parse(match.group(1))
    retained = [
        node
        for node in tree.body
        if isinstance(
            node,
            (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        )
    ]
    exec_tree = ast.fix_missing_locations(ast.Module(body=retained, type_ignores=[]))
    compiled = compile(exec_tree, filename="<ch03_listing>", mode="exec")
    namespace: dict[str, Any] = {}
    exec(compiled, namespace)
    return SimpleNamespace(**namespace)


class TestForceLengthPassiveContract:
    def test_boundary_values_and_slack(self, muscle_mod: Any) -> None:
        flp = muscle_mod.force_length_passive
        assert flp(1.0) == pytest.approx(0.0)
        assert flp(1.6) == pytest.approx(1.0)
        assert flp(1.05) > 0.0

    def test_default_kpe_updated_to_five(self, muscle_mod: Any) -> None:
        sig = inspect.signature(muscle_mod.force_length_passive)
        assert sig.parameters["kPE"].default == 5


class TestForceLengthActiveContract:
    def test_gaussian_actual_values(self, muscle_mod: Any) -> None:
        fla = muscle_mod.force_length_active
        expected = 0.5737534207374327
        assert fla(0.5) == pytest.approx(expected)
        assert fla(1.5) == pytest.approx(expected)
        assert fla(1.0) == pytest.approx(1.0)


class TestForceVelocityContract:
    def test_thelen_interior_endpoints_and_monotonicity(self, muscle_mod: Any) -> None:
        fv = muscle_mod.force_velocity
        a = 0.5
        c = 0.25 + 0.75 * a
        assert fv(-c, a) == pytest.approx(0.0)
        assert fv(0.0, a) == pytest.approx(1.0)
        v_grid = np.linspace(-c, 0.0, 10)
        forces = [fv(v, a) for v in v_grid]
        assert np.all(np.diff(forces) > 0.0)

    def test_independent_inverse_reproduction(self, muscle_mod: Any) -> None:
        fv = muscle_mod.force_velocity
        a, Af, Flen = 0.5, 0.25, 1.4
        c = 0.25 + 0.75 * a

        r_short = 0.4
        v_short = c * (r_short - 1.0) / (1.0 + r_short / Af)
        assert fv(v_short, a, Af=Af, Flen=Flen) == pytest.approx(r_short)

        r_leng = 1.2
        v_leng = c * (r_leng - 1.0) * (Flen - 1.0) / ((2.0 + 2.0 / Af) * (Flen - r_leng))
        assert fv(v_leng, a, Af=Af, Flen=Flen) == pytest.approx(r_leng)

    @pytest.mark.parametrize(
        "case",
        [
            (-0.7, 0.5, 0.25, 1.4),
            (0.0, -0.1, 0.25, 1.4),
            (0.0, 1.1, 0.25, 1.4),
            (np.nan, 0.5, 0.25, 1.4),
            (0.0, np.nan, 0.25, 1.4),
            (0.0, 0.5, 0.0, 1.4),
            (0.0, 0.5, -0.1, 1.4),
            (0.0, 0.5, 0.25, 1.0),
            (0.0, 0.5, 0.25, 0.9),
        ],
    )
    def test_domain_validation_errors(
        self, muscle_mod: Any, case: tuple[float, float, float, float]
    ) -> None:
        v_tilde, a, Af, Flen = case
        with pytest.raises(ValueError):
            muscle_mod.force_velocity(v_tilde, a, Af=Af, Flen=Flen)


class TestMuscleForceAndPennationContract:
    def test_pennation_singularity_raises_value_error(self, muscle_mod: Any) -> None:
        l0_M, alpha0 = 0.1, 0.2
        crit = l0_M * np.sin(alpha0)
        params = muscle_mod.MuscleParameters(
            F0=200.0,
            l0_M=l0_M,
            v0=1.0,
            l_T_slack=0.2,
            alpha0=alpha0,
            gamma=0.45,
            Af=0.25,
            kPE=4.0,
            e0=0.6,
        )
        with pytest.raises(ValueError):
            muscle_mod.muscle_force(0.5, crit, 0.0, params)

    @pytest.mark.parametrize("invalid_a", [-0.1, 1.1, np.nan, np.inf])
    def test_invalid_activation_rejected(self, muscle_mod: Any, invalid_a: float) -> None:
        params = muscle_mod.MuscleParameters(
            F0=200.0,
            l0_M=0.1,
            v0=1.0,
            l_T_slack=0.2,
            alpha0=0.2,
            gamma=0.45,
            Af=0.25,
            kPE=4.0,
            e0=0.6,
        )
        with pytest.raises(ValueError):
            muscle_mod.muscle_force(invalid_a, 0.1, 0.0, params)

    @pytest.mark.parametrize(
        ("param_key", "invalid_val"),
        [
            ("F0", 0.0),
            ("F0", -10.0),
            ("l0_M", 0.0),
            ("l0_M", -0.1),
            ("v0", 0.0),
            ("v0", -1.0),
            ("l_T_slack", 0.0),
            ("alpha0", -0.1),
            ("alpha0", np.pi / 2),
            ("alpha0", 1.6),
        ],
    )
    def test_physical_units_validation(
        self, muscle_mod: Any, param_key: str, invalid_val: float
    ) -> None:
        kw = {
            "F0": 200.0,
            "l0_M": 0.1,
            "v0": 1.0,
            "l_T_slack": 0.2,
            "alpha0": 0.2,
            "gamma": 0.45,
            "Af": 0.25,
            "kPE": 4.0,
            "e0": 0.6,
        }
        kw[param_key] = invalid_val
        with pytest.raises(ValueError):
            params = muscle_mod.MuscleParameters(**kw)
            muscle_mod.muscle_force(0.5, 0.1, 0.0, params)

    def test_reference_operating_point_tendon_force(self, muscle_mod: Any) -> None:
        params = muscle_mod.MuscleParameters(
            F0=200.0,
            l0_M=0.1,
            v0=1.0,
            l_T_slack=0.2,
            alpha0=0.2,
            gamma=0.45,
            Af=0.25,
            kPE=4.0,
            e0=0.6,
        )
        total, active, passive = muscle_mod.muscle_force(0.5, 0.1, 0.0, params)
        expected = 100.0 * np.cos(0.2)
        assert (total, active, passive) == pytest.approx((expected, expected, 0.0))
        assert np.isfinite(total) and total >= 0.0


@pytest.mark.parametrize("force_ratio", [0.4, 1.2])
def test_manufactured_series_equilibrium(muscle_mod: Any, force_ratio: float) -> None:
    """Close series force balance with an independently inverted tendon law."""
    params = muscle_mod.MuscleParameters(200.0, 0.1, 1.0, 0.2, 0.2)
    activation, fiber_length = 0.5, 0.11
    cosine = np.sqrt(1.0 - (params.l0_M * np.sin(params.alpha0) / fiber_length) ** 2)
    active_length = np.exp(-((fiber_length / params.l0_M - 1.0) ** 2) / 0.45)
    passive = np.expm1(5.0 * (fiber_length / params.l0_M - 1.0) / 0.6) / np.expm1(5.0)
    required_force = params.F0 * (activation * active_length * force_ratio + passive) * cosine
    strain = np.log1p(required_force / params.F0 * np.expm1(35.0 * 0.04)) / 35.0
    path_length = params.l_T_slack * (1.0 + strain) + fiber_length * cosine
    tendon_length = path_length - fiber_length * cosine
    tendon_force = params.F0 * np.expm1(35.0 * (tendon_length / params.l_T_slack - 1.0))
    tendon_force /= np.expm1(35.0 * 0.04)
    speed_scale = 0.25 + 0.75 * activation
    if force_ratio <= 1.0:
        velocity = params.v0 * speed_scale * (force_ratio - 1.0) / (1.0 + force_ratio / 0.25)
    else:
        velocity = (
            params.v0 * speed_scale * (force_ratio - 1.0) * 0.4 / (10.0 * (1.4 - force_ratio))
        )
    transmitted, _, _ = muscle_mod.muscle_force(activation, fiber_length, velocity, params)
    assert transmitted == pytest.approx(tendon_force, rel=1e-12)
