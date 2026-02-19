"""Utilities for data validation."""

try:
    from pydantic import BaseModel, ValidationError
except ImportError:
    BaseModel = object
    ValidationError = Exception


class BaseValidator(BaseModel):
    """Base class for data validation using Pydantic."""

    pass
