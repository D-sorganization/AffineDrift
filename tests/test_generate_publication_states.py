"""Publication definitions must follow the existing maturity vocabulary."""

from dataclasses import replace

import pytest

from scripts.generate_publication_states import OUTPUT, render_definitions
from src.tools.utils.maturity import load_maturity_config


def test_all_definitions_and_boundaries_are_preserved() -> None:
    vocabulary = load_maturity_config()
    rendered = render_definitions(vocabulary)
    for state in vocabulary.states.values():
        assert state.definition in rendered
        assert state.does_not_establish in rendered
        assert rendered.count(f"**{state.label}**") == 1


def test_committed_definitions_are_current() -> None:
    assert OUTPUT.read_text(encoding="utf-8") == render_definitions(load_maturity_config())
    assert b"\r\n" not in OUTPUT.read_bytes(), "Evidence hashes require portable LF bytes"


def test_changed_authority_flows_to_both_reader_surfaces() -> None:
    vocabulary = load_maturity_config()
    states = dict(vocabulary.states)
    states["available"] = replace(states["available"], definition="Updated canonical definition.")
    assert "Updated canonical definition." in render_definitions(replace(vocabulary, states=states))


def test_incomplete_vocabulary_is_rejected() -> None:
    vocabulary = load_maturity_config()
    with pytest.raises(ValueError, match="canonical states"):
        render_definitions(replace(vocabulary, states={}))


def test_empty_boundary_is_rejected() -> None:
    vocabulary = load_maturity_config()
    states = dict(vocabulary.states)
    states["available"] = replace(states["available"], does_not_establish="")
    with pytest.raises(ValueError, match="non-empty"):
        render_definitions(replace(vocabulary, states=states))
