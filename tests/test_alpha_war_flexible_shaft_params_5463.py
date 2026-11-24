"""Expose Study 6 stiffness-oracle tests to repository pytest (#5463 slice 2)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_CALCS_TEST = (
    Path(__file__).resolve().parents[1]
    / "research/alpha-war/calcs/test_alpha_war_flexible_shaft_params.py"
)
_spec = importlib.util.spec_from_file_location("alpha_war_flexible_shaft_params_tests", _CALCS_TEST)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load Alpha War flexible-shaft tests from {_CALCS_TEST}")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TestAlphaWarFlexibleShaftParams = _mod.TestAlphaWarFlexibleShaftParams
