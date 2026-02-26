"""Data validation utilities using Pydantic.

This module provides base classes and utilities for validating data structures
using Pydantic models.
"""

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError

from src.tools.utils.logging_utils import setup_logging

logger = setup_logging(__name__)

T = TypeVar("T", bound="BaseValidator")


class BaseValidator(BaseModel):
    """Base class for data validation models.

    Inherits from pydantic.BaseModel and provides a helper method
    for safe validation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def validate_data(cls: type[T], data: dict[str, Any]) -> T | None:
        """Validate a dictionary against the model.

        Args:
            data: The data dictionary to validate.

        Returns:
            An instance of the validator model if valid, None otherwise.
        """
        try:
            return cls(**data)
        except ValidationError as e:
            logger.error(f"Validation error for {cls.__name__}: {e}")
            return None
