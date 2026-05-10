"""Shared pytest fixtures and configuration.

Top-level conftest also enforces thread-safety env vars and disables real
network calls for unit-marked tests. See FLEET_TESTING_STANDARDS.md §5.
"""

from __future__ import annotations

import os

# C-extension thread safety. Many "xdist worker crashed" failures come from
# MKL/OpenBLAS forking under xdist. Pin to single-threaded for tests.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

# matplotlib headless backend, set before any matplotlib import.
os.environ.setdefault("MPLBACKEND", "Agg")

# Qt headless backend, for repos that import PyQt/PySide indirectly.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from collections.abc import (
    Generator,  # noqa: E402 -- reason: thread-safety env vars must be set before these heavy imports
)

import pytest  # noqa: E402 -- reason: thread-safety env vars must be set before these heavy imports

from src.core.contracts import (  # noqa: E402 -- reason: thread-safety env vars must be set before these heavy imports
    ContractLevel,
    get_contract_level,
    set_contract_level,
)


@pytest.fixture(autouse=True)
def _enforce_contracts() -> Generator[None, None, None]:
    """Ensure all tests run with contracts enforced, then restore.

    This is the canonical location for this fixture. Previously it was
    duplicated in ``tests/test_properties.py`` and
    ``tests/unit/test_contracts.py`` (issue #1251).
    """
    original = get_contract_level()
    set_contract_level(ContractLevel.ENFORCE)
    yield
    set_contract_level(original)


@pytest.fixture(autouse=True)
def _no_real_network_in_unit_lane(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Block real outbound HTTP from unit-marked tests by default.

    See FLEET_TESTING_STANDARDS.md §5. Tests that legitimately need network
    must be marked ``requires_network`` (and typically ``slow``).
    """
    if "unit" not in request.keywords:
        return

    def _refuse(*_a: object, **_kw: object) -> None:
        raise RuntimeError(
            "Unit test made a real network call. Mock with `responses` or "
            "`pytest-httpx`, or mark the test `@pytest.mark.requires_network`."
        )

    for module in ("httpx", "requests", "urllib.request"):
        try:
            mod = __import__(module, fromlist=["*"])
            for attr in ("get", "post", "put", "delete", "request"):
                if hasattr(mod, attr):
                    monkeypatch.setattr(mod, attr, _refuse, raising=False)
        except ImportError:
            pass
