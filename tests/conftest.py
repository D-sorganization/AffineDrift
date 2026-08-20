"""Shared pytest fixtures and configuration.

Top-level conftest also enforces thread-safety env vars and disables real
network calls for unit-marked tests. See FLEET_TESTING_STANDARDS.md §5.
"""

from __future__ import annotations

import os
import socket

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

from collections.abc import (  # noqa: E402 -- reason: thread-safety env vars must be set before these heavy imports
    Callable,
    Generator,
)

import pytest  # noqa: E402 -- reason: thread-safety env vars must be set before these heavy imports

from src.core.contracts import (  # noqa: E402 -- reason: thread-safety env vars must be set before these heavy imports
    ContractLevel,
    get_contract_level,
    set_contract_level,
)

# A genuinely public IPv4 address, used to stub DNS in offline tests.
#
# Do NOT "improve" this to a TEST-NET documentation range (192.0.2.x,
# 198.51.100.x, 203.0.113.x): Python's ``ipaddress`` module classifies all
# three as private, so an SSRF guard that rejects private addresses would
# reject the stub too and the tests would fail exactly as they do offline.
PUBLIC_STUB_IP = "93.184.216.34"


@pytest.fixture
def dns_stub(monkeypatch: pytest.MonkeyPatch) -> Callable[[str | BaseException], None]:
    """Pin ``socket.getaddrinfo`` to a fixed answer for the duration of a test.

    Call the returned installer with an IP string to make every hostname
    resolve to it, or with an exception instance (typically
    ``socket.gaierror``) to simulate resolution failure.

    SSRF guards such as ``src.tools.verify_images.is_safe_url`` resolve the
    hostname before any HTTP call, so patching ``requests`` alone does not make
    a test hermetic — the guard still hits real DNS and fails closed whenever
    the machine is offline or the network restricts lookups.
    """

    def _install(answer: str | BaseException) -> None:
        def _resolve(
            *_args: object, **_kwargs: object
        ) -> list[tuple[int, int, int, str, tuple[str, int] | tuple[str, int, int, int]]]:
            if isinstance(answer, BaseException):
                raise answer
            if ":" in answer:
                return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", (answer, 0, 0, 0))]
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (answer, 0))]

        monkeypatch.setattr(socket, "getaddrinfo", _resolve)

    return _install


@pytest.fixture
def stub_public_dns(dns_stub: Callable[[str | BaseException], None]) -> str:
    """Resolve every hostname to a fixed public address, and return it.

    Use in tests that mock HTTP but still cross an SSRF guard, so the guard
    admits the URL regardless of whether the machine has working DNS.
    """
    dns_stub(PUBLIC_STUB_IP)
    return PUBLIC_STUB_IP


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
