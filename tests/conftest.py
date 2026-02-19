"""Shared pytest fixtures and configuration."""

from __future__ import annotations

from collections.abc import Generator

import pytest

from src.core.contracts import ContractLevel, get_contract_level, set_contract_level


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
