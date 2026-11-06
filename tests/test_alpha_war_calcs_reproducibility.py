"""Expose Alpha War calcs reproducibility guards to repository pytest (#5465)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_CALCS_TEST = (
    Path(__file__).resolve().parents[1]
    / "research/alpha-war/calcs/test_alpha_war_reproducibility.py"
)
_spec = importlib.util.spec_from_file_location("alpha_war_reproducibility_tests", _CALCS_TEST)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load Alpha War reproducibility tests from {_CALCS_TEST}")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TestAlphaWarReproducibility = _mod.TestAlphaWarReproducibility
