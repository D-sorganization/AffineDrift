"""Immutable, provider-independent UpstreamDrift companion consumer."""

from .consumer import CompanionConsumer
from .errors import AcquisitionError, ExistingPinConflict
from .models import FetchResult, ImportRequest, ProvenanceRecord, UpdateReport
from .policy import ConsumerPolicy
from .store import SnapshotStore
from .transport import DirectoryTransport, RequestsTransport, Transport

__all__ = [
    "AcquisitionError",
    "CompanionConsumer",
    "ConsumerPolicy",
    "DirectoryTransport",
    "ExistingPinConflict",
    "FetchResult",
    "ImportRequest",
    "ProvenanceRecord",
    "RequestsTransport",
    "SnapshotStore",
    "Transport",
    "UpdateReport",
]
