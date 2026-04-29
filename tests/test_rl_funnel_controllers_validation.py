from __future__ import annotations

import numpy as np
import pytest

from src.core.contracts.definitions import ContractViolationError
from src.tools.rl_funnel_controllers import validate_weight_matrix


def test_validate_weight_matrix_rejects_wrong_shape() -> None:
    with pytest.raises(ContractViolationError, match="Q_sp must have shape"):
        validate_weight_matrix(np.eye(3), (4, 4), "Q_sp")


def test_validate_weight_matrix_accepts_expected_shape() -> None:
    validate_weight_matrix(np.eye(4), (4, 4), "Q_sp")
