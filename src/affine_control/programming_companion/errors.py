"""Errors raised by immutable programming-companion acquisition."""


class AcquisitionError(ValueError):
    """Reject an untrusted or malformed provider acquisition."""


class ExistingPinConflict(AcquisitionError):
    """Reject replacement of an active immutable publication pin."""
