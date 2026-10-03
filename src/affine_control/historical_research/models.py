"""Immutable, detached local research records; no scientific publication authority."""

import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from src.affine_control.programming_companion import ImportRequest

MAX_BYTES = 1_000_000


@dataclass(frozen=True)
class ResearchImportPins:
    """Reviewed independent schema/manifest hashes and byte-size expectations."""

    request: ImportRequest
    manifest_bytes: int
    schema_bytes: int

    def __post_init__(self) -> None:
        self.request.validate_digests()
        for size in (self.manifest_bytes, self.schema_bytes):
            if type(size) is not int or not 0 < size <= MAX_BYTES:
                raise ValueError("Research byte pins must be positive bounded integers")


@dataclass(frozen=True)
class ResearchIdentity:
    """Stable identity suitable for arbitrary historical players."""

    player_id: str
    player_name: str
    swing_id: str
    fit_id: str


@dataclass(frozen=True)
class SourceClock:
    """Exact video presentation interval, never a physical swing clock."""

    start: Fraction
    end: Fraction
    frame_count: int


@dataclass(frozen=True)
class HistoricalResearchRecord:
    """Validated record with immutable evidence bytes and detached serialization."""

    identity: ResearchIdentity
    producer_commit: str
    source_clock: SourceClock
    evidence_json: bytes

    def to_record(self) -> dict[str, Any]:
        """Return a fresh JSON copy; modifications cannot alter admitted evidence."""
        value: dict[str, Any] = json.loads(self.evidence_json)
        return value


@dataclass(frozen=True)
class HistoricalResearchPackage:
    """Checked package bytes and typed records, scoped exclusively to local research."""

    source_commit: str
    manifest_sha256: str
    manifest_bytes: bytes
    records: tuple[HistoricalResearchRecord, ...]
