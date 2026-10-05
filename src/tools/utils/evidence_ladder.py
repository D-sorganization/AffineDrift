"""Evidence ladder rungs and the measured-record rule (WEB-04.3 #4517).

Loads the ordered rungs from ``config/maturity.yml`` and enforces that no page
claims a rung above "qualified simulation" without linking a measured
participant data record: an ``evidence-record`` naming a ``data/datasets.yml``
entry flagged ``measured_participant_data: true``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import yaml

from src.core.contracts import require

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = REPO_ROOT / "config" / "maturity.yml"
DATASETS_PATH = REPO_ROOT / "data" / "datasets.yml"

CANONICAL_RUNGS: tuple[str, ...] = (
    "mathematical-identity",
    "manufactured-fixture",
    "qualified-simulation",
    "measured-participant-result",
    "replicated-result",
    "bounded-application",
)


@dataclass(frozen=True)
class EvidenceRung:
    """One rung of the evidence ladder."""

    key: str
    label: str
    definition: str
    requires_measured_data: bool


@dataclass(frozen=True)
class EvidenceLadder:
    """The ordered rungs plus accepted alternative spellings."""

    rungs: tuple[EvidenceRung, ...]
    aliases: Mapping[str, str]

    def resolve(self, raw: str) -> str | None:
        """Canonical rung key for ``raw``, or None when it is not a known rung."""
        clean = raw.strip().lower()
        if clean in CANONICAL_RUNGS:
            return clean
        return self.aliases.get(clean)

    def requires_measured_data(self, raw: str) -> bool:
        """Whether ``raw`` needs a measured record; unknown rungs fail closed."""
        key = self.resolve(raw)
        return key is None or next(r for r in self.rungs if r.key == key).requires_measured_data


def _rung(spec: Any) -> EvidenceRung:
    """Parse one ``evidence_rungs`` entry, rejecting a missing field."""
    require(isinstance(spec, dict), "each evidence rung must be a mapping", spec)
    for field in ("key", "label", "definition", "requires_measured_data"):
        require(field in spec, f"evidence rung missing '{field}'", spec)
    return EvidenceRung(
        key=str(spec["key"]),
        label=str(spec["label"]).strip(),
        definition=str(spec["definition"]).strip(),
        requires_measured_data=bool(spec["requires_measured_data"]),
    )


@cache
def load_evidence_ladder(config_path: Path = CONFIG_PATH) -> EvidenceLadder:
    """Load and check the evidence ladder from ``config/maturity.yml``."""
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    rungs = tuple(_rung(spec) for spec in data.get("evidence_rungs") or [])
    require(
        tuple(r.key for r in rungs) == CANONICAL_RUNGS,
        "evidence_rungs must list the canonical rungs in order",
        [r.key for r in rungs],
    )
    needs = [r.requires_measured_data for r in rungs]
    require(needs == sorted(needs), "requires_measured_data must not drop once set", needs)
    aliases = {str(k).lower(): str(v) for k, v in (data.get("evidence_rung_aliases") or {}).items()}
    require(set(aliases.values()) <= set(CANONICAL_RUNGS), "aliases must target rungs", aliases)
    return EvidenceLadder(rungs=rungs, aliases=aliases)


@cache
def measured_record_ids(datasets_path: Path = DATASETS_PATH) -> frozenset[str]:
    """Ids of catalogue datasets flagged ``measured_participant_data: true``."""
    data = yaml.safe_load(datasets_path.read_text(encoding="utf-8")) or {}
    return frozenset(
        str(entry["id"])
        for section in data.values()
        if isinstance(section, list)
        for entry in section
        if isinstance(entry, dict) and entry.get("measured_participant_data") is True
    )


def check_evidence_rung(
    fm: Mapping[str, Any],
    rel_path: str,
    *,
    measured_ids: frozenset[str] | None = None,
) -> list[str]:
    """Errors for a page whose rung outruns its linked measured evidence."""
    raw = fm.get("evidence-rung")
    if raw is None or not load_evidence_ladder().requires_measured_data(str(raw)):
        return []
    record = fm.get("evidence-record")
    known = measured_record_ids() if measured_ids is None else measured_ids
    if record is None:
        return [
            f"{rel_path}: evidence-rung '{raw}' is above qualified-simulation and needs "
            "an 'evidence-record' naming a measured dataset in data/datasets.yml"
        ]
    if str(record) not in known:
        return [
            f"{rel_path}: evidence-record '{record}' is not a data/datasets.yml entry "
            "flagged measured_participant_data: true"
        ]
    return []
