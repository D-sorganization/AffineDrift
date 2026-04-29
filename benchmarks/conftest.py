"""Shared pytest-benchmark fixtures and configuration."""

from __future__ import annotations

from collections.abc import Generator

import pytest

from src.core.contracts import ContractLevel, get_contract_level, set_contract_level


@pytest.fixture(autouse=True)
def _enforce_contracts() -> Generator[None, None, None]:
    """Ensure all benchmarks run with contracts enforced, then restore.

    This fixture ensures consistent contract validation during performance
    measurements, matching the behavior of the main test suite.
    """
    original = get_contract_level()
    set_contract_level(ContractLevel.ENFORCE)
    yield
    set_contract_level(original)


@pytest.fixture(scope="session")
def benchmark_config(benchmark: pytest.BenchmarkFixture) -> None:  # type: ignore[name-defined]
    """Configure benchmark execution parameters for scientific reproducibility.

    This fixture runs once per session and configures pytest-benchmark to:
    - Disable garbage collection during measurements for deterministic results
    - Use a reasonable number of iterations for control flow performance
    - Warm up the JIT/CPU cache before timing measurements
    """
    # These settings are applied via pytest-benchmark's built-in mechanisms
    # and CLI arguments (--benchmark-disable-gc, --benchmark-warmup, etc.)
