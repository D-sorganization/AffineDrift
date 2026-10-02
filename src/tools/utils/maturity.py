"""Maturity vocabulary schema and validation (WEB-04.1 #4515).

Loads and enforces the controlled maturity vocabulary from config/maturity.yml.
Defines the canonical six-state publication enum, definitions, scope boundaries,
and legacy string mappings.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml

from src.core.contracts import require


class CanonicalMaturityState(StrEnum):
    """Canonical 6-state publication enum (pages/how-to-read.qmd#publication-states)."""

    AVAILABLE = "available"
    VALIDATED = "validated"
    EXPERIMENTAL = "experimental"
    PLANNED = "planned"
    DEPRECATED = "deprecated"
    OPINION = "opinion"


@dataclass(frozen=True)
class MaturityStateDefinition:
    """Full semantic specification of a canonical publication state."""

    key: str
    label: str
    definition: str
    establishes: str
    does_not_establish: str


@dataclass(frozen=True)
class MaturityVocabulary:
    """Loaded configuration from config/maturity.yml."""

    states: dict[str, MaturityStateDefinition]
    legacy_mappings: dict[str, str]

    def is_canonical(self, key: str) -> bool:
        """Check if a string is a recognized canonical state key."""
        return key.strip().lower() in self.states

    def canonical_keys(self) -> set[str]:
        """Set of all valid canonical state keys."""
        return set(self.states.keys())

    def resolve(self, raw: str, *, allow_legacy: bool = True) -> str:
        """Resolve a raw status string to a canonical state key.

        Raises ValueError if the status is not in the vocabulary.
        """
        require(
            isinstance(raw, str) and bool(raw.strip()), "status must be a non-empty string", raw
        )
        clean = raw.strip().lower()
        if clean in self.states:
            return clean

        if allow_legacy and clean in self.legacy_mappings:
            return self.legacy_mappings[clean]

        raise ValueError(
            f"Invalid maturity status '{raw}'. Must be one of canonical states "
            f"{sorted(self.states.keys())}"
            + (
                f" or known legacy mappings {sorted(self.legacy_mappings.keys())}"
                if allow_legacy
                else ""
            )
        )


_CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "maturity.yml"
_CACHED_VOCABULARY: MaturityVocabulary | None = None


def load_maturity_config(config_path: Path | str | None = None) -> MaturityVocabulary:
    """Load and validate the maturity vocabulary configuration."""
    global _CACHED_VOCABULARY
    if config_path is None and _CACHED_VOCABULARY is not None:
        return _CACHED_VOCABULARY

    path = Path(config_path) if config_path is not None else _CONFIG_PATH
    require(path.is_file(), f"Maturity configuration file not found: {path}")

    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    require("states" in data, "config/maturity.yml must contain 'states' key")
    require("legacy_mappings" in data, "config/maturity.yml must contain 'legacy_mappings' key")

    raw_states = data["states"]
    require(isinstance(raw_states, dict), "'states' must be a mapping")

    states: dict[str, MaturityStateDefinition] = {}
    for key, spec in raw_states.items():
        require(isinstance(spec, dict), f"State '{key}' definition must be a mapping")
        for req_field in ("label", "definition", "establishes", "does_not_establish"):
            require(req_field in spec, f"State '{key}' missing required field: {req_field}")
        states[key.strip().lower()] = MaturityStateDefinition(
            key=key.strip().lower(),
            label=str(spec["label"]).strip(),
            definition=str(spec["definition"]).strip(),
            establishes=str(spec["establishes"]).strip(),
            does_not_establish=str(spec["does_not_establish"]).strip(),
        )

    # Ensure all enum values are present in states
    enum_keys = {e.value for e in CanonicalMaturityState}
    missing_enum = enum_keys - set(states.keys())
    require(not missing_enum, f"Missing canonical enum states in maturity config: {missing_enum}")

    raw_mappings = data["legacy_mappings"]
    require(isinstance(raw_mappings, dict), "'legacy_mappings' must be a mapping")
    legacy_mappings: dict[str, str] = {}
    for legacy_key, target in raw_mappings.items():
        clean_target = str(target).strip().lower()
        require(
            clean_target in states,
            f"Legacy mapping '{legacy_key}' maps to unknown target state '{target}'",
        )
        legacy_mappings[str(legacy_key).strip().lower()] = clean_target

    vocab = MaturityVocabulary(states=states, legacy_mappings=legacy_mappings)
    if config_path is None:
        _CACHED_VOCABULARY = vocab
    return vocab
