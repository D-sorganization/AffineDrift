"""Local-only immutable historical research admission and deterministic presentation."""

from .admission import admit_package, validate_research_schema
from .consumer import HistoricalResearchConsumer
from .models import (
    HistoricalResearchPackage,
    HistoricalResearchRecord,
    ResearchIdentity,
    ResearchImportPins,
    SourceClock,
)
from .rendering import render_research_page

__all__ = [
    "HistoricalResearchConsumer",
    "admit_package",
    "validate_research_schema",
    "HistoricalResearchPackage",
    "HistoricalResearchRecord",
    "ResearchIdentity",
    "ResearchImportPins",
    "SourceClock",
    "render_research_page",
]
