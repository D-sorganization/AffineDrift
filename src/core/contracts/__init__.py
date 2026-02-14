"""Design by Contract (DbC) enforcement for the AffineDrift platform.

This package provides lightweight helpers and decorators for enforcing
pre-conditions, post-conditions, and invariants at runtime.

This ``__init__`` re-exports all public symbols from the sub-modules so
that existing ``from src.core.contracts import ...`` imports continue to
work without modification.

See ``definitions.py`` for core primitives and ``validators.py`` for
numeric helpers.
"""

from __future__ import annotations

# ─── Re-export everything from sub-modules for backward compatibility ──
from src.core.contracts.definitions import (
    CONTRACTS_ENABLED,
    DBC_LEVEL,
    ContractChecker,
    ContractLevel,
    ContractViolationError,
    InvariantError,
    PostconditionError,
    PreconditionError,
    _handle_violation,
    _resolve_contract_level,
    ensure,
    get_contract_level,
    invariant,
    invariant_checked,
    postcondition,
    precondition,
    require,
    set_contract_level,
)
from src.core.contracts.validators import (
    check_finite_array,
    check_non_negative,
    check_positive,
    check_range,
    check_shape,
)

__all__ = [
    # Enforcement levels
    "ContractLevel",
    "DBC_LEVEL",
    "CONTRACTS_ENABLED",
    "set_contract_level",
    "get_contract_level",
    # Exceptions
    "ContractViolationError",
    "PreconditionError",
    "PostconditionError",
    "InvariantError",
    # Core primitives
    "require",
    "ensure",
    "invariant",
    # Decorators
    "precondition",
    "postcondition",
    "invariant_checked",
    # Class mixin
    "ContractChecker",
    # Validators
    "check_finite_array",
    "check_positive",
    "check_non_negative",
    "check_range",
    "check_shape",
]
