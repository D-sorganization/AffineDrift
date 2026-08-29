"""Immutable provider-consumer contracts for the AffineDrift companion site."""

from .manifest_consumer import (
    CompanionConsumer,
    CompanionImportError,
    CompanionPin,
    FetchedPayload,
    HttpFetcher,
    InstalledCompanion,
    UpdateCheck,
    validate_lock,
)

__all__ = [
    "CompanionConsumer",
    "CompanionImportError",
    "CompanionPin",
    "FetchedPayload",
    "HttpFetcher",
    "InstalledCompanion",
    "UpdateCheck",
    "validate_lock",
]
