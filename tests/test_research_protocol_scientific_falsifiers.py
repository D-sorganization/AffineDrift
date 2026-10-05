"""WEB-05.6 (#4527): every research protocol names a scientific falsifier.

The original falsifiers test process ("a manufactured null case is reported
as confirmation"). Each protocol must also state what observation would count
against its scientific hypothesis, name the measurement modality that would
make that observation, and say honestly why no power calculation exists yet.
The schema extension is optional, so older records stay valid.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from src.affine_control.research_readiness.programs import PROGRAMS, ProgramSeed

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = json.loads((ROOT / "data/research_protocols/library.json").read_text(encoding="utf-8"))
SCHEMA = json.loads(
    (ROOT / "schemas/research-protocol-readiness-v1.schema.json").read_text(encoding="utf-8")
)
PROCESS_WORDS = ("manufactured", "promoted", "reported as confirmation", "gate is satisfied")


def _specs() -> list[tuple[str, dict[str, object]]]:
    return [(p["protocol_id"], p["specification"]) for p in LIBRARY["protocols"]]


@pytest.mark.parametrize(("protocol_id", "spec"), _specs())
def test_each_protocol_has_a_scientific_falsifier(
    protocol_id: str, spec: dict[str, object]
) -> None:
    falsifiers = spec["analysis"]["scientific_falsifiers"]  # type: ignore[index]
    assert falsifiers, protocol_id
    for text in falsifiers:
        assert len(text) > 60, protocol_id
        assert not any(word in text for word in PROCESS_WORDS), (protocol_id, text)


@pytest.mark.parametrize(("protocol_id", "spec"), _specs())
def test_each_measurement_names_a_modality(protocol_id: str, spec: dict[str, object]) -> None:
    for measurement in spec["measurements"]:  # type: ignore[attr-defined]
        assert len(measurement["modality"]) > 20, protocol_id


def test_neural_timing_names_emg() -> None:
    spec = dict(_specs())["ad-protocol-neural-timing-001"]
    assert "EMG" in spec["measurements"][0]["modality"]  # type: ignore[index]


@pytest.mark.parametrize(("protocol_id", "spec"), _specs())
def test_power_statement_is_honest_about_its_basis(
    protocol_id: str, spec: dict[str, object]
) -> None:
    power = spec["analysis"]["power_plan"]  # type: ignore[index]
    record = next(p for p in LIBRARY["protocols"] if p["protocol_id"] == protocol_id)
    if record["participant_scope"] == "none":
        assert power.startswith("Not applicable"), protocol_id
    else:
        assert "No sample size" in power and "pilot" in power, protocol_id


def test_schema_extension_is_backward_compatible() -> None:
    record = copy.deepcopy(LIBRARY["protocols"][0])
    del record["specification"]["analysis"]["scientific_falsifiers"]
    for measurement in record["specification"]["measurements"]:
        del measurement["modality"]
    validator = jsonschema.Draft202012Validator(SCHEMA)
    assert list(validator.iter_errors({**LIBRARY, "protocols": [record]})) == []


def test_seed_contract_rejects_an_empty_falsifier() -> None:
    seed = PROGRAMS[0]
    fields = {name: getattr(seed, name) for name in seed.__dataclass_fields__}
    with pytest.raises(ValueError):
        ProgramSeed(**{**fields, "scientific_falsifier": " "})
